"""Author-generated synthetic page with manually specified reference facts."""
from tests.test_compare_ecoevo_formats import tiny_pdf


def pages():
    commands = ['0.5 w']
    for x in (15, 90, 270, 310):
        commands.append(f'{x} 67 m {x} 175 l S')
    for y in (67, 95, 123, 151, 175):
        commands.append(f'15 {y} m 310 {y} l S')
    for x, y, text in (
        (20, 160, 'Sub-item number'), (95, 160, 'Sub-item'), (275, 160, 'Score'),
        (20, 140, '1.1'), (95, 140, 'Report outcomes. [a]'), (275, 140, '8.3'),
        (95, 128, 'Include missing data.'),
        (30, 112, '1.1.1'), (95, 112, 'If measured, report timing.'), (275, 112, '0'),
        (20, 84, '1.2'), (95, 84, 'Report harms.'), (275, 84, '1'),
        (20, 40, '[a] Except when withheld.'),
    ):
        commands.append(f'BT /F1 8 Tf {x} {y} Td ({text}) Tj ET')
    return {'existing-grid': tiny_pdf(), 'nested-notes': tiny_pdf(commands)}

# Manual source annotations in PDF points, top-left origin; not reader output.
REFERENCES = {
    'existing-grid': [
        (('row', 1, '1.1', 'Example requirement.'), [40, 70, 280, 100]),
    ],
    'nested-notes': [
        (('row', 1, '1.1', 'Report outcomes. [a] Include missing data.'), [15, 49, 310, 77]),
        (('row', 1, '1.1.1', 'If measured, report timing.'), [15, 77, 310, 105]),
        (('row', 1, '1.2', 'Report harms.'), [15, 105, 310, 133]),
        (('nested', 1, '1.1.1', '1.1'), [15, 49, 90, 105]),
        (('footnote', 1, 'a', 'Except when withheld.'), [15, 145, 200, 165]),
        (('qualifier_link', 1, '1.1', 'a'), [95, 49, 270, 77]),
        (('qualifier_link', 1, '1.1.1', 'If measured'), [95, 77, 270, 105]),
    ],
}
