#!/usr/bin/env python3
"""
Static site builder for filipcaniga.sk

Generates HTML for 3 languages (sk, en, de) from templates in _src/.
Output goes to /<lang>/<path>/ — e.g. _src/o-mne/index.html → /sk/o-mne/index.html
The root /index.html is a JS redirect that detects browser language.

Templating syntax:
  {% include "_partials/X.html" var1="value" var2="value" %}
  {{ variable }}

Translation keys (defined in _src/_i18n/<lang>.py) become regular variables:
  {{ nav_home }}    →  "Domov" / "Home" / "Startseite"

Usage:
  python3 build.py            # build all languages
  python3 build.py --watch    # rebuild on file changes
"""

import importlib.util
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / '_src'
I18N = SRC / '_i18n'

LANGUAGES = ['sk', 'en', 'de']
DEFAULT_LANG = 'sk'

INCLUDE_RE = re.compile(r'\{%\s*include\s+"([^"]+)"((?:\s+\w+="[^"]*")*)\s*%\}')
ATTR_RE = re.compile(r'(\w+)="([^"]*)"')
VAR_RE = re.compile(r'\{\{\s*(\w+)\s*\}\}')


def load_translations(lang: str) -> dict:
    """Load translation dict from _src/_i18n/<lang>.py."""
    path = I18N / f'{lang}.py'
    spec = importlib.util.spec_from_file_location(f'i18n_{lang}', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return dict(mod.T)


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
    # Multi-pass variable substitution so that translation strings containing
    # {{ base }} (or other vars) get expanded too. Cap at 5 passes to be safe.
    for _ in range(5):
        new = VAR_RE.sub(lambda m: str(vars.get(m.group(1), '')), text)
        if new == text:
            break
        text = new
    return text


def lang_url(current_lang: str, target_lang: str, page_path: str) -> str:
    """Compute URL to switch from current_lang to target_lang for given page.
    page_path is relative to /<lang>/ root (e.g. 'o-mne/index.html', 'index.html').
    """
    # Number of `..` to climb up from /<current_lang>/<page_path> to root
    depth = page_path.count('/')
    base_up = '../' * (depth + 1)  # +1 to leave the lang folder
    return f'{base_up}{target_lang}/{page_path}'


def page_base(page_path: str) -> str:
    """Base path from a page to its <lang> root."""
    return '../' * page_path.count('/')


def build_page(src_file: Path, lang: str, translations: dict) -> Path:
    """Build one source file for one language."""
    rel = src_file.relative_to(SRC).as_posix()  # e.g. 'o-mne/index.html'
    base = page_base(rel)

    vars = dict(translations)
    vars['base'] = base
    # URLs to switch to other languages from this page
    for target in LANGUAGES:
        vars[f'url_{target}'] = lang_url(lang, target, rel)
    # Active language flag
    for L in LANGUAGES:
        vars[f'active_lang_{L}'] = ' active' if L == lang else ''

    out_file = ROOT / lang / rel
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(src_file, encoding='utf-8') as f:
        rendered = render(f.read(), vars)
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(rendered)
    return out_file


def build_root_redirect():
    """Write /index.html — a tiny JS redirect that detects browser language."""
    supported = ', '.join(f"'{L}'" for L in LANGUAGES)
    html = f'''<!DOCTYPE html>
<html lang="{DEFAULT_LANG}">
<head>
<meta charset="UTF-8">
<title>MUDr. Filip Čaniga</title>
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url=./{DEFAULT_LANG}/">
<script>
  (function() {{
    var supported = [{supported}];
    var stored = null;
    try {{ stored = localStorage.getItem('lang'); }} catch (e) {{}}
    var browser = (navigator.language || navigator.userLanguage || '{DEFAULT_LANG}').slice(0, 2).toLowerCase();
    var lang = (stored && supported.indexOf(stored) !== -1)
      ? stored
      : (supported.indexOf(browser) !== -1 ? browser : '{DEFAULT_LANG}');
    window.location.replace('./' + lang + '/');
  }})();
</script>
</head>
<body>
<p>Redirecting… <a href="./{DEFAULT_LANG}/">Slovensky</a> · <a href="./en/">English</a> · <a href="./de/">Deutsch</a></p>
</body>
</html>
'''
    with open(ROOT / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html)


def build_all() -> int:
    count = 0
    for lang in LANGUAGES:
        translations = load_translations(lang)
        for src_file in sorted(SRC.rglob('*.html')):
            if '_partials' in src_file.parts:
                continue
            out = build_page(src_file, lang, translations)
            print(f"  ✓ {out.relative_to(ROOT)}")
            count += 1
    build_root_redirect()
    print(f"  ✓ index.html (root redirect)")
    return count


def watch():
    """Rebuild whenever any file under _src/ changes."""
    print("Watching _src/ for changes (Ctrl+C to stop)...")
    last = {}
    extensions = ('.html', '.py')
    while True:
        changed = False
        for f in SRC.rglob('*'):
            if not f.is_file() or not f.name.endswith(extensions):
                continue
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
        print(f"Done. Built {n} pages across {len(LANGUAGES)} languages.")
