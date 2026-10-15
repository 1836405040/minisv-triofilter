# Feature review map

The tool fork preserves `qinqian/minisv.py` history. Features form an ordered
stack so each PR can show only its incremental change. The first PR targets
upstream main. Dependent PRs target preceding feature branches in the fork;
after predecessors merge upstream, rebase and retarget subsequent work upstream.

| ID | Branch | Feature |
|---|---|---|
| F01 | feature/01-trgt-candidates | TRGT parental-allele hypotheses and input preparation |
| F02 | feature/02-read-locus | Read-query coordinate constraints and molecule extraction |
| F03 | feature/03-local-alleles | Local transmission models, finalization and strict review |
| F04 | feature/04-event-templates | Concrete DEL/INS templates including ≥30 bp indels |
| F05 | feature/05-marker-readability | Marker-linked parental consensus fallback |
| F06 | feature/06-denovo-pipeline | Manifest, CLI, full pipeline and integration tests |

The locked tool commit is a review snapshot, not an upstream release. CI checks
each published PR; merging and release remain review decisions. This workflow
repository has its own feature PR and contains no copied calling implementation.
