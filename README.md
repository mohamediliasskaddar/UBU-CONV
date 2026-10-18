# fileconv

`fileconv` is a local-only file conversion prototype for Ubuntu 24.04+ and
Wayland. It is being built in small milestones; this first milestone provides
the conversion engine and CLI for image-to-image conversions.

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
fileconv targets photo.jpg
fileconv convert photo.jpg png
fileconv doctor
```

Converted files are saved beside the input by default. If the requested name
already exists, `fileconv` chooses `name (1).ext`, then the next available
number, without replacing existing files.

The current milestone supports conversions among JPG, PNG, WEBP, BMP, and TIFF.
HEIC is included only when `pillow-heif` is installed. PDF, office-document,
text, and graphical-menu support are planned for later milestones.

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
ruff check .
```
