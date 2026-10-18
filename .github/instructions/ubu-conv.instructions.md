# fileconv: local file converter with a radial drop menu (Ubuntu / Wayland)
> Tip: copy this file to `.github/copilot-instructions.md` so Copilot keeps the rules in context.

## 1. Goal

A **local-only** desktop tool (no web, no server, no uploads) for Ubuntu 24.04+ running **Wayland**.
The user drops a file onto a radial menu, picks a target format, and the converted file is saved next to the original.
This is a **prototype to learn how it works**: keep it small, readable, and easy to extend.

## 2. Hard constraints

- Python 3.11+, managed with a `.venv` and `pyproject.toml` (src layout).
- GUI: **PySide6** (Qt6). CLI: **Typer**.
- No network calls at runtime. No telemetry.
- **Wayland-safe**: do NOT rely on global key/mouse hooks, on positioning windows at the cursor, or on any X11-only API.
- The engine (`core`, `converters`) must **never import** PySide6. GUI and CLI are thin layers over the engine.
- Call external tools with `subprocess.run([...], check=True, timeout=...)`, as a **list** (never `shell=True`). Handle file names with spaces and accents.
- Never overwrite an existing file: use `name.ext`, then `name (1).ext`, `name (2).ext`...
- Type hints everywhere, small functions, docstrings only where useful.

## 3. Prototype scope (v0)

Only these conversions. Everything else is out of scope for now.

| Input | Output | Tool |
|---|---|---|
| jpg, png, webp, bmp, tiff (+ heic if `pillow-heif` is installed) | any other of these image formats | Pillow |
| jpg, png, webp, bmp, tiff | pdf | img2pdf |
| pdf | png, jpg (one file per page, in a new folder) | PyMuPDF |
| docx, pptx, xlsx, odt | pdf | LibreOffice headless |
| docx | md, html, txt | Pandoc |
| md | docx, html, pdf | Pandoc |
| pdf | txt, md | pymupdf4llm (md) / PyMuPDF (txt) |
| several pdf | one merged pdf | pikepdf |

Explicitly **out of v0**: PDF to DOCX/PPTX, OCR, crop/trim/compress UI, audio/video, conversion chaining, the Shift-drag trigger, packaging.

## 4. Architecture

```
┌───────────────────────────────────────────────┐
│  Interfaces:  CLI (Typer)   |   GUI (PySide6)  │
├───────────────────────────────────────────────┤
│  core: registry + runner + errors + naming      │
├───────────────────────────────────────────────┤
│  converters: one module per tool family         │
│  (Pillow, img2pdf, PyMuPDF, LibreOffice,        │
│   Pandoc, pikepdf)                              │
└───────────────────────────────────────────────┘
```

### 4.1 Registry (heart of the project)

Each converter registers itself with a decorator; the GUI menu and the CLI are generated from the registry.

```python
# core/registry.py
@dataclass(frozen=True)
class Converter:
    src: str                      # lowercase extension, no dot: "docx"
    dst: str                      # "pdf"
    fn: Callable[[Path, Path], None]   # fn(input_path, output_path)
    tool: str | None = None       # external binary required, e.g. "soffice", "pandoc"
    label: str | None = None      # display text, defaults to dst.upper()

    def available(self) -> bool: ...   # True if tool is None or found with shutil.which

def register(src: str, dst: str, tool: str | None = None, label: str | None = None): ...  # decorator

def targets_for(ext: str) -> list[Converter]: ...   # only AVAILABLE converters for this input extension
def get(src: str, dst: str) -> Converter: ...
```

Rules:
- `targets_for` hides converters whose external tool is missing (so the menu never shows a dead slice).
- Extension matching is case-insensitive; `jpeg` is normalized to `jpg`, `tif` to `tiff`, `htm` to `html`.

### 4.2 Runner

