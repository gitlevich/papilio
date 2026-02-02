# Sigil Interchange Format

A JSON format for defining sigils with weighted preferences along contrasts.

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

### contrast_weights

Preferences along contrast dimensions. The weight encodes:
- **Direction**: positive prefers one pole, negative prefers the other
- **Strength**: magnitude indicates how much this contrast matters

| Contrast | Negative Pole (-1) | Positive Pole (+1) |
|----------|--------------------|--------------------|
| abstraction | Representational | Abstract |
| color_mode | Muted/desaturated | Vivid/saturated |
| complexity | Simple/minimal | Complex/detailed |
| setting | Natural/outdoor | Urban/indoor |
| mood | Dark/moody | Bright/cheerful |
| depth | Shallow DoF | Deep DoF |
| motion | Static | Dynamic |

Zero weight = neutral, this contrast doesn't influence collapse.

### category_weights

Subject matter preferences. Categories an observation might belong to.

| Category | Description |
|----------|-------------|
| insects | Macro photography of insects |
| plants | Flora, botanical subjects |
| nature_general | Landscapes, wildlife, natural scenes |
| portraits | Human subjects |
| architecture | Buildings, urban structures |
| abstract | Non-representational imagery |

Positive = prefer, negative = avoid, zero = neutral.

### region_affinities

Geographic preferences for location-tagged observations. Empty = no preference.

### calibration counts

How many examples were used to calibrate each preference type. Higher = more confident weights.

## How an Agent Uses This

An agent wearing this sigil:

1. Attends to a frame of observations
2. For each observation, perceives its position along each contrast
3. Compares positions to sigil preferences
4. Collapses: observations that align with preferences pass through
5. Observations that pass become choices, enter the narrative

```python
def load_sigil(path: Path) -> Sigil:
    data = json.loads(path.read_text())
    return Sigil(
        contrast_weights=data["contrast_weights"],
        category_weights=data.get("category_weights", {}),
    )

# Agent collapses frame using sigil preferences
for obs in frame:
    if agent.aligned(obs, sigil):
        yield Choice(obs)
```

## Collapse Criteria

For an observation to pass collapse:

1. Determine observation's position on each contrast (-1.0 to +1.0)
2. For each contrast, check alignment: does position match preference direction?
3. Weight the alignments by preference strength
4. If aggregate alignment exceeds threshold, observation passes

The threshold can be:
- Fixed (e.g., 0.5)
- Dynamic (top N observations)
- Adaptive (based on attention budget)

## Versioning

The `version` field is a hash identifying the calibration state. Changes to weights update this hash to track sigil evolution over time.
