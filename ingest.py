#!/usr/bin/env python3
"""CLI for photo ingestion pipeline."""

import argparse
import logging
from datetime import datetime
from pathlib import Path

import pillow_heif

from pipeline import Pipeline
from stages import (
    BatchMerge,
    DateFilter,
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


def parse_date(value: str) -> datetime:
    """Parse date string in YYYY-MM-DD format."""
    return datetime.strptime(value, "%Y-%m-%d")


def build_pipeline(
    input_dir: Path,
    output_dir: Path,
    stage_names: list[str],
    date_start: datetime | None = None,
    date_end: datetime | None = None,
) -> Pipeline:
    """Construct pipeline from stage names."""
    pipeline = Pipeline()
    pipeline.add(InputStage(input_dir))

    # Add date filter if specified
    if date_start or date_end:
        pipeline.add(DateFilter(start=date_start, end=date_end))

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
    parser.add_argument(
        "--date-start",
        type=parse_date,
        help="Filter images taken on or after this date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--date-end",
        type=parse_date,
        help="Filter images taken on or before this date (YYYY-MM-DD)",
    )
    args = parser.parse_args()

    if not args.input.is_dir():
        logger.error("Input path is not a directory: %s", args.input)
        return

    stage_names = [s.strip() for s in args.stages.split(",") if s.strip()]
    pipeline = build_pipeline(
        args.input,
        args.output,
        stage_names,
        date_start=args.date_start,
        date_end=args.date_end,
    )

    count = 0
    for item in pipeline.run():
        count += 1 if not isinstance(item, list) else len(item)

    logger.info("Processed %d items", count)


if __name__ == "__main__":
    main()
