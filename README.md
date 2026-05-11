# MUDr. Filip Čaniga — webstránka

Statická stránka generovaná z templates v `_src/`.

## Štruktúra

```
.
├── _src/                          # ZDROJ — tu editujte
│   ├── _partials/                 # Spoločné časti (header, footer, ...)
│   │   ├── head.html              # <head> + meta + CSS
│   │   ├── header.html            # logo + navigácia + mobile-nav
│   │   ├── footer.html            # footer + cookie banner
│   │   ├── ig-icon.html           # Instagram SVG ikona
│   │   └── ig-tile.html           # Instagram dlaždica
│   ├── index.html                 # zdrojová verzia stránok
│   ├── o-mne/index.html
│   └── ...
├── index.html                     # VYGENEROVANÉ — needitujte priamo
├── o-mne/index.html               # vygenerované
├── ...
├── css/, js/, fotky/              # statické assety (nezasahuje sa cez build)
└── build.py                       # generátor (Python 3, bez závislostí)
```

## Workflow

1. **Edit** súbor v `_src/` (napr. zmeň text v `_partials/footer.html`)
2. **Build:** `python3 build.py`
3. **Commit + push** — GitHub Pages servuje root priamo

### Šablónová syntax

Include partial s premennými:

```html
{% include "_partials/header.html" base="../" active_omne=" active" %}
```

Premenné v partials:

```html
<a href="{{ base }}index.html" class="nav-link{{ active_home }}">Domov</a>
```

### Premenné

- `base` — relatívna cesta k root-u (`""` pre root, `"../"` pre /o-mne/, `"../../"` pre /zakroky/foo/, ...)
- `title`, `description` — pre <head>
- `active_home`, `active_omne`, `active_zakroky`, `active_mediach`, `active_faq`, `active_kontakt` — pre zvýraznenie aktívnej položky v nav (nastav na `" active"` na danej stránke)

## Build commands

```bash
python3 build.py            # zbuilduje všetkých 12 stránok
python3 build.py --watch    # automatický rebuild pri zmene súborov v _src/
```

## Hosting na GitHub Pages

1. Push repo na GitHub
2. Settings → Pages → Source: `main` branch, `/ (root)` → Save
3. Stránka beží na `https://USERNAME.github.io/REPO/`

Vlastná doména: Settings → Pages → Custom domain.

GitHub Pages servuje vygenerované HTML súbory v root-e priamo — žiadny build na strane GitHubu nie je potrebný (zbuildujte lokálne pred push-om, alebo pozri `.github/workflows/build.yml` pre auto-build).
