# Run2 real-runner observability verification

Verified3 November2026 against source fingerprint
`184544748e86f608286a031a86bd53519e5c95b7f6b3eee0ffae8e2ba2e6e2fe`.
These are labelled offline-model fixtures, not primary experimental results. No LLM network
request or paid provider probe was made. Langfuse uploads and readback used the configured project.
The separate release gates also pass:715 tests/92 subtests, both complete archive replays and clear
independent reviews. Read the [frozen campaign protocol](run2-protocol.md).

## Actual execution and cloud evidence

`artifacts/run2/gate-b/real-assets-8k-20261103-attempt1/` exercises the original author factory,
`run_manifest`, the frozen18-turn/four-question fixture, pinned local embedding/tokenizer/metric
assets and Run2's8,192/1,000 stage policy. HTTPX MockTransport captures44 synthetic provider responses.
Ordered uninstrumented and instrumented `ReplayController` executions then consume those exact
responses without HTTP. Normalized comparison views omit incidental UUIDs/access timestamps only;
notes, links, metadata, corpus/embedding order, retrieval, predictions and both scoring views match.
Raw evidence and provider-argument strings remain unchanged. An injected tracing-start failure
leaves the same complete memory/scoring outputs and produces an explicit observer-error receipt.

The real Langfuse SDK exports130 observations and56 scores. The modern API readback verifies every
expected observation/score ID, trace hierarchy, original turn/question identity, input/output,
safe wire request, generation settings, usage, cost and metadata. Saved corrected and historical
question results are imported once and read back through Experiments, including all metric values,
references and original predictions. No model or second evaluator runs during import.

- Local proofs: `real-assets-evidence.json`, `trace-capture.json`, `observations-verified.json`,
  `experiments-verified.json`, `trace-failure-evidence.json` and their hash-linked raw readbacks.
- Visible [corrected fixture experiment](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=ca7b19b790e6a949)
  and [historical fixture experiment](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=5b2b08b8f56cedab).

`artifacts/run2/gate-b/executor-8k-20261103-attempt2/` separately exercises the actual Run2 paid-phase
executor and durable permit with only mocked LLM transport, deterministic model-service dependencies
and a clearly labelled24-turn/one-question test partition. Temporary pytest overrides cannot pass
the production population/preflight guard. Two successive8,192-token `length` failures produce
Incomplete parents; exact-state continuations retain their stale index, original fallbacks and
quota history. The third segment completes Degraded. All50 synthetic calls are accounted for in
an isolated fixture ledger; all three phases have independently fetched observations, and the final
saved scoring views have verified Experiments. This is not study spending or a Run2 benchmark cell.
Read `executor-evidence.json` and its three immutable workspace phase receipts for the lineage.

## Investigated integration differences

The preliminary4,000-token direct-runner check remains under `engineering-4k-20261103/`; it is not
the final generation-policy gate. Session-filtered score reads returned no rows despite successful
ingestion. Exact score-ID queries retrieved all56 scores, so verification now uses bounded ID batches.

The first8,192-token executor fixture remains immutable at `executor-8k-20261103-attempt1/`.
Its two recoveries and observations verified, but final Experiments verification rejected a name
mismatch. The SDK's `ExperimentResult.name` identifies the logical group, while the modern API's
`experiments.name` is the SDK's distinct `run_name`. Correction `414b97b` records both and checks the
API against the exact run name. It does not guess names, alter results or reimport the failed fixture.
All fully indexed saved snapshots pass offline characterization; partially indexed snapshots still
reject. The fresh attempt2 verifies the correction against the project.

The verifier decodes only documented JSON transport containers/metadata leaves when the expected
value is not a string. Expected prediction and provider-argument strings remain exact. SDK5.1's
unexported trace-context seed is accepted only for API-classified logical roots; known child parents
remain exact. SDK flush alone never counts as visibility. Readback is bounded and saved; interrupted
imports are not automatically repeated.

## Execution safeguards and limitations

Tracing hooks are passive within the current memory/QA operation. Any observer failure is checked
at the next safe boundary and halts additional work. Missing cloud verification or saved-results
import prevents checkpoint/next-cell release. Local journals, state and spending remain authoritative.
Unknown usage is explicitly incomplete and retains its ledger reservation; no zero cost is invented.
Fixtures prove the integration and failure controls, not hosted DeepSeek reliability or future
Langfuse availability. Every real cell must independently reconcile actual cloud visibility.

Independent final audits resolve the runtime-wiring aspect of [BLK-011](blockers.md#blk-011) for Run2. It does not reconstruct missing Run1 traces or change Run1's historical limitation.
