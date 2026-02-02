"""Tests for built-in stages."""

import tempfile
from pathlib import Path

import pytest
from PIL import Image

from observation import Observation
from stages import BatchMerge, Concat, InputStage, LandscapeOnly, OutputStage


@pytest.fixture
def temp_dir():
    """Create temporary directory with test images."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)

        landscape = Image.new("RGB", (200, 100), color="green")
        landscape.save(root / "landscape.jpg")

        portrait = Image.new("RGB", (100, 200), color="blue")
        portrait.save(root / "portrait.png")

        sub = root / "subdir"
        sub.mkdir()
        square = Image.new("RGB", (100, 100), color="red")
        square.save(sub / "square.tiff")

        yield root


class TestInputStage:
    def test_scan_finds_images(self, temp_dir):
        stage = InputStage(temp_dir)
        observations = list(stage.scan())

        assert len(observations) == 3
        extensions = {obs.path.suffix.lower() for obs in observations}
        assert extensions == {".jpg", ".png", ".tiff"}

    def test_scan_ignores_non_images(self, temp_dir):
        (temp_dir / "readme.txt").write_text("test")

        stage = InputStage(temp_dir)
        observations = list(stage.scan())

        assert len(observations) == 3

    def test_process_adds_sigil(self, temp_dir):
        stage = InputStage(temp_dir)
        observations = list(stage.process(iter([])))

        assert all("InputStage" in obs.sigils for obs in observations)


class TestLandscapeOnly:
    def test_accepts_landscape(self, temp_dir):
        stage = LandscapeOnly()
        obs = Observation(path=temp_dir / "landscape.jpg")

        assert stage.filter(obs) is True

    def test_rejects_portrait(self, temp_dir):
        stage = LandscapeOnly()
        obs = Observation(path=temp_dir / "portrait.png")

        assert stage.filter(obs) is False

    def test_rejects_square(self, temp_dir):
        stage = LandscapeOnly()
        obs = Observation(path=temp_dir / "subdir" / "square.tiff")

        assert stage.filter(obs) is False


class TestBatchMerge:
    def test_batches_observations(self):
        observations = [Observation(path=Path(f"/{i}.jpg")) for i in range(25)]
        merge = BatchMerge(n=10)

        batches = list(merge.merge([iter(observations)]))

        assert len(batches) == 3
        assert len(batches[0]) == 10
        assert len(batches[1]) == 10
        assert len(batches[2]) == 5

    def test_adds_sigil_to_batch_observations(self):
        observations = [Observation(path=Path(f"/{i}.jpg")) for i in range(3)]
        merge = BatchMerge(n=2)

        batches = list(merge.merge([iter(observations)]))

        assert all("BatchMerge" in obs.sigils for batch in batches for obs in batch)


class TestConcat:
    def test_concatenates_streams(self):
        stream1 = iter([Observation(path=Path("/a.jpg"))])
        stream2 = iter([Observation(path=Path("/b.jpg")), Observation(path=Path("/c.jpg"))])

        merge = Concat()
        results = list(merge.merge([stream1, stream2]))

        assert len(results) == 3
        assert [r.path.name for r in results] == ["a.jpg", "b.jpg", "c.jpg"]


class TestOutputStage:
    def test_preserves_small_images(self, temp_dir):
        output_dir = temp_dir / "output"
        stage = OutputStage(output_dir, temp_dir)
        obs = Observation(path=temp_dir / "landscape.jpg")

        result = stage.map(obs)

        assert result.metadata.get("resized") is False
        assert (output_dir / "landscape.jpg").exists()

    def test_resizes_large_images(self, temp_dir):
        large = Image.new("RGB", (5000, 3000), color="purple")
        large.save(temp_dir / "large.jpg")

        output_dir = temp_dir / "output"
        stage = OutputStage(output_dir, temp_dir)
        obs = Observation(path=temp_dir / "large.jpg")

        result = stage.map(obs)

        assert result.metadata.get("resized") is True
        assert result.metadata["original_size"] == (5000, 3000)

        output_img = Image.open(output_dir / "large.jpg")
        assert max(output_img.size) == 3840

    def test_preserves_directory_structure(self, temp_dir):
        output_dir = temp_dir / "output"
        stage = OutputStage(output_dir, temp_dir)
        obs = Observation(path=temp_dir / "subdir" / "square.tiff")

        stage.map(obs)

        assert (output_dir / "subdir" / "square.tiff").exists()
