"""Supported format names and extension normalization."""

from __future__ import annotations

IMAGE_FORMATS = frozenset({"jpg", "png", "webp", "bmp", "tiff"})
DOCUMENT_FORMATS = frozenset({"docx", "pptx", "xlsx", "odt"})
PDF_FORMATS = frozenset({"pdf"})
TEXT_FORMATS = frozenset({"md", "html", "txt"})

_ALIASES = {"jpeg": "jpg", "tif": "tiff", "htm": "html"}


def normalize_extension(extension: str) -> str:
    """Return a lowercase extension without a leading dot, applying aliases."""
    normalized = extension.strip().lower().lstrip(".")
    return _ALIASES.get(normalized, normalized)


def category_for(extension: str) -> str | None:
    """Return the broad category for a known extension, or None if unknown."""
    normalized = normalize_extension(extension)
    if normalized in IMAGE_FORMATS or normalized == "heic":
        return "image"
    if normalized in DOCUMENT_FORMATS:
        return "doc"
    if normalized in PDF_FORMATS:
        return "pdf"
    if normalized in TEXT_FORMATS:
        return "text"
    return None
