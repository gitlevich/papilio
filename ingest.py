#!/usr/bin/env python3
"""CLI for photo pipeline."""

import argparse
import logging
from datetime import datetime
from pathlib import Path

import pillow_heif

from pipeline import Pipeline
from sigils import (
    Batch,
    DateRange,
    Input,
    LandscapeOnly,
    Output,
)

pillow_heif.register_heif_opener()

AVAILABLE_SIGILS = {
    "landscape": LandscapeOnly,
    "batch": Batch,
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
    sigil_names: list[str],
    date_start: datetime | None = None,
    date_end: datetime | None = None,
) -> Pipeline:
    """Construct pipeline from sigil names."""
    pipeline = Pipeline()
    pipeline.add(Input(input_dir))

    if date_start or date_end:
        pipeline.add(DateRange(start=date_start, end=date_end))

    for name in sigil_names:
        if name not in AVAILABLE_SIGILS:
            logger.warning("Unknown sigil: %s, skipping", name)
            continue
        sigil_class = AVAILABLE_SIGILS[name]
        pipeline.add(sigil_class())

    pipeline.add(Output(output_dir, input_dir))
    return pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Photo pipeline")
    parser.add_argument("--input", "-i", type=Path, required=True, help="Input directory")
    parser.add_argument("--output", "-o", type=Path, required=True, help="Output directory")
    parser.add_argument(
        "--sigils",
        "-s",
        type=str,
        default="",
        help=f"Comma-separated sigils: {','.join(AVAILABLE_SIGILS.keys())}",
    )
    parser.add_argument(
        "--date-start",
        type=parse_date,
        help="Pass images taken on or after this date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--date-end",
        type=parse_date,
        help="Pass images taken on or before this date (YYYY-MM-DD)",
    )
    args = parser.parse_args()

    if not args.input.is_dir():
        logger.error("Input path is not a directory: %s", args.input)
        return

    sigil_names = [s.strip() for s in args.sigils.split(",") if s.strip()]
    pipeline = build_pipeline(
        args.input,
        args.output,
        sigil_names,
        date_start=args.date_start,
        date_end=args.date_end,
    )

    count = 0
    for obs in pipeline.run():
        count += 1 if not isinstance(obs, list) else len(obs)

    logger.info("Processed %d observations", count)


if __name__ == "__main__":
    main()
