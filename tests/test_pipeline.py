"""Tests for Pipeline composition."""

from pathlib import Path

from item import ImageItem
from pipeline import Branch, Pipeline
from stage import Stage


class AddTagStage(Stage):
    """Stage that adds a tag to metadata."""

    def __init__(self, tag: str):
        self.tag = tag

    def map(self, item: ImageItem) -> ImageItem:
        tags = item.metadata.setdefault("tags", [])
        tags.append(self.tag)
        return item


class RejectAllStage(Stage):
    """Stage that rejects all items."""

    def filter(self, item: ImageItem) -> bool:
        return False


def test_empty_pipeline():
    pipeline = Pipeline()
    results = list(pipeline.run(iter([])))
    assert results == []


def test_single_stage():
    pipeline = Pipeline([AddTagStage("test")])
    items = [ImageItem(path=Path("/1.jpg"))]

    results = list(pipeline.run(iter(items)))

    assert len(results) == 1
    assert "test" in results[0].metadata["tags"]


def test_chained_stages():
    pipeline = Pipeline()
    pipeline.add(AddTagStage("first"))
    pipeline.add(AddTagStage("second"))

    items = [ImageItem(path=Path("/1.jpg"))]
    results = list(pipeline.run(iter(items)))

    assert results[0].metadata["tags"] == ["first", "second"]


def test_filter_in_chain():
    pipeline = Pipeline()
    pipeline.add(AddTagStage("before"))
    pipeline.add(RejectAllStage())
    pipeline.add(AddTagStage("after"))

    items = [ImageItem(path=Path("/1.jpg"))]
    results = list(pipeline.run(iter(items)))

    assert results == []


def test_pipeline_add_returns_self():
    pipeline = Pipeline()
    result = pipeline.add(AddTagStage("test"))
    assert result is pipeline


def test_fluent_api():
    pipeline = (
        Pipeline()
        .add(AddTagStage("a"))
        .add(AddTagStage("b"))
        .add(AddTagStage("c"))
    )

    items = [ImageItem(path=Path("/1.jpg"))]
    results = list(pipeline.run(iter(items)))

    assert results[0].metadata["tags"] == ["a", "b", "c"]


class TestBranch:
    def test_branch_creates_multiple_streams(self):
        branch1 = Pipeline([AddTagStage("branch1")])
        branch2 = Pipeline([AddTagStage("branch2")])

        branch = Branch([branch1, branch2])
        items = [ImageItem(path=Path("/1.jpg"))]

        streams = branch.process(iter(items))

        assert len(streams) == 2

        results1 = list(streams[0])
        results2 = list(streams[1])

        assert "branch1" in results1[0].metadata["tags"]
        assert "branch2" in results2[0].metadata["tags"]
