# FTEC5660 submission checklist

Deadline supplied by the authoritative brief:13 November2026 at midnight, Hong Kong time.
This checklist records preparation, not submission or a completed recording.

- [x] Runnable frozen author implementation/revision and released dataset hash identified.
- [x] At least one released full-mode behaviour reproduced: conv-50 baseline and exact offline replay.
- [x] Isolated modification implemented: independent strengthening/neighbour-update guards.
- [x] Full-mode candidate equivalence and action-matrix regression evidence retained.
- [x] Fixed, performance-independent fallback and one-build-per-cell protocol recorded.
- [x] Research challenges, failed attempts and resolutions retained in [blockers](docs/reproducibility/blockers.md).
- [ ] Complete selected-scope full-mode baseline (conv-49/conv-50 verified; conv-44 Incomplete, BLK-013).
- [ ] Execute/verify T8 ablation cells, or obtain an explicit revised protocol after a blocker.
- [ ] Verify paired558-question coverage per condition, both author scoring views and separate c5 correctness.
- [ ] Reconcile cumulative ledger, retries, partial failures, stage usage and retained decision overhead.
- [ ] Export verified local comparisons and Langfuse saved-result experiments with unique identities.
- [ ] Finalize [report material](docs/reproducibility/study-report.md), format and verify at most10 pages.
- [ ] Finish GitHub PR review and obtain any necessary merge/publication approval.
- [ ] Verify reproducible setup/commands, artifact inventory and credentials exclusion.
- [ ] Record presentation using the outline below; verify duration at most15 minutes.
- [ ] Upload report/repository link/presentation according to the course submission instructions.

Current status: conv-49/conv-50 completed Degraded and are unchanged. The full conv-44 parent and
one authorized child are Incomplete after two4,000-token exhaustions.610 total notes/counter607,
zero of158 QA; cumulative USD8.407857/4,240 settled requests, zero unknown charges. All paid grants
are consumed; no restart, second recovery or ablation is authorized. First-ablation readiness remains
blocked; no balanced-study or submission completion is claimed. See
[the verified child failure](docs/reproducibility/t8-conv44-recovery-incomplete-20261103.md).

## Presentation outline — target14 minutes30 seconds

| Time | Segment | Evidence to show |
| --- | --- | --- |
|0:00–1:00 | Research question and contribution | Four-condition action matrix; evolution-only question |
|1:00–2:30 | Paper versus released implementation | Frozen revision, missing ablations, data/retrieval differences |
|2:30–4:00 | Controlled protocol | DeepSeek/D3a/D9a, fixed population, cache/build isolation |
|4:00–6:00 | Faithfulness and modification | Exactly two gates; counter99→100; actual candidate replay |
|6:00–8:00 | Debug diary | Raw contract failures, rejected repairs, checkpoint and artifact-validation investigation |
|8:00–10:30 | Verified results | Corrected per-category F1/BLEU-1, separate c5 correctness; clearly label any missing cells |
|10:30–12:00 | Cost and observability | Durable ledger, retries/overhead, point forecast versus hard caps, saved Langfuse imports |
|12:00–13:30 | Validity limits | One repetition, stochastic/provider effects, cross-model/population/scoring limitations |
|13:30–14:30 | Findings and reproducibility | Supported conclusions only; repository instructions and evidence inventory |

Before recording, replace pending-result segments with actual verified findings. If collection is
incomplete, explain the blocker and incurred costs instead of presenting planned results as observed.