```python
# core/runner.py
def convert(src: Path, dst_ext: str, out_dir: Path | None = None) -> Path:
    """Look up converter, compute a non-colliding output path, run it, return the output path.
    Raises ConversionError with a human-readable message on any failure."""

def merge_pdfs(sources: list[Path], out_dir: Path | None = None) -> Path: ...
```

- Output goes next to the source unless `out_dir` is given.
- For `pdf -> png/jpg`, create a folder `<name>_pages/` and write `page-001.png`, ...; return the folder path.
- LibreOffice: use a **temporary profile per call** (`-env:UserInstallation=file:///tmp/<uuid>`) and a 120 s timeout, to avoid lock conflicts and hangs. Convert into a temp dir, then move the result to the final non-colliding path.
- Wrap `subprocess.CalledProcessError`, `TimeoutExpired`, `FileNotFoundError` into `ConversionError`.

### 4.3 GUI: radial drop menu (Wayland-compatible design)

Key idea: Wayland cannot watch drags in other windows, so the app shows **its own** translucent overlay and the user drags the file onto it.

- Entry point `fileconv-menu`, launched by a **GNOME custom keyboard shortcut** (Settings, Keyboard, Custom Shortcuts).
- Optional argument: `fileconv-menu /path/to/file.jpg` pre-loads the file (useful later for a Nautilus context-menu entry).
- Window: frameless, always-on-top, `WA_TranslucentBackground`, fullscreen or large centered; draw a dimmed backdrop. `Esc` or a click on the backdrop closes it. Do not try to place it at the cursor.
- **State 1, waiting:** show a centered ring with a hint ("Drop a file"). Accept drops (`setAcceptDrops(True)`).
- On `dragEnterEvent`, read `mimeData().urls()`: as soon as the file(s) are known, **rebuild the ring** from `registry.targets_for(ext)`.
- **State 2, choosing:** one slice per target format; highlight the slice under the cursor during `dragMoveEvent`; `dropEvent` on a slice triggers the conversion.
- If more than 8 targets, show the first 7 plus a "More" slice that opens a second ring. (Can be a stub in v0.)
- If several PDFs are dropped, add a "Merge" slice.
- Conversion runs in a `QThreadPool`/`QRunnable` worker (never block the UI thread). While running, animate the slice (pulsing or spinner). On finish: desktop notification via `notify-send` (subprocess) with the output file name, then close the window. On error: show the message in the ring center and a notification.
- Slice geometry: `QPainterPath` ring segments built from angle math; hit-testing by angle and radius from the center (`atan2`). Keep this logic in `menu_model.py` as pure functions so it can be unit tested without a display.

## 5. File structure

```
fileconv/
├── pyproject.toml
├── README.md
├── COPILOT_BRIEF.md
├── .github/
│   └── copilot-instructions.md
├── scripts/
│   ├── install_deps.sh            # apt + pip dependencies
│   └── install_shortcut.sh        # prints/creates the GNOME shortcut command
├── src/fileconv/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── errors.py              # ConversionError
│   │   ├── formats.py             # extension normalization + category (image/doc/pdf/text)
│   │   ├── naming.py              # unique_path(path) -> non-colliding path
│   │   ├── registry.py            # Converter, register, targets_for, get
│   │   └── runner.py              # convert(), merge_pdfs()
│   ├── converters/
│   │   ├── __init__.py            # imports all modules so decorators run
│   │   ├── images.py              # Pillow image <-> image, heic optional
│   │   ├── images_pdf.py          # img2pdf, PDF -> images (PyMuPDF)
│   │   ├── office.py              # LibreOffice headless -> pdf
│   │   ├── pandoc.py              # docx/md <-> md/html/txt/pdf
│   │   ├── pdf_text.py            # pdf -> txt/md
│   │   └── pdf_ops.py             # merge (pikepdf)
│   ├── cli/
│   │   ├── __init__.py
│   │   └── main.py                # Typer app: convert, targets, merge, doctor
│   └── gui/
│       ├── __init__.py
│       ├── app.py                 # QApplication, argv parsing, entry point
│       ├── radial_menu.py         # overlay widget (paint, drag/drop events)
│       ├── menu_model.py          # pure geometry: slices, angles, hit test
│       ├── worker.py              # QRunnable calling core.runner.convert
│       └── notify.py              # notify-send wrapper
└── tests/
    ├── fixtures/                  # tiny sample files: .jpg .png .docx .pdf .md
    ├── test_formats.py
    ├── test_naming.py
    ├── test_registry.py
    ├── test_images.py
    ├── test_menu_model.py         # geometry only, no display needed
    └── test_office_pandoc.py      # skipped if soffice/pandoc missing
```

