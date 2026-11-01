# Reproducibility foundation (T1–T4)

The approved study is defined in [the frozen protocol](docs/reproducibility/experimental-protocol.md),
[decision log](docs/reproducibility/decisions.md) and [ticket index](docs/reproducibility/implementation-tickets.md).
This foundation adds isolated support code around the author release `f9a173d`. The original Python,
shell, dataset, requirements and README files remain unchanged.

## Install and check offline behavior

Use Python 3.11 or 3.12 with uv. The lock includes the author runtime as an optional extra; basic tests
need only the provider, reporting and test extras. Installing these packages does not download models.

```sh
uv sync --frozen --python 3.11 --extra test --extra provider --extra reporting
uv run --frozen --extra test --extra provider --extra reporting python -m pytest -q
uv lock --check
```

Tests prohibit socket connections, inject deterministic providers/model boundaries, and exercise the
pinned OpenAI SDK through HTTPX MockTransport. They do not consume `.env` or create live clients.
Pytest collects only `tests/`, avoiding the authors' model-initializing evaluation entrypoints.

Regenerate and compare manifests without importing author model code:

```sh
uv run --frozen python -m amem_repro.manifests --output /tmp/amem-manifests
```

Compare those four JSON files with `manifests/`. They are compact version-2 selections: frozen dataset
hash, selection configuration, original conversation/sample IDs, explicit source QA indices and session
selection. They omit duplicated reference answers, evidence and turn records. `expand_manifest` verifies
the entire dataset SHA-256 AND the approved selection before reconstructing version-1 runtime records.
Each compact file also records the canonical expanded-manifest SHA-256. Regression tests reproduce the
exact four pre-compaction hashes; source QA identities, references, order and cache semantics are preserved.
Existing expanded callers remain supported. Each question keeps its original conversation ID and
zero-based source QA index. Source verification is available as
`amem_repro.config.source_fingerprint(repo_root)`; any changed frozen author file is rejected.

## Component map

| Component | Interface and purpose |
| --- | --- |
| `config.py`, `manifests.py` | Frozen configuration, secret-free fingerprints and source identities |
| `contracts.py`, `adapter.py` | Exact schema extraction, strict-function translation, bounded SDK attempts |
| `artifacts.py`, `runner.py`, `author.py` | Atomic verified caches, durable events, original agent orchestration |
| `measurements.py` | Passive retrieval counts, local action timings and attempt-aware usage estimates |
| `scoring.py` | Original author scoring functions, metric-failure notices and immutable dual rescoring |
| `reporting.py` | Local JSON/CSV and optional import of saved results into Langfuse Experiments |
| `preflight.py`, `budget.py`, `phases.py`, `forecast.py` | Verified local assets, durable spending permits, separately approved T5 phases and cost-only forecasts |

`run_manifest` accepts an injected agent factory/scorer for offline use. Default live construction
remains disabled. A Boolean authorization flag cannot create a real transport or live agent. T5's
`phases` entrypoint binds the original agent to a durable, explicitly approved spending permit;
credentials alone cannot enable execution. Explicit MockTransport remains available for offline tests.
Only original full mode is runnable in this foundation. Other conditions and deterministic replay
are intentionally rejected until T6/T7. No live-experiment CLI is provided in T1–T4.

AST loading is deliberately narrow: direct author imports initialize/download models and NLTK resources.
Every AST loader verifies the exact bytes against the frozen Git blob before parsing/compiling, including
standalone schema/agent loaders. Changed source is rejected before provider invocation. The original
agent class is compiled unchanged, avoiding module-level downloads.
The original memory system is bound temporarily to the isolated controller during construction.
Author scoring functions are compiled from their original definitions; observational exception hooks
identify failures that the author converts to zero. Numerical scoring expressions remain unchanged.
Paired tests compare instrumented functions with uninstrumented frozen functions for normal/empty answers,
category-5 corrected/legacy references, metric exceptions and aggregates: only diagnostic notices differ.

Retrieval observers intercept the existing search rather than issue another search or transform text.
Local strengthening/update timing uses passive Python line tracing of the frozen action branches;
it includes tracing overhead, requires serial execution, and rejects an already occupied tracing hook.
Observer callback errors do not change the author's action result. Both asset initialization and
execution run with Hugging Face/Transformers offline flags, restoring prior environment values.

## Saved-output reporting

Once verified local scoring assets exist, `AuthorScorer` and `rescore_records` produce corrected and
legacy views from saved question records. `write_tables` writes JSON plus question/aggregate CSV with
scoring-policy IDs. Predictions and reference inputs are preserved; no generation is involved.

`export_experiments` defaults to refusing upload. An explicitly authorized export uses the pinned
Langfuse SDK, returns saved predictions/scores, and labels observations `execution_mode=imported_results`.
Export metadata must include condition, population, full expanded-manifest SHA-256, nonnegative build
repetition and original run ID; missing/invalid identity is rejected before SDK initialization. Experiment
names include condition/population/scoring policy; run names include repetition and a full hash of all five
study dimensions plus policy. Full identity is retained in both run and item metadata.
Its timing describes the import, not original inference. Original IDs, configuration, usage and latency
remain in run artifacts/metadata. Failed metrics remain labelled; degraded runs are not silently dropped.

Usage accounting prefers physical attempt records and never adds the duplicate logical usage summary.
Missing usage/cost remains unknown. Supplied prices generate explicitly identified estimates and do not
represent a billing guarantee or assume provider-cache discounts. Local actions incur no separate LLM call.

## Validation and ticket mapping

Each commit references its ticket: T1/#1, T2/#2, T3/#3 and T4/#4. Use
`git log --oneline --reverse f9a173d..HEAD` to inspect the four scoped commits.

| Checkpoint | Executed checks | Result |
| --- | --- | --- |
| T1 | config/manifests tests; deterministic regeneration; frozen lock check | 7 tests passed; all four manifests byte-identical; 137 packages resolved |
| T2 | cumulative T1 + adapter/contracts tests | 18 tests and 7 subtests passed |
| T3 | cumulative T1–T3 tests | 28 tests and 7 subtests passed |
| T4 | complete offline suite | 43 tests and 7 subtests passed |

The end-to-end mocked smoke exercises original note/evolution/retrieval/answer methods with 18 notes
and four questions: exactly 44 generation calls, 18 executed strengthening and neighbor-update branches,
four retrieval observations and no additional generation during dual rescoring.

Focused follow-up validation: 54 tests and 32 subtests passed. Compact-manifest expansion reproduces
all four pre-compaction hashes. Direct AST mutation, instrumented/original scoring parity, reporting
identity separation and live-fuse regression tests pass with network connections denied.

Both Standards and Spec reviews were performed. Review corrections preserve the SBERT-load fallback,
keep asset-network isolation active during execution, isolate observation failures from original behavior,
and share credential-field validation across provenance, artifacts and exports.

## T5 preparation and paid-phase gates

T5 implementation/preflight was authorized on 1 November 2026. The frozen research decisions are
unchanged. See the [T5 runbook](docs/reproducibility/t5-runbook.md) for reproducible asset preparation,
offline checks, unapproved execution plans and the acceptance-criteria status.

The real local embedding and author-metric smoke passes with sockets disabled. The separately approved
first paid compatibility attempt stopped on a provider schema violation after ten requests; see the
[attempt report](docs/reproducibility/t5-compatibility-20261101.md). Compatibility has not passed and
tokenizer parity remains unverified. No pilot, baseline, ablation gate, live Langfuse export or T6 replay
was executed. The separate HW3 repository is untouched.
