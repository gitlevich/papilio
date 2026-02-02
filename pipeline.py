"""Pipeline - attention flowing through sigils."""

import logging
from collections.abc import Iterator
from typing import Any, TypeVar

from observation import Observation
from sigil import MergeSigil, Sigil

logger = logging.getLogger(__name__)

Obs = Observation[Any]
T = TypeVar("T", Obs, list[Obs])


class Pipeline:
    """Compose sigils into an executable flow.

    Observations flow through sigils sequentially.
    Each sigil collapses (filter) and transforms (map).
    """

    def __init__(self, sigils: list[Sigil | MergeSigil] | None = None):
        self.sigils: list[Sigil | MergeSigil] = sigils or []

    def add(self, sigil: Sigil | MergeSigil) -> "Pipeline":
        """Add a sigil. Returns self for chaining."""
        self.sigils.append(sigil)
        return self

    def run(self, initial: Iterator[Obs] | None = None) -> Iterator[T]:
        """Execute pipeline, yielding observations."""
        stream: Iterator[T] = initial or iter([])

        for sigil in self.sigils:
            if isinstance(sigil, MergeSigil):
                stream = sigil.merge([stream])
            else:
                stream = self._process_sigil(sigil, stream)

        yield from stream

    def _process_sigil(self, sigil: Sigil, stream: Iterator[T]) -> Iterator[T]:
        """Process a sigil, handling both observations and batches."""
        if type(sigil).process is not Sigil.process:
            yield from sigil.process(stream)
            return

        for obs in stream:
            if isinstance(obs, list):
                result = []
                for single in obs:
                    if sigil.filter(single):
                        processed = sigil.map(single)
                        processed.sigils.append(sigil.name)
                        result.append(processed)
                if result:
                    yield result
            else:
                if sigil.filter(obs):
                    processed = sigil.map(obs)
                    processed.sigils.append(sigil.name)
                    yield processed


class Branch:
    """Fan-out: feed one stream to multiple downstream pipelines.

    Each branch receives a copy of observations.
    """

    def __init__(self, branches: list[Pipeline]):
        self.branches = branches

    def process(self, stream: Iterator[Obs]) -> list[Iterator[T]]:
        """Process stream through all branches."""
        observations = list(stream)
        return [branch.run(iter(observations)) for branch in self.branches]
