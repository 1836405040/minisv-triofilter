# Minisv Triofilter

Reproducible family de novo SV and indel workflows, benchmarking, and analysis.

The algorithm implementation is developed in feature branches of the
[Minisv upstream fork](https://github.com/1836405040/minisv.py), preserving
[upstream history](https://github.com/qinqian/minisv.py). This repository calls
a pinned tool commit; it does not vendor Minisv source code.

## Install

Use Linux or WSL2, Python 3.12, Git and minimap2 **2.31-r1302**.

```bash
git clone https://github.com/1836405040/minisv-triofilter.git
cd minisv-triofilter
# Until the workflow PR is merged:
git switch feature/reproducible-trio-workflow
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock.txt
curl -fL --retry 3 https://github.com/lh3/minimap2/releases/download/v2.31/minimap2-2.31_x64-linux.tar.bz2 -o /tmp/minimap2.tar.bz2
tar -xjf /tmp/minimap2.tar.bz2 -C /tmp
install /tmp/minimap2-2.31_x64-linux/minimap2 .venv/bin/minimap2
```

`requirements.txt` records direct dependencies; `requirements.lock.txt` pins
the complete Linux/Python 3.12 environment resolved in the passing CI run.
Preflight verifies the installed tool commit and minimap2 version, hashes every
declared data input, and saves the resolved Python environment. Hashing large
BAMs is deliberately a separate cached rule. Archive that environment with a
run when comparing results across machines.

## Run the synthetic example

```bash
python tests/make_demo.py
bash scripts/run.sh demo/config.yaml --dry-run
bash scripts/run.sh demo/config.yaml
bash scripts/run.sh demo/config.yaml benchmark_all
python tests/check_demo.py
```

This example creates indexed BAMs and local allele evidence for a small synthetic
family with a 30 bp indel and a 60 bp SV. It runs the actual pinned Minisv family
command at both minimum lengths and checks high-confidence output, class labels,
provenance, and one-to-one diagnostic truth matching. No real sample download is
required. Fresh caller-to-parent alignment is tested in the tool's integration CI.

## Run a family

1. Prepare an indexed reference, three or more HiFi BAMs, parental haplotype
   assemblies, caller VCFs with RNAMES and TRGT genotype/spanning files.
2. Copy `config/families/HG002.json` or `NA.json`, replacing all `/path/to/`
   entries with local paths. Reference and BAM contigs must agree.
3. Copy `config/example.yaml`. Set a unique run ID, manifest, minimum length,
   sequence tolerance, threads and memory. Paths resolve from the invocation
   directory; use absolute data paths for production runs.
4. Run `bash scripts/run.sh config/example.yaml --dry-run`, inspect the DAG,
   then run without `--dry-run`.

```text
prepared family inputs
       |
input hashes + pinned-tool verification
       |
Minisv family workflow
  candidate union -> read-local C3 / complete local alleles
  -> event review -> optional marker-assisted parental readability
       |
reviewed JSONL -> TSV export + stratified summary
       |
optional post-discovery benchmark (separate truth input)
```

The Snakefile owns input dependencies, family jobs, exports and benchmarking;
the tool owns its algorithm stages and per-stage audit. This version starts
from prepared caller/TRGT/assembly inputs, rather than launching those upstream
programs. Cached local/C3 evidence can be declared explicitly in the manifest.

### SV and indel settings

Use `minimum_variant_length: 50` for the SV analysis and `30` for combined
SV/indel analysis. The tool labels 30–49 bp as `de_novo_indel` and ≥50 bp as
`de_novo_SV`. Use distinct run IDs for each setting or ablation. The default
sequence tolerance is 0.08; it is not a posterior probability or an FP rate.

Confidence remains strict. `parent_readability_policy: marker_assisted` enables
the concrete-INS fallback; `strict` reproduces the original edit-margin audit.
The fallback requires four projected parental assembly paths, parental BAM
HP/PS tags, direct high-quality marker linkage, and consistent full/strand
consensuses. All other conflicts remain blocking. Missing evidence stays
unresolved. C3 alone does not confer high confidence.

## Outputs and reruns

| Output | Contents |
|---|---|
| `results/<run>/provenance.inputs.json` | Full input SHA256, package environment, tool commit |
| `results/<run>/calls/` | Tool tiers, original strict audit, marker audit, stage status, source provenance |
| `results/<run>/events.tsv` | Compact per-event export |
| `results/<run>/summary.tsv` | Counts by sample, SV/indel class, tier and coordinate basis |
| `results/<run>/benchmark.json` | Optional diagnostic truth matches, including ambiguous matches |
| `logs/<run>/` | Commands' output and family resource measurements |
| `results/<run>/.attempts/` | Original launch configuration and failed attempts |

Snakemake skips completed unchanged rules. A failed family job retries in a
fresh attempt directory; it does not resume an incomplete internal tool stage.
Use a new run ID when changing parameters or tool versions to preserve the old
experiment. Do not force reruns into an archived result directory: Snakemake
may remove declared outputs when rerunning a rule.

## Benchmarking and analysis

See [benchmark contracts](docs/BENCHMARKING.md) and
[NA/HG002 study configuration](docs/DATASETS.md). Truth is declared only under
`benchmarks` and is not a dependency of discovery. The lightweight matcher
requires the same sample, chromosome, event type and coordinate basis, with
explicit position/length tolerances, full-interval mask exclusion and one-to-one
assignment. It reports diagnostic compatibility; unmatched candidates are not
automatically false positives. A sequence-aware benchmark is a separate next
analysis step.

## Development and CI

GitHub Actions has separate **unit** and **integration** jobs. Unit tests exercise
configuration isolation, masks, representation bases and duplicate matching.
Integration CI executes Snakemake on generated BAMs at 30/50 bp, checks outputs,
and verifies a second dry run has no work. Synthetic outputs/logs are uploaded
as CI artifacts. No NA/HG002 BAMs, read names or private server paths are stored.

Changes use feature branches and PRs. Algorithm features belong to the
upstream-derived tool fork; workflow/analysis changes belong here. See
[the feature review map](docs/FEATURE_REVIEW.md). No PR is automatically merged.

## Structural candidate review

The pinned tool includes automatic INV/DUP/BND junction review in the family
pipeline. Supply original caller VCFs to recover types removed by older input
adapters. Set `structural_exclude_bed` in the family manifest to exclude
centromeric intervals; the mask is tracked as an input dependency.

Structural evidence is retained in `calls/structural_reviewed.jsonl` and
unresolved records in `calls/structural_unresolved.jsonl`. These experimental
models do not automatically assign high confidence. The diagnostic benchmark
currently supports INS/DEL only and explicitly reports unsupported structural
event IDs and truth rows instead of treating them as misses or false positives.
