"""Tests for Stage abstractions."""

from pathlib import Path

from item import ImageItem
from stage import Stage


class PassthroughStage(Stage):
    """Test stage that accepts all items unchanged."""
    pass


class EvenOnlyStage(Stage):
    """Test stage that only accepts items with even metadata value."""

    def filter(self, item: ImageItem) -> bool:
        return item.metadata.get("value", 0) % 2 == 0


class DoubleValueStage(Stage):
    """Test stage that doubles the metadata value."""

    def map(self, item: ImageItem) -> ImageItem:
        item.metadata["value"] = item.metadata.get("value", 0) * 2
        return item


def test_stage_default_name():
    stage = PassthroughStage()
    assert stage.name == "PassthroughStage"


def test_stage_default_filter_accepts_all():
    stage = PassthroughStage()
    item = ImageItem(path=Path("/fake/path.jpg"))
    assert stage.filter(item) is True


def test_stage_default_map_passthrough():
    stage = PassthroughStage()
    item = ImageItem(path=Path("/fake/path.jpg"))
    result = stage.map(item)
    assert result is item


def test_stage_process_adds_sigil():
    stage = PassthroughStage()
    items = [ImageItem(path=Path("/fake/1.jpg"))]

    results = list(stage.process(iter(items)))

    assert len(results) == 1
    assert "PassthroughStage" in results[0].sigils


def test_filter_stage():
    stage = EvenOnlyStage()
    items = [
        ImageItem(path=Path("/1.jpg"), metadata={"value": 1}),
        ImageItem(path=Path("/2.jpg"), metadata={"value": 2}),
        ImageItem(path=Path("/3.jpg"), metadata={"value": 3}),
        ImageItem(path=Path("/4.jpg"), metadata={"value": 4}),
    ]

    results = list(stage.process(iter(items)))

    assert len(results) == 2
    assert all(r.metadata["value"] % 2 == 0 for r in results)


def test_map_stage():
    stage = DoubleValueStage()
    item = ImageItem(path=Path("/1.jpg"), metadata={"value": 5})

    results = list(stage.process(iter([item])))

    assert results[0].metadata["value"] == 10
