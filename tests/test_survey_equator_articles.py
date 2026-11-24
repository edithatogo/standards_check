"""Bounded batch acquisition: exact identifiers, explicit holds, no content admission."""
import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from scripts.survey_equator_articles import (resolve, query_terms, scan_article, catalogue_report,
                                            lookup, retained_metadata, priority_survey,
                                            identifier_disagreements, oa_worklist, combine_retained_metadata,
                                            bulk_survey, main)

def article_record(pmid="123", doi="10.1234/test", pmcid="PMC42", oa="Y", license_="cc by"):
    return {"source":"MED","id":pmid,"pmid":pmid,"doi":doi,"pmcid":pmcid,
            "isOpenAccess":oa,"inPMC":"Y","license":license_}

def row(id_,pmid=None,doi=None):
    return {"id":"equator:"+id_,"source_blob_sha":"a"*40,"pmid":pmid,"doi":doi}

SPEC={"edition":"fixture-2025","pmcid":"PMC42","pmid":"123","doi":"10.1234/test",
      "table_item_ids":[["1","2"]],"legacy_path":None}

XML=b"""<article xmlns:xlink="http://www.w3.org/1999/xlink">
<front><article-meta><article-id pub-id-type="doi">10.1234/test</article-id>
<article-id pub-id-type="pmid">123</article-id><article-id pub-id-type="pmc">42</article-id>
<permissions><license xlink:href="https://creativecommons.org/licenses/by/4.0/"/></permissions>
</article-meta></front><body><table-wrap id="t1"><label>Table 1</label>
<caption><p>Fixture checklist</p></caption><table><tbody>
<tr><td>Heading</td><td>1</td><td><p>Describe the study.</p><list><list-item><p>Specify exclusions.</p></list-item></list></td></tr>
<tr><td>Other</td><td>2</td><td>Report the results.</td></tr>
</tbody></table></table-wrap></body></article>"""

