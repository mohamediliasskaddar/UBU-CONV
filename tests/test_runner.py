import pytest

import fileconv.converters  # noqa: F401
from fileconv.core.errors import ConversionError
from fileconv.core.runner import convert


def test_convert_requires_an_input_file(tmp_path) -> None:
    with pytest.raises(ConversionError, match="Input file does not exist"):
        convert(tmp_path / "missing.png", "jpg")


def test_convert_supports_output_directory(tmp_path) -> None:
    from PIL import Image

    source = tmp_path / "source.png"
    output_dir = tmp_path / "converted"
    Image.new("RGB", (2, 2), "blue").save(source)

    output = convert(source, "bmp", output_dir)

    assert output.parent == output_dir
    assert output.name == "source.bmp"
