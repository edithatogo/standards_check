import gzip
import json
import unittest
from unittest.mock import Mock, patch

from scripts.source_provider_evidence import (
    crossref_work, openalex_work, convert_ids, oai_article, fetch_priority,
    provider_observations, fetch,
)

DOI = "10.1234/example"
SPEC = {"edition": "example", "doi": DOI, "pmid": "123", "pmcid": "PMC42"}
ARTICLE = b'<article><front><article-meta><article-id pub-id-type="doi">10.1234/example</article-id></article-meta></front><body/></article>'
OAI = (b'<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/">'
       b'<GetRecord><record><header><identifier>oai:pubmedcentral.nih.gov:42</identifier></header>'
       b'<metadata>' + ARTICLE.replace(b'<article>', b'<article xmlns="">') +
       b'</metadata></record></GetRecord></OAI-PMH>')


class ProviderTests(unittest.TestCase):
    def test_transport_bounds_compression_and_no_redirect(self):
        for payload, encoding, status, cap, expected in (
            (b"ok", "", 200, 100, b"ok"),
            (gzip.compress(b"ok"), "gzip", 200, 100, b"ok"),
            (b"long", "", 200, 2, None),
            (gzip.compress(b"a" * 500), "gzip", 200, 100, None),
            (b"", "", 302, 100, None),
        ):
            with self.subTest(status=status, cap=cap, encoding=encoding):
                response = Mock(status=status)
                response.read.return_value = payload
                response.getheader.return_value = encoding
                connection = Mock()
                connection.getresponse.return_value = response
                with patch("scripts.source_provider_evidence.http.client.HTTPSConnection", return_value=connection):
                    if expected is None:
                        with self.assertRaises((ValueError, OSError)):
                            fetch("api.crossref.org", "/works/fixture", cap)
                    else:
                        self.assertEqual(fetch("api.crossref.org", "/works/fixture", cap), expected)
                connection.close.assert_called_once()
        with self.assertRaises(ValueError):
            fetch("example.org", "/anything")

    def test_both_acquisition_routes_can_remain_held(self):
        with patch("scripts.source_provider_evidence.fetch", side_effect=[TimeoutError(), TimeoutError()]):
            article, receipt = fetch_priority("PMC42")
        self.assertIsNone(article)
        self.assertEqual(len(receipt["attempts"]), 2)
        with self.assertRaises(ValueError):
            fetch_priority("PMC42/other")


    def test_explicit_plos_primary_article_route(self):
        doi = "10.1371/journal.pmed.1004587"
        with patch("scripts.source_provider_evidence.fetch", return_value=ARTICLE) as getter:
            raw, receipt = fetch_priority("PMC42", plos_doi=doi)
        getter.assert_called_once_with(
            "journals.plos.org",
            "/plosmedicine/article/file?id=10.1371%2Fjournal.pmed.1004587&type=manuscript",
        )
        self.assertEqual(raw, ARTICLE)
        self.assertEqual(receipt["provider"], "plos")
        self.assertEqual(receipt["response_bytes"], len(ARTICLE))
        self.assertEqual(receipt["representation"], "plos_publisher_jats_xml")

    def test_plos_fallback_and_rejection(self):
        doi = "10.1371/journal.pbio.3000410"
        with patch("scripts.source_provider_evidence.fetch", side_effect=[TimeoutError(), ARTICLE]) as getter:
            _, receipt = fetch_priority("PMC42", plos_doi=doi)
        self.assertEqual(getter.call_count, 2)
        self.assertIn("/plosbiology/", getter.call_args_list[0].args[1])
        self.assertEqual(receipt["provider"], "europe_pmc")
        self.assertEqual([a["provider"] for a in receipt["attempts"]], ["plos", "europe_pmc"])
        with patch("scripts.source_provider_evidence.fetch") as getter:
            with self.assertRaises(ValueError):
                fetch_priority("PMC42", plos_doi="10.1371/journal.pmed.1004587?x=1")
            getter.assert_not_called()

    def test_invalid_converter_response_remains_incomplete(self):
        with patch("scripts.source_provider_evidence.fetch", return_value=b'{"status":"error"}'), \
             patch("scripts.source_provider_evidence.time.sleep"):
            result = convert_ids("pmid", ["123"], "maintainer@example.org")
        self.assertEqual(result["123"]["status"], "lookup_incomplete")

    def test_crossref_doi_identity_and_safe_link_evidence(self):
        data = {"message": {"DOI": DOI.upper(), "title": ["Article"],
                            "license": [{"URL": "https://creativecommons.org/licenses/by/4.0/"}],
                            "link": [{"URL": "https://publisher.example/checklist.pdf?token=private"},
                                     {"URL": "file:///secret"}]}}
        with patch("scripts.source_provider_evidence.fetch", return_value=json.dumps(data).encode()):
            result = crossref_work(DOI)
        self.assertEqual(result["status"], "exact_doi_metadata")
        self.assertEqual(result["links"], ["https://publisher.example/checklist.pdf"])
        self.assertEqual(result["rights"], "metadata_only_not_reuse_permission")
        data["message"]["DOI"] = "10.1234/other"
        with patch("scripts.source_provider_evidence.fetch", return_value=json.dumps(data).encode()):
            self.assertEqual(crossref_work(DOI)["status"], "identifier_conflict")

    def test_openalex_rejects_conflicting_pmid(self):
        data = {"id": "https://openalex.org/W42", "doi": "https://doi.org/" + DOI,
                "ids": {"pmid": "https://pubmed.ncbi.nlm.nih.gov/123/"},
                "locations": [{"is_oa": True, "pdf_url": "https://publisher.example/a.pdf"}]}
        with patch("scripts.source_provider_evidence.fetch", return_value=json.dumps(data).encode()):
            self.assertEqual(openalex_work(DOI, "123")["status"], "exact_identifier_metadata")
            self.assertEqual(openalex_work(DOI, "999")["status"], "identifier_conflict")
            self.assertEqual(openalex_work(None, "123")["resolved_doi"], DOI)

    def test_pmc_conversion_retains_ambiguity_and_missing_not_nonexistence(self):
        data = {"status": "ok", "records": [
            {"requested-id": "123", "pmid": 123, "pmcid": "PMC42", "doi": DOI},
            {"requested-id": "456", "pmid": 456, "pmcid": "PMC43"},
            {"requested-id": "456", "pmid": 456, "pmcid": "PMC44"}]}
        with patch("scripts.source_provider_evidence.fetch", return_value=json.dumps(data).encode()):
            result = convert_ids("pmid", ["123", "456", "789"], "maintainer@example.org")
        self.assertEqual(result["123"]["pmcid"], "PMC42")
        self.assertEqual(result["456"]["status"], "ambiguous_identifier")
        self.assertEqual(result["789"]["status"], "no_pmc_mapping_observed")
        self.assertEqual(convert_ids("pmid", ["123"], None)["123"]["status"], "contact_not_configured")

    def test_oai_wrapper_binds_requested_identity_and_retains_response_fingerprint(self):
        article, evidence = oai_article(OAI, "PMC42")
        self.assertTrue(article.startswith(b"<article>"))
        self.assertEqual(evidence["representation"], "pmc_oai_article_xml_projection")
        self.assertNotEqual(evidence["response_sha256"], evidence["article_sha256"])
        for bad in (OAI.replace(b'nih.gov:42', b'nih.gov:43'),
                    b'<OAI-PMH><error>not permitted</error></OAI-PMH>'):
            with self.assertRaises(ValueError):
                oai_article(bad, "PMC42")

    def test_priority_fallback_only_on_transport_failure(self):
        with patch("scripts.source_provider_evidence.fetch", side_effect=[TimeoutError(), OAI]):
            article, evidence = fetch_priority("PMC42")
        self.assertEqual(evidence["provider"], "pmc_oai")
        self.assertEqual(evidence["attempts"][0]["status"], "transport_or_http_failure")
        with patch("scripts.source_provider_evidence.fetch", return_value=ARTICLE) as getter:
            _, evidence = fetch_priority("PMC42")
            self.assertEqual(getter.call_count, 1)
            self.assertEqual(evidence["representation"], "europe_pmc_primary_xml")

    def test_rejects_entity_bearing_non_utf8_oai(self):
        body = OAI.decode("utf-8").replace("<body/>", "<body>&inserted;</body>")
        raw = ('<!DOCTYPE OAI-PMH [<!ENTITY inserted "unsafe">]>' + body).encode("utf-16")
        with self.assertRaises(ValueError):
            oai_article(raw, "PMC42")

    def test_provider_budget_and_no_override(self):
        records = [{"id": "equator:a", "pmid": "123", "doi": DOI, "status": "lookup_incomplete"},
                   {"id": "equator:b", "pmid": "123", "doi": DOI, "status": "oa_xml_candidate"},
                   {"id": "equator:c", "pmid": "456", "doi": "10.1234/other", "status": "lookup_incomplete"}]
        with patch("scripts.source_provider_evidence.crossref_work", return_value={"status":"exact_doi_metadata"}) as cr, \
             patch("scripts.source_provider_evidence.openalex_work", return_value={"status":"exact_identifier_metadata"}) as oa, \
             patch("scripts.source_provider_evidence.time.sleep"):
            output = provider_observations(records, [], None, 1)
        self.assertEqual(cr.call_count, 1)
        self.assertEqual(oa.call_count, 1)
        self.assertEqual(records[0]["status"], "lookup_incomplete")
        self.assertEqual(output["records"]["equator:c"]["crossref"]["status"], "deferred_request_budget")
        self.assertEqual(output["canonical_packs_promoted"], 0)


if __name__ == "__main__":
    unittest.main()
