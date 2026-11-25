import unittest
from scripts.survey_projections import project_survey, validate, SCHEMAS


class SurveyProjectionTests(unittest.TestCase):
    def inputs(self):
        c={'source_revision':'a'*40,'published_count':1,'guidelines':[{'id':'equator:example','page_url':'https://equator-network.org/reporting-guidelines/example/','source_blob_sha':'b'*40,'metadata_status':'extracted_unverified','title':'Example'}]}
        s={'source_revision':'a'*40,'summary':{'canonical_packs_promoted':0,'published_count':1},'records':[{'id':'equator:example','source_blob_sha':'b'*40,'status':'oa_xml_candidate','provider_disagreements':['conflict']}],'priority_articles':[{'edition':'example-1','status':'expected_numbered_rows_observed','source_sha256':'d'*64,'expected_rows':1,'matched_rows':1,'canonical_packs_promoted':0,'tables':[{'table_id':'t','items':[{'item_id':'1','source_anchor':'t:1','normalized_text_sha256':'c'*64,'text':'never export'}]}]}]}
        return c,s,{'canonical_packs_promoted':0,'findings':[{'record':'catalogue:equator:example','code':'provider_conflict'}]}

    def test_join_retains_holds_and_hashes_not_source_text(self):
        c,s,r=self.inputs();t=project_survey(c,s,r)
        self.assertEqual(t['catalogue_identity'][0]['disposition'],'held_identity_conflict')
        self.assertEqual(t['catalogue_identity'][0]['rights_status'],'unassessed')
        self.assertEqual(t['acquisition_items'][0]['fingerprint'],'c'*64)
        self.assertNotIn('never export',str(t))
        self.assertEqual(t['acquisitions'][0]['disposition'],'held_review')
        self.assertEqual(len(t['review_findings']),1)
        validate(t)

    def test_incomplete_mismatched_join_and_nonzero_promotion_rejected(self):
        c,s,r=self.inputs();s['records'][0]['source_blob_sha']='d'*40
        with self.assertRaises(ValueError): project_survey(c,s,r)
        c,s,r=self.inputs();s['records']=[]
        with self.assertRaises(ValueError): project_survey(c,s,r)
        c,s,r=self.inputs();s['summary']['canonical_packs_promoted']=1
        with self.assertRaises(ValueError): project_survey(c,s,r)

    def test_grouped_source_hold_survives_catalogue_projection(self):
        c, s, r = self.inputs()
        s["records"][0].pop("provider_disagreements")
        s["records"][0].update(pmcid="PMC42", resolved_doi="10.1/a")
        c["guidelines"].append({
            **c["guidelines"][0], "id": "equator:another",
            "page_url": "https://equator-network.org/reporting-guidelines/another/",
        })
        s["records"].append({
            **s["records"][0], "id": "equator:another", "resolved_doi": "10.1/b",
        })
        c["published_count"] = s["summary"]["published_count"] = 2
        s["oa_source_worklist"] = [{
            "pmcid": "PMC42", "status": "held_identity",
            "source_ids": ["equator:example", "equator:another"],
            "issues": ["conflicting_catalogue_article_identities"],
        }]
        tables = project_survey(c, s, r)
        self.assertEqual(len(tables["catalogue_identity"]), 2)
        for row in tables["catalogue_identity"]:
            self.assertTrue(row["identity_conflict"])
            self.assertEqual(row["disposition"], "held_identity_conflict")
        validate(tables)
        s["oa_source_worklist"][0]["source_ids"] = ["equator:unknown"]
        with self.assertRaisesRegex(ValueError, "unbound source-level"):
            project_survey(c, s, r)

    def test_roundtrip_all_four_tables(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from scripts.source_reconciliation import write_parquet
        import polars as pl
        tables=project_survey(*self.inputs())
        with TemporaryDirectory() as temp:
            manifest=write_parquet(tables,Path(temp),schemas=SCHEMAS,validator=validate)
            self.assertEqual(set(manifest['tables']),set(tables))
            for name,rows in tables.items():
                self.assertEqual(pl.read_parquet(Path(temp)/(name+'.parquet')).height,len(rows))
