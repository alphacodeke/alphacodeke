"""
Shared helpers for the alphacodeke profile generation toolkit.

Every generator script imports from here so that colors, fonts and
JSON loading stay in one place instead of being duplicated across files.
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_json(relative_path):
    path = os.path.join(ROOT, relative_path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def theme():
    return load_json("config/theme.json")


def profile():
    return load_json("config/profile.json")


def projects():
    return load_json("data/projects.json")


def technologies():
    return load_json("data/technologies.json")


def write_svg(relative_path, svg_content):
    path = os.path.join(ROOT, relative_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg_content.strip() + "\n")
    return path


def esc(text):
    """Minimal XML escaping for text placed inside SVG <text> nodes."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def wrap_words(text, max_chars):
    """Greedy word-wrap used to lay out multi-line SVG labels."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = (current + " " + word).strip()
        if len(candidate) > max_chars and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines
