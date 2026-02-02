"""Tests for Stage abstractions."""

from pathlib import Path

from observation import Observation
from stage import Stage


class PassthroughStage(Stage):
    """Test stage that accepts all observations unchanged."""
    pass


class EvenOnlyStage(Stage):
    """Test stage that only accepts observations with even metadata value."""

    def filter(self, obs: Observation) -> bool:
        return obs.metadata.get("value", 0) % 2 == 0


class DoubleValueStage(Stage):
    """Test stage that doubles the metadata value."""

    def map(self, obs: Observation) -> Observation:
        obs.metadata["value"] = obs.metadata.get("value", 0) * 2
        return obs


def test_stage_default_name():
    stage = PassthroughStage()
    assert stage.name == "PassthroughStage"


def test_stage_default_filter_accepts_all():
    stage = PassthroughStage()
    obs = Observation(path=Path("/fake/path.jpg"))
    assert stage.filter(obs) is True


def test_stage_default_map_passthrough():
    stage = PassthroughStage()
    obs = Observation(path=Path("/fake/path.jpg"))
    result = stage.map(obs)
    assert result is obs


def test_stage_process_adds_sigil():
    stage = PassthroughStage()
    observations = [Observation(path=Path("/fake/1.jpg"))]

    results = list(stage.process(iter(observations)))

    assert len(results) == 1
    assert "PassthroughStage" in results[0].sigils


def test_filter_stage():
    stage = EvenOnlyStage()
    observations = [
        Observation(path=Path("/1.jpg"), metadata={"value": 1}),
        Observation(path=Path("/2.jpg"), metadata={"value": 2}),
        Observation(path=Path("/3.jpg"), metadata={"value": 3}),
        Observation(path=Path("/4.jpg"), metadata={"value": 4}),
    ]

    results = list(stage.process(iter(observations)))

    assert len(results) == 2
    assert all(r.metadata["value"] % 2 == 0 for r in results)


def test_map_stage():
    stage = DoubleValueStage()
    obs = Observation(path=Path("/1.jpg"), metadata={"value": 5})

    results = list(stage.process(iter([obs])))

    assert results[0].metadata["value"] == 10
