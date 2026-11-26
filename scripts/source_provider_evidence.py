"""Small, read-only scholarly API adapters. Registry hits are source leads, not rights."""

from __future__ import annotations

import gzip
import hashlib
import http.client
import io
import json
import re
import time
from urllib.parse import quote, urlencode, urlsplit, urlunsplit
from xml.etree import ElementTree as ET

if __package__:
    from .source_xml import parse_xml
else:
    from source_xml import parse_xml

EUROPE = "www.ebi.ac.uk"
PMC = "pmc.ncbi.nlm.nih.gov"
CROSSREF = "api.crossref.org"
OPENALEX = "api.openalex.org"
PLOS = "journals.plos.org"
HOSTS = {EUROPE, PMC, CROSSREF, OPENALEX, PLOS}
MAX_BYTES = 8_000_000
DOI = re.compile(r"10\.\d{4,9}/[A-Za-z0-9._;()/:+<>\-]{1,220}", re.I)
PMID = re.compile(r"[1-9]\d{0,9}")
PMCID = re.compile(r"PMC[1-9]\d{0,9}")
OAI = "{http://www.openarchives.org/OAI/2.0/}"
FAILURES = (OSError, ValueError, KeyError, TypeError, http.client.HTTPException)


def fetch(host: str, path: str, max_bytes: int = MAX_BYTES) -> bytes:
    """Only fixed official API hosts; no redirects or arbitrary link dereferencing."""
    if host not in HOSTS or not path.startswith("/") or path.startswith("//"):
        raise ValueError("unsupported provider endpoint")
    connection = http.client.HTTPSConnection(host, timeout=12)
    try:
        connection.request(
            "GET",
            path,
            headers={"User-Agent": "StandardFlow-source-evidence/1.0", "Accept-Encoding": "gzip"},
        )
        response = connection.getresponse()
        if response.status != 200:
            raise OSError(f"provider HTTP {response.status}")
        raw = response.read(max_bytes + 1)
        if len(raw) > max_bytes:
            raise ValueError("provider response too large")
        if response.getheader("Content-Encoding", "").lower() == "gzip":
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
                raw = stream.read(max_bytes + 1)
        if len(raw) > max_bytes:
            raise ValueError("decompressed provider response too large")
        return raw
    finally:
        connection.close()


