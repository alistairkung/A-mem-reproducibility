# Implementation tickets

Protocol: [experimental-protocol.md](experimental-protocol.md).
Decision record: [decisions.md](decisions.md).
Created 1 November 2026; every issue is open and unstarted.

Issue creation is planning authorization only. Implementation, dependency installation, commits/pushes,
paid API calls and paid recovery remain subject to separate user approval. A closed dependency does
not itself authorize a blocked ticket's execution. T5 and T8 require explicit paid-phase approvals.

## Tracker and dependency map

| Ticket | GitHub issue / deliverable | Direct blockers |
| --- | --- | --- |
| T1 | [#1: Freeze study inputs, manifests and environment](https://github.com/alistairkung/A-mem-reproducibility/issues/1) | None; implementation approval still required |
| T2 | [#2: Add isolated DeepSeek strict-output adapter and offline contracts](https://github.com/alistairkung/A-mem-reproducibility/issues/2) | [T1](https://github.com/alistairkung/A-mem-reproducibility/issues/1) |
| T3 | [#3: Add provenance-verified run artifacts, caches and snapshots](https://github.com/alistairkung/A-mem-reproducibility/issues/3) | [T1](https://github.com/alistairkung/A-mem-reproducibility/issues/1) |
| T4 | [#4: Capture costs and retrieval measurements; export dual scoring to Langfuse](https://github.com/alistairkung/A-mem-reproducibility/issues/4) | [T2](https://github.com/alistairkung/A-mem-reproducibility/issues/2), [T3](https://github.com/alistairkung/A-mem-reproducibility/issues/3) |
| T5 | [#5: Run separately approved compatibility, pilot and original full-mode baseline](https://github.com/alistairkung/A-mem-reproducibility/issues/5) | [T1](https://github.com/alistairkung/A-mem-reproducibility/issues/1), [T2](https://github.com/alistairkung/A-mem-reproducibility/issues/2), [T3](https://github.com/alistairkung/A-mem-reproducibility/issues/3), [T4](https://github.com/alistairkung/A-mem-reproducibility/issues/4) |
| T6 | [#6: Establish deterministic replay regression from the archived baseline](https://github.com/alistairkung/A-mem-reproducibility/issues/6) | [T5](https://github.com/alistairkung/A-mem-reproducibility/issues/5) |
| T7 | [#7: Gate strengthening and neighbor updates independently with full-mode equivalence](https://github.com/alistairkung/A-mem-reproducibility/issues/7) | [T6](https://github.com/alistairkung/A-mem-reproducibility/issues/6) |
| T8 | [#8: Execute approved remaining conditions and assemble comparative evidence](https://github.com/alistairkung/A-mem-reproducibility/issues/8) | [T4](https://github.com/alistairkung/A-mem-reproducibility/issues/4), [T5](https://github.com/alistairkung/A-mem-reproducibility/issues/5), [T7](https://github.com/alistairkung/A-mem-reproducibility/issues/7) |

The issues contain the acceptance checklists and native GitHub blocking relationships, mirrored in
their bodies. Their self-contained criteria are reviewable before these local documents are committed.

## Execution order

T1 enables T2 and T3. T4 follows both; T5 requires all offline preparation and separate paid approvals.
Archive the selected original full-mode baseline in T5 before T6 replay characterization and T7 action
refactoring. T8 follows equivalence and reporting readiness, with its own execution approval.
Valid archived full-mode results can supply that condition; avoid unnecessary duplicated spending.

No extra framework, alternative scorer, robust-pipeline substitution, retrieval tuning or context
transformation is part of these tickets. Keep each implementation diff small and independently reviewable.
