"""Observation - what attention focuses on as it flows through the pipeline."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from PIL import Image


@dataclass
class Observation:
    """An image under attention.

    Attributes:
        path: Original source path
        metadata: Accumulated annotations from sigils
        sigils: Marks left by sigils this observation passed through
    """
    path: Path
    metadata: dict[str, Any] = field(default_factory=dict)
    sigils: list[str] = field(default_factory=list)
    _image: Image.Image | None = field(default=None, repr=False)

    @property
    def image(self) -> Image.Image:
        """Lazy-load image data on first access."""
        if self._image is None:
            self._image = Image.open(self.path)
        return self._image

    @image.setter
    def image(self, value: Image.Image) -> None:
        self._image = value

    def unload(self) -> None:
        """Release image data from memory."""
        if self._image is not None:
            self._image.close()
            self._image = None
