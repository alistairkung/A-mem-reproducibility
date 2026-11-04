# GPT-4o-mini via OpenRouter — first Full baseline

Authority: the user's 4 November 2026 handover, recorded in [decisions](decisions.md).
This is a separate reproduction campaign. Run1 and Run2 DeepSeek campaigns remain
immutable exploratory engineering evidence; no result, memory build or expenditure
is credited to this campaign.

## Scope and release gates

Campaign ID: `amem-gpt4omini-openrouter-20261104-v1`. All new local approvals,
requests/responses, caches, checkpoints, ledgers and cloud readbacks live under
`artifacts/gpt4omini/`. Only Full / conv-44 (675 original turns, 158 questions) is
authorized. The other eleven preselected cells are design records only. Retain
conv-44/49/50, four action configurations, original question ordering and references.

The user authorizes implementation, tests, independent Standards/Spec reviews,
focused PRs and normal merge, one bounded compatibility phase and one baseline
lineage including supported bounded continuations, followed by outcome PR/merge.
No routine intermediate approval is required. Stop for material scientific
deviation, unsupported route, unaffordability, unknown financial exposure or broken
provenance. No further cell, top-up or contingency expenditure is authorized.

Before baseline admission require four original-schema contracts, verified dated
model/provider/limits/prices, unchanged-author versus Full action-gate saved-response
equivalence, original malformed-decision fallback, exact stale-index/counter
restoration across two successive continuations, no implicit/gateway fallback
retries, isolated accounting/cache/provenance, real-runner Langfuse generation and
both saved-result Experiment readbacks, and traced/untraced equivalence. Run the
complete offline suite, archived reference/candidate replay and independent reviews.
Freeze reviewed source, configuration, assets, forecast, gate evidence and phase
authorization immutably before transmission.

## Native provider policy (candidate until compatibility freeze)

`https://openrouter.ai/api/v1/chat/completions`, exact
`openai/gpt-4o-mini-2024-07-18`; `OPENROUTER_API_KEY` is loaded privately from `.env`.
Use provider `order=["openai"]`, `only=["openai"]`, `allow_fallbacks=false`,
`require_parameters=true`. Preserve exact original system/user messages and
`response_format=json_schema`; no tools translation, thinking parameter, repair,
semantic retry, prompt transformation or model fallback. HTTPX transport makes one
physical request per admitted logical call, with retries disabled and redirects
disabled. Record actual provider, response model, fingerprint, IDs and raw bytes.

