from datetime import datetime
from pathlib import Path

from frameflow.providers import LocalFileProvider


def test_local_file_provider_discovers_supported_images(tmp_path: Path) -> None:
    image_path = tmp_path / "family.jpg"
    image_path.write_bytes(b"fake image")

    provider = LocalFileProvider(library_id="family", root_path=tmp_path)

    candidates = list(provider.discover())

    assert len(candidates) == 1
    assert candidates[0].library_id == "family"
    assert candidates[0].path == image_path
    assert candidates[0].filename == "family.jpg"
    assert candidates[0].size == len(b"fake image")
    assert isinstance(candidates[0].modified_at, datetime)


def test_local_file_provider_discovers_images_recursively(tmp_path: Path) -> None:
    nested_dir = tmp_path / "nested"
    nested_dir.mkdir()
    image_path = nested_dir / "vacation.png"
    image_path.write_bytes(b"fake image")

    provider = LocalFileProvider(library_id="family", root_path=tmp_path)

    candidates = list(provider.discover())

    assert [candidate.path for candidate in candidates] == [image_path]


def test_local_file_provider_ignores_unsupported_files(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("not an image")

    provider = LocalFileProvider(library_id="family", root_path=tmp_path)

    assert list(provider.discover()) == []


def test_local_file_provider_ignores_hidden_files_and_directories(
    tmp_path: Path,
) -> None:
    hidden_file = tmp_path / ".hidden.jpg"
    hidden_file.write_bytes(b"fake image")

    hidden_dir = tmp_path / ".hidden"
    hidden_dir.mkdir()
    hidden_nested_file = hidden_dir / "nested.jpg"
    hidden_nested_file.write_bytes(b"fake image")

    visible_image = tmp_path / "visible.webp"
    visible_image.write_bytes(b"fake image")

    provider = LocalFileProvider(library_id="family", root_path=tmp_path)

    candidates = list(provider.discover())

    assert [candidate.path for candidate in candidates] == [visible_image]


def test_local_file_provider_handles_missing_root_path(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing"

    provider = LocalFileProvider(library_id="family", root_path=missing_path)

    assert list(provider.discover()) == []


def test_local_file_provider_supports_case_insensitive_extensions(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "family.JPG"
    image_path.write_bytes(b"fake image")

    provider = LocalFileProvider(library_id="family", root_path=tmp_path)

    candidates = list(provider.discover())

    assert len(candidates) == 1
    assert candidates[0].path == image_path
