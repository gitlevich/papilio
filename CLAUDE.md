## Photo Ingestion Pipeline

Build a streaming photo pipeline in Python with these characteristics:

**Core abstraction**: A `Stage` is a sigil - it names a concern and embodies two operations:

- `filter(item) -> bool` — does this item belong to this sigil's world?
- `map(item) -> item` — apply this sigil's preferences to transform/annotate the item

Stages compose into a pipeline. Each stage receives a stream, applies filter then map, emits a stream.

**Branching**: Fan-out for parallel processing. One stream feeds multiple downstream stages concurrently. Each branch
processes independently. Use case: apply different transformations in parallel, run CPU-bound and IO-bound work
separately.

**Merging**: Fan-in with semantics. A merge stage receives multiple input streams and can:

- Combine (interleave or concatenate)
- Window (collect N items, or items within time/batch bounds, then emit as group)
- Join (match items across streams by key)

Merge stages implement `merge(streams: list[Iterator]) -> Iterator` instead of filter/map.

**Pipeline item**: An `ImageItem` carrying the image path, lazy-loaded image data, accumulated metadata dict, and a
`sigils: list[str]` tracking which stages it passed through.

**Input stage**: Recursively walk a directory. Recognize `.jpg`, `.jpeg`, `.png`, `.tiff`, `.tif`, `.heic`, `.heif`
natively. Other formats: installable via a stage immediately after input that handles the decode.

**Output stage**: Resize to 4K (3840px on long edge) if larger; passthrough if already ≤4K. Preserve aspect ratio. Write
to output directory mirroring source structure.

**Extensibility**: Inserting a new stage at any point should require only: (1) define the Stage class with filter/map, (
2) register it in the pipeline definition at the desired position.

Use generators for memory efficiency. Keep dependencies minimal (Pillow, pillow-heif for HEIF).

Create a simple CLI: `ingest.py --input <dir> --output <dir> [--stages stage1,stage2,...]`

Include example stages: `LandscapeOnly` (filter to width > height), and a `BatchMerge(n=10)` that windows items into
groups of N.

---