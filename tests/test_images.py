import pytest
from PIL import Image

import fileconv.converters  # noqa: F401
from fileconv.core.runner import convert


def test_image_conversion_and_non_overwrite(tmp_path) -> None:
    source = tmp_path / "source image.png"
    Image.new("RGBA", (8, 6), (20, 80, 140, 255)).save(source)

    output = convert(source, "jpg")
    second_output = convert(source, "jpeg")

    assert output.name == "source image.jpg"
    assert second_output.name == "source image (1).jpg"
    with Image.open(output) as converted:
        assert converted.format == "JPEG"
        assert converted.size == (8, 6)


def test_png_preserves_transparency(tmp_path) -> None:
    source = tmp_path / "transparent.png"
    Image.new("RGBA", (4, 4), (0, 0, 0, 0)).save(source)

    output = convert(source, "webp")

    with Image.open(output) as converted:
        assert converted.mode == "RGBA"
        assert converted.getpixel((0, 0))[3] == 0


def test_heic_conversion_when_optional_plugin_is_installed(tmp_path) -> None:
    pytest.importorskip("pillow_heif")
    source = tmp_path / "source.png"
    Image.new("RGB", (3, 3), "green").save(source)

    heic_output = convert(source, "heic")
    png_output = convert(heic_output, "png")

    assert heic_output.suffix == ".heic"
    with Image.open(png_output) as converted:
        assert converted.size == (3, 3)
