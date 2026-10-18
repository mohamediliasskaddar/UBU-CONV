"""PDF operations powered by pikepdf."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pikepdf

from fileconv.core.errors import ConversionError


def merge_pdfs(sources: list[Path], output: Path) -> None:
    """Merge source PDFs in order and atomically write the destination."""
    try:
        merged = pikepdf.Pdf.new()
        try:
            for source in sources:
                with pikepdf.open(source) as document:
                    merged.pages.extend(document.pages)

            with tempfile.TemporaryDirectory(prefix="fileconv-merge-", dir=output.parent) as temp:
                temporary_output = Path(temp) / "merged.pdf"
                merged.save(temporary_output)
                os.replace(temporary_output, output)
        finally:
            merged.close()
    except pikepdf.PdfError as exc:
        raise ConversionError(f"Could not merge PDF files: {exc}") from exc
