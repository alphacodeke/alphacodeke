"""
Generate the profile-wide diagrams that are not tied to a single project
"""

from _common import theme, projects, write_svg, esc


def monogram_svg(t):
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="120" height="120" role="img" aria-label="AK monogram">
  <rect x="2" y="2" width="116" height="116" rx="24" fill="{t['surface']}" stroke="{t['primary']}" stroke-width="2"/>
  <text x="50%" y="58%" text-anchor="middle" dominant-baseline="middle"
        font-family="{t['fonts']['display']}" font-size="46" font-weight="700"
        fill="{t['primary']}">AK</text>
</svg>
""".strip()


def _elbow_path(x1, y1, x2, y2):
    """A right-angled route between two points, for a circuit-board feel
    instead of a straight diagonal wire."""
    mid_x = (x1 + x2) / 2
    return f"M {x1} {y1} L {mid_x} {y1} L {mid_x} {y2} L {x2} {y2}"


def hero_background_svg(t):
    """
    A quiet, animated network of connected systems: nodes that pulse,
    orthogonal circuit-style paths between them, and a few slow-moving
    light points that travel along those paths. It echoes the profile's
    subject (connected backend systems) without competing with the
    identity text that sits above and below it in the README.

    Everything here is SMIL (<animate>/<animateMotion>), which keeps
    working when the SVG is embedded through <img src="...">, unlike
    CSS or JavaScript animation. The first frame (t=0) already looks
    complete on its own, so nothing depends on animation actually
    playing: a viewer or renderer with no SMIL support still sees a
    finished, static network illustration.
    """
    width, height = 1200, 300

    nodes = [
        (80, 70), (230, 190), (370, 90), (520, 215), (630, 60),
        (770, 175), (905, 85), (985, 235), (1085, 115), (160, 255),
    ]
    edges = [
        (0, 1), (1, 2), (2, 4), (1, 3), (3, 5),
        (4, 6), (5, 6), (6, 7), (6, 8), (3, 9),
    ]
    
    particle_edges = [0, 3, 6, 9]
    pulse_durations = [3.4, 4.1, 3.7, 4.6, 3.2, 4.3, 3.9, 4.8, 3.5, 4.0]

    parts = [f'<rect x="0" y="0" width="{width}" height="{height}" fill="{t["background"]}"/>']

    grid = []
    for x in range(0, width + 1, 80):
        grid.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{height}" stroke="{t["border"]}" stroke-width="1" opacity="0.14"/>')
    for y in range(0, height + 1, 80):
        grid.append(f'<line x1="0" y1="{y}" x2="{width}" y2="{y}" stroke="{t["border"]}" stroke-width="1" opacity="0.14"/>')
    parts.append(f'<g>{"".join(grid)}</g>')

    edge_parts = []
    for i, (a, b) in enumerate(edges):
        x1, y1 = nodes[a]
        x2, y2 = nodes[b]
        edge_parts.append(
            f'<path id="hero-edge-{i}" d="{_elbow_path(x1, y1, x2, y2)}" '
            f'fill="none" stroke="{t["muted"]}" stroke-width="1" opacity="0.32"/>'
        )
    parts.append(f'<g>{"".join(edge_parts)}</g>')

   
    node_parts = []
    for i, (x, y) in enumerate(nodes):
        dur = pulse_durations[i % len(pulse_durations)]
        begin = round(i * 0.35, 2)
        radius = 3.2 if i % 3 else 4.2
        node_parts.append(
            f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{t["primary"]}" opacity="0.35">'
            f'<animate attributeName="opacity" values="0.3;0.9;0.3" dur="{dur}s" '
            f'begin="{begin}s" repeatCount="indefinite"/>'
            f"</circle>"
        )
    parts.append(f'<g>{"".join(node_parts)}</g>')

    particle_parts = []
    for j, edge_index in enumerate(particle_edges):
        dur = 7 + j * 1.6
        begin = j * 1.1
        particle_parts.append(
            f'<circle r="2.6" fill="{t["primary"]}" opacity="0.85">'
            f'<animateMotion dur="{dur}s" begin="{begin}s" repeatCount="indefinite" '
            f'path="{_elbow_path(*nodes[edges[edge_index][0]], *nodes[edges[edge_index][1]])}"/>'
            f"</circle>"
        )
    parts.append(f'<g>{"".join(particle_parts)}</g>')

    return f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="Animated network of connected systems">
  {''.join(parts)}
</svg>
""".strip()