The 4 November free endpoint catalogue lists OpenAI, strict structured outputs,
128,000 context and 16,384 output tokens; USD0.15/M input, USD0.60/M output,
USD0.075/M cached input. Conservatively do not credit cache discounts. Authentication
and credit reads return HTTP200, USD50 total credits/zero usage; key USD50 remaining
and weekly reset. The durable local lifetime ceiling is independent of that reset.
Sources: [endpoint catalogue](https://openrouter.ai/api/v1/models/openai/gpt-4o-mini-2024-07-18/endpoints),
[routing](https://openrouter.ai/docs/guides/routing/provider-selection),
[native structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs).

Investigate 1,000-token metadata/query/answer and 4,096-token shared decision limits.
The latter is a prospective GPT-specific output policy, not Run2's 8,192-token
adaptation. The original decision echoes five neighbours' contexts/tags, making
1,000 a poor conservative bound in the preserved engineering evidence. Verify
representative large original prompts in the bounded compatibility phase before
freezing; disclose limits and uncertainty uniformly for all future conditions.
Temperature stays0.7 (category5 answer0.5), k=10, construction neighbours5,
counter/consolidation and original stale-index semantics unchanged. Strict original
schema validation has no DeepSeek D3a integer-string exception.

## Financial and recovery boundary

New campaign USD50 total, USD8 protected, USD42 usable; this sole cell including
compatibility is capped at USD5. Compatibility model charges are capped at USD0.25
and at most eight physical requests. The baseline has exactly1,666 nominal calls;
continuation never repeats a completed turn or question or resets any cap. Every
physical request reserves its full context/output price upper bound in a separate
durable SQLite ledger before HTTP. Settlement records reported usage/cost and an
upward-rounded no-cache conservative amount; raw bytes precede settlement. Missing
usage/cost, local persistence faults and unsupported transports stop with reservation
retained. Paid compatibility is charged to this same cell.

Only a fully received, settled shared-decision output exhaustion can checkpoint
after the unchanged original failed-evolution fallback, preserving the new note and
unchanged neighbours/counter/index. A normally finished malformed object uses only
the independently verified original fallback without accepting/repairing its JSON.
All other failures are terminal. Sequential immutable children verify ancestry,
source/config/data, exact ordered state and remaining calls/spending; no rebuilding.
Recovered completed lineages are Degraded. Unknown exposure is never adjudicated
using the historical BLK-022 exception.

## Observations and completion

Retain Langfuse5.1.0 and `run2-audit-essential-v1` as the already verified export
policy, with16-span batches and the existing serialized-size guard. New campaign,
run/phase and Experiment identities separate all evidence. Keep every generation,
action, retrieval, scoring output, failure/fallback and continuation; both complete
saved-result scoring views retain all metric scores. New-provider costs come from
the settled campaign ledger, not the historical DeepSeek observer rates. Read back
actual observations, Experiment items, scores and original QA trace associations.
Local raw audit records remain authoritative; successful flush is insufficient.

Completion requires675 ordered turns/158 ordered questions, exact memory/index/
counter verification, corrected/historical F1 and BLEU-1 with adversarial correctness
separate, both verified Experiments and generations, actual route/model identities,
reconciled OpenRouter charges/credits and unchanged prior evidence. Classify Clean
or Degraded from actual history; otherwise retain Incomplete and report the blocker.
Forecast the remaining eleven cells without running them. First paired-ablation
readiness is a report, not paid authority.

## Status

Engineering and offline verification in progress. No model request has been sent.
Free credential/model/credit evidence is under `artifacts/gpt4omini/verification/`.

## Historical regression fixture isolation

The preserved Run2 recovery tests intentionally reject added/changed scientific
source inventories. A new provider campaign must not become eligible for a consumed
DeepSeek migration merely to make historical tests pass. Their optional reviewed
source selector uses an exact pre-GPT checkout (`b8b3656`); all assertions, original
fixtures and production migration restrictions stay unchanged. Combine it with the
already documented immutable transport-stop and sequential evidence fixtures:

```sh
git worktree add --detach .worktrees/gpt4omini-legacy-source b8b3656f1342bceda4c79ffe7e824c1fc79afbab
AMEM_RUN2_REVIEWED_SOURCE_ROOT="$PWD/.worktrees/gpt4omini-legacy-source" \
AMEM_BLK022_EVIDENCE_ROOT="$PWD/artifacts/run2/reporting-recovery/historical-fixture" \
AMEM_RUN2_SEQUENTIAL_EVIDENCE_ROOT="$PWD/artifacts/run2/reporting-recovery/sequential-fixture" \
.venv/bin/pytest -q
```

The default-evidence and new-source rejection logs remain preserved. This selection
is offline test context only; it cannot authorize a historical phase or new model
request. A fresh clone without optional private historical evidence still runs its
portable tests and explicitly skips unavailable archives.

## Preservation anchor and isolated execution checkout

The pre-transmission audit found that a preserved synthetic Run2 workspace links
support files directly to the original research checkout. Changing that checkout
would change the fixture's visible source bytes. No OpenRouter request was admitted:
the original prepared approval remains unconsumed/ineligible, with no paid ledger.

Keep `/Users/alistair/projects/FTEC/A-mem-reproducibility` detached at the clean
pre-task `b8b3656f1342bceda4c79ffe7e824c1fc79afbab`. Run the new campaign from the
separate `.worktrees/gpt4omini-baseline` checkout, with physical new campaign
artifacts/ledger/cache there. The original `artifacts/gpt4omini` is a convenience
link to that new namespace; every older study artifact/link remains untouched.
Shared immutable assets and historical regression inputs are read-only links.

`prior-preservation-authoritative.json` retains both earlier inventories and pins
all1,534 older file contents. It reconciles the original tracked-source aliases
against the independently recorded clean pre-task Git commit; the earlier partial
snapshots and failed check remain preserved. All29 source aliases match original
Git bytes. The driver checks this frozen legacy checkout before each phase and
checks immutable legacy-file signatures at each work boundary. Do not advance the
preservation checkout while the historical source aliases depend on it.

The fresh compatibility plan/approval uses `compatibility-v2/`, retaining the
pre-transmission attempt rather than replacing or reusing its source binding.
This changes operational isolation only; prompts, schemas, generation/scoring
policies, population, provider route and financial caps are unchanged.
