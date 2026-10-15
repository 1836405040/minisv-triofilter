# Feature review map

The tool fork preserves `qinqian/minisv.py` history. Features form an ordered
stack so each PR can show only its incremental change. The first PR targets
upstream main. Dependent PRs target preceding feature branches in the fork;
after predecessors merge upstream, rebase and retarget subsequent work upstream.

| ID | Pull request | Feature |
|---|---|---|
| F01 | [Upstream #5](https://github.com/qinqian/minisv.py/pull/5) | TRGT parental-allele hypotheses and input preparation |
| F02 | [Fork #1](https://github.com/1836405040/minisv.py/pull/1) | Read-query coordinate constraints and molecule extraction |
| F03 | [Fork #2](https://github.com/1836405040/minisv.py/pull/2) | Local transmission models, finalization and strict review |
| F04 | [Fork #3](https://github.com/1836405040/minisv.py/pull/3) | Concrete DEL/INS templates including ≥30 bp indels |
| F05 | [Fork #4](https://github.com/1836405040/minisv.py/pull/4) | Marker-linked parental consensus fallback |
| F06 | [Fork #5](https://github.com/1836405040/minisv.py/pull/5) | Manifest, CLI, full pipeline and integration tests |

The locked tool commit is a review snapshot, not an upstream release. CI checks
each published PR; merging and release remain review decisions. This workflow
repository has its own feature PR and contains no copied calling implementation.

Additional structural review features:

| Feature | PR | Scope |
|---|---|---|
| F07 | [Fork #6](https://github.com/1836405040/minisv.py/pull/6) | Structural retention and interval lengths |
| F08 | [Fork #7](https://github.com/1836405040/minisv.py/pull/7) | INV/DUP/BND junction review |
