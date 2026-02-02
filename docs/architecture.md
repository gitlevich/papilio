# Papilio Architecture

Naming and concepts follow the [Attention Language](https://sigilsnotspells.com).

## Core Concepts

### Attention

A finite resource. Can be spent on framerate (more observations) or resolution (deeper examination of each). These compete - you can scan quickly with low detail, or slowly with high detail.

### Frame

The current sensorium. What attention holds now. Has depth in time. In Papilio, the observations currently under attention before collapse.

### Observation

What attention focuses on. In Papilio, an image with:
- Path to source file
- Lazy-loaded image data
- Metadata accumulated through the pipeline
- Sigil marks (which sigils it passed through)

An observation *has* a position along each contrast - it sits somewhere on each spectrum.

### Contrast

A span between opposites. A dimension that exists. Passive - it doesn't do anything.

Examples:
- Orientation: landscape ↔ portrait
- Date: in-range ↔ out-of-range
- Color mode: muted ↔ vivid
- Setting: natural ↔ urban
- Complexity: simple ↔ complex

Observations have positions on contrasts. Sigils have preferences along contrasts. The contrast itself just *is*.

### Sigil

A pattern plus preferences. A labeled door. When worn by an observer, transforms them into an agent.

A sigil embodies:
- **Preferences along contrasts**: direction and strength
- **Transform**: how to modify observations that pass

The sigil doesn't act - it configures the agent who wears it.

### Observer

Watches without preference. Pure attention on the frame.

### Agent

Observer wearing a sigil. The active one.

The agent:
- Attends to frames (within attention budget)
- Perceives observations along contrasts
- Collapses each frame according to sigil preferences
- Operates at a framerate and resolution (inversely proportional - same attention budget)

### Collapse

The transformation of many possibilities into fewer. The agent collapses each frame along all contrasts they can attend to, guided by the sigil's preferences.

Binary collapse: observation passes or doesn't.
Weighted collapse: preferences have direction and strength; observation must align sufficiently to pass.

### Choice

An observation that survived collapse. Enters the agent's narrative.

### Narrative

History of choices. What happened as attention flowed through sigils. Currently represented as the `sigils` list on each observation.

## Current Implementation Mapping

| Concept | Implementation |
|---------|----------------|
| Observation | `Observation` class |
| Frame | Input stream to a sigil |
| Contrast | Implicit in `Sigil.filter()` |
| Sigil | `Sigil` class |
| Observer | `Pipeline` (implicit) |
| Agent | Pipeline executing a sigil |
| Collapse | Filter operation |
| Choice | Observation post-filter |
| Transform | `Sigil.map()` method |
| Narrative | `observation.sigils` list |

## Pipeline as Agent

```
Agent (Pipeline wearing Sigil)
    ↓
Attends to Frame (input stream)
    ↓
Perceives along Contrasts
    ↓
Collapses (observations pass or don't)
    ↓
Transforms (applies preferences)
    ↓
Choices enter Narrative (sigil marks)
    ↓
Next sigil (agent dons new sigil)
```

## Future Evolution

### Weighted Preferences

Move from binary filter to weighted alignment:

```python
class Sigil:
    contrast_preferences: dict[str, float]  # contrast name -> preference direction/strength

class Agent:
    def collapse(self, frame: Frame) -> Iterator[Choice]:
        """Collapse frame according to sigil preferences."""
        for obs in frame:
            if self.aligned(obs):
                yield Choice(obs)

    def aligned(self, obs: Observation) -> bool:
        """Does observation align with sigil preferences across contrasts?"""
        ...
```

### Attention Budget

Model framerate vs resolution trade-off:

```python
class Agent:
    attention_budget: float

    def attend(self, frames: Iterator[Frame], framerate: float):
        """Higher framerate = lower resolution per frame."""
        resolution = self.attention_budget / framerate
        ...
```
