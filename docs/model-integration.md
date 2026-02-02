# Model Integration

A sigil holds preferences. An agent perceives. For some contrasts, perception requires a model.

A model can also embody high-level aesthetic preferences directly - "good", "beautiful", "interesting". These aren't contrasts with two poles; they're learned judgments that collapse to pass/reject.

## Contrast Types

### Computable Contrasts

Position determined directly from observation data:

| Contrast | How to Compute |
|----------|----------------|
| orientation | width / height ratio |
| date_range | EXIF DateTimeOriginal |
| color_saturation | HSV histogram analysis |
| brightness | luminance histogram |
| aspect_ratio | dimensional ratio |
| file_size | proxy for resolution/detail |

These need no model - the agent can perceive them directly.

### Model-Dependent Contrasts

Position requires a model to perceive:

| Contrast | Model Task |
|----------|------------|
| abstraction | representational ↔ abstract classification |
| setting | natural ↔ urban scene classification |
| mood | dark/moody ↔ bright/cheerful sentiment |
| complexity | simple ↔ complex visual analysis |
| subject_category | multi-label classification |

The model becomes the agent's eyes for these dimensions.

## Architecture

```
Observation
    ↓
Model (perceives position on complex contrasts)
    ↓
Agent wearing Sigil
    ↓
Collapse (using sigil preferences + perceived positions)
    ↓
Choices
```

## Model Interface

```python
class ContrastModel:
    """Perceives observation positions on model-dependent contrasts."""

    def perceive(self, obs: Observation) -> dict[str, float]:
        """Return positions on contrasts this model can perceive.

        Returns:
            dict mapping contrast name to position (-1.0 to +1.0)
        """
        ...


class VisionModel(ContrastModel):
    """Uses a vision model (CLIP, etc.) to perceive contrasts."""

    def perceive(self, obs: Observation) -> dict[str, float]:
        # Extract embeddings
        # Map to contrast positions
        ...


class CategoryModel(ContrastModel):
    """Multi-label classifier for subject categories."""

    def perceive(self, obs: Observation) -> dict[str, float]:
        # Run classifier
        # Return category presence as positions
        ...
```

## Agent with Model

```python
class Agent:
    def __init__(self, sigil: Sigil, models: list[ContrastModel] = None):
        self.sigil = sigil
        self.models = models or []

    def perceive(self, obs: Observation) -> dict[str, float]:
        """Perceive observation's position on all contrasts."""
        positions = {}

        # Computable contrasts
        positions["orientation"] = self._compute_orientation(obs)
        positions["color_saturation"] = self._compute_saturation(obs)

        # Model-dependent contrasts
        for model in self.models:
            positions.update(model.perceive(obs))

        return positions

    def collapse(self, frame: Frame) -> Iterator[Choice]:
        """Collapse frame using sigil preferences."""
        for obs in frame:
            positions = self.perceive(obs)
            if self._aligned(positions):
                yield Choice(obs)
```

## Pluggable Models

Different models for different needs:

| Model | Speed | Accuracy | Contrasts |
|-------|-------|----------|-----------|
| CLIP | Fast | Good | Most visual contrasts |
| Custom CNN | Fast | Varies | Trained-for contrasts |
| Vision LLM | Slow | Excellent | Any describable contrast |

The agent can swap models based on attention budget:
- High framerate: fast model, fewer contrasts
- High resolution: slow model, more contrasts

## Example: Photographic Taste Agent

```python
# Load sigil with preferences
taste = load_sigil("photographic_taste.json")

# Create agent with vision model for complex contrasts
agent = Agent(
    sigil=taste,
    models=[CLIPContrastModel()]
)

# Collapse a frame
for choice in agent.collapse(frame):
    # Observation aligned with taste preferences
    ...
```

The sigil defines *what* to prefer. The model enables *perceiving* along contrasts. The agent *collapses* based on both.

## Aesthetic Judgment Models

Beyond perceiving positions on contrasts, a model can embody aesthetic judgment directly:

- **"Good"** - technical quality, composition, focus
- **"Beautiful"** - aesthetic appeal
- **"Interesting"** - novelty, uniqueness
- **"Portfolio-worthy"** - meets professional standard

These aren't two-pole contrasts. They're learned preferences that act as their own sigils.

```python
class AestheticModel:
    """Model that embodies aesthetic judgment."""

    def judge(self, obs: Observation) -> float:
        """How strongly does this observation align with aesthetic?

        Returns: 0.0 (reject) to 1.0 (strongly aligned)
        """
        ...


class BeautyModel(AestheticModel):
    """Trained on aesthetic preferences."""
    ...


class QualityModel(AestheticModel):
    """Technical quality assessment."""
    ...
```

An aesthetic model *is* a sigil's preferences made executable. Instead of weighted contrasts, it directly learned what "good" means from examples.

```python
# Model as sigil
beauty_sigil = ModelSigil(BeautyModel(), threshold=0.7)

# Agent wearing beauty
agent = Agent(sigil=beauty_sigil)

# Collapse to beautiful observations
for choice in agent.collapse(frame):
    ...
```

This inverts the relationship: instead of sigil preferences + model perception, the model *is* the preference.
