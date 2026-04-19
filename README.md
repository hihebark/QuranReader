# Quran Gnome

A native GNOME application for reading the Quran, built with Python, GTK4, and libadwaita.

## Features

- **Mushaf mode** - Authentic page-by-page rendering using ligature-based SVG pages (604 pages, Mushaf Qatar / qpc-hafs font)
- **Text mode** - Ayah-by-ayah view with Arabic text and English translation (Sahih International)
- **Bilingual sidebar** - Surah list in Arabic or English with live search
- **RTL-aware layout** - Sidebar moves to the right in Arabic mode
- **Keyboard navigation** - Arrow keys and Page Up/Down in Mushaf mode
- **Ayah selection** - Multi-select with right-click context menu (Copy Arabic, Copy English, Copy Reference)
- **Offline** - Fully offline after one-time text database setup

## Screenshots

| Mushaf mode | Text mode |
|---|---|
| SVG page rendering | Arabic + English per ayah |

## Requirements

- Python 3.8+
- GTK 4
- libadwaita 1.0+
- PyGObject

**Debian / Ubuntu:**
```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1
```

**Fedora:**
```bash
sudo dnf install python3-gobject gtk4 libadwaita
```

## Setup

```bash
git clone https://github.com/hihebark/quran-gnome.git
cd quran-gnome
python3 src/main.py
```

## Project Structure

```
data/
  mushaf-qatar-layout.db    # Mushaf Qatar page/line layout (from qul.tarteel.ai)
  quran-pages/              # 604 ligature-based SVG pages   (from qul.tarteel.ai)
  quran-text.db             # Arabic + English ayah text (bundled)
scripts/
  build_text_db.py          # Regenerate quran-text.db from alquran.cloud (optional)
src/
  main.py                   # Entry point
  quran_gnome/
    __init__.py
    constants.py            # Paths, CSS, surah metadata
    db.py                   # Database access layer
    window.py               # GTK4 / Adwaita application and UI
```

## Data Sources

Mushaf layout and SVG pages are from the
[QUL - Quran Universal Library](https://qul.tarteel.ai/resources) by Tarteel AI.

- `mushaf-qatar-layout.db` - Qatar Foundation mushaf page/line/word layout
- `quran-pages/*.svg` - Vector mushaf pages (Mushaf Qatar, qpc-hafs font)

English translation (Sahih International) is fetched via the
[alquran.cloud API](https://alquran.cloud/api) and cached locally.

## License

This project is released into the public domain under [The Unlicense](LICENSE).

Quran data from QUL (Tarteel AI) is used under their respective terms.
See [qul.tarteel.ai/resources](https://qul.tarteel.ai/resources) for details.
