from pathlib import Path

import pymupdf
from PIL import Image

import fileconv.converters  # noqa: F401
from fileconv.core.runner import convert

FIXTURES = Path(__file__).parent / "fixtures"


def test_alpha_png_to_pdf_flattens_on_white(tmp_path) -> None:
    source = FIXTURES / "sample.png"

    output = convert(source, "pdf", tmp_path)

    with pymupdf.open(output) as document:
        assert len(document) == 1
        pixel = (
            document[0]
            .get_pixmap(
                matrix=pymupdf.Matrix(1, 1),
                clip=pymupdf.Rect(0, 0, 1, 1),
                alpha=False,
            )
            .samples[:3]
        )
        assert pixel[0] > pixel[1] > 100


def test_pdf_to_images_returns_pages_directory(tmp_path) -> None:
    output = convert(FIXTURES / "sample.pdf", "png", tmp_path)

    assert output == tmp_path / "sample_pages"
    assert sorted(path.name for path in output.iterdir()) == [
        "page-001.png",
        "page-002.png",
    ]
    with Image.open(output / "page-001.png") as page:
        assert round(page.info.get("dpi", (0, 0))[0]) == 150


def test_pdf_to_jpg_uses_unique_pages_folder(tmp_path) -> None:
    (tmp_path / "sample_pages").mkdir()

    output = convert(FIXTURES / "sample.pdf", "jpg", tmp_path)

    assert output == tmp_path / "sample_pages (1)"
    assert sorted(path.name for path in output.iterdir()) == [
        "page-001.jpg",
        "page-002.jpg",
    ]
