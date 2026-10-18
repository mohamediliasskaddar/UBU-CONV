# fileconv

**fileconv** is a local file converter for Ubuntu 24.04+ and Wayland. Drop a
file onto its radial menu, choose a format, and the converted file is written
beside the original. A command-line interface is also available.

The application runs conversions on the local machine: files are not uploaded,
and the project does not make network requests or collect telemetry.

> **Project status:** Prototype for learning and personal use. The conversion
> engine, CLI, radial-menu geometry, and initial GUI are implemented; see the
> support matrix and limitations below before relying on it.

## Quick start

See [QUICKSTART.md](QUICKSTART.md) for environment setup, optional system
tools, example conversions, and instructions for binding the GNOME keyboard
shortcut.

## Supported conversions

| Input | Output | Requirement |
| --- | --- | --- |
| JPG, PNG, WEBP, BMP, TIFF | Each other listed image format | Pillow |
| HEIC | JPG, PNG, WEBP, BMP, TIFF | Optional `pillow-heif` package |
| JPG, PNG, WEBP, BMP, TIFF | PDF | `img2pdf` |
| PDF | PNG or JPG pages in a `<name>_pages/` folder | PyMuPDF |
| DOCX, PPTX, XLSX, ODT | PDF | LibreOffice (`soffice`) |
| DOCX | Markdown, HTML, TXT | Pandoc |
| Markdown | DOCX, HTML | Pandoc |
| Markdown | PDF | Pandoc and an installed PDF engine |
| PDF | TXT or Markdown | PyMuPDF / pymupdf4llm |
| Two or more PDFs | One merged PDF | pikepdf |

`fileconv doctor` lists registered conversions grouped by input type and
identifies missing external tools. The GUI only offers conversions whose
required external tools are available.

## Interfaces

### Radial menu

Run `fileconv-menu` to open the fullscreen overlay, then drag a supported file
from Nautilus onto it. You can also preload a file by passing its path:

```sh
fileconv-menu "$HOME/Documents/report.docx"
```

Choose a slice to convert. For several PDFs, choose **Merge**. Press **Esc** to
close the menu. A GNOME shortcut can be installed with
[`scripts/install_shortcut.sh`](scripts/install_shortcut.sh).

### Command line

```sh
fileconv targets photo.jpg
fileconv convert photo.jpg png
fileconv convert report.docx pdf
fileconv convert document.pdf md
fileconv merge first.pdf second.pdf
fileconv doctor
```

Conversions are saved next to the source unless `--out-dir DIRECTORY` is
provided. Existing files are never overwritten: subsequent outputs get names
such as `photo (1).png`. PDF page images are written into a uniquely named
`<name>_pages/` directory.

## Project layout

- `src/fileconv/core/` — conversion registry, output naming, errors, and runner
- `src/fileconv/converters/` — image, PDF, office, and text converters
- `src/fileconv/cli/` — Typer command-line interface
- `src/fileconv/gui/` — pure geometry and PySide6 radial overlay
- `tests/` — unit tests and small conversion fixtures
- `scripts/` — Ubuntu setup helpers

## Limitations

- PDF-to-DOCX/PPTX, OCR, audio/video, conversion chaining, and a system-wide
  Shift-drag trigger are outside the current scope.
- PDF-to-DOCX/PPTX conversion is inherently limited because PDFs store
  positioned glyphs rather than document structure.
- Scanned PDFs require OCR software, which is not included.
- A normal Wayland application cannot listen for global key or mouse events.
  The supported workflow is to open the overlay and drop a file onto it.
- PyMuPDF is AGPL-licensed. This project's MIT license applies to the project
  code, not to third-party dependencies; review their licenses before
  redistribution.

## Tests and development

```sh
pytest
ruff check src tests
```

Tests that require LibreOffice or Pandoc are skipped when the corresponding
tool is unavailable.

## Author and contributions

Created by **Mohamed iliass KADDAR**.

Questions, bug reports, and contribution discussions: [mohamediliassk@gmail.com](mailto:mohamediliassk@gmail.com).

Contributions are welcome. Please contact me before substantial changes, and
include relevant tests and a clear description of the behavior changed.

## License

The project code is licensed under the [MIT License](LICENSE). Third-party
dependencies remain under their own licenses.
