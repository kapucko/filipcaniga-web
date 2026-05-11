#!/usr/bin/env python3
"""
Static site builder for filipcaniga.sk

Reads templates from _src/, outputs final HTML to project root.
Supports two directives:
  {% include "_partials/X.html" var1="value" var2="value" %}
  {{ variable }}

Usage:
  python3 build.py            # build all pages
  python3 build.py --watch    # rebuild on file changes
"""

import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / '_src'

INCLUDE_RE = re.compile(r'\{%\s*include\s+"([^"]+)"((?:\s+\w+="[^"]*")*)\s*%\}')
ATTR_RE = re.compile(r'(\w+)="([^"]*)"')
VAR_RE = re.compile(r'\{\{\s*(\w+)\s*\}\}')


def render(text: str, vars: dict) -> str:
    """Recursively expand {% include %} directives, then substitute {{ vars }}."""

    def replace_include(m):
        partial_path = SRC / m.group(1)
        sub_vars = dict(vars)
        for am in ATTR_RE.finditer(m.group(2)):
            sub_vars[am.group(1)] = am.group(2)
        with open(partial_path, encoding='utf-8') as f:
            return render(f.read(), sub_vars)

    text = INCLUDE_RE.sub(replace_include, text)
    text = VAR_RE.sub(lambda m: vars.get(m.group(1), ''), text)
    return text


def build_one(src_file: Path) -> Path:
    rel = src_file.relative_to(SRC)
    out_file = ROOT / rel
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(src_file, encoding='utf-8') as f:
        rendered = render(f.read(), {})
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(rendered)
    return out_file


def build_all() -> int:
    count = 0
    for src_file in sorted(SRC.rglob('*.html')):
        if '_partials' in src_file.parts:
            continue
        out_file = build_one(src_file)
        rel = out_file.relative_to(ROOT)
        print(f"  ✓ {rel}")
        count += 1
    return count


def watch():
    """Rebuild whenever any file under _src/ changes."""
    print("Watching _src/ for changes (Ctrl+C to stop)...")
    last = {}
    while True:
        changed = False
        for f in SRC.rglob('*.html'):
            mtime = f.stat().st_mtime
            if last.get(f) != mtime:
                last[f] = mtime
                changed = True
        if changed:
            print("\nRebuilding...")
            build_all()
            print("Done.")
        time.sleep(0.5)


if __name__ == '__main__':
    if not SRC.exists():
        print(f"Error: {SRC} does not exist", file=sys.stderr)
        sys.exit(1)

    if '--watch' in sys.argv:
        build_all()
        try:
            watch()
        except KeyboardInterrupt:
            print("\nStopped.")
    else:
        print("Building...")
        n = build_all()
        print(f"Done. Built {n} pages.")
