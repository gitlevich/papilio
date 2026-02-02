"""Built-in pipeline stages."""

import logging
from collections.abc import Iterator
from pathlib import Path
from typing import TypeVar

from PIL import Image

from item import ImageItem
from stage import MergeStage, Stage

logger = logging.getLogger(__name__)

T = TypeVar("T", ImageItem, list[ImageItem])

# Supported image extensions
IMAGE_EXTENSIONS = frozenset({
    ".jpg", ".jpeg", ".png", ".tiff", ".tif", ".heic", ".heif"
})


class InputStage(Stage):
    """Recursively walk directory, yielding ImageItems for recognized formats."""

    def __init__(self, root: Path):
        self.root = root

    def scan(self) -> Iterator[ImageItem]:
        """Generate ImageItems from directory tree."""
        for path in sorted(self.root.rglob("*")):
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
                yield ImageItem(path=path)

    def process(self, stream: Iterator[ImageItem]) -> Iterator[ImageItem]:
        """InputStage ignores incoming stream, generates from filesystem."""
        # Consume any incoming stream (typically empty)
        for _ in stream:
            pass
        # Generate from filesystem
        for item in self.scan():
            item.sigils.append(self.name)
            yield item


class OutputStage(Stage):
    """Resize to 4K if larger, write to output directory preserving structure."""

    MAX_LONG_EDGE = 3840

    def __init__(self, output_root: Path, input_root: Path):
        self.output_root = output_root
        self.input_root = input_root

    def map(self, item: ImageItem) -> ImageItem:
        """Resize if needed and write to output."""
        try:
            img = item.image
            width, height = img.size
            long_edge = max(width, height)

            if long_edge > self.MAX_LONG_EDGE:
                scale = self.MAX_LONG_EDGE / long_edge
                new_size = (int(width * scale), int(height * scale))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                item.image = img
                item.metadata["resized"] = True
                item.metadata["original_size"] = (width, height)
            else:
                item.metadata["resized"] = False

            # Preserve directory structure
            relative = item.path.relative_to(self.input_root)
            output_path = self.output_root / relative
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save with appropriate format
            img.save(output_path, quality=95)
            item.metadata["output_path"] = output_path

            logger.info("Wrote %s", output_path)

        except Exception as e:
            logger.warning("Failed to process %s: %s", item.path, e)

        return item


class LandscapeOnly(Stage):
    """Filter to images where width > height."""

    def filter(self, item: ImageItem) -> bool:
        try:
            width, height = item.image.size
            return width > height
        except Exception as e:
            logger.warning("Failed to check orientation for %s: %s", item.path, e)
            return False


class BatchMerge(MergeStage):
    """Window items into groups of N, emitting list[ImageItem]."""

    def __init__(self, n: int = 10):
        self.n = n

    def merge(self, streams: list[Iterator[T]]) -> Iterator[list[ImageItem]]:
        """Collect items from all streams into batches of size n."""
        batch: list[ImageItem] = []

        for stream in streams:
            for item in stream:
                # Handle both single items and lists
                items = item if isinstance(item, list) else [item]
                for single in items:
                    batch.append(single)
                    if len(batch) >= self.n:
                        for i in batch:
                            i.sigils.append(self.name)
                        yield batch
                        batch = []

        # Emit remaining items
        if batch:
            for i in batch:
                i.sigils.append(self.name)
            yield batch


class Concat(MergeStage):
    """Concatenate multiple streams sequentially."""

    def merge(self, streams: list[Iterator[T]]) -> Iterator[T]:
        for stream in streams:
            yield from stream


class Interleave(MergeStage):
    """Interleave items from multiple streams round-robin."""

    def merge(self, streams: list[Iterator[T]]) -> Iterator[T]:
        active = list(streams)
        while active:
            next_active = []
            for stream in active:
                try:
                    yield next(stream)
                    next_active.append(stream)
                except StopIteration:
                    pass
            active = next_active
