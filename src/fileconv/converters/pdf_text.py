"""Text and Markdown extraction from PDF documents."""

from __future__ import annotations

from pathlib import Path

import pymupdf
import pymupdf4llm

from fileconv.core.registry import register


@register("pdf", "txt")
def pdf_to_text(source: Path, output: Path) -> None:
    """Extract page text from a PDF with PyMuPDF."""
    with pymupdf.open(source) as document:
        text = "\n\n".join(page.get_text() for page in document)
    output.write_text(text, encoding="utf-8")


@register("pdf", "md")
def pdf_to_markdown(source: Path, output: Path) -> None:
    """Extract structured Markdown from a PDF with pymupdf4llm."""
    output.write_text(pymupdf4llm.to_markdown(source), encoding="utf-8")
