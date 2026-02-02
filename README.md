<p align="center">
  <img src="papilio_machaon.png" width="120" alt="Papilio">
</p>

# Papilio

A streaming photo pipeline. Observations flow through composable sigils that apply contrasts and transformations.

Naming inspired by the [Attention Language](https://sigilsnotspells.com).

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
ingest --input ./photos --output ./processed --sigils landscape

# Pass only images within date range
ingest --input ./photos --output ./processed --date-start 2025-02-01 --date-end 2025-02-28
```

## Architecture

**Observation** - What attention focuses on. An image with path, lazy-loaded data, metadata, and sigil marks.

**Sigil** - A pattern plus preferences. Each sigil implements:

- `filter(obs) -> bool` — apply a contrast: does this observation pass?
- `map(obs) -> obs` — transform the observation

**MergeSigil** - Collapse multiple streams into one (batch, concat, interleave).

**Pipeline** - Composes sigils. Observations flow through as generators.

## Built-in Sigils

| Sigil | Type | Description |
| ----- | ---- | ----------- |
| `Input` | Source | Recursively walks directory for images |
| `Output` | Sink | Resizes to 4K if larger, writes preserving structure |
| `DateRange` | Contrast | In-range vs out-of-range by EXIF date |
| `LandscapeOnly` | Contrast | Landscape vs portrait orientation |
| `Batch` | Collapse | Windows observations into groups of N |
| `Concat` | Merge | Concatenates streams sequentially |
| `Interleave` | Merge | Round-robin from multiple streams |

## Extending

```python
from sigil import Sigil
from observation import Observation

class Grayscale(Sigil):
    """Transform: convert to grayscale."""

    def map(self, obs: Observation) -> Observation:
        obs.image = obs.image.convert("L")
        return obs
```

Register in `ingest.py`:

```python
AVAILABLE_SIGILS["grayscale"] = Grayscale
```

## Supported Formats

`.jpg`, `.jpeg`, `.png`, `.tiff`, `.tif`, `.heic`, `.heif`

## License

MIT
