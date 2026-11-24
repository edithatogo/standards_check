"""Seeded mutation fuzzing at the shared untrusted source XML boundary."""
import random
import unittest
from scripts.source_xml import parse_xml

SEED = 721114987
CASES = 512
SAMPLE = b'<article><body><table-wrap id="T"><table><tbody><tr><td>1</td><td>Report.</td></tr></tbody></table></table-wrap></body></article>'
ENTITY = '<!DOCTYPE article [<!ENTITY inserted "untrusted replacement">]><article>&inserted;</article>'


class SourceXmlTests(unittest.TestCase):
    def test_rejects_entity_declarations_even_in_utf16_and_utf32(self):
        for encoding in ('utf-8', 'utf-16', 'utf-16-le', 'utf-16-be', 'utf-32'):
            with self.subTest(encoding=encoding), self.assertRaises(ValueError):
                parse_xml(ENTITY.encode(encoding), 4096)

    def test_accepts_utf8_and_external_dtd_without_loading_it(self):
        xml = b'<!DOCTYPE article SYSTEM "https://example.invalid/no-network.dtd">' + SAMPLE
        self.assertEqual(parse_xml(xml, 4096).tag, 'article')
        self.assertEqual(parse_xml(b'\xef\xbb\xbf' + SAMPLE, 4096).tag, 'article')
        for raw, limit in ((b'', 100), (SAMPLE, 1), (b'\xff', 100), (b'<article>', 100)):
            with self.subTest(raw=raw[:12]), self.assertRaises(ValueError):
                parse_xml(raw, limit)

    def test_seeded_byte_mutations_are_bounded_and_deterministic(self):
        rng = random.Random(SEED)
        accepted = rejected = 0
        from xml.etree.ElementTree import tostring
        for case in range(CASES):
            data = bytearray(SAMPLE)
            for _ in range(rng.randint(1, 8)):
                i = rng.randrange(len(data))
                op = rng.randrange(3)
                if op == 0:
                    data[i] = rng.randrange(256)
                elif op == 1:
                    del data[i]
                else:
                    data.insert(i, rng.randrange(256))
            raw = bytes(data)
            with self.subTest(seed=SEED, case=case):
                try:
                    tree = parse_xml(raw, 4096)
                except ValueError:
                    rejected += 1
                    continue
                accepted += 1
                self.assertNotIn(b'\x00', raw)
                self.assertNotIn(b'<!ENTITY', raw.upper())
                self.assertEqual(tostring(tree), tostring(parse_xml(raw, 4096)))
        self.assertGreater(accepted, 0)
        self.assertGreater(rejected, 0)


if __name__ == '__main__':
    unittest.main()
