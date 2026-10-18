from pathlib import Path

import pikepdf
import pytest
from typer.testing import CliRunner

import fileconv.converters  # noqa: F401
from fileconv.cli.main import app
from fileconv.core.errors import ConversionError
from fileconv.core.runner import merge_pdfs

FIXTURES = Path(__file__).parent / "fixtures"


def test_merge_pdfs_preserves_page_order_and_avoids_overwrite(tmp_path) -> None:
    sources = [FIXTURES / "sample.pdf", FIXTURES / "sample.pdf"]

    output = merge_pdfs(sources, tmp_path)
    second_output = merge_pdfs(sources, tmp_path)

    assert output == tmp_path / "merged.pdf"
    assert second_output == tmp_path / "merged (1).pdf"
    with pikepdf.open(output) as document:
        assert len(document.pages) == 4


def test_merge_pdfs_requires_two_existing_pdf_files(tmp_path) -> None:
    with pytest.raises(ConversionError, match="At least two PDF"):
        merge_pdfs([FIXTURES / "sample.pdf"], tmp_path)
    with pytest.raises(ConversionError, match="not a PDF"):
        merge_pdfs([FIXTURES / "sample.pdf", FIXTURES / "sample.md"], tmp_path)


def test_cli_merges_pdf_files(tmp_path) -> None:
    result = CliRunner().invoke(
        app,
        [
            "merge",
            str(FIXTURES / "sample.pdf"),
            str(FIXTURES / "sample.pdf"),
            "--out-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert result.output.strip() == str(tmp_path / "merged.pdf")
    with pikepdf.open(tmp_path / "merged.pdf") as document:
        assert len(document.pages) == 4