class BatchTests(unittest.TestCase):
    def test_exact_join_and_rights_boundary(self):
        records=[article_record(),article_record("124","10.1234/other","PMC43","N")]
        self.assertEqual(resolve(row("both","123","10.1234/test"),records)["status"],"oa_xml_candidate")
        self.assertEqual(resolve(row("closed","124","10.1234/other"),records)["status"],"metadata_only")
        self.assertEqual(resolve(row("cross","123","10.1234/other"),records)["status"],"identifier_conflict")
        self.assertEqual(resolve(row("none"),records)["status"],"missing_identifier")
        self.assertEqual(resolve(row("absent","999"),records)["status"],"unresolved_identifier")
        self.assertEqual(resolve(row("dup","123"),records+[article_record("123","10.1234/test","PMC44")])["status"],"ambiguous_identifier")

    def test_queries_deduplicate_and_reject_untrusted_query_syntax(self):
        terms=query_terms([row("a","123","10.1234/test"),row("b","123","10.1234/test"),
                           row("c","123 OR 1",'10.1234/" OR *')])
        self.assertEqual(terms,['(EXT_ID:123 AND SRC:MED)','DOI:"10.1234/test"'])

    def test_failed_batch_is_not_missing_record(self):
        cat={"source_revision":"b"*40,"published_count":2,"guidelines":[row("a","123"),row("b")]}
        result=catalogue_report(cat,[],failed_terms={'(EXT_ID:123 AND SRC:MED)'})
        self.assertEqual(result["summary"]["published_count"],2)
        self.assertEqual(result["records"][0]["status"],"lookup_incomplete")
        self.assertEqual(result["records"][1]["status"],"missing_identifier")
        self.assertEqual(result["summary"]["canonical_packs_promoted"],0)

    def test_priority_uses_ordered_source_items_and_nested_blocks_without_text_export(self):
        result=scan_article(XML,SPEC,None)
        self.assertEqual(result["status"],"expected_numbered_rows_observed")
        self.assertEqual(result["expected_rows"],2)
        self.assertEqual(result["matched_rows"],2)
        self.assertEqual([r["item_id"] for r in result["tables"][0]["items"]],["1","2"])
        self.assertIn("structure",result["tables"][0])
        self.assertNotIn("Describe the study.",str(result))
        self.assertEqual(result["canonical_packs_promoted"],0)

    def test_holds_wrong_identity_rights_and_missing_rows(self):
        for raw in (XML.replace(b"10.1234/test",b"10.1234/no"),
                    XML.replace(b"/by/4.0/",b"/by-nc/4.0/")):
            with self.assertRaises(ValueError):
                scan_article(raw,SPEC,None)
        result=scan_article(XML.replace(b"<td>2</td>",b"<td>9</td>"),SPEC,None)
        self.assertEqual(result["status"],"held_table_identity_or_structure")
        self.assertEqual(result["matched_rows"],0)
        self.assertEqual(result["canonical_packs_promoted"],0)


    def test_failed_lookup_circuit_breaker_and_successful_batch(self):
        records = [row("a", str(i)) for i in range(1, 82)]
        good = json.dumps({"hitCount": 1, "resultList": {"result": [article_record()]}}).encode()
        with patch("scripts.survey_equator_articles.fetch", side_effect=[good, TimeoutError(), TimeoutError(), TimeoutError()]) as getter, \
             patch("scripts.survey_equator_articles.time.sleep"):
            hits, failed, deferred = lookup(records)
        self.assertEqual(hits, [article_record()])
        self.assertEqual(len(failed), 60)
        self.assertEqual(len(deferred), 1)
        self.assertEqual(getter.call_count, 4)
        result = catalogue_report({"source_revision":"b"*40,"published_count":81,
                                   "guidelines":[row(str(i),str(i)) for i in range(1,82)]},
                                   hits, failed, deferred)
        self.assertEqual(sum(r.get("lookup_reason")=="deferred_provider_circuit_breaker" for r in result["records"]),1)
        with patch("scripts.survey_equator_articles.fetch", return_value=b'{"hitCount":2,"resultList":{"result":[]}}'), \
             patch("scripts.survey_equator_articles.time.sleep"):
            _, fail, rest = lookup([row("a","123")])
        self.assertTrue(fail)
        self.assertFalse(rest)

    def test_resume_requires_unchanged_source_and_exact_ids(self):
        a, b = row("a","123","10.1234/test"), row("b","123","10.1234/test")
        previous = {"records":[resolve(a,[article_record()]),resolve(b,[article_record()])]}
        cat = {"source_revision":"b"*40,"published_count":2,"guidelines":[a,{**b,"source_blob_sha":"c"*40}]}
        keep=retained_metadata(cat,previous)
        self.assertEqual(list(keep),["equator:a"])
        report=catalogue_report(cat,[],set(),retained=keep)
        self.assertEqual(report["records"][0]["lookup_origin"],"retained_previous_receipt")
        self.assertEqual(report["records"][1]["status"],"unresolved_identifier")

    def test_priority_transport_fallback_receipt_and_held(self):
        with patch("scripts.survey_equator_articles.fetch_priority",
                   side_effect=[(XML,{"provider":"pmc_oai"}),(None,{"attempts":[{"status":"unavailable"}]})]), \
             patch("scripts.survey_equator_articles.time.sleep"):
            results=priority_survey([SPEC,{**SPEC,"edition":"second"}],None)
        self.assertEqual(results[0]["status"],"expected_numbered_rows_observed")
        self.assertEqual(results[0]["acquisition"]["provider"],"pmc_oai")
        self.assertEqual(results[1]["status"],"held")
        self.assertTrue(results[1]["acquisition"]["attempts"])

    def test_provider_disagreement_and_oa_worklist_deduplication(self):
        a=resolve(row("a","123","10.1234/test"),[article_record()])
        b={**a,"id":"equator:b"}
        c={**a,"id":"equator:c","pmcid":"PMC43"}
        e={"equator:a":{"pmc_by_pmid":{"status":"pmc_mapping_candidate","pmcid":"PMC99"}}}
        self.assertIn("pmcid_disagreement",identifier_disagreements(a,e["equator:a"]))
        work=oa_worklist({"records":[a,b,c]},e,[],[{"pmcid":"PMC43"}])
        self.assertEqual(len(work),2)
        self.assertEqual(work[0]["status"],"held_identity")
        self.assertEqual(work[0]["source_ids"],["equator:a","equator:b"])
        self.assertEqual(work[1]["status"],"priority_or_retained_source")

    def test_cli_retains_partial_census_and_provider_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            cat=root/"catalogue.json"
            out=root/"report.json"
            cat.write_text(json.dumps({"source_revision":"b"*40,"published_count":1,
                                       "guidelines":[row("a","123","10.1234/test")]}))
            with patch("sys.argv",["survey","--catalogue",str(cat),"--output",str(out),"--registry-limit","0","--bulk-limit","0"]), \
                 patch("scripts.survey_equator_articles.lookup",return_value=([article_record()],set(),set())), \
                 patch("scripts.survey_equator_articles.priority_survey",return_value=[]), \
                 patch("scripts.survey_equator_articles.provider_observations",return_value={"records":{}}):
                main()
            result=json.loads(out.read_text())
            self.assertEqual(result["summary"]["published_count"],1)
            self.assertEqual(result["summary"]["canonical_packs_promoted"],0)
            self.assertEqual(result["records"][0]["status"],"oa_xml_candidate")
            self.assertEqual(result["oa_source_worklist"][0]["pmcid"],"PMC42")


    def test_multiple_receipts_recover_disjoint_and_hold_conflict(self):
        a, b = row("a", "123"), row("b", "124")
        catalogue = {"source_revision": "b"*40, "published_count": 2, "guidelines": [a,b]}
        prior = catalogue_report(catalogue, [article_record()], set())
        later = catalogue_report(catalogue, [article_record(pmid="124",pmcid="PMC43")], set())
        retained, conflicts = combine_retained_metadata(catalogue, [prior,later])
        self.assertEqual(set(retained), {"equator:a","equator:b"})
        self.assertFalse(conflicts)
        conflicting = catalogue_report(catalogue, [article_record(pmcid="PMC99")], set())
        retained, conflicts = combine_retained_metadata(catalogue,[prior,later,conflicting])
        self.assertEqual(set(retained), {"equator:b"})
        self.assertEqual(conflicts, {"equator:a"})
        with self.assertRaises(ValueError):
            combine_retained_metadata(catalogue, [{"records": []}])
        prior["records"][0]["provider_disagreements"] = ["pmcid_disagreement"]
        retained, conflicts = combine_retained_metadata(catalogue, [prior, later])
        self.assertIn("equator:a", conflicts)
        self.assertNotIn("equator:a", retained)

    def test_conflicting_prior_status_blocks_unchanged_success_in_either_order(self):
        catalogue = {"source_revision": "b"*40, "published_count": 1,
                     "guidelines": [row("a", "123")]}
        good = catalogue_report(catalogue, [article_record()], set())
        for status in ("identifier_conflict", "ambiguous_identifier"):
            held = catalogue_report(catalogue, [article_record()], set())
            held["records"][0]["status"] = status
            for receipts in ([good, held], [held, good]):
                retained, conflicts = combine_retained_metadata(catalogue, receipts)
                self.assertNotIn("equator:a", retained)
                self.assertEqual(conflicts, {"equator:a"})
        held["records"][0]["source_blob_sha"] = "c"*40
        retained, conflicts = combine_retained_metadata(catalogue, [good, held])
        self.assertIn("equator:a", retained)
        self.assertFalse(conflicts)

    def test_bulk_inventory_budget_resume_and_circuit_breaker(self):
        records = [resolve(row(str(i),str(i)), [article_record(pmid=str(i),pmcid="PMC"+str(i))])
                   for i in range(1,5)]
        report = {"records": records,"oa_source_worklist":oa_worklist({"records":records},{},[],[])}
        observed = {"status":"held_table_identity_or_structure","source_sha256":"b"*64,
                    "table_inventory":[],"canonical_packs_promoted":0}
        with patch("scripts.survey_equator_articles.priority_survey", return_value=[observed.copy()]) as fetcher:
            first = bulk_survey(report, [], None, 1)
        self.assertEqual(fetcher.call_count,1)
        self.assertEqual(first[0]["status"],"source_inventory_observed_not_reconciled")
        self.assertEqual(first[1]["status"],"deferred_acquisition_budget")
        with patch("scripts.survey_equator_articles.priority_survey",
                   side_effect=lambda *args:[{"status":"held","canonical_packs_promoted":0}]) as fetcher:
            second = bulk_survey(report,[{"bulk_articles":first}],None,4)
        self.assertEqual(fetcher.call_count,2)
        self.assertEqual(second[0]["acquisition_origin"],"retained_previous_receipt")
        self.assertEqual(second[-1]["status"],"deferred_acquisition_budget")

if __name__=="__main__":
    unittest.main()
