# Run2 Full conv-44 — preserved financial stop

Status: **Incomplete; zero completed Run2 cells or QA**. No later cell or recovery has executed.
This records a material financial/provenance stopping condition, not a completed ablation study.

## Verified engineering and first execution

GateA merged in [PR#25](https://github.com/alistairkung/A-mem-reproducibility/pull/25), and the
real-runner Langfuse/campaign implementation merged in
[PR#26](https://github.com/alistairkung/A-mem-reproducibility/pull/26) as
`207eac03fb92e32fb4d0571cd67359da6875463d`. The frozen source/configuration passed715 offline
tests/92 subtests, both complete568-note/204-Q original/full-candidate archive replays, independent
Standards/Spec reviews, actual cloud fixture audits and current-source runtime preflight.
Read [the frozen protocol](run2-protocol.md) and [GateB proof](run2-observability-verification.md).

The immutable campaign approval activated only after the final factual audit and normal merge.
Cell0 `run2-full-conv-44-r0-p0` hadUSD5/1,666 logical/4,998 physical limits under the separateUSD42
usable campaign allocation and protectedUSD8 reserve. Its live requests retained the original
algorithm/prompts/schemas/parsers, DeepSeek Flash/fingerprint, disabled thinking, temperatures,
five construction neighbours, k=10 and scoring. Shared decisions requested8,192 output tokens;
other stages retained1,000. The hosted service accepted the setting, but the largest completed
decision was3,512 tokens. No observed Run2 output exhausted the limit; adequacy above4K is still
unproven by this partial sample. Do not pool these results with exploratory Run1.

## BLK-022: response validity and financial completeness differ

At `D10:10`, shared logical call454's first attempt454 received HTTP200, then a body-read
`RemoteProtocolError` after60.529s, with no captured body or usage. The existing genuine-transport
retry policy allowed attempt455. It returned a valid response after34.465s, with3,611 input/2,822
output tokens. The original argument string was returned unchanged and the original actions
finished note227/counter226. This was not a malformed-JSON, `length`, settlement or observed
120-second timeout incident. The underlying network/provider/proxy cause is unverified.

The first attempt keeps its full324,404-microUSD reservation. The next `D10:11` metadata generation
is blocked before transmission by the durable unknown-charge guard. A successful retry does not
prove that the earlier request was unbilled. No part of the unknown reservation was released, nor was its historical row corrected or reset.
The first body/request ID/detailed exception message were not captured and cannot be fabricated
from the valid retry. The [provider's keep-alive documentation](https://api-docs.deepseek.com/quick_start/rate_limit/)
does not identify this60-second error or establish its cost. The provider console requires sign-in;
no authenticated request-level billing evidence is currently available.

| Preserved result | Verified value |
| --- | ---: |
| Memory notes / planned |227 /675 |
| Evolution counter |226 |
| Exact stale retrieval index |227×384 float32 |
| Logical calls |454 |
| Physical attempts |455, including one genuine retry |
| Questions / planned |0 /158 |
| Audited D3a deviations / transformed indices |140 /521 |
| Verified Langfuse observations / traces |1,278 /230 |
| QA scores / Experiments |Unavailable; no QA generated |

The original-note serialization restore/export matches every note, link, metadata field, outcome,
index document/order and float32 embedding byte without calling a model or encoder. This verifies
the preserved prefix, not authorization or implementation of a new recovery mechanism.448 turns
and158 QA remain, requiring1,212 logical calls/at most3,636 attempts hypothetically. There is no
automatic recovery: the grant only covers BLK-013 length failures, and this phase explicitly reports
`recoverable_length_failure:false`, `usable_for_next_phase:false`. Unknown-charge checks also reject
later cells. [BLK-022](blockers.md#blk-022) remains Investigating.

## Spending and observability

| Run2 accounting | USD |
| --- | ---: |
| Settled conservative cost,454 attempts |0.720433 |
| Retained unknown reservation, one attempt |0.324404 |
| Total charged or reserved exposure |1.044837 |
| Unused part of originalUSD5 cell allocation |3.955163 |

These are conservative peak-rate charges/reservations, not an invoice or proof of the unknown
attempt's actual cost. Run1's separateUSD8.530133 ledger and all557 archived files remain byte-identical.
The current provider-only point forecast isUSD39.056674 including incurred exposure, orUSD47.056674
with the protectedUSD8. It still uses Run1 cost proxies for unmeasured complete Run2 stages and
cannot establish affordability or authorize execution while an unknown charge remains.

Actual paid tracing worked: all1,278 observations and230 traces were fetched and exactly verified,
including the valid retry output and explicit partial usage/cost. The affected span reports one
unknown-usage attempt, no invented complete cost and the ledger as authoritative. No QA results,
metric zeros or experiment-import success are claimed. Corrected/historical F1/BLEU-1, adversarial
correctness and comparisons with Table3 are **unavailable** until complete balanced predictions exist.

The user upgraded Langfuse to Core; the authenticated UI confirms a new3 November–3 December
period and100K documented included units. An offline check of the actual SDK5.1.0 importer reveals
that each question/view creates root/task/evaluation-group and per-metric evaluator observations,
including a span when an evaluator returns no value. Normal campaign volume is approximately
221,508–235,524 units: **USD9.72–10.84 incremental Core overage** at the published proportional rate,
before tax/rounding and extra failures. Two continuations per cell give a structural scenario near
249,788 units/USD11.98; this is not a bound. See `artifacts/run2/langfuse-unit-forecast.{md,json}` and
[Langfuse pricing](https://langfuse.com/pricing), [unit definition](https://langfuse.com/docs/administration/billable-units).
The Core subscription was handled by the user; no agent upgrade or overage authorization is inferred.
If incremental service fees shareUSD42, the initial provider forecast plus normal overage exceeds
that allocation even before the protected reserve. Service-cost allocation needs a separate decision.

## Evidence, checks and decisions needed

Authoritative local evidence:

- `artifacts/run2/runs/run2-full-conv-44-r0-p0/`: immutable approval, exact journals/raw returned
  arguments, partial memory/index, trace capture, cloud readbacks/proof and sealed Incomplete receipt.
- `artifacts/run2/budget.sqlite`, `transport-incident.json`, `frozen/{manifest,activation,campaign-approval}.json`:
  retained accounting, request/body references, approved source and financial limits.
- `artifacts/run2/offline/transport-state-roundtrip.json`, `transport-review.md`: independent exact-state,
  financial and cloud evidence checks. The synthetic HTTP200 body-read regression reproduces the
  observed error class and safe stop, without inventing a historical fragment or changing retry policy.
- `artifacts/run2/analysis/transport-stop-20261103/`: saved-only inventory/CSV exports with no complete
  condition aggregates or fabricated quality values. `forecasts/transport-stop-cost-only.json` is
  financial planning only, not an executable recovery approval.

The focused transport group passes28 tests. The post-incident complete suite passes716 tests/92
subtests in661.43s with17 expected warnings; independent Standards and Spec reviews verify the actual
state, financial/cloud proofs and corrected unit forecast. [PR#27](https://github.com/alistairkung/A-mem-reproducibility/pull/27)
records the outcome/regression. Production code/settings and all phase/ledger evidence remain
unchanged. No paid probe, retry phase or later experimental cell was launched.

Recommended next step: seek request-level billing/usage for attempt454. If it cannot be resolved,
obtain an explicit decision on a narrowly scoped fully charged upper-bound adjudication and exact-state
continuation, retaining unknown usage as a limitation. Never mark it unbilled or rewrite the original
row/evidence. Separately decide whether incremental Langfuse fees have their own bounded allocation.
No recovery-policy, spending-validation, timeout, streaming, prompt or schema change is implemented here.
