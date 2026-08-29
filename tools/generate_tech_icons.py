"""
Generate local SVG icon tiles for every technology listed in data/technologies.json.

These are deliberately NOT copies of official third-party product logos.
Reproducing trademarked brand marks is not something this toolkit does.
Instead every technology gets a consistent, theme-colored monogram tile
(dark card, rounded corners, accent-colored initials) so the stack
section renders reliably without depending on any external icon CDN.

Run:
    python tools/generate_tech_icons.py
"""

from _common import theme, technologies, write_svg, esc


def initials(name):
    parts = [p for p in name.replace(".", " ").split() if p]
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[1][0]).upper()


def icon_svg(name, t):
    label = initials(name)
    size = 96
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}" role="img" aria-label="{esc(name)} icon">
  <rect x="1" y="1" width="{size-2}" height="{size-2}" rx="18" fill="{t['surface']}" stroke="{t['border']}" stroke-width="1.5"/>
  <text x="50%" y="54%" text-anchor="middle" dominant-baseline="middle"
        font-family="{t['fonts']['mono']}" font-size="30" font-weight="600"
        fill="{t['primary']}">{esc(label)}</text>
</svg>
""".strip()


def slug_from_path(icon_path):
    # data/technologies.json stores paths like assets/icons/python.svg
    return icon_path.rsplit("/", 1)[-1].replace(".svg", "")


def main():
    t = theme()
    written = []
    for group in technologies():
        for item in group["items"]:
            svg = icon_svg(item["name"], t)
            path = write_svg(item["icon"], svg)
            written.append(path)
    print(f"Generated {len(written)} technology icon tiles under assets/icons/")


if __name__ == "__main__":
    main()
