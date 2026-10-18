from fileconv.core.naming import reserve_unique_path, unique_path


def test_unique_path_adds_number_before_extension(tmp_path) -> None:
    original = tmp_path / "résumé draft.png"
    original.touch()
    (tmp_path / "résumé draft (1).png").touch()

    assert unique_path(original) == tmp_path / "résumé draft (2).png"


def test_reserve_unique_path_claims_available_name(tmp_path) -> None:
    requested = tmp_path / "photo.jpg"
    reserved = reserve_unique_path(requested)

    assert reserved == requested
    assert reserved.is_file()
    assert reserve_unique_path(requested) == tmp_path / "photo (1).jpg"
