import unittest
from scripts.survey_projections import project_survey, validate


class ProjectionInvariantTests(unittest.TestCase):
    def tables(self):
        catalogue = {'source_revision': 'a'*40, 'published_count': 1,
                     'guidelines': [{'id':'equator:example','page_url':'https://equator-network.org/reporting-guidelines/example/',
                                     'source_blob_sha':'b'*40,'metadata_status':'extracted_unverified'}]}
        survey = {'source_revision':'a'*40,'summary':{'published_count':1,'canonical_packs_promoted':0},
                  'records':[{'id':'equator:example','source_blob_sha':'b'*40,'status':'identifier_conflict'}],
                  'priority_articles':[{'edition':'example-1','status':'expected_numbered_rows_observed',
                                        'source_sha256':'d'*64,'expected_rows':1,'matched_rows':1,'canonical_packs_promoted':0,
                                        'tables':[{'table_id':'t','items':[{'item_id':'1','source_anchor':'t:row:1:item:1','normalized_text_sha256':'c'*64}]}]}]}
        return project_survey(catalogue,survey,{'canonical_packs_promoted':0,'findings':[]})

    def test_acquisition_rights_cannot_be_promoted_in_projection(self):
        tables=self.tables()
        validate(tables)
        tables['acquisitions'][0]['rights_status']='cleared'
        with self.assertRaises(ValueError): validate(tables)

    def test_conflict_disposition_cannot_be_silently_downgraded(self):
        tables=self.tables()
        tables['catalogue_identity'][0]['disposition']='discovery_only'
        with self.assertRaises(ValueError): validate(tables)

    def test_item_count_fingerprint_and_anchor_conservation(self):
        for table,key,value in [('acquisitions','matched_rows',2),('acquisition_items','fingerprint','bad'),
                                ('acquisition_items','source_anchor',''),('acquisitions','source_sha256',None)]:
            with self.subTest(key=key):
                tables=self.tables(); tables[table][0][key]=value
                with self.assertRaises(ValueError): validate(tables)
