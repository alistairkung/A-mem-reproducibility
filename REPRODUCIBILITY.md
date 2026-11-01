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

Compare those four JSON files with `manifests/`. Each question keeps its original conversation ID and
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

`run_manifest` accepts an injected agent factory/scorer for offline use. Default live construction
requires an explicit paid-authorization declaration; credentials alone cannot enable execution.
Only original full mode is runnable in this foundation. Other conditions and deterministic replay
are intentionally rejected until T6/T7. No live-experiment CLI is provided in T1–T4.

The original agent class is compiled unchanged from author source, avoiding module-level downloads.
The original memory system is bound temporarily to the isolated controller during construction.
Author scoring functions are compiled from their original definitions; observational exception hooks
identify failures that the author converts to zero. Numerical scoring expressions remain unchanged.

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

Both Standards and Spec reviews were performed. Review corrections preserve the SBERT-load fallback,
keep asset-network isolation active during execution, isolate observation failures from original behavior,
and share credential-field validation across provenance, artifacts and exports.

## T5 preflight and authorization requirements

T5 has not started. Offline success does not establish live beta compatibility.

1. Review this foundation and authorize any T5 preparation/execution separately.
2. Prepare the locked `author` runtime extra and verify local model/tokenizer files at the revisions in
   `config/assets.json`. Freeze NLTK resource checksums and confirm the installed BERTScore checkpoint.
   The author extra is resolved/locked but was not installed or exercised with real model assets here.
3. Validate a documented context-token counting method. The pinned DeepSeek tokenizer repository is a
   candidate; equivalence to the hosted model remains unverified. Label estimates honestly and resolve
   any requirement change before paid execution.
4. Set credentials privately in the process environment. No credential values belong in configs,
   commands, issues, logs or commits. Confirm provider version/fingerprint information at execution.
5. Approve a bounded compatibility/functional phase separately (provisional USD 1–2): four schema probes
   if required plus the 44-call fixture (48 nominal calls total when both are run), with bounded retries.
   Verify strict-schema acceptance/output reliability and preserve all responses and attempt costs.
6. Only after compatibility success, approve the complete conv-50 full-mode pilot separately
   (provisional USD 5–10; 1,544 nominal generation calls before retries).
7. Before paid execution, verify phase-specific spending/stop controls and account for unknown charges;
   the T1–T4 API authorization flag is not a budget-enforcement mechanism or proof of user approval.
8. Forecast incurred spending + remaining four-condition cost + USD 8 contingency within USD 50. Select
   all ten conversations or the exact fallback from costs alone before comparative performance review.
   If neither fits, stop. Extra repetitions, recovery/reruns and main-condition execution need approval.

No ablation gates, paid baseline, live Langfuse export, T6 replay engine or T5–T8 execution was performed.
The separate HW3 repository is untouched.
