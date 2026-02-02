"""Built-in sigils for image observations."""

import logging
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from typing import TypeVar

from PIL import Image
from PIL.ExifTags import IFD

from observation import Observation
from sigil import MergeSigil, Sigil

logger = logging.getLogger(__name__)

# Type alias for image observations
ImageObservation = Observation[Image.Image]

T = TypeVar("T", ImageObservation, list[ImageObservation])

IMAGE_EXTENSIONS = frozenset({
    ".jpg", ".jpeg", ".png", ".tiff", ".tif", ".heic", ".heif"
})


def load_image(path: Path) -> Image.Image:
    """Load image from path."""
    return Image.open(path)


class Input(Sigil):
    """Source: generate observations from directory tree."""

    def __init__(self, root: Path):
        self.root = root

    def scan(self) -> Iterator[ImageObservation]:
        """Walk directory, yield observations for recognized images."""
        for path in sorted(self.root.rglob("*")):
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
                yield Observation(path=path, loader=load_image)

    def process(self, stream: Iterator[ImageObservation]) -> Iterator[ImageObservation]:
        """Ignore incoming stream, generate from filesystem."""
        for _ in stream:
            pass
        for obs in self.scan():
            obs.sigils.append(self.name)
            yield obs


class Output(Sigil):
    """Sink: resize to 4K if larger, write preserving structure."""

    MAX_LONG_EDGE = 3840

    def __init__(self, output_root: Path, input_root: Path):
        self.output_root = output_root
        self.input_root = input_root

    def map(self, obs: ImageObservation) -> ImageObservation:
        """Resize if needed and write to output."""
        try:
            img = obs.content
            width, height = img.size
            long_edge = max(width, height)

            if long_edge > self.MAX_LONG_EDGE:
                scale = self.MAX_LONG_EDGE / long_edge
                new_size = (int(width * scale), int(height * scale))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                obs.content = img
                obs.metadata["resized"] = True
                obs.metadata["original_size"] = (width, height)
            else:
                obs.metadata["resized"] = False

            relative = obs.path.relative_to(self.input_root)
            output_path = self.output_root / relative
            output_path.parent.mkdir(parents=True, exist_ok=True)

            img.save(output_path, quality=95)
            obs.metadata["output_path"] = output_path

            logger.info("Wrote %s", output_path)

        except Exception as e:
            logger.warning("Failed to process %s: %s", obs.path, e)

        return obs


class LandscapeOnly(Sigil):
    """Contrast: landscape vs portrait. Passes width > height."""

    def filter(self, obs: ImageObservation) -> bool:
        try:
            width, height = obs.content.size
            return width > height
        except Exception as e:
            logger.warning("Failed to check orientation for %s: %s", obs.path, e)
            return False


class DateRange(Sigil):
    """Contrast: in-range vs out-of-range by EXIF DateTimeOriginal."""

    EXIF_DATE_FORMAT = "%Y:%m:%d %H:%M:%S"

    def __init__(self, start: datetime | None = None, end: datetime | None = None):
        self.start = start
        self.end = end

    def _get_date_taken(self, obs: ImageObservation) -> datetime | None:
        """Extract DateTimeOriginal from EXIF."""
        try:
            img = obs.content
            exif = img.getexif()
            if not exif:
                return None

            exif_ifd = exif.get_ifd(IFD.Exif)
            date_str = exif_ifd.get(36867) if exif_ifd else None

            if not date_str:
                date_str = exif.get(306)
            if not date_str:
                return None

            return datetime.strptime(date_str, self.EXIF_DATE_FORMAT)
        except Exception as e:
            logger.warning("Failed to read EXIF date for %s: %s", obs.path, e)
            return None

    def filter(self, obs: ImageObservation) -> bool:
        date_taken = self._get_date_taken(obs)
        if date_taken is None:
            logger.warning("No EXIF date for %s, skipping", obs.path)
            return False

        obs.metadata["date_taken"] = date_taken

        if self.start and date_taken < self.start:
            return False
        if self.end and date_taken > self.end:
            return False

        return True


class Batch(MergeSigil):
    """Collapse: window observations into groups of N."""

    def __init__(self, n: int = 10):
        self.n = n

    def merge(self, streams: list[Iterator[T]]) -> Iterator[list[ImageObservation]]:
        """Collect observations into batches of size n."""
        batch: list[ImageObservation] = []

        for stream in streams:
            for item in stream:
                items = item if isinstance(item, list) else [item]
                for single in items:
                    batch.append(single)
                    if len(batch) >= self.n:
                        for obs in batch:
                            obs.sigils.append(self.name)
                        yield batch
                        batch = []

        if batch:
            for obs in batch:
                obs.sigils.append(self.name)
            yield batch


class Concat(MergeSigil):
    """Merge: concatenate streams sequentially."""

    def merge(self, streams: list[Iterator[T]]) -> Iterator[T]:
        for stream in streams:
            yield from stream


class Interleave(MergeSigil):
    """Merge: round-robin from multiple streams."""

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
