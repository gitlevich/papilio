"""Tests for Sigil abstractions."""

from pathlib import Path

from observation import Observation
from sigil import Sigil


def identity_loader(path: Path) -> None:
    return None


def make_obs(path: str, **metadata) -> Observation:
    return Observation(path=Path(path), loader=identity_loader, metadata=metadata)


class PassthroughSigil(Sigil):
    """Test sigil that accepts all observations unchanged."""
    pass


class EvenOnlySigil(Sigil):
    """Test sigil: contrast on even vs odd metadata value."""

    def filter(self, obs: Observation) -> bool:
        return obs.metadata.get("value", 0) % 2 == 0


class DoubleValueSigil(Sigil):
    """Test sigil that doubles the metadata value."""

    def map(self, obs: Observation) -> Observation:
        obs.metadata["value"] = obs.metadata.get("value", 0) * 2
        return obs


def test_sigil_default_name():
    sigil = PassthroughSigil()
    assert sigil.name == "PassthroughSigil"


def test_sigil_default_filter_accepts_all():
    sigil = PassthroughSigil()
    obs = make_obs("/fake/path.jpg")
    assert sigil.filter(obs) is True


def test_sigil_default_map_passthrough():
    sigil = PassthroughSigil()
    obs = make_obs("/fake/path.jpg")
    result = sigil.map(obs)
    assert result is obs


def test_sigil_process_adds_mark():
    sigil = PassthroughSigil()
    observations = [make_obs("/fake/1.jpg")]

    results = list(sigil.process(iter(observations)))

    assert len(results) == 1
    assert "PassthroughSigil" in results[0].sigils


def test_contrast_sigil():
    sigil = EvenOnlySigil()
    observations = [
        make_obs("/1.jpg", value=1),
        make_obs("/2.jpg", value=2),
        make_obs("/3.jpg", value=3),
        make_obs("/4.jpg", value=4),
    ]

    results = list(sigil.process(iter(observations)))

    assert len(results) == 2
    assert all(r.metadata["value"] % 2 == 0 for r in results)


def test_transform_sigil():
    sigil = DoubleValueSigil()
    obs = make_obs("/1.jpg", value=5)

    results = list(sigil.process(iter([obs])))

    assert results[0].metadata["value"] == 10
