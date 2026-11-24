"""Bounded batch acquisition: exact identifiers, explicit holds, no content admission."""
import unittest
from scripts.survey_equator_articles import resolve, query_terms, scan_article, catalogue_report

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

if __name__=="__main__":
    unittest.main()
