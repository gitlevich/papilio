"""Observation - what attention focuses on."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")


@dataclass
class Observation(Generic[T]):
    """What attention focuses on.

    Generic over content type T. Content is lazy-loaded on first access.

    Attributes:
        path: Source path
        loader: Loads content from path
        metadata: Accumulated annotations from sigils
        sigils: Marks left by sigils this observation passed through
    """
    path: Path
    loader: Callable[[Path], T]
    metadata: dict[str, Any] = field(default_factory=dict)
    sigils: list[str] = field(default_factory=list)
    _content: T | None = field(default=None, repr=False)

    @property
    def content(self) -> T:
        """Lazy-load content on first access."""
        if self._content is None:
            self._content = self.loader(self.path)
        return self._content

    @content.setter
    def content(self, value: T) -> None:
        self._content = value

    def unload(self) -> None:
        """Release content from memory."""
        self._content = None
