from datetime import UTC, datetime
from pathlib import Path

from PIL import Image

from frameflow.metadata import MetadataExtractor
from frameflow.providers import FileCandidate


def test_metadata_extractor(tmp_path: Path) -> None:
    image_path = tmp_path / "photo.jpg"

    Image.new("RGB", (640, 480)).save(image_path)

    stat = image_path.stat()

    candidate = FileCandidate(
        library_id="family",
        path=image_path,
        filename=image_path.name,
        size=stat.st_size,
        modified_at=datetime.fromtimestamp(stat.st_mtime, UTC),
    )

    photo = MetadataExtractor().extract(candidate)

    assert photo.library_id == "family"
    assert photo.source_path == image_path
    assert photo.width == 640
    assert photo.height == 480
    assert photo.image_format == "JPEG"
    assert photo.file_size == stat.st_size
    assert photo.content_hash is not None
    assert len(photo.content_hash) == 64
