import shutil
from pathlib import Path

import pymupdf
import pytest
from PIL import Image
from typer.testing import CliRunner

import fileconv.converters  # noqa: F401
from fileconv.cli.main import app


def test_cli_lists_targets_and_converts_image(tmp_path) -> None:
    source = tmp_path / "photo.jpg"
    Image.new("RGB", (5, 3), "orange").save(source)
    runner = CliRunner()

    targets_result = runner.invoke(app, ["targets", str(source)])
    conversion_result = runner.invoke(app, ["convert", str(source), "png"])

    assert targets_result.exit_code == 0
    assert "png: PNG" in targets_result.output
    assert conversion_result.exit_code == 0
    assert conversion_result.output.strip() == str(tmp_path / "photo.png")
    assert (tmp_path / "photo.png").is_file()


def test_cli_doctor_reports_registered_converters() -> None:
    result = CliRunner().invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "Conversions grouped by source format:" in result.output
    assert "jpg:" in result.output
    assert "png: available" in result.output


def test_cli_doctor_shows_missing_external_tools() -> None:
    result = CliRunner().invoke(app, ["doctor"])

    assert result.exit_code == 0
    if shutil.which("pandoc") is None:
        assert "md [pandoc]: unavailable (missing tool: pandoc)" in result.output


@pytest.mark.skipif(shutil.which("soffice") is None, reason="LibreOffice is not installed")
def test_cli_converts_docx_to_pdf_and_pdf_to_markdown(tmp_path) -> None:
    fixtures = Path(__file__).parent / "fixtures"
    runner = CliRunner()
    office_result = runner.invoke(
        app,
        ["convert", str(fixtures / "sample.docx"), "pdf", "--out-dir", str(tmp_path)],
    )
    markdown_result = runner.invoke(
        app,
        ["convert", str(fixtures / "sample.pdf"), "md", "--out-dir", str(tmp_path)],
    )

    assert office_result.exit_code == 0, office_result.output
    assert markdown_result.exit_code == 0, markdown_result.output
    assert Path(office_result.output.strip()).is_file()
    markdown = Path(markdown_result.output.strip()).read_text(encoding="utf-8")
    assert "First fixture page" in markdown
    assert "Second fixture page" in markdown
    with pymupdf.open(office_result.output.strip()) as document:
        assert "Fileconv fixture document" in document[0].get_text()