def product_ecosystem_svg(t, all_projects):
    categories = {}
    for p in all_projects:
        categories.setdefault(p["category"], []).append(p["name"])
    cat_names = list(categories.keys())

    label_font_size = 11.5
    char_width = label_font_size * 0.62
    box_widths = [max(110, len(cat.upper()) * char_width + 36) for cat in cat_names]
    col_gap = 22
    width = int(sum(box_widths) + col_gap * (len(cat_names) - 1) + 60)

    max_projects = max(len(v) for v in categories.values())
    branch_y = 190
    height = branch_y + 24 + max_projects * 20 + 20

    center_x, center_y = width / 2, 86
    title = "ALPHACODE SOLUTIONS"
    title_w = max(260, len(title) * 13.5 + 40)

    parts = [
        f'<rect x="{center_x-title_w/2:.1f}" y="{center_y-30}" width="{title_w:.1f}" height="60" rx="16" '
        f'fill="{t["surface"]}" stroke="{t["primary"]}" stroke-width="2"/>',
        f'<text x="{center_x}" y="{center_y+6}" text-anchor="middle" font-family="{t["fonts"]["display"]}" '
        f'font-size="19" font-weight="700" fill="{t["primary"]}">{esc(title)}</text>',
    ]

    x = 30
    top_y = center_y + 30
    for i, cat in enumerate(cat_names):
        box_w = box_widths[i]
        cx = x + box_w / 2
        parts.append(f'<line x1="{center_x}" y1="{top_y}" x2="{cx}" y2="{branch_y-30}" stroke="{t["border"]}" stroke-width="1.5"/>')
        parts.append(
            f'<rect x="{x:.1f}" y="{branch_y-28}" width="{box_w:.1f}" height="34" rx="10" '
            f'fill="{t["surface_alt"]}" stroke="{t["border"]}" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{branch_y-6}" text-anchor="middle" font-family="{t["fonts"]["mono"]}" '
            f'font-size="{label_font_size}" letter-spacing="0.4" fill="{t["text"]}">{esc(cat.upper())}</text>'
        )
        proj_y = branch_y + 20
        for name in categories[cat]:
            parts.append(
                f'<text x="{cx:.1f}" y="{proj_y}" text-anchor="middle" font-family="{t["fonts"]["body"]}" '
                f'font-size="12" fill="{t["muted"]}">{esc(name)}</text>'
            )
            proj_y += 20
        x += box_w + col_gap

    return f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="Product ecosystem diagram">
  <rect x="0" y="0" width="{width}" height="{height}" fill="{t['background']}"/>
  {''.join(parts)}
</svg>
""".strip()


def engineering_architecture_svg(t):
    layers = [
        ("Frontend", "Server-rendered templates, Tailwind CSS, vanilla JavaScript"),
        ("Django Application", "URL routing, views, forms, permissions"),
        ("Business Logic", "Domain services: billing, booking, attendance, queueing"),
        ("Database", "MySQL in production, SQLite for local development"),
        ("External Services", "Authentication, payment APIs, email, webhooks, network integrations, background tasks"),
    ]
    box_w, box_h, gap = 620, 62, 30
    width = box_w + 260
    height = 30 + len(layers) * (box_h + gap)
    parts = []
    y = 20
    for i, (title, detail) in enumerate(layers):
        x = 30
        parts.append(f'<rect x="{x}" y="{y}" width="{box_w}" height="{box_h}" rx="12" fill="{t["surface"]}" stroke="{t["primary"]}" stroke-width="1.5"/>')
        parts.append(f'<text x="{x+24}" y="{y+26}" font-family="{t["fonts"]["display"]}" font-size="17" font-weight="700" fill="{t["text"]}">{esc(title)}</text>')
        parts.append(f'<text x="{x+24}" y="{y+46}" font-family="{t["fonts"]["body"]}" font-size="12.5" fill="{t["muted"]}">{esc(detail)}</text>')
        if i < len(layers) - 1:
            cx = x + box_w / 2
            y1 = y + box_h
            y2 = y + box_h + gap
            parts.append(f'<line x1="{cx}" y1="{y1}" x2="{cx}" y2="{y2-8}" stroke="{t["muted"]}" stroke-width="1.5"/>')
            parts.append(f'<polygon points="{cx-5},{y2-8} {cx+5},{y2-8} {cx},{y2}" fill="{t["muted"]}"/>')
        y += box_h + gap

    return f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="Engineering architecture diagram">
  <rect x="0" y="0" width="{width}" height="{height}" fill="{t['background']}"/>
  {''.join(parts)}
</svg>
""".strip()


def development_workflow_svg(t):
    stages = ["DISCOVER", "PLAN", "DESIGN", "BUILD", "TEST", "SECURE", "DEPLOY", "MONITOR", "IMPROVE"]
    box_w, box_h, gap = 92, 60, 14
    width = len(stages) * box_w + (len(stages) - 1) * gap + 40
    height = 100
    parts = []
    x = 20
    y = 20
    for i, stage in enumerate(stages):
        parts.append(f'<rect x="{x}" y="{y}" width="{box_w}" height="{box_h}" rx="10" fill="{t["surface"]}" stroke="{t["primary"]}" stroke-width="1.5"/>')
        parts.append(
            f'<text x="{x+box_w/2}" y="{y+box_h/2+4}" text-anchor="middle" font-family="{t["fonts"]["mono"]}" '
            f'font-size="11.5" letter-spacing="0.5" fill="{t["text"]}">{esc(stage)}</text>'
        )
        if i < len(stages) - 1:
            arrow_x = x + box_w
            cy = y + box_h / 2
            parts.append(f'<line x1="{arrow_x}" y1="{cy}" x2="{arrow_x+gap-6}" y2="{cy}" stroke="{t["muted"]}" stroke-width="1.5"/>')
            parts.append(f'<polygon points="{arrow_x+gap-6},{cy-5} {arrow_x+gap-6},{cy+5} {arrow_x+gap},{cy}" fill="{t["muted"]}"/>')
        x += box_w + gap

    return f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="Development workflow diagram">
  <rect x="0" y="0" width="{width}" height="{height}" fill="{t['background']}"/>
  {''.join(parts)}
</svg>
""".strip()


def main():
    t = theme()
    all_projects = projects()
    write_svg("assets/branding/monogram.svg", monogram_svg(t))
    write_svg("assets/branding/hero-background.svg", hero_background_svg(t))
    write_svg("assets/diagrams/product-ecosystem.svg", product_ecosystem_svg(t, all_projects))
    write_svg("assets/diagrams/engineering-architecture.svg", engineering_architecture_svg(t))
    write_svg("assets/diagrams/development-workflow.svg", development_workflow_svg(t))
    print("Generated monogram, hero background, product ecosystem, architecture and workflow diagrams.")


if __name__ == "__main__":
    main()
