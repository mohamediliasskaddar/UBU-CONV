# fileconv

`fileconv` is a local-only file conversion prototype for Ubuntu 24.04+ and
Wayland. The current milestone provides image, PDF, office-document, and text
conversions through a command-line interface.

## Install

```sh
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
```

To enable HEIC support, install the optional extra:

```sh
python -m pip install -e '.[heic]'
```

## Use

```sh
fileconv targets image.jpg
fileconv convert image.jpg png
fileconv doctor
```

Converted files are saved beside the input by default. If the requested name
already exists, `fileconv` chooses `name (1).ext`, then the next available
number, without replacing existing files.

The current milestone supports conversions among JPG, PNG, WEBP, BMP, and TIFF.
HEIC is included only when `pillow-heif` is installed. It also supports image
to PDF; PDF to PNG/JPG, TXT, or Markdown; DOCX/PPTX/XLSX/ODT to PDF; DOCX to
Markdown/HTML/TXT; Markdown to DOCX/HTML; and merging multiple PDFs.
Markdown-to-PDF is offered only when Pandoc and a supported PDF engine are
installed. The graphical menu remains planned for a later milestone.

## Step 2 testing

```sh
mkdir -p converted
fileconv convert tests/fixtures/sample.docx pdf --out-dir converted
fileconv convert tests/fixtures/sample.pdf md --out-dir converted
fileconv convert tests/fixtures/sample.png pdf --out-dir converted
fileconv convert tests/fixtures/sample.pdf png --out-dir converted
fileconv merge tests/fixtures/sample.pdf tests/fixtures/sample.pdf --out-dir converted
fileconv doctor
```

Install LibreOffice to enable office-document conversions, and install Pandoc
to enable DOCX/Markdown conversions. `doctor` lists conversions by source
format and identifies missing external tools. Tests for conversions requiring
those tools are skipped when the tools are unavailable.

## Known limits

- PDF-to-DOCX/PPTX conversion is inherently limited because PDFs store
  positioned glyphs rather than document structure; `pdf2docx` may be explored
  later.
- Scanned PDFs need OCR support such as `ocrmypdf` and Tesseract; this is out
  of scope for the prototype.
- A normal Wayland application cannot provide a system-wide “hold Shift while
  dragging” trigger. That would require a GNOME Shell extension.
- PyMuPDF is AGPL-licensed. Re-check its licensing implications before
  distributing a version that uses it.

## Development

```sh
pytest
ruff check src tests
```
