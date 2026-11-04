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

**Stopped on BLK-025.** The first actual compatibility completion returned HTTP403
on4 November2026. The separately authorized updated-key check also returned403. A separately authorized third request also returned403. Three physical
requests across three consumed approvals, no automatic retry, no baseline started.
Retain all three unknown reservations, USD0.058950 total, despite account usage showing zero. All operational policies
above remain candidates; no baseline freeze or release exists. Read the
[verified stopping outcome](gpt4omini-openrouter-blocked-20261104.md).

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

`prior-preservation-authoritative-v2.json` retains both earlier inventories and pins
all1,534 older file contents. It reconciles the original tracked-source aliases
against the independently recorded clean pre-task Git commit; the earlier partial
snapshots and failed check remain preserved. All44 tracked-source aliases (30 support/config and14 frozen author/runtime) and
all61 symlink targets match the preservation anchor. The separate reconciliation
supplement records all three earlier-snapshot deltas against original Git bytes. The driver checks this frozen legacy checkout before each phase and
checks immutable legacy-file signatures at each work boundary. Do not advance the
preservation checkout while the historical source aliases depend on it.

The fresh compatibility plan/approval uses `compatibility-v2/`, retaining the
pre-transmission attempt rather than replacing or reusing its source binding.
This changes operational isolation only; prompts, schemas, generation/scoring
policies, population, provider route and financial caps are unchanged.


### Updated-key access check — 4 November2026

After the first403 and retained USD0.019650 reservation were reported, the user
updated the private API key and explicitly requested another attempt. This permits
one fresh exact metadata compatibility POST with a new immutable approval; retain
the original terminal phase/halt and full unknown reservation unchanged. The same
USD0.25 compatibility/USD5 cell caps apply cumulatively. Maximum cumulative
reservation for these two attempts is USD0.039300. No baseline release, individual
charge settlement, general terminal-state bypass or repeated retry is inferred.
Verify current private authentication, exact prior ledger snapshot/raw403/provenance,
reviewed source and independent Standards/Spec reviews before this one request.
A new failure stops; even a successful access check cannot release the baseline
while the earlier unknown exposure and outstanding release gates remain unresolved.


### Updated-key outcome — same prohibition; no baseline release

At06:49:31 UTC the new single metadata access check also returns HTTP403 with the
same provider Terms Of Service prohibition, no generation ID/output/usage and null
provider name. The fresh approval is consumed; no third request, continuation or
baseline is authorized. Both terminal phases/halts and all original rows remain.
The ledger now retains two full unknown reservations, USD0.039300 total. Read-only
account/key reads at06:50 UTC still show USD50/zero recorded usage; individual
charges remain unreconciled. Cell remainder USD4.960700 and usable campaign
remainder USD41.960700 are arithmetic ceilings, not execution authority; protected
USD8 remains untouched. BLK-025 stays Open. Read the
[complete outcome](gpt4omini-openrouter-blocked-20261104.md).


### One further explicit access check — 4 November2026

After both403 responses and USD0.039300 retained unknown exposure were reported,
the user explicitly requested one more attempt. Authorize exactly one original
metadata payload with the current private key and a fresh source-bound approval,
retaining both terminal phases/halts, original errors/raw responses and unknown
reservations. No key regeneration, model/provider/route/schema change or automatic
retry. Keep cumulative USD0.25 compatibility/USD5 cell caps and USD8 protected.
Maximum cumulative reservation is USD0.058950. Require exact two-phase ancestry,
prior raw403 evidence, private authentication and independent scoped reviews before
transmission. Either outcome leaves baseline release and charge adjudication closed.
This new grant is single-use and does not authorize a fourth request or another cell.


### Third access outcome — 4 November2026,15:08 HKT (07:08 UTC)

The freshly approved third metadata request at07:08:42 UTC returns the sameHTTP403
provider Terms Of Service prohibition, null provider name and no generation ID,
model/output/usage. Preserve `compatibility-v4/` approval/reviews/raw000003/error/
receipt/seal and halt. Exactly one new POST; three campaign POSTs total, no automatic
retry, no fourth request and no baseline. Source `56a1464` has scoped independent
Standards/Spec PASS,47 passing tests and actual-launcher success/denial mocks;
source fingerprint `a0ae8a73909ee5e7e8d6df0312893dd42ec356ccc76d8cb124fbd464d36abcbd`.
Both prior SQL histories match the frozen pre-third snapshot exactly.

All three phases are consumed/terminal. Three unknown full USD0.019650 reservations
remain held, USD0.058950 total. Final read-only account/key reads show USD50/zero
recorded usage; no individual charge is settled or released. Cell remainder
USD4.941050 and usable campaign remainder USD41.941050 are arithmetic ceilings,
not paid authority; USD8 remains protected. BLK-025 stays Open. No baseline freeze,
full-mode metrics, actual serving identity or paired-ablation readiness is claimed.
Provider/account clarification and request-level financial evidence remain needed;
no route/model/key workaround or further transmission is authorized by this grant.


### Final third-key access grant — 4 November2026

The user supplied a third private API key and explicitly requested one last attempt
after the three403 outcomes and USD0.058950 retained exposure were reported. Fresh
private authentication verifies a changed key, HTTP200 and zero key usage. Account
aggregate usage is now USD0.011651; the user confirms separate testing. Preserve
that evidence as an opening reconciliation offset, without assigning or settling any
earlier individual campaign charge or importing any external result/request.
Available prepaid credits are USD49.988349; USD8 remains protected.

Authorize exactly one fourth physical metadata POST, the identical original payload,
dated model/OpenAI-only routing/native schema and cumulative USD0.25 smoke/USD5 cell
caps. A distinct fresh approval must verify all three terminal parents, exact original
request,22 evidence hashes and independent scoped reviews. Retain all old phases,
errors, raw responses and reservations. Maximum campaign reservation after this
request is USD0.078600 (USD0.090251 including the external opening offset). This
single-use grant authorizes no fifth request, financial settlement, baseline release,
provider/model workaround, additional cell or contingency use.