`pyproject.toml` entry points:

```toml
[project.scripts]
fileconv = "fileconv.cli.main:app"
fileconv-menu = "fileconv.gui.app:main"
```

Dependencies: `pillow`, `pillow-heif` (optional extra), `img2pdf`, `pymupdf`, `pymupdf4llm`, `pikepdf`, `typer`, `PySide6`; dev: `pytest`, `ruff`.
System packages (apt): `libreoffice pandoc poppler-utils libnotify-bin fonts-crosextra-carlito fonts-crosextra-caladea`.

## 6. CLI spec (used to test the engine before the GUI exists)

```
fileconv targets report.docx          # lists available output formats for this file
fileconv convert report.docx pdf      # converts, prints output path
fileconv merge a.pdf b.pdf            # merges into merged.pdf (unique name)
fileconv doctor                       # shows which external tools are found (soffice, pandoc...) and which converters are therefore available
```

## 7. Build order (do one step at a time, stop after each)

1. **Engine skeleton:** `core/*`, `formats.py`, `naming.py`, registry, runner, `errors.py`, plus `converters/images.py` and the CLI commands `targets`, `convert`, `doctor`. Tests for formats, naming, registry, images. *Done when* `fileconv convert photo.jpg png` works.
2. **More converters:** `images_pdf.py`, `office.py`, `pandoc.py`, `pdf_text.py`, `pdf_ops.py` + `merge` CLI command. *Done when* `fileconv convert doc.docx pdf` and `fileconv convert doc.pdf md` work on the fixtures.
3. **Menu geometry:** `gui/menu_model.py` (slice angles, ring paths data, hit-test) with unit tests. No Qt widgets yet.
4. **Radial overlay:** `radial_menu.py` + `app.py`: transparent overlay, waiting state, rebuild ring on `dragEnter`, highlight on `dragMove`, convert on `drop` via the worker, notification at the end.
5. **Hotkey integration:** `scripts/install_shortcut.sh` that explains or runs the `gsettings` commands to bind a shortcut to `fileconv-menu`; document in README.
6. **Polish:** error display in the ring, "More" slice with second ring, "Merge" slice for multiple PDFs.

## 8. Acceptance checklist for v0

- [ ] `pytest` passes (tests needing soffice/pandoc are skipped if absent).
- [ ] `fileconv doctor` correctly reports missing tools and hides unavailable converters.
- [ ] Dropping a `.jpg` on the overlay shows only valid targets and converts correctly.
- [ ] Dropping a `.docx` offers PDF (and md/html/txt) and produces a correct file.
- [ ] Output never overwrites an existing file.
- [ ] The UI stays responsive during a 10 s LibreOffice conversion.
- [ ] Works under `XDG_SESSION_TYPE=wayland` with no X11-only calls.

## 9. Known limits to document in the README (not to fix now)

- PDF to DOCX/PPTX quality is inherently limited (PDF stores positioned glyphs, not paragraphs); planned later via `pdf2docx`.
- Scanned PDFs need OCR (`ocrmypdf` + `tesseract-ocr` with `fra`, `ara`, `eng`), planned later.
- A true "hold Shift while dragging anywhere" trigger is not possible from a normal Wayland app; it would need a GNOME Shell extension, planned much later.
- PyMuPDF is AGPL-licensed: fine for personal use, to re-check before distributing.