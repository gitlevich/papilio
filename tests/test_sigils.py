"""Tests for built-in sigils."""

import tempfile
from pathlib import Path

import pytest
from PIL import Image

from observation import Observation
from sigils import Batch, Concat, Input, LandscapeOnly, Output, load_image


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


class TestInput:
    def test_scan_finds_images(self, temp_dir):
        sigil = Input(temp_dir)
        observations = list(sigil.scan())

        assert len(observations) == 3
        extensions = {obs.path.suffix.lower() for obs in observations}
        assert extensions == {".jpg", ".png", ".tiff"}

    def test_scan_ignores_non_images(self, temp_dir):
        (temp_dir / "readme.txt").write_text("test")

        sigil = Input(temp_dir)
        observations = list(sigil.scan())

        assert len(observations) == 3

    def test_process_adds_sigil_mark(self, temp_dir):
        sigil = Input(temp_dir)
        observations = list(sigil.process(iter([])))

        assert all("Input" in obs.sigils for obs in observations)


class TestLandscapeOnly:
    def test_passes_landscape(self, temp_dir):
        sigil = LandscapeOnly()
        obs = Observation(path=temp_dir / "landscape.jpg", loader=load_image)

        assert sigil.filter(obs) is True

    def test_rejects_portrait(self, temp_dir):
        sigil = LandscapeOnly()
        obs = Observation(path=temp_dir / "portrait.png", loader=load_image)

        assert sigil.filter(obs) is False

    def test_rejects_square(self, temp_dir):
        sigil = LandscapeOnly()
        obs = Observation(path=temp_dir / "subdir" / "square.tiff", loader=load_image)

        assert sigil.filter(obs) is False


class TestBatch:
    def test_batches_observations(self, temp_dir):
        observations = [
            Observation(path=Path(f"/{i}.jpg"), loader=load_image)
            for i in range(25)
        ]
        sigil = Batch(n=10)

        batches = list(sigil.merge([iter(observations)]))

        assert len(batches) == 3
        assert len(batches[0]) == 10
        assert len(batches[1]) == 10
        assert len(batches[2]) == 5

    def test_adds_sigil_mark_to_batch(self, temp_dir):
        observations = [
            Observation(path=Path(f"/{i}.jpg"), loader=load_image)
            for i in range(3)
        ]
        sigil = Batch(n=2)

        batches = list(sigil.merge([iter(observations)]))

        assert all("Batch" in obs.sigils for batch in batches for obs in batch)


class TestConcat:
    def test_concatenates_streams(self):
        stream1 = iter([Observation(path=Path("/a.jpg"), loader=load_image)])
        stream2 = iter([
            Observation(path=Path("/b.jpg"), loader=load_image),
            Observation(path=Path("/c.jpg"), loader=load_image),
        ])

        sigil = Concat()
        results = list(sigil.merge([stream1, stream2]))

        assert len(results) == 3
        assert [r.path.name for r in results] == ["a.jpg", "b.jpg", "c.jpg"]


class TestOutput:
    def test_preserves_small_images(self, temp_dir):
        output_dir = temp_dir / "output"
        sigil = Output(output_dir, temp_dir)
        obs = Observation(path=temp_dir / "landscape.jpg", loader=load_image)

        result = sigil.map(obs)

        assert result.metadata.get("resized") is False
        assert (output_dir / "landscape.jpg").exists()

    def test_resizes_large_images(self, temp_dir):
        large = Image.new("RGB", (5000, 3000), color="purple")
        large.save(temp_dir / "large.jpg")

        output_dir = temp_dir / "output"
        sigil = Output(output_dir, temp_dir)
        obs = Observation(path=temp_dir / "large.jpg", loader=load_image)

        result = sigil.map(obs)

        assert result.metadata.get("resized") is True
        assert result.metadata["original_size"] == (5000, 3000)

        output_img = Image.open(output_dir / "large.jpg")
        assert max(output_img.size) == 3840

    def test_preserves_directory_structure(self, temp_dir):
        output_dir = temp_dir / "output"
        sigil = Output(output_dir, temp_dir)
        obs = Observation(path=temp_dir / "subdir" / "square.tiff", loader=load_image)

        sigil.map(obs)

        assert (output_dir / "subdir" / "square.tiff").exists()