def doi_value(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip().lower().removeprefix("https://doi.org/")
    return value if DOI.fullmatch(value) else None


def pmid_value(value: object) -> str | None:
    if not isinstance(value, (int, str)):
        return None
    value = str(value).removeprefix("https://pubmed.ncbi.nlm.nih.gov/").strip("/")
    return value if PMID.fullmatch(value) else None


def links(values: list) -> list[str]:
    """Keep locator hints only; strip query strings/credentials and never fetch them."""
    found = set()
    for value in values:
        if not isinstance(value, str) or len(value) > 2048:
            continue
        try:
            url = urlsplit(value)
            if (
                url.scheme in {"https", "http"}
                and url.hostname
                and not (url.username or url.password)
            ):
                found.add(urlunsplit((url.scheme, url.netloc, url.path, "", "")))
        except ValueError:
            continue
    return sorted(found)[:12]


def crossref_work(doi: str) -> dict:
    if doi_value(doi) != doi:
        raise ValueError("invalid DOI")
    record = json.loads(fetch(CROSSREF, "/works/" + quote(doi, safe="")))["message"]
    if doi_value(record.get("DOI")) != doi:
        return {"status": "identifier_conflict"}
    return {
        "status": "exact_doi_metadata",
        "resolved_doi": doi,
        "licence_links": links([item.get("URL") for item in record.get("license", [])]),
        "links": links([item.get("URL") for item in record.get("link", [])]),
        "rights": "metadata_only_not_reuse_permission",
    }


def openalex_work(doi: str | None, pmid: str | None) -> dict:
    if doi and doi_value(doi) == doi:
        key = "doi:" + quote(doi, safe="")
    elif pmid and pmid_value(pmid) == pmid:
        key = "pmid:" + pmid
    else:
        raise ValueError("missing valid OpenAlex lookup ID")
    # Exact singleton lookups only; never invoke priced search/content endpoints.
    record = json.loads(fetch(OPENALEX, "/works/" + key))
    resolved_doi, resolved_pmid = (
        doi_value(record.get("doi")),
        pmid_value((record.get("ids") or {}).get("pmid")),
    )
    if (doi and resolved_doi and doi != resolved_doi) or (
        pmid and resolved_pmid and pmid != resolved_pmid
    ):
        return {"status": "identifier_conflict"}
    status = (
        "exact_identifier_metadata"
        if (not doi or doi == resolved_doi) and (not pmid or pmid == resolved_pmid)
        else "partial_identifier_evidence"
    )
    locations = [loc for loc in record.get("locations", []) if loc.get("is_oa") is True]
    return {
        "status": status,
        "resolved_doi": resolved_doi,
        "resolved_pmid": resolved_pmid,
        "openalex_id": record.get("id"),
        "links": links(
            [loc.get(field) for loc in locations for field in ("landing_page_url", "pdf_url")]
        ),
        "rights": "metadata_only_not_reuse_permission",
    }


def convert_ids(kind: str, values: list[str], contact: str | None) -> dict:
    normalise = pmid_value if kind == "pmid" else doi_value if kind == "doi" else None
    if normalise is None:
        raise ValueError("unsupported conversion type")
    unique = sorted({v for v in values if normalise(v) == v})
    if not contact or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", contact):
        return {v: {"status": "contact_not_configured"} for v in unique}
    result = {}
    for start in range(0, len(unique), 100):
        batch = unique[start : start + 100]
        path = "/tools/idconv/api/v1/articles/?" + urlencode(
            {
                "ids": ",".join(batch),
                "idtype": kind,
                "format": "json",
                "tool": "standardflow",
                "email": contact,
            }
        )
        try:
            payload = json.loads(fetch(PMC, path))
            if payload.get("status") != "ok" or not isinstance(payload.get("records"), list):
                raise ValueError("invalid converter response")
            for value in batch:
                matches = set()
                for row in payload["records"]:
                    if (
                        normalise(row.get("requested-id")) != value
                        or normalise(row.get(kind)) != value
                    ):
                        continue
                    pmcid = row.get("pmcid")
                    if isinstance(pmcid, str) and PMCID.fullmatch(pmcid):
                        matches.add((pmid_value(row.get("pmid")), doi_value(row.get("doi")), pmcid))
                if len(matches) == 1:
                    pmid, doi, pmcid = next(iter(matches))
                    result[value] = {
                        "status": "pmc_mapping_candidate",
                        "pmid": pmid,
                        "doi": doi,
                        "pmcid": pmcid,
                        "rights": "unassessed",
                    }
                else:
                    result[value] = {
                        "status": "ambiguous_identifier" if matches else "no_pmc_mapping_observed"
                    }
        except FAILURES:
            result.update({v: {"status": "lookup_incomplete"} for v in batch})
        time.sleep(0.35)
    return result


def oai_article(raw: bytes, pmcid: str) -> tuple[bytes, dict]:
    if not PMCID.fullmatch(pmcid):
        raise ValueError("invalid OAI response input")
    root = parse_xml(raw, MAX_BYTES)
    record = root.find(f"{OAI}GetRecord/{OAI}record")
    if root.tag != OAI + "OAI-PMH" or record is None:
        raise ValueError("OAI record unavailable or reuse restricted")
    identifier = record.findtext(f"{OAI}header/{OAI}identifier")
    metadata = record.find(f"{OAI}metadata")
    if (
        identifier != "oai:pubmedcentral.nih.gov:" + pmcid[3:]
        or metadata is None
        or len(metadata) != 1
        or metadata[0].tag != "article"
    ):
        raise ValueError("OAI record identity or article structure mismatch")
    article = ET.tostring(metadata[0], encoding="utf-8")
    return article, {
        "provider": "pmc_oai",
        "representation": "pmc_oai_article_xml_projection",
        "response_sha256": hashlib.sha256(raw).hexdigest(),
        "response_bytes": len(raw),
        "article_sha256": hashlib.sha256(article).hexdigest(),
    }


def fetch_priority(
    pmcid: str, *, plos_doi: str | None = None
) -> tuple[bytes | None, dict]:
    if not PMCID.fullmatch(pmcid):
        raise ValueError("invalid selected PMCID")
    attempts = []
    if plos_doi is not None:
        # Fixed single-article JATS route documented at api.plos.org/text-and-data-mining.html.
        match = re.fullmatch(r"10\.1371/journal\.(pmed|pbio)\.\d{7}", plos_doi)
        if not match:
            raise ValueError("invalid selected PLOS article DOI")
        journal = {"pmed": "plosmedicine", "pbio": "plosbiology"}[match[1]]
        try:
            path = f"/{journal}/article/file?" + urlencode(
                {"id": plos_doi, "type": "manuscript"}
            )
            raw = fetch(PLOS, path)
            return raw, {
                "provider": "plos",
                "representation": "plos_publisher_jats_xml",
                "response_sha256": hashlib.sha256(raw).hexdigest(),
                "response_bytes": len(raw),
                "attempts": [{"provider": "plos", "status": "retrieved"}],
            }
        except (OSError, ValueError, http.client.HTTPException) as exc:
            attempts.append(
                {
                    "provider": "plos",
                    "status": "transport_or_http_failure",
                    "error_type": type(exc).__name__,
                }
            )
    try:
        raw = fetch(EUROPE, "/europepmc/webservices/rest/" + pmcid + "/fullTextXML")
        return raw, {
            "provider": "europe_pmc",
            "representation": "europe_pmc_primary_xml",
            "response_sha256": hashlib.sha256(raw).hexdigest(),
            "response_bytes": len(raw),
            "attempts": [*attempts, {"provider": "europe_pmc", "status": "retrieved"}],
        }
    except (OSError, http.client.HTTPException) as exc:
        attempts.append(
            {
                "provider": "europe_pmc",
                "status": "transport_or_http_failure",
                "error_type": type(exc).__name__,
            }
        )
    # An alternative official endpoint, not an automatic replacement of existing pins.
    try:
        path = "/api/oai/v1/mh/?" + urlencode(
            {
                "verb": "GetRecord",
                "identifier": "oai:pubmedcentral.nih.gov:" + pmcid[3:],
                "metadataPrefix": "pmc",
            }
        )
        article, evidence = oai_article(fetch(PMC, path), pmcid)
        return article, {
            **evidence,
            "attempts": [*attempts, {"provider": "pmc_oai", "status": "retrieved"}],
        }
    except (OSError, ValueError, http.client.HTTPException) as exc:
        attempts.append(
            {
                "provider": "pmc_oai",
                "status": "unavailable_or_held",
                "error_type": type(exc).__name__,
            }
        )
        return None, {"attempts": attempts}


def provider_observations(
    records: list[dict], priorities: list[dict], contact: str | None, limit: int
) -> dict:
    if not 0 <= limit <= 100:
        raise ValueError("registry request limit outside 0..100")
    work = [{**r, "id": "edition:" + r["edition"]} for r in priorities]
    work += sorted(
        records, key=lambda r: (r.get("status") in {"oa_xml_candidate", "metadata_only"}, r["id"])
    )
    pairs = [
        (
            r,
            doi_value(r.get("doi") or r.get("resolved_doi")),
            pmid_value(r.get("pmid") or r.get("resolved_pmid")),
        )
        for r in work
    ]
    pmc_by_pmid = convert_ids("pmid", [p for _, _, p in pairs if p], contact)
    pmc_by_doi = convert_ids("doi", [d for _, d, _ in pairs if d], contact)
    crossref, alex = {}, {}
    output = {}
    for record, doi, pmid in pairs:
        evidence = {}
        if pmid:
            evidence["pmc_by_pmid"] = pmc_by_pmid[pmid]
        if doi:
            evidence["pmc_by_doi"] = pmc_by_doi[doi]
            if doi not in crossref and len(crossref) < limit:
                try:
                    crossref[doi] = crossref_work(doi)
                except FAILURES:
                    crossref[doi] = {"status": "lookup_incomplete"}
                time.sleep(0.35)
            evidence["crossref"] = crossref.get(doi, {"status": "deferred_request_budget"})
        if doi or pmid:
            pair = (doi, pmid)
            if pair not in alex and len(alex) < limit:
                try:
                    alex[pair] = openalex_work(doi, pmid)
                except FAILURES:
                    alex[pair] = {"status": "lookup_incomplete"}
                time.sleep(0.35)
            evidence["openalex"] = alex.get(pair, {"status": "deferred_request_budget"})
        output[record["id"]] = evidence
    return {
        "records": output,
        "canonical_packs_promoted": 0,
        "claim_boundary": "Registry and official endpoint evidence only; no identity override or rights decision.",
    }
