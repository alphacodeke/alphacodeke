"""
Generate local GitHub statistics SVG cards from the GitHub REST API:

    assets/graphs/github-stats.svg        public repos, followers, stars
    assets/graphs/github-languages.svg    language breakdown across public repos
"""

import os
import sys
import urllib.request
import urllib.error
import json
from collections import Counter

from _common import theme, profile, write_svg, esc

API = "https://api.github.com"


def api_get(path, token=None):
    req = urllib.request.Request(f"{API}{path}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "alphacodeke-profile-toolkit")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_all_repos(username, token):
    repos = []
    page = 1
    while True:
        batch = api_get(f"/users/{username}/repos?per_page=100&page={page}", token)
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return repos


def stats_card_svg(t, username, user, total_stars, repo_count):
    width, height = 420, 190
    rows = [
        ("Public repositories", str(user.get("public_repos", repo_count))),
        ("Followers", str(user.get("followers", "-"))),
        ("Total stars", str(total_stars)),
    ]
    row_parts = []
    y = 92
    for label, value in rows:
        row_parts.append(f'<text x="24" y="{y}" font-family="{t["fonts"]["body"]}" font-size="14" fill="{t["muted"]}">{esc(label)}</text>')
        row_parts.append(f'<text x="{width-24}" y="{y}" text-anchor="end" font-family="{t["fonts"]["mono"]}" font-size="15" font-weight="700" fill="{t["primary"]}">{esc(value)}</text>')
        y += 28
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="GitHub stats for {esc(username)}">
  <rect x="1" y="1" width="{width-2}" height="{height-2}" rx="16" fill="{t['surface']}" stroke="{t['border']}" stroke-width="1.5"/>
  <text x="24" y="40" font-family="{t['fonts']['display']}" font-size="18" font-weight="700" fill="{t['text']}">GitHub Activity</text>
  <text x="24" y="60" font-family="{t['fonts']['mono']}" font-size="12" fill="{t['muted']}">@{esc(username)}</text>
  {''.join(row_parts)}
</svg>
""".strip()


def languages_card_svg(t, username, language_counts):
    width, height = 420, 190
    top = language_counts.most_common(6)
    total = sum(c for _, c in top) or 1
    bar_x, bar_w = 150, 240
    row_parts = []
    y = 46
    for name, count in top:
        pct = count / total
        row_parts.append(f'<text x="24" y="{y+11}" font-family="{t["fonts"]["body"]}" font-size="13" fill="{t["text"]}">{esc(name)}</text>')
        row_parts.append(f'<rect x="{bar_x}" y="{y}" width="{bar_w}" height="10" rx="5" fill="{t["surface_alt"]}"/>')
        row_parts.append(f'<rect x="{bar_x}" y="{y}" width="{bar_w*pct:.1f}" height="10" rx="5" fill="{t["primary"]}"/>')
        y += 26
    if not top:
        row_parts.append(f'<text x="24" y="60" font-family="{t["fonts"]["body"]}" font-size="13" fill="{t["muted"]}">No public language data available yet.</text>')
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="Most used languages for {esc(username)}">
  <rect x="1" y="1" width="{width-2}" height="{height-2}" rx="16" fill="{t['surface']}" stroke="{t['border']}" stroke-width="1.5"/>
  <text x="24" y="26" font-family="{t['fonts']['display']}" font-size="16" font-weight="700" fill="{t['text']}">Most Used Languages</text>
  {''.join(row_parts)}
</svg>
""".strip()


def placeholder_svg(t, username, title, reason):
    width, height = 420, 190
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="{esc(title)} unavailable">
  <rect x="1" y="1" width="{width-2}" height="{height-2}" rx="16" fill="{t['surface']}" stroke="{t['border']}" stroke-width="1.5"/>
  <text x="24" y="34" font-family="{t['fonts']['display']}" font-size="16" font-weight="700" fill="{t['text']}">{esc(title)}</text>
  <text x="24" y="60" font-family="{t['fonts']['body']}" font-size="12.5" fill="{t['muted']}">{esc(reason)}</text>
  <text x="24" y="80" font-family="{t['fonts']['body']}" font-size="12.5" fill="{t['muted']}">Rerun tools/generate_github_stats.py to refresh.</text>
</svg>
""".strip()


def main():
    p = profile()
    username = p["github_username"]
    token = os.environ.get("GITHUB_TOKEN")
    t = theme()

    try:
        user = api_get(f"/users/{username}", token)
        repos = fetch_all_repos(username, token)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        stats_exists = os.path.exists(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets/graphs/github-stats.svg"))
        if stats_exists:
            print(f"WARNING: GitHub API unavailable ({exc}). Leaving existing stats assets untouched.", file=sys.stderr)
        else:
            reason = "GitHub API rate limit reached." if "403" in str(exc) else "GitHub API request failed."
            write_svg("assets/graphs/github-stats.svg", placeholder_svg(t, username, "GitHub Activity", reason))
            write_svg("assets/graphs/github-languages.svg", placeholder_svg(t, username, "Most Used Languages", reason))
            print(f"WARNING: {exc}. No prior stats existed, so wrote safe placeholders instead of leaving broken image links.", file=sys.stderr)
        sys.exit(1)

    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    language_counts = Counter(r["language"] for r in repos if r.get("language"))

    write_svg("assets/graphs/github-stats.svg", stats_card_svg(t, username, user, total_stars, len(repos)))
    write_svg("assets/graphs/github-languages.svg", languages_card_svg(t, username, language_counts))
    print(f"Generated github-stats.svg and github-languages.svg for @{username} ({len(repos)} public repos).")


if __name__ == "__main__":
    main()
