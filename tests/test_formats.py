from fileconv.core.formats import category_for, normalize_extension


def test_normalize_extension_aliases() -> None:
    assert normalize_extension(".JPEG") == "jpg"
    assert normalize_extension(" TIF ") == "tiff"
    assert normalize_extension(".HTM") == "html"


def test_category_for_known_and_unknown_extensions() -> None:
    assert category_for("png") == "image"
    assert category_for("docx") == "doc"
    assert category_for(".PDF") == "pdf"
    assert category_for("md") == "text"
    assert category_for("unknown") is None
