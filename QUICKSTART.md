# fileconv quick start

This guide sets up fileconv on Ubuntu 24.04+ and explains the CLI, radial
overlay, and optional GNOME keyboard shortcut. The application is local-only:
conversions happen on your computer; there are no uploads or runtime network
calls.

## 1. Install

Install Python 3.11 or newer. From the project directory:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

To enable HEIC input and output, also install the optional extra:

```sh
python -m pip install -e '.[heic]'
```

Conversions that rely on system programs need those programs installed. For
Ubuntu, for example:

```sh
sudo apt update
sudo apt install libreoffice pandoc poppler-utils libnotify-bin
```

LibreOffice enables DOCX/PPTX/XLSX/ODT to PDF. Pandoc enables DOCX/Markdown
conversions. Markdown-to-PDF additionally needs a PDF engine that Pandoc can
use. `fileconv doctor` reports registered conversions and whether external
tools are available.

## 2. Convert files

```sh
fileconv targets photo.jpg
fileconv convert photo.jpg png
fileconv convert report.docx pdf
fileconv convert report.pdf md
fileconv merge first.pdf second.pdf
fileconv doctor
```

By default, output is saved beside the source. To choose a destination folder:

```sh
fileconv convert report.docx pdf --out-dir "$HOME/Documents/converted"
```

Existing output is not overwritten. PDF-to-PNG/JPG conversion creates a
uniquely named folder such as `report_pages/`, containing one image per page.

## 3. Open the radial menu

Open the fullscreen overlay:

```sh
fileconv-menu
```

Then drag a supported file from Nautilus onto the overlay. Hover over a format
slice and release to convert. For several PDFs, choose **Merge**. The output
is saved next to the input file, and the menu reports completion with a desktop
notification. Press **Esc** to close the overlay.

You can also open the menu with one file already loaded:

```sh
fileconv-menu "$HOME/Pictures/photo.png"
```

Click a target-format slice to start that conversion. The conversion itself
runs in the background so the overlay remains responsive.

## 4. Add a GNOME keyboard shortcut (optional)

The project includes [`scripts/install_shortcut.sh`](scripts/install_shortcut.sh).
It configures a custom GNOME shortcut and preserves existing custom shortcuts.
The default binding is **Super+Shift+C**, and the default command points to
this project's `.venv/bin/fileconv-menu`.

Run it from the project directory:

```sh
chmod +x scripts/install_shortcut.sh
./scripts/install_shortcut.sh
```

Choose a different binding:

```sh
./scripts/install_shortcut.sh "" "<Control><Alt>c"
```

The empty first argument keeps the default menu command; the second argument
sets the GNOME key-binding syntax. To use a different executable path:

```sh
./scripts/install_shortcut.sh "$HOME/.local/bin/fileconv-menu" "<Super><Shift>c"
```

The script can be re-run to update the command or binding. To remove the
shortcut, open **Settings → Keyboard → Custom Shortcuts** and delete the
“fileconv menu” entry.

## 5. Test and diagnose

```sh
pytest
ruff check src tests
fileconv doctor
```

Conversions requiring missing external tools are omitted from the menu and
shown as unavailable by `doctor`. Tests for optional external programs skip
when the program is not installed.

## Help and contributions

Created by **Mohamed iliass KADDAR**. For help, bug reports, or contribution
ideas, contact [mohamediliassk@gmail.com](mailto:mohamediliassk@gmail.com).
See [README.md](README.md) for supported formats, project structure,
limitations, and license information.
