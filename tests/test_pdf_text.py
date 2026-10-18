from pathlib import Path

import fileconv.converters  # noqa: F401
from fileconv.core.runner import convert

FIXTURES = Path(__file__).parent / "fixtures"


def test_pdf_to_text_extracts_all_pages(tmp_path) -> None:
    output = convert(FIXTURES / "sample.pdf", "txt", tmp_path)
    text = output.read_text(encoding="utf-8")

    assert "First fixture page" in text
    assert "Second fixture page" in text


def test_pdf_to_markdown_extracts_page_content(tmp_path) -> None:
    output = convert(FIXTURES / "sample.pdf", "md", tmp_path)
    markdown = output.read_text(encoding="utf-8")

    assert "First fixture page" in markdown
    assert "Second fixture page" in markdown
