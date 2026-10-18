import shutil
from pathlib import Path

import pymupdf
import pytest

import fileconv.converters  # noqa: F401
from fileconv.core.runner import convert

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.skipif(shutil.which("soffice") is None, reason="LibreOffice is not installed")
def test_docx_to_pdf_with_libreoffice(tmp_path) -> None:
    output = convert(FIXTURES / "sample.docx", "pdf", tmp_path)

    assert output == tmp_path / "sample.pdf"
    with pymupdf.open(output) as document:
        assert len(document) >= 1
        assert "Fileconv fixture document" in document[0].get_text()
