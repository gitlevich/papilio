"""Stage abstractions - the pipeline's building blocks."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import TypeVar

from item import ImageItem

T = TypeVar("T", ImageItem, list[ImageItem])


class Stage(ABC):
    """A sigil - names a concern, embodies filter and map.

    Subclasses implement filter() and map() to define behavior.
    The pipeline handles stream mechanics.
    """

    @property
    def name(self) -> str:
        """Stage name used in sigils list."""
        return self.__class__.__name__

    def filter(self, item: ImageItem) -> bool:
        """Does this item belong to this stage's world? Default: accept all."""
        return True

    def map(self, item: ImageItem) -> ImageItem:
        """Transform/annotate the item. Default: passthrough."""
        return item

    def process(self, stream: Iterator[ImageItem]) -> Iterator[ImageItem]:
        """Apply filter then map to stream, tracking sigils."""
        for item in stream:
            if self.filter(item):
                result = self.map(item)
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
