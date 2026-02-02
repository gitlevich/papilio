#!/usr/bin/env python3
"""Demo: show pipeline concepts with synthetic images."""

import tempfile
from pathlib import Path

from PIL import Image

from observation import Observation
from pipeline import Pipeline
from stage import Stage
from stages import BatchMerge, InputStage, LandscapeOnly


class Grayscale(Stage):
    """Transform: convert to grayscale."""

    def map(self, obs: Observation) -> Observation:
        obs.image = obs.image.convert("L")
        obs.metadata["grayscale"] = True
        return obs


class AnnotateSize(Stage):
    """Transform: record dimensions in metadata."""

    def map(self, obs: Observation) -> Observation:
        w, h = obs.image.size
        obs.metadata["width"] = w
        obs.metadata["height"] = h
        obs.metadata["aspect"] = "landscape" if w > h else "portrait" if h > w else "square"
        return obs


def create_test_images(directory: Path) -> None:
    """Create a mix of landscape and portrait images."""
    colors = ["red", "green", "blue", "yellow", "purple"]

    for i, color in enumerate(colors):
        # Landscape
        img = Image.new("RGB", (200, 100), color=color)
        img.save(directory / f"landscape_{i}.jpg")

        # Portrait
        img = Image.new("RGB", (100, 200), color=color)
        img.save(directory / f"portrait_{i}.jpg")

    print(f"Created {len(colors) * 2} test images in {directory}")


def demo_basic_pipeline():
    """Demo: input -> annotate -> output."""
    print("\n=== Basic Pipeline ===")
    print("InputStage -> AnnotateSize")

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        create_test_images(root)

        pipeline = (
            Pipeline()
            .add(InputStage(root))
            .add(AnnotateSize())
        )

        for obs in pipeline.run():
            print(f"  {obs.path.name}: {obs.metadata['aspect']} ({obs.metadata['width']}x{obs.metadata['height']})")
            print(f"    sigils: {obs.sigils}")


def demo_filter_pipeline():
    """Demo: filter contrast (landscape vs portrait)."""
    print("\n=== Filter (Contrast) Pipeline ===")
    print("InputStage -> LandscapeOnly -> AnnotateSize")
    print("Contrast: landscape passes, portrait rejected")

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        create_test_images(root)

        pipeline = (
            Pipeline()
            .add(InputStage(root))
            .add(LandscapeOnly())
            .add(AnnotateSize())
        )

        results = list(pipeline.run())
        print(f"  Passed: {len(results)} observations (all landscape)")
        for obs in results[:3]:
            print(f"    {obs.path.name}: {obs.metadata['aspect']}")


def demo_batch_pipeline():
    """Demo: merge stage batching observations."""
    print("\n=== Batch (Merge) Pipeline ===")
    print("InputStage -> BatchMerge(n=3)")
    print("Groups observations into batches")

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        create_test_images(root)

        pipeline = (
            Pipeline()
            .add(InputStage(root))
            .add(BatchMerge(n=3))
        )

        for i, batch in enumerate(pipeline.run()):
            print(f"  Batch {i}: {len(batch)} observations")
            for obs in batch:
                print(f"    - {obs.path.name}")


def demo_transform_pipeline():
    """Demo: map transformation."""
    print("\n=== Transform (Map) Pipeline ===")
    print("InputStage -> Grayscale")

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        create_test_images(root)

        pipeline = (
            Pipeline()
            .add(InputStage(root))
            .add(Grayscale())
        )

        results = list(pipeline.run())
        print(f"  Transformed: {len(results)} observations")
        for obs in results[:3]:
            mode = obs.image.mode
            print(f"    {obs.path.name}: mode={mode}, grayscale={obs.metadata.get('grayscale')}")


if __name__ == "__main__":
    demo_basic_pipeline()
    demo_filter_pipeline()
    demo_batch_pipeline()
    demo_transform_pipeline()

    print("\n=== Summary ===")
    print("- Observation: what attention focuses on")
    print("- Stage.filter(): contrast - pass or reject")
    print("- Stage.map(): transformation")
    print("- MergeStage: combine streams (batch, concat, interleave)")
    print("- sigils: marks left by stages the observation passed through")
