# T6 deterministic replay gate

Authority: [2 November T6 authorization](decisions.md#authorization--t6-deterministic-replay-on-the-completed-conv-50-lineage),
[issue #6](https://github.com/alistairkung/A-mem-reproducibility/issues/6). No paid calls or T7 work.
Baseline: [verified conv-50 lineage](t5-conv50-baseline-20261101.md), frozen author `f9a173d`.

## Architecture

```text
immutable captured generation records
  -> ReplayController (ordered request/settings checks, no SDK/transport)
  -> existing DeepSeekController and original strict contracts/D3a validation
  -> unchanged author memory/answer methods
  -> comparison copies, historical checkpoints and T6 state-hash oracle
```

`amem_repro/replay.py` supplies a drop-in `get_completion` controller. The pure local client compares
the complete forced-function request, including messages, schema, model, thinking, temperature and
stage-specific output allowance. It returns the captured provider object to the existing adapter,
which returns the exact argument string or raises the original `AdapterError`. The observed stage,
settings, validation/audit outcome and returned bytes must match the recording. No paid factory,
credentials, SDK, HTTP transport or permit is created. The entire archive command also denies sockets.

Missing, extra, reordered and mismatched requests raise terminal `ReplayMismatch`, deliberately outside
`Exception` so original fallback handlers and observational hooks cannot absorb a regression. A recorded
provider rejection remains an ordinary adapter exception, preserving the original unevolved-note
fallback and counter. This is replay control, not a new provider acceptance policy.

`amem_repro/replay_baseline.py` verifies the archived parent/child inventories, lineage, dataset,
scientific source hashes and complete cache. It reuses `run_manifest`, the original agent binding and
author scorer, with an explicit `deterministic_replay` execution type and separate output/cache namespace.
It replays only 1,544 transmitted logical calls. The parent's subsequent blocked metadata event has no
provider response and is excluded; the first child metadata response resumes the same logical trajectory.
The original parent abort/blocked-event evidence is retained unchanged, not presented as a new replayed call.

The archive gate checks every insertion against the frozen T6 hash oracle, every recorded outcome,
all five consolidations, the full historical states at263/568, all204 retrieval observations/contexts,
original prompts/predictions/QA identities, primary author metrics and both rescoring views. No floating
tolerance or rounding is applied. The observed source environment uses pinned local CPU embeddings.
`factory_builder` is an explicit existing-agent-factory seam for future T7 full-mode comparison; it
does not load arbitrary plugins or implement switches. Candidate work must still preserve the frozen
author, provider and scorer sources. T7 must inject its full-mode candidate rather than merely rerun
the reference implementation and claim candidate equivalence.

## Reference data and normalisation

- `tests/fixtures/conv50-opening-replay.json`: four exact archived completions for the first two real
  turns. Original event hashes and parent receipt identify their origin. Its comparison states were
  generated offline through frozen author code with a deterministic **2D test embedding stub**;
  they are labelled as such, not represented as historical embeddings or per-insertion snapshots.
- `tests/fixtures/conv50-replay-state-hashes.json`: 568 compact comparison hashes from the first
  complete frozen-author replay, anchored to parent/child receipts, author revision and dataset hash.
  These are **T6-derived regression oracles**, not historical per-step state captures. A fresh process
  must reproduce them exactly, so future transient state/vector changes cannot hide behind consolidation.
- Synthetic unit fixtures are explicitly labelled and cover action sets, negative/positive/no-action
  decisions, directed duplicate links, counter boundaries, malformed JSON and answer categories.
  No synthetic response is described as a past DeepSeek completion.

`memory_view` copies snapshots, maps generated note UUIDs and changed-note IDs to insertion indices,
and removes only note `last_accessed` wall-clock values. Dataset timestamps, text, tags, keywords,
links/order, embeddings/dtype/rows and corpus remain exact. Raw artifacts are unchanged. Build failure
provenance is distinct from memory state; original provider rejection and audits are checked through
the replay controller and retained baseline archive, while replay status must remain degraded.

## T7 regression commands

Portable offline gate, requiring the locked test/author dependencies but no API credentials or private runs:

```sh
.venv/bin/pytest tests/test_replay.py tests/test_checkpoint.py tests/test_type_compatibility_characterization.py -q
```

On the research workspace, the complete baseline gate additionally requires the preserved local T5
artifacts/cache and pinned assets. Use a fresh output directory on every invocation:

```sh
.venv/bin/python -m amem_repro.replay_baseline \
  --assets artifacts/assets \
  --output artifacts/replays/t7-reference-check
```

For T7 candidate tests, call `replay_baseline(..., factory_builder=full_mode_candidate_builder)` with
the same controller/counter interfaces, reference fixtures and unchanged oracle. Compare the candidate
against the frozen per-insertion state hashes and all historical observations. Add this invocation to
T7's regression tests; the CLI above runs the unchanged reference by default. Do not regenerate golden
states or rewrite recordings to make a candidate pass. A mismatch is evidence requiring investigation.

## Coverage and limits

Coverage includes initial metadata, all four decision action sets, valid negatives/positive no-ops,
strengthening's tag enrichment, neighbour updates, ordered directed duplicate links, original failure
fallback, counter99→100 and consolidation, stale index restoration, linked context expansion, category
1–5 original answer prompts/scoring, strict request matching and exhaustion/extra-request rejection.

The archive lacks historical full states at every insertion and historical query vectors (BLK-015).
The two stored checkpoints, all requests/outcomes and final retrieval/predictions constrain the replay;
T6-derived hashes then freeze intermediate reference execution. Pinned local CPU recomputation matches
historical float32 state exactly on this environment. Another platform/library/device may differ and
must fail or be investigated; the gate does not silently substitute tolerances or cached neighbours.
Portable stub-embedding tests do not establish equality of arbitrary real embedding implementations.

Replay supports this no-retry baseline, not simulation of arbitrary transport retries or SDK/network
failure histories. Missing raw artifacts cause the archive command to fail, not generate new responses.
The portable suite remains usable from a fresh clone; archive validation requires the separately
preserved research artifacts. Replay is not an independent stochastic trial or a benchmark repetition.
All generated outputs live in a new `artifacts/replays/` directory; original runs/cache/ledger are
protected by final hash checks. Existing directories and baseline run/cache output locations are refused.
