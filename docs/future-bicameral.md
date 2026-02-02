# Future: Bicameral Mind

Beyond Papilio. A note on the larger architectural vision.

## McGilchrist's Divided Brain

Ian McGilchrist's work describes two modes of attention:

**Right hemisphere**
- Holistic, gestalt perception
- Attends to the whole, the embodied, the present
- Sees relationships, context, the living
- Pre-linguistic

**Left hemisphere**
- Analytical, sequential
- Abstracts, categorizes, names
- Manipulates representations
- Language-based

Neither is complete alone. The corpus callosum integrates them.

## Mapping to Models

**Right hemisphere → Vision models (DINO, etc.)**
- Direct perception of images
- Embeddings capture gestalt, similarity, relationships
- No language intermediary
- "Sees" without naming

**Left hemisphere → LLM**
- Reasons in language
- Categorizes, analyzes, explains
- Sequential, logical
- Names and abstracts

## Bicameral Agent

An observer with both modes:

```
Observation
    ↓
Right (DINO): perceives gestalt, embeddings, similarity
Left (LLM): categorizes, reasons, judges
    ↓
Corpus Callosum: integrates both perceptions
    ↓
Agent wearing Sigil
    ↓
Collapse with full perception
    ↓
Choice
```

The right hemisphere attends to *what is there*.
The left hemisphere attends to *what it means*.
The corpus callosum makes them one observer.

## Not This Project

Papilio is the photo pipeline - sigils, contrasts, collapse.

The bicameral mind is a separate architecture for the observer/agent itself. It would:
- Use DINO for right-hemisphere perception
- Use LLM for left-hemisphere reasoning
- Build integration (corpus callosum) to unify them

That architecture feeds *into* systems like Papilio, providing richer perception for agents wearing sigils.

## References

- McGilchrist, Iain. *The Master and His Emissary*
- McGilchrist, Iain. *The Matter with Things*
- DINO: Self-Distillation with No Labels (Meta AI)
