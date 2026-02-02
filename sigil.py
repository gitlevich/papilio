"""Sigil - pattern plus preferences."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any, TypeVar

from observation import Observation

# Observation with any content type
Obs = Observation[Any]
T = TypeVar("T", Obs, list[Obs])


class Sigil(ABC):
    """A pattern plus preferences.

    When worn by an observer, transforms them into an agent.
    The agent collapses observations through the sigil's contrasts.
    """

    @property
    def name(self) -> str:
        """Sigil name recorded in observation's sigils list."""
        return self.__class__.__name__

    def filter(self, obs: Obs) -> bool:
        """Apply contrast: does this observation pass? Default: accept all."""
        return True

    def map(self, obs: Obs) -> Obs:
        """Transform the observation. Default: passthrough."""
        return obs

    def process(self, stream: Iterator[Obs]) -> Iterator[Obs]:
        """Apply filter then map, marking observation with this sigil."""
        for obs in stream:
            if self.filter(obs):
                result = self.map(obs)
                result.sigils.append(self.name)
                yield result


class MergeSigil(ABC):
    """Sigil that collapses multiple streams into one.

    Implements merge() instead of filter/map.
    Semantics: batch, concatenate, interleave.
    """

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def merge(self, streams: list[Iterator[T]]) -> Iterator[T]:
        """Collapse multiple streams into one."""
        ...
