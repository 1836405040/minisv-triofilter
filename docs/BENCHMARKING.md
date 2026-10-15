# Benchmark contracts

Truth TSV columns: `truth_id`, `sample`, `chrom`, `start`, `end`, `type`, `delta`,
`basis`. Coordinates must be 0-based, half-open on the same reference as calls.
For an insertion, start=end is a boundary and is treated as one base for mask
intersection. Types are INS/DEL; basis is REFERENCE or PARENT_ALLELE. Delta is
signed (positive insertion, negative deletion). A mapped TR directory start is
a locus locator, not an exact breakpoint. Document mapping and matching rules.

Do not compare a reference-relative insertion length directly with a parent-
relative delta. The matcher requires matching basis. Cross-reference mapping,
full allele reconstruction and exact sequence reconciliation must precede
claims of sequence equivalence. A GIAB BED is an evaluable region, not a de novo
truth list; overlap alone is not a true-positive label.

Truth is an input only to the `benchmark` rule. The default `all` target never
opens it. A maximum-cardinality one-to-one diagnostic matching avoids counting
one event multiple times against duplicated nearby truth records. All possible
matches and tiers remain in the JSON. With incomplete truth, no precision is
computed and unmatched calls remain unclassified.

## Ablations

Use independent named runs in the same configuration, sharing the same family
manifest. Compare error_rate 0.05/0.06/0.08 and strict/marker_assisted readability
with all other inputs fixed. Each run preserves input hashes and tool source
hashes. Do not sum events from different representations or branches without
sequence-aware deduplication. Study-level counts require a full rerun, not adding
individual rescued loci to historical totals.

The initial NA truth records informed development. HG002 short-indel threshold
extension and marker review followed inspection of gaps. Their results are
development/external comparison evidence, not a fully held-out blind benchmark.
For independent validation, freeze software and parameters before evaluating a
new family or a held-out set.
