"""
Validate the profile repository before considering a change complete.

Checks:
    - config/profile.json, config/theme.json, data/projects.json,
      data/technologies.json all parse as valid JSON
    - every project has the required case-study fields (problem, solution,
      features, stack, status, category)
    - every asset path referenced from data/projects.json,
      data/technologies.json and README.md points at a file that exists
    - README.md exists and is non-empty

Exits with status 1 and a list of problems if anything fails, so it can
be used as a pre-commit or CI gate. Exits 0 with a summary on success.

Run:
    python tools/validate_profile.py
"""

import json
import os
import re
import sys

from _common import ROOT, load_json

REQUIRED_PROJECT_FIELDS = [
    "id", "name", "tagline", "category", "status",
    "problem", "solution", "features", "stack", "flow", "architecture",
]

REQUIRED_PROFILE_FIELDS = [
    "name", "title", "company", "location", "email", "portfolio",
    "linkedin", "github_username", "positioning_statement",
]


def check_json_files(problems):
    for rel_path in [
        "config/profile.json",
        "config/theme.json",
        "data/projects.json",
        "data/technologies.json",
    ]:
        path = os.path.join(ROOT, rel_path)
        if not os.path.exists(path):
            problems.append(f"Missing required file: {rel_path}")
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                json.load(f)
        except json.JSONDecodeError as exc:
            problems.append(f"Invalid JSON in {rel_path}: {exc}")


def check_profile_fields(problems):
    try:
        p = load_json("config/profile.json")
    except Exception as exc:
        problems.append(f"Could not load config/profile.json: {exc}")
        return
    for field in REQUIRED_PROFILE_FIELDS:
        if field not in p or not p[field]:
            problems.append(f"config/profile.json is missing required field: {field}")


def check_projects(problems):
    try:
        all_projects = load_json("data/projects.json")
    except Exception as exc:
        problems.append(f"Could not load data/projects.json: {exc}")
        return

    seen_ids = set()
    for p in all_projects:
        name = p.get("name", "<unnamed project>")
        for field in REQUIRED_PROJECT_FIELDS:
            if field not in p or p[field] in (None, "", []):
                problems.append(f"Project '{name}' is missing required field: {field}")
        if p.get("id") in seen_ids:
            problems.append(f"Duplicate project id: {p.get('id')}")
        seen_ids.add(p.get("id"))
        for asset_field in ("architecture",):
            if asset_field in p and p[asset_field]:
                asset_path = os.path.join(ROOT, p[asset_field])
                if not os.path.exists(asset_path):
                    problems.append(f"Project '{name}' references missing asset: {p[asset_field]}")


def check_technologies(problems):
    try:
        groups = load_json("data/technologies.json")
    except Exception as exc:
        problems.append(f"Could not load data/technologies.json: {exc}")
        return
    for group in groups:
        category = group.get("category", "<uncategorized>")
        for item in group.get("items", []):
            for field in ("name", "purpose", "icon"):
                if field not in item or not item[field]:
                    problems.append(f"Technology in '{category}' is missing field: {field}")
                    continue
            icon_path = os.path.join(ROOT, item.get("icon", ""))
            if item.get("icon") and not os.path.exists(icon_path):
                problems.append(f"Technology '{item.get('name')}' references missing icon: {item['icon']}")


def check_readme(problems):
    readme_path = os.path.join(ROOT, "README.md")
    if not os.path.exists(readme_path):
        problems.append("README.md does not exist. Run tools/build_readme.py.")
        return
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()
    if len(content.strip()) == 0:
        problems.append("README.md is empty.")

    # Find local (non-http) image/src references and confirm they exist.
    for match in re.finditer(r'(?:src|href)="([^"]+)"', content):
        ref = match.group(1)
        if ref.startswith("http") or ref.startswith("mailto:") or ref.startswith("#"):
            continue
        ref_path = os.path.join(ROOT, ref)
        if not os.path.exists(ref_path):
            problems.append(f"README.md references missing local asset: {ref}")

    for match in re.finditer(r'!\[[^\]]*\]\(([^)]+)\)', content):
        ref = match.group(1)
        if ref.startswith("http"):
            continue
        ref_path = os.path.join(ROOT, ref)
        if not os.path.exists(ref_path):
            problems.append(f"README.md references missing local asset: {ref}")

    for banned in ["TODO", "ADD IMAGE HERE", "YOUR_TOKEN_HERE"]:
        if banned in content:
            problems.append(f"README.md still contains a placeholder: {banned}")


def main():
    problems = []
    check_json_files(problems)
    check_profile_fields(problems)
    check_projects(problems)
    check_technologies(problems)
    check_readme(problems)

    if problems:
        print(f"Validation failed with {len(problems)} problem(s):\n")
        for problem in problems:
            print(f"  - {problem}")
        sys.exit(1)

    print("Validation passed: JSON is valid, required fields are present, all referenced assets exist.")


if __name__ == "__main__":
    main()
