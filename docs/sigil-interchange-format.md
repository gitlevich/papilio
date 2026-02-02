# Sigil Interchange Format

A JSON format for defining sigils with weighted preferences across contrasts.

## Schema

```json
{
  "user_id": "string",
  "version": "string",
  "created_at": "ISO8601 timestamp",
  "updated_at": "ISO8601 timestamp",
  "category_weights": {
    "category_name": "float (-1.0 to 1.0)"
  },
  "contrast_weights": {
    "contrast_name": "float (-1.0 to 1.0)"
  },
  "region_affinities": ["region_name"],
  "categories_calibrated": "int",
  "contrasts_calibrated": "int"
}
```

## Example: Photographic Taste

```json
{
  "user_id": "demo",
  "version": "dfba287e277efbf1",
  "created_at": "2026-02-02T03:37:35.562612+00:00",
  "updated_at": "2026-02-02T04:11:44.635580+00:00",
  "category_weights": {
    "insects": 0.62,
    "plants": -0.44,
    "nature_general": 0.44
  },
  "contrast_weights": {
    "abstraction": 0.0,
    "color_mode": 0.68,
    "complexity": 0.08,
    "setting": -0.68
  },
  "region_affinities": [],
  "categories_calibrated": 3,
  "contrasts_calibrated": 3
}
```

## Field Definitions

### category_weights

Subject matter preferences. Positive weight = prefer, negative = avoid, zero = neutral.

| Category | Description |
|----------|-------------|
| insects | Macro photography of insects |
| plants | Flora, botanical subjects |
| nature_general | Landscapes, wildlife, natural scenes |
| portraits | Human subjects |
| architecture | Buildings, urban structures |
| abstract | Non-representational imagery |

### contrast_weights

Aesthetic dimension preferences. Weight indicates direction and strength.

| Contrast | Negative Pole | Positive Pole |
|----------|---------------|---------------|
| abstraction | Representational | Abstract |
| color_mode | Muted/desaturated | Vivid/saturated |
| complexity | Simple/minimal | Complex/detailed |
| setting | Natural/outdoor | Urban/indoor |
| mood | Dark/moody | Bright/cheerful |
| depth | Shallow DoF | Deep DoF |
| motion | Static | Dynamic |

### region_affinities

Geographic preferences for location-tagged images. Empty array = no preference.

### calibration counts

How many examples were used to calibrate each preference type. Higher = more confident weights.

## Usage

A sigil defined in this format can be loaded and used to score observations:

```python
def load_sigil(path: Path) -> Sigil:
    data = json.loads(path.read_text())
    return Sigil(
        contrast_weights=data["contrast_weights"],
        category_weights=data.get("category_weights", {}),
        region_affinities=data.get("region_affinities", []),
    )

# Score an observation
score = sigil.score(observation)

# Collapse frame to choices above threshold
choices = [obs for obs in frame if sigil.score(obs) > 0.5]
```

## Scoring Algorithm

```
total_score = 0

for each contrast in sigil.contrast_weights:
    contrast_score = contrast.evaluate(observation)  # -1.0 to 1.0
    weight = sigil.contrast_weights[contrast]
    total_score += contrast_score * weight

for each category in sigil.category_weights:
    if observation has category:
        total_score += sigil.category_weights[category]

normalize by number of weights applied
```

## Versioning

The `version` field is a hash identifying the calibration state. Changes to weights should update this hash to track sigil evolution.
