"""
Build README.md from templates/README.template.md and the JSON data files.
"""

import os
from string import Template

from _common import ROOT, profile, projects, technologies, esc

WHAT_I_BUILD = [
    ("Business Systems", "Point of sale, inventory, customer records and reporting for day-to-day operations."),
    ("Payments and Billing", "Recurring billing, invoicing, payment integrations and financial record keeping."),
    ("Education Technology", "Attendance, scholarship workflows and learning management for schools and institutions."),
    ("Networking", "Subscriber and billing systems that integrate with MikroTik network infrastructure."),
    ("Marketplaces and Booking", "Buyer and seller platforms, and service booking for industries like beauty and wellness."),
    ("Automation", "Queue management and workflow systems that replace manual, in-person processes."),
]

SECURITY_POINTS = [
    "Authentication and authorization are enforced on every protected view and API endpoint, not assumed from the frontend.",
    "Input is validated on both the frontend and the backend; the backend validation is the one that is trusted.",
    "CSRF protection, secure session handling and password hashing follow the underlying framework's current defaults rather than custom implementations.",
    "Sensitive configuration, including database credentials and API keys, is kept in environment variables and never committed to source control.",
    "Traffic runs over HTTPS, with rate limiting and bot protection such as Cloudflare Turnstile applied to public-facing forms where appropriate.",
    "Errors are handled and logged deliberately, so failures are visible to the developer without exposing internals to the end user.",
]


def build_what_i_build():
    cells = [
        f'<td width="50%" valign="top"><strong>{esc(title)}</strong><br/><sub>{esc(detail)}</sub></td>'
        for title, detail in WHAT_I_BUILD
    ]
    rows = ["".join(cells[i:i + 2]) for i in range(0, len(cells), 2)]
    return (
        '<table width="100%">\n<tbody>\n'
        + "\n".join(f"<tr>{row}</tr>" for row in rows)
        + '\n</tbody>\n</table>'
    )


def build_technology_stack():
    groups = technologies()
    blocks = []
    for group in groups:
        rows = []
        for item in group["items"]:
            rows.append(
                f'<tr>'
                f'<td width="56"><img src="{esc(item["icon"])}" width="40" height="40" alt="{esc(item["name"])} icon"/></td>'
                f'<td><strong>{esc(item["name"])}</strong><br/><sub>{esc(item["purpose"])}</sub></td>'
                f'</tr>'
            )
        blocks.append(
            f'<tr><td colspan="2" align="center"><strong>{esc(group["category"].upper())}</strong></td></tr>\n'
            + "\n".join(rows)
        )
    return '<table width="100%">\n<tbody>\n' + "\n".join(blocks) + '\n</tbody>\n</table>'


def build_project_cards():
    cards = []
    for p in projects():
        feature_chips = " ".join(f"`{esc(f)}`" for f in p["features"])
        stack_chips = " ".join(f"`{esc(s)}`" for s in p["stack"])
        repo_line = esc(p["repository"]) if p["repository"] else "Private repository"
        card = f"""
<table width="100%">
<tr>
<td>

<h3 align="center">{esc(p['name'].upper())}</h3>

<p align="center"><sub>{esc(p['tagline'])}</sub></p>

<p align="center"><code>{esc(p['category'].upper())}</code>&nbsp;&nbsp;<code>{esc(p['status'].upper())}</code></p>

**The problem**<br/>
{esc(p['problem'])}

**The solution**<br/>
{esc(p['solution'])}

**Capabilities**<br/>
{feature_chips}

**Stack**<br/>
{stack_chips}

<p align="center">
<img src="{esc(p['architecture'])}" width="340" alt="{esc(p['name'])} flow diagram"/>
</p>

**Links:** {repo_line}

</td>
</tr>
</table>
""".strip()
        cards.append(card)
    return "\n\n".join(cards)


def build_security_points():
    return "\n".join(f"- {point}" for point in SECURITY_POINTS)


def main():
    p = profile()
    template_path = os.path.join(ROOT, "templates", "README.template.md")
    with open(template_path, "r", encoding="utf-8") as f:
        template = Template(f.read())

    output = template.safe_substitute(
        name=p["name"],
        title=p["title"],
        company_name=p["company"]["name"],
        company_url=p["company"]["url"],
        location=p["location"],
        portfolio=p["portfolio"],
        linkedin=p["linkedin"],
        email=p["email"],
        github_username=p["github_username"],
        positioning_statement=p["positioning_statement"],
        what_i_build=build_what_i_build(),
        technology_stack=build_technology_stack(),
        project_cards=build_project_cards(),
        security_points=build_security_points(),
    )

    readme_path = os.path.join(ROOT, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(output.strip() + "\n")
    print(f"Wrote {readme_path} ({len(output)} characters).")


if __name__ == "__main__":
    main()
