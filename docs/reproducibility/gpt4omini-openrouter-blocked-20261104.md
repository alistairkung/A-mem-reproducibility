# GPT-4o-mini OpenRouter compatibility stop — 4 November2026

## Outcome and scope

The first live compatibility completion was rejected with HTTP403. **No GPT-4o-mini
Full/conv-44 baseline has started:0/675 turns and0/158 questions.** Corrected and
historical F1/BLEU-1 and adversarial correctness are unavailable. The compatibility
phase is Incomplete; Clean/Degraded baseline classification does not apply.
BLK-025 is Open. The updated-key access check is recorded separately below.

Campaign `amem-gpt4omini-openrouter-20261104-v1` is separate from all DeepSeek work.
Only Full/conv-44 was granted. Conv-49/50 and all four configurations remain in the
frozen design; none of the other eleven cells has run. Prior results are engineering
evidence only, with no memory, prediction, metric or charge imported as GPT results.

## Provider verification and candidate configuration

Private authentication, key and credit GETs returned HTTP200. The dated endpoint
catalogue advertised `openai/gpt-4o-mini-2024-07-18`, OpenAI structured outputs,
128,000 context/16,384 maximum output tokens and USD0.15/M input/USD0.60/M output
(USD0.075/M cached input; no cache discount credited to conservative accounting).
Catalogue support is distinct from actual access, actual routing and serving identity.
See the [OpenRouter endpoint catalogue](https://openrouter.ai/api/v1/models/openai/gpt-4o-mini-2024-07-18/endpoints).

The exact request uses `https://openrouter.ai/api/v1/chat/completions`, original
native `response_format=json_schema`, OpenAI `order`/`only`, disabled fallbacks,
required parameters, HTTPX retries0 and redirectsfalse. No DeepSeek forced-function
translation, integer-string exception, repair or semantic retry is used.
Candidate caps are1,000 tokens for metadata/query/answer and4,096 for the shared
link/evolution decision. The latter is prospective GPT-specific engineering policy,
not a frozen validated allowance. Original prompts/schemas,0.7/0.5 temperatures,
k=10,5 construction neighbours, algorithm, consolidation/counter/stale index,
question order/references and both scoring policies remain unchanged.

Live contract/output sufficiency and actual dated model/provider verification have
not passed. There is **no frozen baseline approval or operational release**.
Provider-free evidence is `verification/provider-free-probes-v2.json`; the complete
native candidate is documented in [the campaign specification](gpt4omini-baseline.md).

## First request and financial stop

At06:22:08 UTC on4 November2026, the first of six planned compatibility probes
(metadata) returned HTTP403: “The request is prohibited due to a violation of
provider Terms Of Service.” `provider_name` is null. There is no generation ID,
response model, accepted output or usage. The responsible entity and cause are
unconfirmed; this does not establish a location, account or user violation.

The ledger admitted exactly one physical request and retained its full
USD0.019650 reservation. There was no retry, route fallback, JSON repair, second
probe, baseline or recovery. The terminal phase/halt and original response/error,
approval and receipt are preserved under `compatibility-v2/`. The earlier
`compatibility/` preparation failed preservation before any client/ledger/POST;
its unused/ineligible approval and diagnostic remain preserved separately.

Read-only account/key reads at06:26 UTC show USD50 credits, USD0 recorded usage
and USD50 key remaining. **Aggregate usage does not settle the individual attempt.**
The reservation remains unknown and unreleased. Before the newly authorized access
probe, conservative campaign exposure is USD0.019650, cell remainder USD4.980350,
usable campaign remainder USD41.980350 and protected contingency USD8. No top-up or
contingency is used. Local durable accounting remains authoritative.

## Updated-key request

After the403 and unknown reservation were reported, the user updated the private
API key and explicitly asked to try again. Authentication/key/credit GETs at06:37
UTC succeed, showing USD50/zero recorded usage. A fresh one-request access-check
plan retains the original terminal phase/halt/reservation, exact metadata payload
and cumulative USD0.25 compatibility/USD5 cell caps. It grants no baseline release
or individual-charge adjudication. Maximum cumulative exposure for two fully
reserved metadata requests is USD0.039300. Independent Standards and Spec reviews PASS at `79e480b`;40 transport/accounting
tests and isolated actual-launcher success/denial scenarios pass. Source fingerprint
is `d70695b9e3f6f422bec95a703bf1b1294771486ded7b2628320af036c48dff34`.
The approval pins11 evidence files, exact prior SQL rows/seal/request and the privately
authenticated credential, without exposing it.

**Actual result:** at06:49:31 UTC this one request also returns the same HTTP403
prohibition, null provider name and no generation ID/output/model/usage. The new
phase is terminal/Incomplete; its approval is consumed. Exactly two physical POSTs
occurred across the campaign, with no automatic retry or third attempt. The first
phase and all of its SQL rows/seal/halt/reservation remain unchanged.

At06:50 UTC read-only account/key reads still show USD50 credits/zero recorded usage.
Both USD0.019650 reservations remain unknown and held: **USD0.039300 conservative
exposure**, no settled reported model cost. Cell remainder is USD4.960700; usable
campaign remainder USD41.960700; protected USD8 remains untouched. Individual charges
are unreconciled. No baseline or further paid authority is released by these balances.

## Engineering verification and review boundaries

PR[#35](https://github.com/alistairkung/A-mem-reproducibility/pull/35) merged normally
as `c90d5afb5f8a41cf6da9ca1aeed5552fa4851bc5` (head `05016c9`) for native transport,
configuration, isolated accounting and compatibility controls. Source `3fd147d`
subsequently has independent **compatibility-only** Standards/Spec PASS receipts;
source fingerprint is `52c746f3cffd9d134a24dfa3bdc50a823877915f08cbaf82c9228d049893d232`.
Later baseline core and the access checker are preserved in
[draft PR#36](https://github.com/alistairkung/A-mem-reproducibility/pull/36), head
`79e480bc6f8dd9aef5a90b14f2a1382d42adfc3f`. It remains unmerged, with no final
baseline review/release. The updated-key review is scoped to one access check,
not the baseline core. This outcome PR changes documentation only.

- Native transport/observation focused review:49 tests pass independently. Earlier
  broader transport/configuration/observation/verifier checks:85 pass. Historical
  fixture/source-context subset:37 pass with unchanged assertions and fixtures.
- Native runner tests verify all four mocked native contracts, unchanged-author/
  Full action-gate equivalence, traced/untraced requests/state/predictions/scores,
  malformed-decision original fallback and two exact stale-index/counter restores.
- Actual-executor tests cover675 turns/158 QA/1,666 **mock** posts, exact cache
  identity/counter, two sealed continuations, wrong-parent/ancestor changes,
  persistence faults and observed Degraded rescoring faults. No GPT result is implied.
- Complete offline suite at `3fd147d`: **853 passed,1 failed,92 subtests passed**
  (17 expected serializer warnings). Failure is
  `tests/test_replay.py::test_full_replay_refuses_existing_or_protected_output_directories`:
  historical adapter source-pin mismatch occurs before its intended directory guard.
  The log remains intact; no assertion, fixture or oracle was weakened. This is an
  outstanding baseline release check, regardless of the provider stop.
- Separately invoked fixed archive reference and actual Full action-gate replay
  both pass:1,544 saved calls/568 notes/204 QA, exact recorded requests, outcomes,
  retrievals, states, predictions, scores and376 failure records. Their existing
  historical Degraded label is not a GPT baseline result. Network was disabled;
  zero paid calls. `verification/archive-equivalence.json` hashes both proofs.
- Runtime/assets offline preflight passes. Real-cloud native Gatev4 passes actual
  readback under the current `3fd147d` source, as detailed below. These gates do not
  waive the failing whole-suite check or establish live provider compatibility.

## Langfuse evidence

There are **no GPT-4o-mini baseline traces or baseline Experiments**. The real-runner
engineering gate uses144 synthetic native completions and zero LLM network requests.
It verifies113 observations/25 traces, all four generation stages,8 Experiment
items/112 scores/8 reporting traces and4 original QA trace associations. Three
production-executor fixture phases verify two exact checkpoint continuations.
Exports use16-span batches and the existing serialized-size guard; old failed gate
IDs/receipts remain preserved and are not reused.

These links contain **synthetic engineering gate evidence only**:

- [Corrected gate Experiment](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=014f456840d86ea8).
- [Historical gate Experiment](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=6d798b3f4177c823).
- [Example engineering trace](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/traces/0b92dd436a654c87a7f67980b036c7db).

The first live compatibility failure has authoritative local raw/generation evidence;
it is not a fully observed scientific run. Gate receipts/cloud readbacks and all
original Run1/Run2 cloud evidence remain separate and unchanged.

## Preservation and independent outcome audits

The pre-transmission check caught synthetic historical source links into the main
checkout before any OpenRouter POST. Restore/preserve that checkout at clean
pre-task `b8b3656f1342bceda4c79ffe7e824c1fc79afbab`; new engineering and physical
artifacts live in `.worktrees/gpt4omini-baseline`. The original
`artifacts/gpt4omini` convenience link points only to this new namespace.

The authoritative V2 preservation record and reconciliation supplement retain both
earlier maps/failed checks and reconcile all three source deltas against original
Git bytes. Independent Standards and Spec outcome audits reverify1,534 old files,
the dataset,61 link targets and44 tracked-source aliases. No original artifact/link
was rewritten. Do not advance the preservation checkout while those aliases rely
on it. The earlier preliminary alias counts are retained as investigation history.
Run1 remains USD8.530133; Run2 remains USD4.166489 including unknown454's full
USD0.324404 reservation. Their receipts/results/caches/ledgers remain immutable.

## Cost forecast and paired-ablation readiness

The pre-probe pricing scenario is USD4.88406010 for the first cell including the
full USD0.25 compatibility allowance. It combines1.5 times the largest preserved
engineering prompt count, twice native schema tokens plus256 overhead, every output
at its proposed cap and no cache discounts. This **conditional stress scenario is
neither an expected cost nor a guaranteed upper bound**. It uses historical prompts
only as size evidence, with no scientific result imported. A denied request yields
no GPT token-use evidence or validated output allowance; no baseline forecast freeze
occurred.

For the other eleven cells, the same preparatory scenario extrapolates16,814 nominal
calls to **USD49.24357230** excluding any future compatibility/recovery. This exceeds
the campaign's USD42 usable allocation even before the first cell. There is no
GPT-measured forecast or affordability conclusion. Actual usage/output evidence and
a new budget/design decision are needed before proposing paid additional cells.
Do not treat an affordable point estimate or unused prepaid balance as authority.

The first paired ablation is **not ready**: no completed Full baseline exists,
live contracts/routing/caps and both unknown charges remain unresolved, the
whole-suite gate has one failure, and final baseline independent reviews/freeze
remain outstanding. All other eleven cells remain unexecuted. Provider/account
clarification and request-level financial evidence are needed before any further
paid authority can release the campaign. [OpenRouter support](https://openrouter.ai/support/)
is a user-facing path for clarification; no support message was sent.

## Private audit inventory

All paths below are under the physical new `artifacts/gpt4omini/` namespace. They
remain local/private; raw responses may contain account identifiers and are not
committed. No credential is printed or committed.

- `compatibility-v2/{plan-v2,approval,receipt,generation-1}.json`, raw request/response,
  `financial-readback-after-denial.json`, remaining-eleven stress scenario.
- `compatibility-v3/` updated-key authentication, exact retained financial snapshot,
  consumed one-probe approval/reviews/journal/receipt and final financial readback.
- `budget.sqlite`: every original/new attempt and reservation, with phase seals/halts.
- `verification/`: scoped reviews, outcome audits, all failed/successful test logs,
  preservation V2/reconciliation, preflight and archive-equivalence proof.
- `gate-b/native-20261104-v4/`: synthetic real-runner cloud readbacks and gate receipt.
- `archive-{reference,candidate}-3fd147d/`: fixed-oracle offline replay outputs.
