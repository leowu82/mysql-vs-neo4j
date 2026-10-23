"""Render one ER diagram with fixed table positions and orthogonal connectors.

Run from any directory: python3 docs/diagrams/render_er.py
Only Python's standard library is required.
"""

from html import escape
from pathlib import Path


class Diagram:
    def __init__(self, title, description, width, height):
        self.width = width
        self.height = height
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}" '
            'role="img" aria-labelledby="title description">',
            f'<title id="title">{escape(title)}</title>',
            f'<desc id="description">{escape(description)}</desc>',
            '<style>'
            'text{font-family:Arial,Helvetica,sans-serif;fill:#172b4d}'
            '.name{font-size:17px;font-weight:700}'
            '.field{font-family:monospace;font-size:14px}'
            '.key{font-size:11px;font-weight:700;fill:#415a77}'
            '.line{fill:none;stroke:#415a77;stroke-width:1.6}'
            '</style>',
            f'<rect width="{width}" height="{height}" fill="#fff"/>',
        ]
        self.tables = []
        self.edges = []

    def table(self, name, x, y, width, fields):
        height = 42 + 27 * len(fields)
        self.tables.append((x, y, width, height))
        self.parts.extend([
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
            'fill="#fff" stroke="#415a77" stroke-width="1.5"/>',
            f'<rect x="{x + 1}" y="{y + 1}" width="{width - 2}" '
            'height="39" fill="#edf3f9"/>',
            f'<path class="line" d="M{x},{y + 40} H{x + width}"/>',
            f'<text class="name" x="{x + 12}" y="{y + 26}">{escape(name)}</text>',
        ])
        for index, (key, field) in enumerate(fields):
            baseline = y + 62 + index * 27
            self.parts.append(
                f'<text class="key" x="{x + 12}" y="{baseline}">{escape(key)}</text>'
                f'<text class="field" x="{x + 65}" y="{baseline}">{escape(field)}</text>'
            )
        return height

    def relation(self, points, identifying=False, minimum=0):
        """Parent (exactly one) to child (zero or one through many)."""
        assert all(a[0] == b[0] or a[1] == b[1]
                   for a, b in zip(points, points[1:])), "Non-orthogonal edge"
        self.edges.append(points)
        path = "M" + " L".join(f"{x},{y}" for x, y in points)
        dash = '' if identifying else ' stroke-dasharray="6 4"'
        self.parts.append(f'<path class="line"{dash} d="{path}"/>')
        self.endpoint(points[0], points[1], many=False)
        self.endpoint(points[-1], points[-2], many=True, minimum=minimum)

    def endpoint(self, point, toward, many, minimum=0):
        x, y = point
        dx = (toward[0] > x) - (toward[0] < x)
        dy = (toward[1] > y) - (toward[1] < y)

        def pos(distance, side=0):
            return f'{x + dx * distance - dy * side},{y + dy * distance + dx * side}'

        if many:
            self.parts.append(
                f'<path class="line" d="M{pos(1, -7)} L{pos(15)} L{pos(1, 7)} '
                f'M{pos(1)} L{pos(15)}"/>'
            )
            if minimum == 0:
                self.parts.append(
                    f'<circle cx="{x + dx * 25}" cy="{y + dy * 25}" '
                    'r="5" fill="#fff" stroke="#415a77" stroke-width="1.6"/>'
                )
            else:
                self.parts.append(f'<path class="line" d="M{pos(25, -7)} L{pos(25, 7)}"/>')
        else:
            self.parts.append(
                f'<path class="line" d="M{pos(9, -7)} L{pos(9, 7)} '
                f'M{pos(17, -7)} L{pos(17, 7)}"/>'
            )

    def save(self, filename):
        # Prevent a later layout edit from routing connectors through a table.
        for points in self.edges:
            for (x1, y1), (x2, y2) in zip(points, points[1:]):
                for x, y, width, height in self.tables:
                    if x1 == x2:
                        assert not (x < x1 < x + width and
                                    max(min(y1, y2), y) < min(max(y1, y2), y + height))
                    else:
                        assert not (y < y1 < y + height and
                                    max(min(x1, x2), x) < min(max(x1, x2), x + width))
        for index, edge in enumerate(self.edges):
            for other in self.edges[index + 1:]:
                for a, b in zip(edge, edge[1:]):
                    for c, d in zip(other, other[1:]):
                        if (a[0] == b[0]) == (c[0] == d[0]):
                            continue
                        vertical, horizontal = ((a, b), (c, d)) if a[0] == b[0] else ((c, d), (a, b))
                        vx = vertical[0][0]
                        hy = horizontal[0][1]
                        assert not (min(p[0] for p in horizontal) <= vx <= max(p[0] for p in horizontal)
                                    and min(p[1] for p in vertical) <= hy <= max(p[1] for p in vertical)), \
                            f'Crossing connectors in {filename}'
        Path(__file__).with_name(filename).write_text('\n'.join(self.parts + ['</svg>']) + '\n')


