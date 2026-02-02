<p align="center">
  <img src="papilio_machaon.png" width="120" alt="Papilio">
</p>

# Papilio

A streaming photo pipeline. Observations flow through composable sigils that apply contrasts and transformations.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

```bash
# Process all images
ingest --input ./photos --output ./processed

# Pass only landscape orientation (width > height)
ingest --input ./photos --output ./processed --stages landscape

# Pass only images within date range
ingest --input ./photos --output ./processed --date-start 2025-02-01 --date-end 2025-02-28
```

## Architecture

Naming follows the [Attention Language](https://sigilsnotspells.com) framework.

**Observation** - What attention focuses on. An image with path, lazy-loaded data, metadata, and sigil marks.

**Stage (Sigil)** - A pattern plus preferences. Each stage implements:
- `filter(obs) -> bool` — apply a contrast: does this observation pass?
- `map(obs) -> obs` — transform the observation

**MergeStage** - Fan-in combining multiple streams (batch, concat, interleave).

**Pipeline** - Composes stages. Observations flow through as generators for memory efficiency.

## Built-in Stages

| Stage | Type | Description |
|-------|------|-------------|
| `InputStage` | Source | Recursively walks directory for images |
| `OutputStage` | Sink | Resizes to 4K if larger, writes preserving structure |
| `DateFilter` | Contrast | In-range vs out-of-range by EXIF date |
| `LandscapeOnly` | Contrast | Landscape vs portrait orientation |
| `BatchMerge` | Merge | Windows observations into groups of N |
| `Concat` | Merge | Concatenates streams sequentially |
| `Interleave` | Merge | Round-robin from multiple streams |

## Extending

```python
from stage import Stage
from observation import Observation

class Grayscale(Stage):
    """Transform: convert to grayscale."""

    def map(self, obs: Observation) -> Observation:
        obs.image = obs.image.convert("L")
        return obs
```

Register in `ingest.py`:
```python
AVAILABLE_STAGES["grayscale"] = Grayscale
```

## Supported Formats

`.jpg`, `.jpeg`, `.png`, `.tiff`, `.tif`, `.heic`, `.heif`

## License

MIT
