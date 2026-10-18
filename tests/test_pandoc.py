import shutil
from pathlib import Path

import pytest

import fileconv.converters  # noqa: F401
from fileconv.core.runner import convert

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="Pandoc is not installed")
@pytest.mark.parametrize(
    ("source_name", "destination"),
    [
        ("sample.docx", "md"),
        ("sample.docx", "html"),
        ("sample.docx", "txt"),
        ("sample.md", "docx"),
        ("sample.md", "html"),
    ],
)
def test_pandoc_document_conversions(
    tmp_path,
    source_name: str,
    destination: str,
) -> None:
    output = convert(FIXTURES / source_name, destination, tmp_path)

    assert output.is_file()
    assert output.stat().st_size > 0


@pytest.mark.skipif(
    shutil.which("pandoc") is None
    or not any(
        shutil.which(engine)
        for engine in (
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
    ),
    reason="Pandoc or a supported PDF engine is not installed",
)
def test_markdown_to_pdf(tmp_path) -> None:
    output = convert(FIXTURES / "sample.md", "pdf", tmp_path)

    assert output.is_file()
    assert output.read_bytes().startswith(b"%PDF")
