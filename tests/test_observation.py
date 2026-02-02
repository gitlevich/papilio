"""Tests for Observation."""

import tempfile
from pathlib import Path

import pytest
from PIL import Image

from observation import Observation


@pytest.fixture
def sample_image_path():
    """Create a temporary test image."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img = Image.new("RGB", (100, 50), color="red")
        img.save(f, format="PNG")
        yield Path(f.name)


def test_observation_creation(sample_image_path):
    obs = Observation(path=sample_image_path)
    assert obs.path == sample_image_path
    assert obs.metadata == {}
    assert obs.sigils == []


def test_lazy_image_loading(sample_image_path):
    obs = Observation(path=sample_image_path)
    assert obs._image is None

    img = obs.image
    assert img is not None
    assert img.size == (100, 50)
    assert obs._image is not None


def test_image_setter(sample_image_path):
    obs = Observation(path=sample_image_path)
    new_img = Image.new("RGB", (200, 100), color="blue")
    obs.image = new_img

    assert obs.image.size == (200, 100)


def test_unload(sample_image_path):
    obs = Observation(path=sample_image_path)
    _ = obs.image  # Force load
    assert obs._image is not None

    obs.unload()
    assert obs._image is None
