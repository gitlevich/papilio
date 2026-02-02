"""Sigil - pattern plus preferences for entanglement."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import TypeVar

from observation import Observation

T = TypeVar("T", Observation, list[Observation])


class Sigil(ABC):
    """A pattern plus preferences.

    A sigil names a concern and embodies two operations:
    - filter(): apply a contrast - does this observation pass?
    - map(): transform the observation
    """

    @property
    def name(self) -> str:
        """Sigil name recorded in observation's sigils list."""
        return self.__class__.__name__

    def filter(self, obs: Observation) -> bool:
        """Apply contrast: does this observation pass? Default: accept all."""
        return True

    def map(self, obs: Observation) -> Observation:
        """Transform the observation. Default: passthrough."""
        return obs

    def process(self, stream: Iterator[Observation]) -> Iterator[Observation]:
        """Apply filter then map, marking observation with this sigil."""
        for obs in stream:
            if self.filter(obs):
                result = self.map(obs)
                result.sigils.append(self.name)
                yield result


class MergeSigil(ABC):
    """Sigil that combines multiple streams (fan-in).

    Implements merge() instead of filter/map.
    Semantics: interleave, concatenate, window, join.
    """

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def merge(self, streams: list[Iterator[T]]) -> Iterator[T]:
        """Combine multiple streams into one."""
        ...
