"""Pandoc conversions for DOCX and Markdown files."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from fileconv.core.registry import register

_PDF_ENGINES = (
    "pdflatex",
    "xelatex",
    "lualatex",
    "latexmk",
    "tectonic",
    "wkhtmltopdf",
    "weasyprint",
    "prince",
    "context",
    "typst",
)
_PDF_ENGINE = next((engine for engine in _PDF_ENGINES if shutil.which(engine)), None)


def _pandoc_convert(source: Path, output: Path) -> None:
    command = ["pandoc", str(source), "--output", str(output)]
    if output.suffix.lower() == ".pdf" and _PDF_ENGINE is not None:
        command.extend(["--pdf-engine", _PDF_ENGINE])
    subprocess.run(command, check=True, timeout=120)


for _destination_extension in ("md", "html", "txt"):
    register("docx", _destination_extension, tool="pandoc")(_pandoc_convert)

for _destination_extension in ("docx", "html"):
    register("md", _destination_extension, tool="pandoc")(_pandoc_convert)

if _PDF_ENGINE is not None:
    register("md", "pdf", tool="pandoc")(_pandoc_convert)
