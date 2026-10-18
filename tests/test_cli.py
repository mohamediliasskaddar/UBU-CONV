from PIL import Image
from typer.testing import CliRunner

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
    assert "jpg -> png: available" in result.output
