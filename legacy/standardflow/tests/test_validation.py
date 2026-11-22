import json
from pathlib import Path
import unittest

from jsonschema import validate, ValidationError


class TestValidation(unittest.TestCase):
    def test_all_diagram_variants_validate_and_reject_bad_counts(self):
        for name in ('prisma', 'prisma_2020_updated', 'consort', 'consort_cluster',
                     'strobe', 'strobe_cohort'):
            data = json.loads(Path(f'data/{name}_data.json').read_text())
            schema = json.loads(Path(f'schemas/{name.split("_")[0]}_schema.json').read_text())
            validate(data, schema)
            for key, value in data.items():
                if not isinstance(value, int):
                    continue
                for invalid in (-1, '5', True):
                    with self.subTest(variant=name, field=key, invalid=invalid):
                        with self.assertRaises(ValidationError):
                            validate({**data, key: invalid}, schema)
            with self.assertRaises(ValidationError):
                validate({**data, 'diagram_type': 'UNKNOWN'}, schema)

    def test_schema_objects_have_unique_keys(self):
        def unique_keys(pairs):
            result = dict(pairs)
            self.assertEqual(len(result), len(pairs), 'Duplicate JSON schema key')
            return result

        for path in Path('schemas').glob('*.json'):
            with self.subTest(path=path):
                json.loads(path.read_text(), object_pairs_hook=unique_keys)

    def test_multiple_choice_requires_options(self):
        schema = json.loads(Path('schemas/checklist_schema.json').read_text())
        item = {'section': 'Methods', 'id': '1', 'description': 'Choose',
                'type': 'multiple_choice'}
        data = {'checklist_type': 'CONSORT', 'title': 'Example', 'items': [item]}
        with self.assertRaises(ValidationError):
            validate(data, schema)
        item['options'] = ['Yes', 'No']
        validate(data, schema)


if __name__ == '__main__':
    unittest.main()
