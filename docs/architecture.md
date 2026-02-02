# Papilio Architecture

Naming and concepts follow the [Attention Language](https://sigilsnotspells.com).

## Core Concepts

### Observation

What attention focuses on. In Papilio, an image with:
- Path to source file
- Lazy-loaded image data
- Metadata accumulated through the pipeline
- Sigil marks (which sigils it passed through)

### Frame

The current sensorium. All observations across all potential contrasts before any filtering. The full field of attention before collapse.

### Contrast

A span between opposites. The basis for distinguishing observations.

Examples:
- Orientation: landscape ↔ portrait
- Date range: in-range ↔ out-of-range
- Color mode: muted ↔ vivid
- Setting: natural ↔ urban
- Complexity: simple ↔ complex

A contrast can be:
- **Binary**: pass/reject (current implementation)
- **Continuous**: score from -1.0 to +1.0 (future)

### Sigil

A pattern plus preferences. When an observer wears a sigil, they become an agent.

A sigil embodies:
- **Contrasts it's sensitive to**: which dimensions matter
- **Preferences**: which side of each contrast is favored (weights)
- **Transform**: how to modify observations that pass

### Collapse

The transformation of many possibilities into fewer. Applied when an agent evaluates observations through a sigil's contrasts.

Binary collapse: observations either pass or don't.
Weighted collapse: observations score against preferences, threshold determines passage.

### Choice

An observation that survived collapse. What remains after the sigil's contrasts are applied.

### Observer

Watches without preference. Pure attention on the frame.

### Agent

Observer wearing a sigil. The sigil's preferences guide collapse. Each choice enters the agent's narrative.

### Narrative

History of choices. What happened as attention flowed through sigils. Currently represented as the `sigils` list on each observation - the marks left by sigils it passed through.

## Current Implementation Mapping

| Concept | Implementation |
|---------|----------------|
| Observation | `Observation` class |
| Frame | Input stream to a sigil |
| Contrast | `Sigil.filter()` method (binary) |
| Sigil | `Sigil` class |
| Collapse | Filter operation |
| Choice | Observation post-filter |
| Transform | `Sigil.map()` method |
| Observer | `Pipeline` (implicit) |
| Agent | Pipeline executing a sigil |
| Narrative | `observation.sigils` list |

## Pipeline Flow

```
Frame (all observations)
    ↓
Agent wearing Sigil
    ↓
Collapse (apply contrasts)
    ↓
Choices (observations that passed)
    ↓
Transform (apply preferences)
    ↓
Mark with sigil name
    ↓
Next sigil...
```

## Future Evolution

### Weighted Contrasts

Move from binary filter to continuous scoring:

```python
class Contrast:
    def score(self, obs: Observation) -> float:
        """Score observation on this contrast. -1.0 to +1.0"""
        ...

class Sigil:
    contrast_weights: dict[str, float]

    def score(self, obs: Observation) -> float:
        """Aggregate score across weighted contrasts."""
        return sum(
            CONTRASTS[name].score(obs) * weight
            for name, weight in self.contrast_weights.items()
        )
```

### Rich Narrative

Expand narrative to capture more than sigil names:
- Timestamp of each choice
- Scores at each sigil
- Branch paths taken
- Metadata evolution
