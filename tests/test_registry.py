import pytest

from fileconv.core.errors import ConversionError
from fileconv.core.registry import Converter, get, register, targets_for


def test_targets_for_normalizes_extension_and_filters_unavailable_tools(monkeypatch) -> None:
    from fileconv.core import registry

    monkeypatch.setattr(registry, "_CONVERTERS", [])

    @register("JPEG", "png")
    def jpg_to_png(src, dst):
        return None

    @register("jpg", "pdf", tool="missing-tool")
    def jpg_to_pdf(src, dst):
        return None

    monkeypatch.setattr(registry.shutil, "which", lambda _: None)
    assert [converter.dst for converter in targets_for(".JPG")] == ["png"]


def test_get_reports_missing_converter() -> None:
    with pytest.raises(ConversionError, match="No converter is registered"):
        get("unknown", "png")


def test_converter_without_tool_is_available() -> None:
    converter = Converter("jpg", "png", lambda src, dst: None)
    assert converter.available()
