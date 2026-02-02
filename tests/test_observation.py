"""Tests for Observation."""

import tempfile
from pathlib import Path

import pytest
from PIL import Image

from observation import Observation


def load_image(path: Path) -> Image.Image:
    return Image.open(path)


@pytest.fixture
def sample_image_path():
    """Create a temporary test image."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img = Image.new("RGB", (100, 50), color="red")
        img.save(f, format="PNG")
        yield Path(f.name)


def test_observation_creation(sample_image_path):
    obs = Observation(path=sample_image_path, loader=load_image)
    assert obs.path == sample_image_path
    assert obs.metadata == {}
    assert obs.sigils == []


def test_lazy_content_loading(sample_image_path):
    obs = Observation(path=sample_image_path, loader=load_image)
    assert obs._content is None

    content = obs.content
    assert content is not None
    assert content.size == (100, 50)
    assert obs._content is not None


def test_content_setter(sample_image_path):
    obs = Observation(path=sample_image_path, loader=load_image)
    new_img = Image.new("RGB", (200, 100), color="blue")
    obs.content = new_img

    assert obs.content.size == (200, 100)


def test_unload(sample_image_path):
    obs = Observation(path=sample_image_path, loader=load_image)
    _ = obs.content  # Force load
    assert obs._content is not None

    obs.unload()
    assert obs._content is None


def test_generic_observation():
    """Test that Observation works with any content type."""
    def load_text(path: Path) -> str:
        return path.read_text()

    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
        f.write("hello world")
        f.flush()
        path = Path(f.name)

    obs: Observation[str] = Observation(path=path, loader=load_text)
    assert obs.content == "hello world"
