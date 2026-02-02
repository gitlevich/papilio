"""Stage abstractions - the pipeline's building blocks."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import TypeVar

from observation import Observation

T = TypeVar("T", Observation, list[Observation])


class Stage(ABC):
    """A sigil - names a concern, embodies filter and map.

    Subclasses implement filter() and map() to define behavior.
    The pipeline handles stream mechanics.
    """

    @property
    def name(self) -> str:
        """Stage name used in sigils list."""
        return self.__class__.__name__

    def filter(self, obs: Observation) -> bool:
        """Apply contrast: does this observation pass? Default: accept all."""
        return True

    def map(self, obs: Observation) -> Observation:
        """Transform the observation. Default: passthrough."""
        return obs

    def process(self, stream: Iterator[Observation]) -> Iterator[Observation]:
        """Apply filter then map to stream, marking with sigil."""
        for obs in stream:
            if self.filter(obs):
                result = self.map(obs)
                result.sigils.append(self.name)
                yield result


class MergeStage(ABC):
    """Fan-in stage that combines multiple input streams.

    Subclasses implement merge() to define combination semantics:
    interleave, concatenate, window, join, etc.
    """

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def merge(self, streams: list[Iterator[T]]) -> Iterator[T]:
        """Combine multiple streams into one."""
        ...
