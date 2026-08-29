"""
Regenerate the entire profile: icons, diagrams, GitHub stats, then README.md.

This is the single entry point used by both local development and the
GitHub Actions workflow (.github/workflows/update-profile.yml). It calls
the other tools/ scripts in the order that makes the output correct:
static and per-project assets first, GitHub API data second (since it
can fail independently of everything else), README last (since it
references every asset generated before it).

Run:
    python tools/update_profile.py

GitHub stats/contribution failures are logged but do not stop the run,
so a temporary GitHub API outage never blocks a README rebuild.
"""

import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")


def run(script, required=True):
    path = os.path.join(TOOLS, script)
    result = subprocess.run([sys.executable, path], cwd=TOOLS)
    if result.returncode != 0:
        message = f"{script} exited with status {result.returncode}."
        if required:
            print(f"ERROR: {message}", file=sys.stderr)
            sys.exit(result.returncode)
        else:
            print(f"WARNING: {message} Continuing with existing assets.", file=sys.stderr)


def main():
    run("generate_tech_icons.py")
    run("generate_project_diagrams.py")
    run("generate_static_diagrams.py")
    run("generate_github_stats.py", required=False)
    run("generate_contributions.py", required=False)
    run("build_readme.py")
    print("Profile update complete.")


if __name__ == "__main__":
    main()
