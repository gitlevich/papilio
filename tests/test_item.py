"""Tests for ImageItem."""

import tempfile
from pathlib import Path

import pytest
from PIL import Image

from item import ImageItem


@pytest.fixture
def sample_image_path():
    """Create a temporary test image."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img = Image.new("RGB", (100, 50), color="red")
        img.save(f, format="PNG")
        yield Path(f.name)


def test_item_creation(sample_image_path):
    item = ImageItem(path=sample_image_path)
    assert item.path == sample_image_path
    assert item.metadata == {}
    assert item.sigils == []


def test_lazy_image_loading(sample_image_path):
    item = ImageItem(path=sample_image_path)
    assert item._image is None

    img = item.image
    assert img is not None
    assert img.size == (100, 50)
    assert item._image is not None


def test_image_setter(sample_image_path):
    item = ImageItem(path=sample_image_path)
    new_img = Image.new("RGB", (200, 100), color="blue")
    item.image = new_img

    assert item.image.size == (200, 100)


def test_unload(sample_image_path):
    item = ImageItem(path=sample_image_path)
    _ = item.image  # Force load
    assert item._image is not None

    item.unload()
    assert item._image is None
