# Langfuse readiness before the next paid phase

## Verified D9a saved-result import — 1 November 2026

After the successful `compatibility-d9a-20261101` fixture, the existing locked SDK 5.1.0 exporter
created two saved-result experiments and the modern CLI Observations API returned all eight question
traces. Condition/population/repetition, original question IDs, predictions, both scoring-policy IDs,
D3a/D9a policy metadata, source hash, original degraded status/deviation count and USD0.053118 phase
cost metadata were checked. No LLM evaluator or model call was made; the ledger and immutable phase
artifacts are unchanged. Import usage/cost fields are empty, with actual inference usage/cost in the
explicitly labelled original-phase metadata/local artifacts. Import timing is not inference timing.

- [Corrected experiment](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=a2ca1a936b9b2427)
- [Historical experiment](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=f00c6621e4195c75)

Safe local receipts: `artifacts/compatibility-d9a-langfuse-export.json` and
`artifacts/compatibility-d9a-langfuse-verified.json`; response headers and SDK project-key attributes
are excluded. This verifies the optional reporting path. BLK-011 remains Open because automatic
construction-time generation tracing is still unwired; local artifacts remain authoritative.
The following configuration/initial-failure notes are retained as history.

Checked 1 November 2026, Hong Kong time. Uses the existing locked **Langfuse Python 5.1.0**; no
dependency, `.env`, model/provider or evaluation change was made.

## Confirmed configuration and connectivity

The project's private `.env` already contains the required public/secret project keys and base URL.
The process environment does not shadow them with a different project. Values were read privately,
passed to the client/CLI in memory and never printed, committed or included in receipts. The base URL
was checked for HTTPS and absence of embedded credentials. CLI calls also received the documented host
alias privately. There is no need to paste keys into chat or commit another configuration file.

Using the [Langfuse skill](https://github.com/langfuse/skills/tree/main/skills/langfuse) and current
[SDK documentation](https://langfuse.com/docs/observability/sdk/overview):

1. CLI project-list authentication succeeded with the selected project keys.
2. SDK 5.1.0 created and flushed one synthetic span named
   `A-MEM/langfuse-configuration-smoke`, environment `configuration-preflight`.
3. The current observations API returned that exact span. Input/output, type and zero model usage
   were checked; the API's JSON-string input/output representation was decoded only for verification.

Trace ID: `a8e18a92ccdc5a873f595010f1e3c283`.
Observation ID: `56d4b434cfe14653`.
The span is **not a benchmark result**, contains no dataset/provider output, and invokes no LLM.
Its input states the configuration-check purpose; output records the successful probe. Model and
usage/cost fields are empty, rather than fabricated zero-token generation statistics.

Safe local receipts: `artifacts/blk007-offline-investigation/langfuse-smoke.json`,
`langfuse-readback-raw.json` and `langfuse-verified.json` in the same directory. They contain no keys
or private connection settings. These ignored files are local evidence, not public download links.

## Why the first fixture did not appear

The T4 [reporting module](../../amem_repro/reporting.py) implements an optional, explicitly authorized
**saved QA experiment import**. It does not automatically instrument an OpenAI client or the memory
loop. The T5 entrypoint (`502b376:amem_repro/phases.py`) neither creates a Langfuse observation nor calls
that exporter. Credentials alone cannot activate this path. In addition, the incomplete fixture
produced zero QA rows, while the exporter requires nonempty saved question results.

This is a missing runtime connection (BLK-011), not a failed-authentication finding. A configuration
probe now reaches Langfuse, but automatic tracing of the next T5 model call is **not yet wired**.
Old failure artifacts were not altered or exported to manufacture prior traces.

## Smallest runtime connection proposed for review

Keep the current SDK/client, provider transport, retries and author evaluator. Add an explicit optional
observer at the existing T5 orchestration/controller seam, rather than replacing the OpenAI SDK with
an auto-instrumented client during compatibility investigation:

- Load only the allowed Langfuse variables from the chosen private configuration **before** creating
  its client. Preserve the existing deliberate control of dotenv/model-library imports.
- Start one actual phase span before execution. Wrap the unchanged `get_completion` call with an
  explicitly populated generation observation, so failed construction calls are captured before QA.
  Delegate once; the original SDK still owns its bounded transport retries.
- Use the existing sanitized completion event for model/settings, raw versus effective schema status,
  attempt counts, usage, returned fingerprint and original latency. Record budget-blocked calls as
  untransmitted; never count them as paid attempts or hide failed charges.
- Record error **types/categories**, not exception text or headers. Handle `BudgetStop` in finalization
  so the trace closes, but re-raise it unchanged. Observability failures must not repair or retry
  model output or change original failure/counter semantics.
- Flush in `finally`, including incomplete runs. Keep local artifacts and the SQLite budget ledger
  authoritative. Persist trace IDs and observer failures in a new run's artifacts.
- After QA exists, use the existing author-derived corrected/historical experiment importer, retaining
  condition, population, full manifest hash, repetition, run ID and scoring-policy identity. No LLM
  judge, new metric or re-generation is needed.

The two scoring views reference one set of model generations. Do not count their experiment imports
as two sets of inference charges; preserve the ledger's actual attempts and its explicitly conservative
cost basis. Include the proposed provider-contract policy as a separate metadata/identity dimension.

Bind an observation-policy ID to the new run metadata. Use actual inference timing for live generation
observations; an import trace must remain labelled as import timing. Do not turn a callback emitted
after completion into a misleading near-zero-latency inference observation.

Offline checks before the next paid phase: mocked SDK tracing captures success, provider failure and
budget stop; request arguments and call counts stay identical; a broken observer does not affect
original outputs; secrets are absent; finalization flushes; and study identities remain distinct.
Then repeat a **non-LLM** trace smoke and read it back. The synthetic smoke here verifies connectivity,
not that this proposed future runner connection is already implemented.

No automatic model execution, historic data export or compatibility acceptance is authorized by
Langfuse readiness. BLK-007 remains unresolved, and paid testing/recovery still needs separate approval.