def render():
    diagram = Diagram(
        'Catalog entity relationship diagram',
        'All sixteen catalog tables in one connected ER diagram. Resource is the central '
        'entity, with junction tables and lookups to the left, citations to the right, '
        'source notes above, and resource relationships below. Supporting citation '
        'foreign keys are listed in the tables without extra connectors.',
        2200, 1680,
    )
    diagram.parts.extend([
        '<text class="name" x="100" y="45" style="font-size:26px">Catalog entity relationship diagram</text>',
        '<text x="100" y="155" style="font-size:16px">PK = primary key   ·   FK = foreign key   ·   Crow’s foot = many</text>',
        '<text x="100" y="182" style="font-size:16px">Circle = optional   ·   Bar = required   ·   Solid = identifying   ·   Dashed = non-identifying</text>',
    ])

    diagram.table('resource', 850, 620, 300, [
        ('PK', 'id'), ('', 'title'), ('', 'publication_value'),
        ('', 'publication_precision'), ('', 'container_title'), ('', 'verification_status'),
    ])
    specs = [
        ('resource_agent', 'agent', 'agent_id', [('PK', 'contribution_role'), ('PK', 'credit_order')]),
        ('resource_topic', 'topic', 'topic_id', []),
        ('resource_audience', 'audience', 'audience_id', []),
        ('resource_format', 'format', 'format_id', []),
    ]
    for index, (join, lookup, foreign_key, extra) in enumerate(specs):
        y = 360 + index * 220
        key = 'FK' if lookup == 'agent' else 'PK,FK'
        diagram.table(join, 430, y, 300, [
            ('PK,FK', 'resource_id'), (key, foreign_key), *extra, ('FK', 'source_mention_id'),
        ])
        fields = [('PK', 'id'), ('', 'name')]
        if lookup in ('topic', 'audience'):
            fields.append(('FK', 'source_id'))
        diagram.table(lookup, 100, y, 250, fields)
        lane = (800, 770, 770, 800)[index]
        port = 660 + index * 30
        diagram.relation([(850, port), (lane, port), (lane, y + 65), (730, y + 65)], identifying=True)
        diagram.relation([(350, y + 95), (430, y + 95)], identifying=lookup != 'agent')

    diagram.table('source_document', 1350, 260, 320, [('PK', 'id'), ('', 'filename')])
    diagram.table('source_mention', 1350, 620, 320, [
        ('PK', 'id'), ('FK', 'resource_id'), ('FK', 'source_id'), ('', 'citation_raw'),
    ])
    diagram.table('quality_issue', 1810, 620, 300, [
        ('PK', 'id'), ('FK', 'mention_id'), ('', 'issue_code'), ('', 'review_status'),
    ])
    diagram.table('identifier', 1350, 1020, 320, [
        ('PK', 'id'), ('FK', 'resource_id'), ('FK', 'source_mention_id'),
        ('', 'identifier_kind'), ('', 'identifier_value'),
    ])
    diagram.table('planning_statement', 1810, 260, 300, [
        ('PK', 'id'), ('FK', 'source_id'), ('', 'statement_kind'), ('', 'statement_text'),
    ])
    diagram.table('age_definition', 1350, 30, 320, [
        ('PK', 'id'), ('FK', 'source_id'), ('FK', 'audience_id'),
        ('', 'minimum_age'), ('', 'comparison_operator'),
    ])
    diagram.table('resource_relation', 850, 1370, 380, [
        ('PK', 'id'), ('FK', 'from_resource_id'), ('FK', 'to_resource_id'),
        ('FK', 'from_mention_id'), ('FK', 'to_mention_id'),
        ('', 'relation_kind'), ('', 'review_status'),
    ])

    diagram.relation([(1150, 690), (1350, 690)], minimum=1)
    diagram.relation([(1430, 356), (1430, 620)])
    diagram.relation([(1670, 710), (1810, 710)])
    diagram.relation([(1080, 824), (1080, 1090), (1350, 1090)])
    diagram.relation([(1550, 770), (1550, 1020)])
    diagram.relation([(1670, 310), (1810, 310)])
    diagram.relation([(1510, 260), (1510, 207)])
    diagram.relation([(100, 900), (40, 900), (40, 100), (1350, 100)])
    diagram.relation([(1350, 300), (1280, 300), (1280, 220), (60, 220), (60, 850), (100, 850)])
    diagram.relation([(1350, 350), (1250, 350), (1250, 240), (80, 240), (80, 650), (100, 650)])
    diagram.relation([(930, 824), (930, 1370)])
    diagram.relation([(1040, 824), (1040, 1370)])
    diagram.parts.extend([
        '<text x="920" y="1310" text-anchor="end" style="font-size:15px">from</text>',
        '<text x="1050" y="1310" style="font-size:15px">to</text>',
        '<text x="100" y="1630" style="font-size:16px">Selected fields shown. Supporting citation keys are listed; their extra connectors are omitted for clarity.</text>',
    ])
    diagram.save('er-catalog.svg')


if __name__ == '__main__':
    render()
