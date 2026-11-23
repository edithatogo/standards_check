"""Synthetic tests for bounded EQUATOR source-link discovery."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.equator_source_links import extract_links, collect


class SourceLinksTests(unittest.TestCase):
    def test_extracts_downloads_without_claiming_rights_or_content(self):
        data = {
            'downloads': 'Download [checklist](checklist.pdf) or [docx](https://example.org/guide.docx).',
            'relevant-urls': 'Read [the statement](https://doi.org/10.1000/example) and <https://example.org/info>.',
        }
        links = extract_links(data, 'https://equator-network.org/reporting-guidelines/example/')
        assert [(x['url'], x['source_field'], x['type']) for x in links] == [
            ('https://equator-network.org/reporting-guidelines/example/checklist.pdf', 'downloads', 'source_file_candidate'),
            ('https://example.org/guide.docx', 'downloads', 'source_file_candidate'),
            ('https://doi.org/10.1000/example', 'relevant-urls', 'doi_landing_candidate'),
            ('https://example.org/info', 'relevant-urls', 'landing_page_candidate'),
        ]
        assert all(x['qualification'] == 'unverified_link_only' for x in links)

    def test_parentheses_in_publisher_urls_remain_intact_without_false_truncated_links(self):
        ispor = "https://www.ispor.org/heor-resources/good-practices/article/consolidated-health-economic-evaluation-reporting-standards-2022-(cheers-2022)-statement"
        elsevier = "https://linkinghub.elsevier.com/retrieve/pii/S2589-5370(24)00566-2"
        data = {
            "relevant-urls": f"See [ISPOR]({ispor})",
            "full-bibliographic-reference": f"[Full text]({elsevier}) and {elsevier}",
        }
        links = extract_links(data, "https://equator-network.org/reporting-guidelines/cheers/")
        self.assertEqual([item["url"] for item in links], [ispor, elsevier])

    def test_malformed_candidate_is_reported_and_later_links_survive(self):
        issues = []
        data = {"downloads": "[Broken](https://[not-a-valid-host/file.pdf) [Valid](https://example.org/checklist.pdf)"}
        links = extract_links(data, "https://equator-network.org/reporting-guidelines/example/", issues)
        self.assertEqual([x["url"] for x in links], ["https://example.org/checklist.pdf"])
        self.assertIn("malformed_candidate_url", issues)

    def test_ipv6_literal_is_not_truncated_or_rejected_as_malformed(self):
        issues = []
        links = extract_links(
            {"downloads": "https://[2606:4700:4700::1111]/guide.pdf"},
            "https://equator-network.org/reporting-guidelines/example/", issues)
        self.assertEqual([x["url"] for x in links], ["https://[2606:4700:4700::1111]/guide.pdf"])
        self.assertEqual(issues, [])

    def test_unsafe_or_unrecognised_fields_do_not_create_leads(self):
        data = {"downloads": ["not a string"], "relevant-urls": "[No](mailto:test@example.org) "
                "[Local](http://localhost/file.pdf) "
                "[Credential](https://user:pw@example.org/file.pdf) "
                "[Safe](https://example.org/files/guide.CSV)"}
        links = extract_links(data, "https://equator-network.org/reporting-guidelines/example/")
        self.assertEqual([x["url"] for x in links], ["https://example.org/files/guide.CSV"])
        self.assertEqual(links[0]["type"], "source_file_candidate")

    def test_duplicate_links_across_fields_are_deduplicated(self):
        url = "https://example.org/guide.pdf"
        result = extract_links({"downloads": f"[Checklist]({url}) {url}",
                                "relevant-urls": f"Read {url}."},
                               "https://equator-network.org/reporting-guidelines/example/")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["source_field"], "downloads")

    def test_bibliographic_links_are_candidates_not_primary_evidence(self):
        links = extract_links({"full-bibliographic-reference":
            "[Full text](https://www.bmj.com/content/383/bmj-2023-076386)\n"
            "[Issue](https://www.bmj.com/content/383/bmj-2023-076386)"},
            "https://equator-network.org/reporting-guidelines/spirit-define/")
        assert len(links) == 1
        assert links[0]["source_field"] == "full-bibliographic-reference"
        assert links[0]["qualification"] == "unverified_link_only"

    def test_does_not_accept_script_file_or_credential_urls(self):
        data = {'downloads': '[bad](javascript:alert) [bad](file:///etc/passwd) '
                '[bad](https://user:secret@example.org/file.pdf) [bad](http://127.0.0.1/private.pdf) [valid](https://example.org/public.pdf)'}
        assert [x['url'] for x in extract_links(data, 'https://equator-network.org/reporting-guidelines/a/')] == [
            'https://example.org/public.pdf'
        ]

    def test_development_and_missing_title_are_not_silently_dropped(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            subprocess.run(['git','init','-q',str(root)],check=True)
            subprocess.run(['git','-C',str(root),'config','user.email','test@example.invalid'],check=True)
            subprocess.run(['git','-C',str(root),'config','user.name','Test'],check=True)
            for name,content in {
                'reporting-guidelines/one/index.qmd': '---\ntitle: ""\ndownloads: "[Checklist](item.pdf)"\n---\nnot copied',
                'reporting-guidelines/two/index.qmd': '---\ntitle: Second\ndownloads: ""\n---\nnot copied',
                'reporting-guidelines/under-development/draft/index.qmd': '---\ntitle: Draft\n---\nnot copied',
            }.items():
                path=root/name; path.parent.mkdir(parents=True,exist_ok=True);path.write_text(content)
            subprocess.run(['git','-C',str(root),'add','.'],check=True)
            subprocess.run(['git','-C',str(root),'commit','-qm','fixture'],check=True)
            head=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
            catalogue={'source_revision':head,'published_count':2,'guidelines':[]}
            for slug in ('one','two'):
                path=f'reporting-guidelines/{slug}/index.qmd'
                sha=subprocess.check_output(['git','-C',str(root),'rev-parse',f'HEAD:{path}'],text=True).strip()
                catalogue['guidelines'].append({'id':'equator:'+slug,'page_url':f'https://equator-network.org/reporting-guidelines/{slug}/','source_path':path,'source_blob_sha':sha,'metadata_status':'extracted_unverified'})
            result=collect(root,catalogue)
            assert result['published_count']==2
            assert result['summary']['records_with_candidates']==1
            assert result['summary']['link_count']==1
            assert result['summary']['records_needing_review']==1
            assert 'not copied' not in json.dumps(result)
            assert result['guidelines'][0]['status']=='needs_review'
            # Run the exact CLI on a pinned local source, with no web requests.
            catalogue_file = root / 'catalogue.json'
            catalogue_file.write_text(json.dumps(catalogue))
            export = root / 'candidates.json'
            import sys
            process = subprocess.run(
                [sys.executable, '-m', 'scripts.equator_source_links',
                 '--source', str(root), '--catalogue', str(catalogue_file),
                 '--output', str(export)],
                capture_output=True, text=True, cwd=Path(__file__).resolve().parents[1])
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertEqual(json.loads(export.read_text())['published_count'], 2)
            self.assertEqual(json.loads(export.read_text())['summary']['records_needing_review'], 1)

            # Missing/duplicate/unexpected source metadata cannot silently pass.
            with self.assertRaisesRegex(ValueError, 'invalid upstream catalogue count'):
                collect(root, {**catalogue, 'published_count': 3})
            wrong = json.loads(json.dumps(catalogue))
            wrong['guidelines'][0]['source_blob_sha'] = 'a' * 40
            with self.assertRaisesRegex(ValueError, 'source identity'):
                collect(root, wrong)
            repeated = json.loads(json.dumps(catalogue))
            repeated['guidelines'][1] = repeated['guidelines'][0]
            with self.assertRaises(ValueError):
                collect(root, repeated)

            catalogue['source_revision']='a'*40
            with self.assertRaisesRegex(ValueError,'source revision'):
                collect(root,catalogue)

    def test_bad_frontmatter_is_explicit_review_debt_not_authority(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            subprocess.run(['git','init','-q',str(root)],check=True)
            subprocess.run(['git','-C',str(root),'config','user.email','test@example.invalid'],check=True)
            subprocess.run(['git','-C',str(root),'config','user.name','Test'],check=True)
            path='reporting-guidelines/one/index.qmd'
            (root/path).parent.mkdir(parents=True)
            (root/path).write_text('not YAML frontmatter')
            subprocess.run(['git','-C',str(root),'add','.'],check=True)
            subprocess.run(['git','-C',str(root),'commit','-qm','fixture'],check=True)
            head=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
            sha=subprocess.check_output(['git','-C',str(root),'rev-parse',f'HEAD:{path}'],text=True).strip()
            report=collect(root,{'source_revision':head,'published_count':1,'guidelines':[{'id':'equator:one','page_url':'https://equator-network.org/reporting-guidelines/one/','source_path':path,'source_blob_sha':sha,'metadata_status':'needs_review'}]})
            assert report['guidelines'][0]['status']=='needs_review'
            assert report['summary']['records_needing_review']==1


    def test_oversized_candidate_list_and_bad_metadata_are_review_debt(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            subprocess.run(['git','-C',str(root),'config','user.email','test@example.invalid'], check=True)
            subprocess.run(['git','-C',str(root),'config','user.name','Test'], check=True)
            file = root / 'reporting-guidelines/example/index.qmd'
            file.parent.mkdir(parents=True)
            links = '\n'.join(f'  [Source {i}](https://example.org/{i}.pdf)' for i in range(70))
            file.write_text('---\ntitle: Example\nrelevant-urls: |-\n' + links +
                            '\ndownloads: \n  - invalid-structured-field\n---\nDo not export body.')
            subprocess.run(['git','-C',str(root),'add','.'], check=True)
            subprocess.run(['git','-C',str(root),'commit','-qm','fixture'], check=True)
            head = subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'], text=True).strip()
            sha = subprocess.check_output(['git','-C',str(root),'rev-parse',
                                           'HEAD:reporting-guidelines/example/index.qmd'],
                                          text=True).strip()
            report = collect(root, {'source_revision': head, 'published_count': 1,
                      'guidelines': [{
                        'id': 'equator:example',
                        'page_url': 'https://equator-network.org/reporting-guidelines/example/',
                        'source_path': 'reporting-guidelines/example/index.qmd',
                        'source_blob_sha': sha,
                        'metadata_status': 'extracted_unverified'
                      }]})
            row = report['guidelines'][0]
            self.assertEqual(len(row['candidates']), 64)
            self.assertIn('link_limit_exceeded', row['issues'])
            self.assertIn('invalid_downloads', row['issues'])
            self.assertEqual(row['status'], 'needs_review')
            self.assertEqual(report['summary']['records_needing_review'], 1)
            self.assertNotIn('Do not export body', json.dumps(report))



if __name__ == '__main__':
    unittest.main()
