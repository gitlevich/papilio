#!/usr/bin/env python3
"""CLI for photo ingestion pipeline."""

import argparse
import logging
from pathlib import Path

import pillow_heif

from pipeline import Pipeline
from stages import (
    BatchMerge,
    InputStage,
    LandscapeOnly,
    OutputStage,
)

# Register HEIF/HEIC support with Pillow
pillow_heif.register_heif_opener()

# Stage registry for CLI access
AVAILABLE_STAGES = {
    "landscape": LandscapeOnly,
    "batch": BatchMerge,
}

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def build_pipeline(
    input_dir: Path,
    output_dir: Path,
    stage_names: list[str],
) -> Pipeline:
    """Construct pipeline from stage names."""
    pipeline = Pipeline()
    pipeline.add(InputStage(input_dir))

    for name in stage_names:
        if name not in AVAILABLE_STAGES:
            logger.warning("Unknown stage: %s, skipping", name)
            continue
        stage_class = AVAILABLE_STAGES[name]
        pipeline.add(stage_class())

    pipeline.add(OutputStage(output_dir, input_dir))
    return pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Photo ingestion pipeline")
    parser.add_argument("--input", "-i", type=Path, required=True, help="Input directory")
    parser.add_argument("--output", "-o", type=Path, required=True, help="Output directory")
    parser.add_argument(
        "--stages",
        "-s",
        type=str,
        default="",
        help=f"Comma-separated stages: {','.join(AVAILABLE_STAGES.keys())}",
    )
    args = parser.parse_args()

    if not args.input.is_dir():
        logger.error("Input path is not a directory: %s", args.input)
        return

    stage_names = [s.strip() for s in args.stages.split(",") if s.strip()]
    pipeline = build_pipeline(args.input, args.output, stage_names)

    count = 0
    for item in pipeline.run():
        count += 1 if not isinstance(item, list) else len(item)

    logger.info("Processed %d items", count)


if __name__ == "__main__":
    main()
