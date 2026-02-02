"""Pipeline composition and execution."""

import logging
from collections.abc import Iterator
from typing import TypeVar

from observation import Observation
from stage import MergeStage, Stage

logger = logging.getLogger(__name__)

T = TypeVar("T", Observation, list[Observation])


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

    def run(self, initial: Iterator[Observation] | None = None) -> Iterator[T]:
        """Execute pipeline, yielding results."""
        stream: Iterator[T] = initial or iter([])

        for stage in self.stages:
            if isinstance(stage, MergeStage):
                stream = stage.merge([stream])
            else:
                stream = self._process_stage(stage, stream)

        yield from stream

    def _process_stage(self, stage: Stage, stream: Iterator[T]) -> Iterator[T]:
        """Process a stage, handling both observations and batches."""
        if type(stage).process is not Stage.process:
            yield from stage.process(stream)
            return

        for obs in stream:
            if isinstance(obs, list):
                result = []
                for single in obs:
                    if stage.filter(single):
                        processed = stage.map(single)
                        processed.sigils.append(stage.name)
                        result.append(processed)
                if result:
                    yield result
            else:
                if stage.filter(obs):
                    processed = stage.map(obs)
                    processed.sigils.append(stage.name)
                    yield processed


class Branch:
    """Fan-out: feed one stream to multiple downstream pipelines.

    Each branch receives a copy of observations. For now, processes sequentially.
    Designed so threading/multiprocessing can be swapped in later.
    """

    def __init__(self, branches: list[Pipeline]):
        self.branches = branches

    def process(self, stream: Iterator[Observation]) -> list[Iterator[T]]:
        """Process stream through all branches.

        Currently materializes the stream to allow multiple passes.
        Future: could use itertools.tee or queue-based distribution.
        """
        observations = list(stream)
        return [branch.run(iter(observations)) for branch in self.branches]
