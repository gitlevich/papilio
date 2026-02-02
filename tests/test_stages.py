"""Tests for built-in stages."""

import tempfile
from pathlib import Path

import pytest
from PIL import Image

from item import ImageItem
from stages import BatchMerge, Concat, InputStage, LandscapeOnly, OutputStage


@pytest.fixture
def temp_dir():
    """Create temporary directory with test images."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)

        # Create landscape image
        landscape = Image.new("RGB", (200, 100), color="green")
        landscape.save(root / "landscape.jpg")

        # Create portrait image
        portrait = Image.new("RGB", (100, 200), color="blue")
        portrait.save(root / "portrait.png")

        # Create subdirectory with image
        sub = root / "subdir"
        sub.mkdir()
        square = Image.new("RGB", (100, 100), color="red")
        square.save(sub / "square.tiff")

        yield root


class TestInputStage:
    def test_scan_finds_images(self, temp_dir):
        stage = InputStage(temp_dir)
        items = list(stage.scan())

        assert len(items) == 3
        extensions = {item.path.suffix.lower() for item in items}
        assert extensions == {".jpg", ".png", ".tiff"}

    def test_scan_ignores_non_images(self, temp_dir):
        (temp_dir / "readme.txt").write_text("test")

        stage = InputStage(temp_dir)
        items = list(stage.scan())

        assert len(items) == 3  # Still only images

    def test_process_adds_sigil(self, temp_dir):
        stage = InputStage(temp_dir)
        items = list(stage.process(iter([])))

        assert all("InputStage" in item.sigils for item in items)


class TestLandscapeOnly:
    def test_accepts_landscape(self, temp_dir):
        stage = LandscapeOnly()
        item = ImageItem(path=temp_dir / "landscape.jpg")

        assert stage.filter(item) is True

    def test_rejects_portrait(self, temp_dir):
        stage = LandscapeOnly()
        item = ImageItem(path=temp_dir / "portrait.png")

        assert stage.filter(item) is False

    def test_rejects_square(self, temp_dir):
        stage = LandscapeOnly()
        item = ImageItem(path=temp_dir / "subdir" / "square.tiff")

        assert stage.filter(item) is False


class TestBatchMerge:
    def test_batches_items(self):
        items = [ImageItem(path=Path(f"/{i}.jpg")) for i in range(25)]
        merge = BatchMerge(n=10)

        batches = list(merge.merge([iter(items)]))

        assert len(batches) == 3
        assert len(batches[0]) == 10
        assert len(batches[1]) == 10
        assert len(batches[2]) == 5

    def test_adds_sigil_to_batch_items(self):
        items = [ImageItem(path=Path(f"/{i}.jpg")) for i in range(3)]
        merge = BatchMerge(n=2)

        batches = list(merge.merge([iter(items)]))

        assert all("BatchMerge" in item.sigils for batch in batches for item in batch)


class TestConcat:
    def test_concatenates_streams(self):
        stream1 = iter([ImageItem(path=Path("/a.jpg"))])
        stream2 = iter([ImageItem(path=Path("/b.jpg")), ImageItem(path=Path("/c.jpg"))])

        merge = Concat()
        results = list(merge.merge([stream1, stream2]))

        assert len(results) == 3
        assert [r.path.name for r in results] == ["a.jpg", "b.jpg", "c.jpg"]


class TestOutputStage:
    def test_preserves_small_images(self, temp_dir):
        output_dir = temp_dir / "output"
        stage = OutputStage(output_dir, temp_dir)
        item = ImageItem(path=temp_dir / "landscape.jpg")

        result = stage.map(item)

        assert result.metadata.get("resized") is False
        assert (output_dir / "landscape.jpg").exists()

    def test_resizes_large_images(self, temp_dir):
        # Create oversized image
        large = Image.new("RGB", (5000, 3000), color="purple")
        large.save(temp_dir / "large.jpg")

        output_dir = temp_dir / "output"
        stage = OutputStage(output_dir, temp_dir)
        item = ImageItem(path=temp_dir / "large.jpg")

        result = stage.map(item)

        assert result.metadata.get("resized") is True
        assert result.metadata["original_size"] == (5000, 3000)

        # Verify output dimensions
        output_img = Image.open(output_dir / "large.jpg")
        assert max(output_img.size) == 3840

    def test_preserves_directory_structure(self, temp_dir):
        output_dir = temp_dir / "output"
        stage = OutputStage(output_dir, temp_dir)
        item = ImageItem(path=temp_dir / "subdir" / "square.tiff")

        stage.map(item)

        assert (output_dir / "subdir" / "square.tiff").exists()
