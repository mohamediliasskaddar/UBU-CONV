"""Image format conversions powered by Pillow."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from fileconv.core.formats import IMAGE_FORMATS
from fileconv.core.registry import ConversionFunction, register

_PIL_FORMATS = {
    "jpg": "JPEG",
    "png": "PNG",
    "webp": "WEBP",
    "bmp": "BMP",
    "tiff": "TIFF",
}

_IMAGE_INPUTS = set(IMAGE_FORMATS)
try:
    import pillow_heif
except ImportError:
    pillow_heif = None
else:
    pillow_heif.register_heif_opener()
    _IMAGE_INPUTS.add("heic")
    _PIL_FORMATS["heic"] = "HEIF"


def _convert_image(src: Path, dst: Path, destination_format: str) -> None:
    with Image.open(src) as image:
        rgba: Image.Image | None = None
        if destination_format == "JPEG":
            if image.mode in {"RGBA", "LA"} or "transparency" in image.info:
                rgba = image.convert("RGBA")
                background = Image.new("RGB", rgba.size, "white")
                background.paste(rgba, mask=rgba.getchannel("A"))
                image_to_save = background
            else:
                image_to_save = image.convert("RGB")
        elif destination_format == "BMP":
            image_to_save = image.convert("RGB") if image.mode not in {"RGB", "L"} else image
        else:
            image_to_save = image
        try:
            image_to_save.save(dst, format=destination_format)
        finally:
            if image_to_save is not image:
                image_to_save.close()
            if rgba is not None:
                rgba.close()


def _make_converter(destination_format: str) -> ConversionFunction:
    def convert_image(src: Path, dst: Path) -> None:
        _convert_image(src, dst, destination_format)

    return convert_image


for _source in sorted(_IMAGE_INPUTS):
    for _destination, _pillow_format in _PIL_FORMATS.items():
        if _source != _destination:
            register(_source, _destination)(_make_converter(_pillow_format))
