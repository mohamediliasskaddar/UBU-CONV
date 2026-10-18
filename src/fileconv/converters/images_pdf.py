"""Image-to-PDF and PDF-to-image conversions."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import img2pdf
import pymupdf
from PIL import Image

from fileconv.core.registry import register


def _flattened_png(source: Path) -> bytes:
    with Image.open(source) as image:
        if image.mode in {"RGBA", "LA"} or "transparency" in image.info:
            rgba = image.convert("RGBA")
            background = Image.new("RGB", rgba.size, "white")
            background.paste(rgba, mask=rgba.getchannel("A"))
            rgba.close()
        else:
            background = image.convert("RGB")

        buffer = BytesIO()
        try:
            background.save(buffer, format="PNG")
            return buffer.getvalue()
        finally:
            background.close()


@register("jpg", "pdf")
@register("png", "pdf")
@register("webp", "pdf")
@register("bmp", "pdf")
@register("tiff", "pdf")
def image_to_pdf(source: Path, output: Path) -> None:
    """Embed a flattened RGB PNG image in a PDF using img2pdf."""
    output.write_bytes(img2pdf.convert(_flattened_png(source)))


def _pdf_to_images(source: Path, output: Path, extension: str) -> None:
    with pymupdf.open(source) as document:
        for page_number, page in enumerate(document, start=1):
            pixmap = page.get_pixmap(dpi=150, colorspace=pymupdf.csRGB, alpha=False)
            page_path = output / f"page-{page_number:03d}.{extension}"
            pixmap.save(page_path)


@register("pdf", "png", output_is_directory=True)
def pdf_to_png(source: Path, output: Path) -> None:
    """Render each PDF page to a 150 dpi PNG in the output directory."""
    _pdf_to_images(source, output, "png")


@register("pdf", "jpg", output_is_directory=True)
def pdf_to_jpg(source: Path, output: Path) -> None:
    """Render each PDF page to a 150 dpi JPEG in the output directory."""
    _pdf_to_images(source, output, "jpg")
