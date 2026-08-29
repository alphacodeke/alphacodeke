"""
Generate a local contribution activity SVG card:

    assets/graphs/github-activity.svg

GitHub's contribution calendar is not exposed by the public REST API,
only by the GraphQL API, which requires an authenticated token. This
script therefore has two modes:

1. GITHUB_TOKEN is set: queries the GraphQL API for the real weekly
   contribution totals over the last year and renders an actual
   12-month activity bar chart.

2. GITHUB_TOKEN is not set: renders an honest placeholder card that
   explains a token is required, instead of guessing numbers or
   leaving a broken image reference in the README. This keeps the
   README rendering correctly either way (see rule in
   private/guidelines/troubleshooting.md).

Run:
    GITHUB_TOKEN=xxxx python tools/generate_contributions.py
"""

import os
import sys
import json
import urllib.request
import urllib.error

from _common import theme, profile, write_svg, esc

GRAPHQL_URL = "https://api.github.com/graphql"

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""


def fetch_weekly_totals(username, token):
    body = json.dumps({"query": QUERY, "variables": {"login": username}}).encode("utf-8")
    req = urllib.request.Request(GRAPHQL_URL, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "alphacodeke-profile-toolkit")
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [sum(day["contributionCount"] for day in w["contributionDays"]) for w in weeks]


def activity_chart_svg(t, username, weekly_totals):
    width, height = 760, 160
    chart_x, chart_w = 24, width - 48
    max_val = max(weekly_totals) or 1
    bar_gap = 2
    bar_w = (chart_w / len(weekly_totals)) - bar_gap
    bars = []
    x = chart_x
    for total in weekly_totals:
        bar_h = 0 if max_val == 0 else (total / max_val) * 80
        y = 120 - bar_h
        bars.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" rx="1.5" fill="{t["primary"]}" opacity="0.85"/>')
        x += bar_w + bar_gap
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="Weekly contribution activity for {esc(username)}">
  <rect x="1" y="1" width="{width-2}" height="{height-2}" rx="16" fill="{t['surface']}" stroke="{t['border']}" stroke-width="1.5"/>
  <text x="24" y="30" font-family="{t['fonts']['display']}" font-size="16" font-weight="700" fill="{t['text']}">Contribution Activity, Last 52 Weeks</text>
  {''.join(bars)}
</svg>
""".strip()


def placeholder_svg(t, username):
    width, height = 760, 160
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="Contribution activity unavailable">
  <rect x="1" y="1" width="{width-2}" height="{height-2}" rx="16" fill="{t['surface']}" stroke="{t['border']}" stroke-width="1.5"/>
  <text x="24" y="30" font-family="{t['fonts']['display']}" font-size="16" font-weight="700" fill="{t['text']}">Contribution Activity</text>
  <text x="24" y="60" font-family="{t['fonts']['body']}" font-size="13" fill="{t['muted']}">Set GITHUB_TOKEN and rerun tools/generate_contributions.py</text>
  <text x="24" y="80" font-family="{t['fonts']['body']}" font-size="13" fill="{t['muted']}">to render live weekly activity for @{esc(username)}.</text>
</svg>
""".strip()


def main():
    p = profile()
    username = p["github_username"]
    token = os.environ.get("GITHUB_TOKEN")
    t = theme()

    if not token:
        write_svg("assets/graphs/github-activity.svg", placeholder_svg(t, username))
        print("No GITHUB_TOKEN set. Wrote a placeholder github-activity.svg (this is expected, not an error).")
        return

    try:
        weekly_totals = fetch_weekly_totals(username, token)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, KeyError) as exc:
        print(f"WARNING: contribution query failed ({exc}). Leaving existing github-activity.svg untouched.", file=sys.stderr)
        sys.exit(1)

    write_svg("assets/graphs/github-activity.svg", activity_chart_svg(t, username, weekly_totals))
    print(f"Generated github-activity.svg from {len(weekly_totals)} weeks of real contribution data.")


if __name__ == "__main__":
    main()
