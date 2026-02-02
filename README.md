<p align="center">
  <img src="papilio_machaon.png" width="120" alt="Papilio">
</p>

# Papilio

A streaming photo pipeline in Python. Images flow through composable stages that filter and transform.

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

# Filter to landscape orientation
ingest --input ./photos --output ./processed --stages landscape

# Filter by EXIF date
ingest --input ./photos --output ./processed --date-start 2025-02-01 --date-end 2025-02-28
```

## Architecture

**Stage** - A sigil naming a concern. Each stage implements:
- `filter(item) -> bool` — does this item belong?
- `map(item) -> item` — transform/annotate

**MergeStage** - Fan-in combining multiple streams (batch, concat, interleave).

**Pipeline** - Composes stages. Items flow through as generators for memory efficiency.

**ImageItem** - The unit of work: path, lazy-loaded image, metadata dict, and sigils tracking provenance.

## Built-in Stages

| Stage | Type | Description |
|-------|------|-------------|
| `InputStage` | Source | Recursively walks directory for images |
| `OutputStage` | Sink | Resizes to 4K if larger, writes preserving structure |
| `DateFilter` | Filter | EXIF DateTimeOriginal within date range |
| `LandscapeOnly` | Filter | Width > height |
| `BatchMerge` | Merge | Windows items into groups of N |
| `Concat` | Merge | Concatenates streams sequentially |
| `Interleave` | Merge | Round-robin from multiple streams |

## Extending

```python
from stage import Stage
from item import ImageItem

class Grayscale(Stage):
    def map(self, item: ImageItem) -> ImageItem:
        item.image = item.image.convert("L")
        return item
```

Register in `ingest.py`:
```python
AVAILABLE_STAGES["grayscale"] = Grayscale
```

## Supported Formats

`.jpg`, `.jpeg`, `.png`, `.tiff`, `.tif`, `.heic`, `.heif`

## License

MIT
