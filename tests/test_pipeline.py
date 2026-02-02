"""Tests for Pipeline composition."""

from pathlib import Path

from observation import Observation
from pipeline import Branch, Pipeline
from sigil import Sigil


def identity_loader(path: Path) -> None:
    return None


def make_obs(path: str, **metadata) -> Observation:
    return Observation(path=Path(path), loader=identity_loader, metadata=metadata)


class AddTagSigil(Sigil):
    """Sigil that adds a tag to metadata."""

    def __init__(self, tag: str):
        self.tag = tag

    def map(self, obs: Observation) -> Observation:
        tags = obs.metadata.setdefault("tags", [])
        tags.append(self.tag)
        return obs


class RejectAllSigil(Sigil):
    """Sigil that rejects all observations."""

    def filter(self, obs: Observation) -> bool:
        return False


def test_empty_pipeline():
    pipeline = Pipeline()
    results = list(pipeline.run(iter([])))
    assert results == []


def test_single_sigil():
    pipeline = Pipeline([AddTagSigil("test")])
    observations = [make_obs("/1.jpg")]

    results = list(pipeline.run(iter(observations)))

    assert len(results) == 1
    assert "test" in results[0].metadata["tags"]


def test_chained_sigils():
    pipeline = Pipeline()
    pipeline.add(AddTagSigil("first"))
    pipeline.add(AddTagSigil("second"))

    observations = [make_obs("/1.jpg")]
    results = list(pipeline.run(iter(observations)))

    assert results[0].metadata["tags"] == ["first", "second"]


def test_contrast_in_chain():
    pipeline = Pipeline()
    pipeline.add(AddTagSigil("before"))
    pipeline.add(RejectAllSigil())
    pipeline.add(AddTagSigil("after"))

    observations = [make_obs("/1.jpg")]
    results = list(pipeline.run(iter(observations)))

    assert results == []


def test_pipeline_add_returns_self():
    pipeline = Pipeline()
    result = pipeline.add(AddTagSigil("test"))
    assert result is pipeline


def test_fluent_api():
    pipeline = (
        Pipeline()
        .add(AddTagSigil("a"))
        .add(AddTagSigil("b"))
        .add(AddTagSigil("c"))
    )

    observations = [make_obs("/1.jpg")]
    results = list(pipeline.run(iter(observations)))

    assert results[0].metadata["tags"] == ["a", "b", "c"]


class TestBranch:
    def test_branch_creates_multiple_streams(self):
        branch1 = Pipeline([AddTagSigil("branch1")])
        branch2 = Pipeline([AddTagSigil("branch2")])

        branch = Branch([branch1, branch2])
        observations = [make_obs("/1.jpg")]

        streams = branch.process(iter(observations))

        assert len(streams) == 2

        results1 = list(streams[0])
        results2 = list(streams[1])

        assert "branch1" in results1[0].metadata["tags"]
        assert "branch2" in results2[0].metadata["tags"]
