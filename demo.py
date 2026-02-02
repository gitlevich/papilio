#!/usr/bin/env python3
"""Demo: pipeline concepts with synthetic images."""

import tempfile
from pathlib import Path

from PIL import Image

from pipeline import Pipeline
from sigil import Sigil
from sigils import Batch, ImageObservation, Input, LandscapeOnly


class Grayscale(Sigil):
    """Transform: convert to grayscale."""

    def map(self, obs: ImageObservation) -> ImageObservation:
        obs.content = obs.content.convert("L")
        obs.metadata["grayscale"] = True
        return obs


class AnnotateSize(Sigil):
    """Transform: record dimensions in metadata."""

    def map(self, obs: ImageObservation) -> ImageObservation:
        w, h = obs.content.size
        obs.metadata["width"] = w
        obs.metadata["height"] = h
        obs.metadata["aspect"] = "landscape" if w > h else "portrait" if h > w else "square"
        return obs


def create_test_images(directory: Path) -> None:
    """Create a mix of landscape and portrait images."""
    colors = ["red", "green", "blue", "yellow", "purple"]

    for i, color in enumerate(colors):
        img = Image.new("RGB", (200, 100), color=color)
        img.save(directory / f"landscape_{i}.jpg")

        img = Image.new("RGB", (100, 200), color=color)
        img.save(directory / f"portrait_{i}.jpg")

    print(f"Created {len(colors) * 2} test images in {directory}")


def demo_basic_pipeline():
    """Demo: input -> annotate."""
    print("\n=== Basic Pipeline ===")
    print("Input -> AnnotateSize")

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        create_test_images(root)

        pipeline = (
            Pipeline()
            .add(Input(root))
            .add(AnnotateSize())
        )

        for obs in pipeline.run():
            print(f"  {obs.path.name}: {obs.metadata['aspect']} ({obs.metadata['width']}x{obs.metadata['height']})")
            print(f"    sigils: {obs.sigils}")


def demo_contrast_pipeline():
    """Demo: contrast (landscape vs portrait)."""
    print("\n=== Contrast Pipeline ===")
    print("Input -> LandscapeOnly -> AnnotateSize")
    print("Contrast: landscape passes, portrait rejected")

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        create_test_images(root)

        pipeline = (
            Pipeline()
            .add(Input(root))
            .add(LandscapeOnly())
            .add(AnnotateSize())
        )

        results = list(pipeline.run())
        print(f"  Passed: {len(results)} observations (all landscape)")
        for obs in results[:3]:
            print(f"    {obs.path.name}: {obs.metadata['aspect']}")


def demo_collapse_pipeline():
    """Demo: collapse (batch observations into groups)."""
    print("\n=== Collapse Pipeline ===")
    print("Input -> Batch(n=3)")
    print("Many observations collapse into groups")

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        create_test_images(root)

        pipeline = (
            Pipeline()
            .add(Input(root))
            .add(Batch(n=3))
        )

        for i, batch in enumerate(pipeline.run()):
            print(f"  Batch {i}: {len(batch)} observations")
            for obs in batch:
                print(f"    - {obs.path.name}")


def demo_transform_pipeline():
    """Demo: map transformation."""
    print("\n=== Transform Pipeline ===")
    print("Input -> Grayscale")

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        create_test_images(root)

        pipeline = (
            Pipeline()
            .add(Input(root))
            .add(Grayscale())
        )

        results = list(pipeline.run())
        print(f"  Transformed: {len(results)} observations")
        for obs in results[:3]:
            mode = obs.content.mode
            print(f"    {obs.path.name}: mode={mode}, grayscale={obs.metadata.get('grayscale')}")


if __name__ == "__main__":
    demo_basic_pipeline()
    demo_contrast_pipeline()
    demo_collapse_pipeline()
    demo_transform_pipeline()

    print("\n=== Attention Language ===")
    print("- Observation[T]: what attention focuses on, generic over content")
    print("- Sigil: pattern + preferences (filter/map)")
    print("- Contrast: filter - pass or reject")
    print("- Collapse: many possibilities -> fewer (Batch)")
    print("- sigils list: marks left by sigils passed through")
