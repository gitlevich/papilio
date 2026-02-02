"""Pipeline composition and execution."""

import logging
from collections.abc import Iterator
from typing import TypeVar

from item import ImageItem
from stage import MergeStage, Stage

logger = logging.getLogger(__name__)

T = TypeVar("T", ImageItem, list[ImageItem])


class Pipeline:
    """Compose stages into an executable pipeline.

    Supports linear pipelines. Branching/merging handled explicitly
    via Branch and merge stages.
    """

    def __init__(self, stages: list[Stage | MergeStage] | None = None):
        self.stages: list[Stage | MergeStage] = stages or []

    def add(self, stage: Stage | MergeStage) -> "Pipeline":
        """Add a stage. Returns self for chaining."""
        self.stages.append(stage)
        return self

    def run(self, initial: Iterator[ImageItem] | None = None) -> Iterator[T]:
        """Execute pipeline, yielding results."""
        stream: Iterator[T] = initial or iter([])

        for stage in self.stages:
            if isinstance(stage, MergeStage):
                # MergeStage expects list of streams; wrap single stream
                stream = stage.merge([stream])
            else:
                stream = self._process_stage(stage, stream)

        yield from stream

    def _process_stage(self, stage: Stage, stream: Iterator[T]) -> Iterator[T]:
        """Process a stage, handling both items and batches."""
        for item in stream:
            if isinstance(item, list):
                # Batch: apply stage to each item in batch
                result = []
                for single in item:
                    if stage.filter(single):
                        processed = stage.map(single)
                        processed.sigils.append(stage.name)
                        result.append(processed)
                if result:
                    yield result
            else:
                # Single item
                if stage.filter(item):
                    processed = stage.map(item)
                    processed.sigils.append(stage.name)
                    yield processed


class Branch:
    """Fan-out: feed one stream to multiple downstream pipelines.

    Each branch receives a copy of items. For now, processes sequentially.
    Designed so threading/multiprocessing can be swapped in later.
    """

    def __init__(self, branches: list[Pipeline]):
        self.branches = branches

    def process(self, stream: Iterator[ImageItem]) -> list[Iterator[T]]:
        """Process stream through all branches.

        Currently materializes the stream to allow multiple passes.
        Future: could use itertools.tee or queue-based distribution.
        """
        items = list(stream)
        return [branch.run(iter(items)) for branch in self.branches]
