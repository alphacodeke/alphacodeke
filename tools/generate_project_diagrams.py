"""
Generate a local architecture/flow SVG for each project listed in
data/projects.json:

    assets/diagrams/projects/<id>.svg

A vertical flow diagram of the project's data flow, built from the
"flow" array in data/projects.json (the same flow described in the
project's case study). This is the one visual per project card; the
project's name, category and status render as text in the README
itself rather than duplicating them into a separate banner image.

Run:
    python tools/generate_project_diagrams.py
"""

from _common import theme, projects, write_svg, esc


def accent_for(project, t):
    return project.get("theme_color") or t["primary"]


def flow_diagram_svg(project, t):
    steps = project["flow"]
    accent = accent_for(project, t)
    box_w, box_h, gap = 480, 56, 34
    width = box_w + 80
    height = 40 + len(steps) * (box_h + gap)

    parts = []
    y = 30
    for i, step in enumerate(steps):
        x = 40
        parts.append(
            f'<rect x="{x}" y="{y}" width="{box_w}" height="{box_h}" rx="12" '
            f'fill="{t["surface"]}" stroke="{accent}" stroke-width="1.5"/>'
        )
        parts.append(
            f'<text x="{x + box_w/2}" y="{y + box_h/2 + 5}" text-anchor="middle" '
            f'font-family="{t["fonts"]["body"]}" font-size="16" font-weight="600" '
            f'fill="{t["text"]}">{esc(step)}</text>'
        )
        if i < len(steps) - 1:
            arrow_y1 = y + box_h
            arrow_y2 = y + box_h + gap
            cx = x + box_w / 2
            parts.append(
                f'<line x1="{cx}" y1="{arrow_y1}" x2="{cx}" y2="{arrow_y2 - 8}" '
                f'stroke="{t["muted"]}" stroke-width="1.5"/>'
            )
            parts.append(
                f'<polygon points="{cx-5},{arrow_y2-8} {cx+5},{arrow_y2-8} {cx},{arrow_y2} " '
                f'fill="{t["muted"]}"/>'
            )
        y += box_h + gap

    return f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="{esc(project['name'])} flow diagram">
  <rect x="0" y="0" width="{width}" height="{height}" fill="{t['background']}"/>
  {''.join(parts)}
</svg>
""".strip()


def main():
    t = theme()
    count = 0
    for project in projects():
        write_svg(project["architecture"], flow_diagram_svg(project, t))
        count += 1
    print(f"Generated flow diagrams for {count} projects.")


if __name__ == "__main__":
    main()
