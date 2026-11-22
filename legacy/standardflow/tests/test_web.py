import base64
import copy
import html
import io
import json
from pathlib import Path
import re
import unittest
from unittest.mock import patch
import zipfile

from src.main import generate_artifact
from web.app import app


class TestWebApp(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()
        self.prisma = json.loads(Path('data/prisma_data.json').read_text())
        self.checklist = {
            'checklist_type': 'CONSORT',
            'title': 'Synthetic checklist',
            'items': [{
                'id': '1a', 'section': 'Title and abstract',
                'description': 'Identification as a randomised trial in the title',
                'type': 'boolean',
            }],
        }

    def raw_form(self, data, **controls):
        return {'json_toggle': 'on', 'json_data': json.dumps(data), **controls}

    def download_bytes(self, response):
        self.assertEqual(response.status_code, 200)
        link = re.search(
            rb'href="data:([^;]+);base64,([^"]+)" download="([^"]+)"',
            response.data,
        )
        self.assertIsNotNone(link)
        return link[1], base64.b64decode(link[2], validate=True), link[3]

    def viewer_checklist_data(self, response):
        self.assertEqual(response.status_code, 200)
        field = re.search(r'name="json_data" value="([^"]+)"', response.text)
        self.assertIsNotNone(field)
        return json.loads(html.unescape(field[1]))

    def test_forms_include_raw_json_control(self):
        for route in ('/', '/checklist'):
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'name="json_toggle"', response.data)

    def test_all_diagram_forms_and_raw_inputs(self):
        for stem in ('prisma', 'prisma_2020_updated', 'consort', 'consort_cluster', 'strobe', 'strobe_cohort'):
            data = json.loads(Path(f'data/{stem}_data.json').read_text())
            form = {key: str(value) for key, value in data.items() if key == 'diagram_type' or isinstance(value, int)}
            for submission in (form, self.raw_form(data)):
                with self.subTest(stem=stem, raw='json_toggle' in submission):
                    response = self.client.post('/', data={**submission, 'output_format': 'svg'})
                    mimetype, content, filename = self.download_bytes(response)
                    self.assertEqual(mimetype, b'image/svg+xml')
                    self.assertEqual(filename, b'diagram.svg')
                    self.assertIn(b'<svg', content)

    def test_raw_json_ignores_inactive_form_values(self):
        response = self.client.post('/', data=self.raw_form(
            self.prisma, diagram_type='CONSORT', records_identified='not an integer',
            output_format='svg',
        ))
        _, content, _ = self.download_bytes(response)
        self.assertIn(str(self.prisma['records_identified']).encode(), content)

    def test_download_formats_and_temporary_cleanup(self):
        for output_format, mimetype, signature in (
            ('png', b'image/png', b'\x89PNG\r\n\x1a\n'),
            ('svg', b'image/svg+xml', b'<?xml'),
            ('pdf', b'application/pdf', b'%PDF'),
        ):
            with self.subTest(output_format=output_format):
                with patch('web.app.generate_artifact', wraps=generate_artifact) as generate:
                    response = self.client.post('/', data=self.raw_form(self.prisma, output_format=output_format))
                actual_type, content, filename = self.download_bytes(response)
                self.assertEqual(actual_type, mimetype)
                self.assertTrue(content.startswith(signature))
                self.assertEqual(filename, f'diagram.{output_format}'.encode())
                self.assertFalse(generate.call_args.args[1].exists())
                self.assertEqual(b'<img ' in response.data, output_format != 'pdf')

    def test_invalid_diagram_inputs_return_400(self):
        bad_count = {**self.prisma, 'records_identified': -1}
        for data in ([], {}, bad_count, {'diagram_type': 'UNKNOWN'}, self.checklist):
            with self.subTest(data=data):
                response = self.client.post('/', data=self.raw_form(data))
                self.assertEqual(response.status_code, 400)
        self.assertEqual(self.client.post('/', data={'json_toggle': 'on', 'json_data': '{'}).status_code, 400)
        form = {key: str(value) for key, value in self.prisma.items() if key != 'style'}
        form['records_identified'] = 'invalid'
        self.assertEqual(self.client.post('/', data=form).status_code, 400)
        for output_format in ('typ', '../svg', 'html'):
            with self.subTest(output_format=output_format):
                response = self.client.post('/', data=self.raw_form(self.prisma, output_format=output_format))
                self.assertEqual(response.status_code, 400)

    def test_checklist_editor_keeps_items_and_options_after_gaps(self):
        response = self.client.post('/checklist', data={
            'checklist_type': 'CONSORT',
            'id-1': '1a', 'section-1': 'Introduction',
            'description-1': 'First retained item', 'type-1': 'boolean',
            'id-3': '3a', 'section-3': 'Methods',
            'description-3': 'Third retained item', 'type-3': 'multiple_choice',
            'option-3-1': 'First choice', 'option-3-3': 'Third choice',
        })
        data = self.viewer_checklist_data(response)
        self.assertEqual([item['id'] for item in data['items']], ['1a', '3a'])
        self.assertEqual(data['items'][1]['options'], ['First choice', 'Third choice'])
        self.assertIn(b'Third retained item', response.data)
        self.assertIn(b'Third choice', response.data)

    def test_checklist_raw_json_and_download_are_independent(self):
        second = copy.deepcopy(self.checklist)
        second['items'][0]['description'] = 'Second request only'
        first_view = self.client.post('/checklist', data=self.raw_form(self.checklist))
        second_view = self.client.post('/checklist', data=self.raw_form(second))
        for view, expected in ((first_view, self.checklist), (second_view, second)):
            with self.subTest(description=expected['items'][0]['description']):
                data = self.viewer_checklist_data(view)
                self.assertEqual(data, expected)
                response = self.client.post('/download_checklist', data=self.raw_form(data))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.mimetype, 'application/zip')
                self.assertIn('attachment', response.headers['Content-Disposition'])
                self.assertIn('checklist.zip', response.headers['Content-Disposition'])
                with zipfile.ZipFile(io.BytesIO(response.data)) as archive:
                    self.assertEqual(archive.namelist(), ['Title_and_abstract.md'])
                    self.assertIn(expected['items'][0]['description'].encode(), archive.read('Title_and_abstract.md'))
                response.close()

    def test_checklist_text_remains_escaped(self):
        data = copy.deepcopy(self.checklist)
        data['items'][0]['description'] = '<script>synthetic</script> [link](javascript:synthetic)'
        response = self.client.post('/checklist', data=self.raw_form(data))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'<script>', response.data)
        self.assertNotIn(b'href="javascript:', response.data)
        self.assertIn(b'&lt;script&gt;synthetic&lt;/script&gt;', response.data)
        self.assertEqual(self.viewer_checklist_data(response), data)

    def test_invalid_checklists_are_rejected_before_download(self):
        unsafe = copy.deepcopy(self.checklist)
        unsafe['items'][0]['section'] = '../outside'
        collision = copy.deepcopy(self.checklist)
        collision['items'].append({**collision['items'][0], 'id': '2', 'section': 'Title_and_abstract'})
        for route in ('/checklist', '/download_checklist'):
            for data in ([], {}, self.prisma, unsafe, collision):
                with self.subTest(route=route, data=data):
                    self.assertEqual(self.client.post(route, data=self.raw_form(data)).status_code, 400)
            self.assertEqual(self.client.post(route, data={'json_toggle': 'on', 'json_data': '{'}).status_code, 400)

    def test_missing_form_fields_return_400(self):
        for route, data in (
            ('/', {}),
            ('/', {'diagram_type': 'PRISMA'}),
            ('/', {'json_toggle': 'on'}),
            ('/checklist', {}),
            ('/checklist', {'checklist_type': 'CONSORT', 'id-1': '1'}),
            ('/download_checklist', {'json_toggle': 'on'}),
        ):
            with self.subTest(route=route, data=data):
                self.assertEqual(self.client.post(route, data=data).status_code, 400)

    def test_no_shared_last_generated_download(self):
        self.assertEqual(self.client.get('/download_checklist').status_code, 405)
        self.assertEqual(self.client.get('/download_diagram/diagram.svg').status_code, 404)


if __name__ == '__main__':
    unittest.main()
