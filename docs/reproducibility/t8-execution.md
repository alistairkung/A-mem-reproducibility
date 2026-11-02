# T8 execution and comparative evidence

Status: first T8 cell Incomplete; paid collection halted2 November2026 after BLK-013 recurrence.
Authority: [latest decision](decisions.md#authorization--t8-implementation-and-paid-main-execution),
[issue #8](https://github.com/alistairkung/A-mem-reproducibility/issues/8).
Integration branch: `codex/t8-study-execution`, based on T7 merge `577a1e3`.

## Population and budget fixed before comparative performance

Activate only the predefined D10a fallback using the already saved cost-only forecast
`artifacts/checkpoint-child-cost-forecast.json`. Full scope projects USD127.391486; fallback projects
USD42.762234 including incurred spending and USD8 contingency. This is a point forecast, not a bound;
the fallback's2× remaining-cost sensitivity exceeds the ceiling. No accuracy-based selection is made.

| Conversation | Turns | QA | Original sample index |
| --- | --- | --- | --- |
| conv-49 |509 |196 |8 |
| conv-50 |568 |204 |9 |
| conv-44 |675 |158 |5 |

All558 original questions remain, in frozen manifest order, for all four conditions. Initial repetition
is0: one independently built store per conversation/condition. The verified Degraded full-mode conv-50
parent/child lineage is reused once. Two missing full-mode cells complete T5 before nine ablation cells.
No condition inherits another condition's memory state or cache. Full-mode baseline collection uses
the frozen author factory; other modes use T7's verified action-gate factory.

At authorization the durable ledger contains1610 settled attempts / USD3.025799, zero unknown charges.
Usable additional maximum is USD38.974201, preserving USD8 under the USD50 total. The eleven remaining
fresh cells total16936 logical generations and at most50808 physical attempts. Each approval must bind
its workload, hard spending/request/attempt caps and scientific/source provenance before transmission.
Unspent allocation is not approval for recovery or an extra repetition.

Use a pooled cumulative allowance: each complete-conversation phase has at most USD10 as a hard
phase ceiling, while all new phases together remain limited to USD38.974201 by the fixed USD42
usable study ledger ceiling. Phase caps are not additive spending authority. Avoid artificial
proportional per-cell limits that could prevent completion despite headroom in the approved pool.
Reforecast the entire remaining balanced study from usage/cost before each phase; stop if it no
longer fits. A claimed phase's limit is immutable and never increased automatically.

Official DeepSeek pricing/model documentation was checked2 November2026: request model `deepseek-flash`,
documented version DeepSeek-V4.1-Flash-1017,1M context and peak cache-miss input/output rates
USD0.30/1.20 per million tokens remain unchanged. Continue to reserve/charge at these conservative
peak rates without assuming cache/off-peak discounts. [Provider pricing](https://api-docs.deepseek.com/quick_start/pricing/).

## Engineering and execution gates

- Preserve frozen author/provider/scorer/configuration/manifests and raw baseline evidence.
- Test at existing phase planner/executor, durable permit-ledger, manifest runner and saved-result
  export interfaces with deterministic offline fixtures. Run the complete offline suite and independent
  Standards/Spec reviews before paid execution.
- Require current network-disabled runtime preflight and an explicit reviewed support-source migration
  from the historical compatibility/T7 receipts; unchanged scientific contracts remain mandatory.
- Keep initial metadata/shared decisions, D3a validation-copy policy and D9a output caps identical.
  No prompt/schema/parser/retrieval/model/scoring change is part of T8.
- Verify exact complete-conversation execution partitions and original question IDs/order. Bound actions,
  condition, population and repetition in every immutable approval/run/cache identity.
- Use the existing fixed ledger and pre-transmission reservations; retain unknown/interrupted charges,
  SDK attempt limits and terminal settlement/provider/contract failure handling.
- Reconcile affordability using cost evidence between phases. If balanced completion no longer fits,
  stop for a revised decision. Any paid recovery requires separate approval.
- Preserve partial artifacts and costs if any phase fails; do not present incomplete comparison cells
  as complete benchmark results or continue the remaining paid schedule automatically.

## Reporting and submission material

Use the authors' saved corrected/historical scoring views on identical predictions and IDs. Report
per-category F1/BLEU-1, category5 adversarial correctness separately, secondary metrics, paired question
coverage, degraded/incomplete classifications, provider deviations/failures, costs/retries/tokens/latency
and retained decision-call overhead. No stochastic-robustness claim follows from one build per cell.

Reuse existing local table exports and Langfuse Experiments imports. Imports return saved outputs and
metrics; they do not run the application or evaluators again. Keep condition/population/scoring-policy/
repetition/run lineage distinct and retain local evidence even if optional reporting is unavailable.
Project authentication was rechecked successfully2 November using the CLI (HTTP200); a filtered
receipt in `artifacts/t8-langfuse-project-readback.json` retains no credentials or request/response headers.
Pinned Langfuse SDK5.1.0 remains the tested protocol choice; no dependency upgrade is introduced.
[Saved-result workflow](https://langfuse.com/resources/engineering/evaluate-existing-application),
[Experiments SDK](https://langfuse.com/docs/evaluation/experiments/experiments-via-sdk).

Report material must fit10 pages; presentation outline must fit15 minutes. The actual recording and
submission remain human deliverables. Deadline:13 November2026 at midnight Hong Kong time. Preserve
the debug diary/blocker IDs and separate HW3 repository boundary. Exact phase plans/commands, test
and review evidence, PR and actual run outcomes will be appended as they become available.

## Pre-paid engineering checkpoint

[Draft PR #17](https://github.com/alistairkung/A-mem-reproducibility/pull/17) contains the integration
work. The first integrated suite passed472 tests/92 subtests and the network-disabled runtime preflight
passed. The real-history first-cell planner produced an **unapproved** conv-49 full-mode plan:
USD10,1,410 logical calls, at most4,230 attempts, with a ledger-rounded balanced forecast USD42.770085
including contingency. No approval has been claimed and no T8 paid request has occurred.

Independent pre-paid review then found four gaps not covered by that green suite: malformed provider
identity types could bypass a halt; critical local journal failures were best-effort; failed completion
SQL could leave a reusable receipt; and saved-result source checks omitted the scoring wrapper.
The first two are tracked as BLK-017. All corrections, targeted regressions, full-suite tests and
independent correction reviews are required before paid execution. Initial plans/preflight receipts
are retained as engineering evidence and must be regenerated if their source fingerprint changes.

## Final pre-transmission verification

Reviewed source commit `ae23e291`, source fingerprint
`42ee5de8ffb64090fbafa564bd4ea3e41fd042e846271349ff18b370991a9fe0`:

- Complete offline suite: **519 tests and92 subtests passed**,16 intentional invalid-metadata SDK
  serialization warnings; `artifacts/t8/offline/final-serial-frontier-suite.txt`.
- Current runtime preflight: `artifacts/t8/preflight-final.json`, assets ready/runtime pass, sockets denied.
- Both final Standards/Spec reviews clear; independent threaded/fault rechecks each pass six tests.
  BLK-016/017/018 are Resolved as implementation defects, not provider-reliability guarantees.
- Exact original cache serialization/restore, historical phase inventories and all ledger-prefix charges
  verify in `artifacts/t8/offline/final-integrity-proof.json`. The ledger remains1610 settled attempts /
  USD3.025799 /zero unknown; original cache files and scientific sources/fixtures are unchanged.
- Financial/artifact support migration is explicit. The historical T6 guard is unchanged; prior T7
  numerical replay evidence is not relabelled as a test of new T8 financial controls.

The first exact plan is `artifacts/t8/plan-final-full49.json`: full-mode conv-49,509 turns/196 QA,
USD10 phase ceiling,1,410 logical calls and at most4,230 attempts, within the pooled allowance.
Its planner output is unapproved. The user's existing explicit T8 paid authority permits a separate
immutable approved copy after these gates; it does not permit recovery, extra repetitions or raising caps.

Reproducible preparation commands, from the repository root (fresh output filenames required):

```sh
.venv/bin/pytest -q
.venv/bin/python -m amem_repro.phases preflight \
  --assets artifacts/assets --output artifacts/t8/preflight-final.json
.venv/bin/python -m amem_repro.study plan \
  --receipt artifacts/t8/preflight-final.json --assets artifacts/assets \
  --condition full --conversation conv-49 --run-id t8-full-conv49-r0-20261102 \
  --output artifacts/t8/plan-final-full49.json
```

Execution requires the separately materialized, user-authorized approval, not the unapproved plan.
Only the key needed by the process is loaded privately from `.env`; no key/header is printed or stored.
Actual approval/run identities, commands and outcomes follow below when execution begins.

## Main collection: full conv-49

On2 November2026 the reviewed gates above passed and the user's T8 paid authority was materialized
as immutable approval `artifacts/t8/approvals/t8-full-conv49-r0-20261102.json`, approval ID
`d21bb38c-7a87-4661-bb79-8b3071319cb2`, run ID `t8-full-conv49-r0-20261102`.
It binds509 turns/196 questions,1,410 logical calls, at most4,230 physical attempts and a USD10
phase ceiling under the pooled USD42 usable study limit. Source fingerprint remains `42ee5de8` above;
code commit is `881b35d`. This approval is consumed when claimed and cannot authorize recovery.

Execution uses the reviewed executor with only the needed provider key privately loaded:

```sh
.venv/bin/python -m amem_repro.study run \
  --approval artifacts/t8/approvals/t8-full-conv49-r0-20261102.json \
  --receipt artifacts/t8/preflight-final.json --assets artifacts/assets
```

Local evidence is `artifacts/runs/t8-full-conv49-r0-20261102/`, with the console log at
`artifacts/t8/live/full-conv49-r0.log`. The initial responses return `deepseek-flash` and fingerprint
`bc19ba97cbe016479903222bb1578db6`, matching the archived conv-50 baseline. Collection is in progress;
this entry does not assert completion, final spending or any comparative result. Previously described
unapproved plans and the pre-paid checkpoint remain historical engineering evidence.

## Paid hold — BLK-013 recurrence

The first T8 cell ended **Incomplete** at12:20:33 UTC on2 November2026. The413th shared decision,
for `D22:2`, exhausted the unchanged D9a4,000-token cap: HTTP200, `finish_reason=length`,6,551 prompt
and4,000 completion tokens, unfinished JSON inside a neighbor tag. This reopens BLK-013; it differs
from BLK-014's normally finished malformed JSON. Request ID `8b6bea1e-bc8e-40bf-8b38-22627f0edf4a`;
raw arguments SHA256 `51be35f7cefb5a2da8623dcf23ea54bdb8fdc3f8e7f4c3c5d2e2d1e66cd1b962`.
Wire and SDK argument strings match; original prompts/schema/temperature/thinking/endpoint/cap verify.
The adapter correctly rejected the incomplete finish before returning arguments to A-MEM.

The author fallback retained the413th note and failed evolution, with no neighbor changes and counter411.
`partial-memory.json` retains413 ordered notes/index rows, including the original stale embeddings.
The next metadata operation was blocked before transmission. No failed response was repaired/retried,
no QA ran, and no conv-44/ablation phase was launched. The partial build is not a reusable completed cache.

| Observation | Verified value |
| --- | --- |
| Physical requests / admitted logical calls | 826 /826; zero retries |
| Generation journal records | 827; includes one blocked, untransmitted metadata notice |
| Preserved notes / evolution counter | 413 /411 |
| Questions completed | 0 of196 |
| Accepted outputs with exact provider-argument identity | 825 |
| Audited D3a deviations / integer-string transformations | 270 /1,066 |
| Phase conservative settled spending | USD1.413246 |
| Cumulative study conservative settled spending | USD4.439045 /2,436 attempts |
| Unknown charges | 0 |
| Phase status / usable for next phase | Incomplete /false; durable halt persisted |

Offline saved-response SDK replay makes zero network requests and reproduces the exact request and
rejection. Evidence: `artifacts/t8/offline/conv49-length-reproduce.py` and
`artifacts/t8/offline/conv49-length-reproducer.json`; phase inventory/partial state verify. The original
run directory/log are unchanged. The final519-test/92-subtest suite remains applicable to the unchanged
code. The observed halt demonstrates safety controls, not successful benchmark completion.
Independent forensic review agrees; `artifacts/t8/offline/review/conv49-truncation-review.md` verifies
all826 attempt/usage/charge rows and an exact finite413×384 float32 state round-trip. Read-only ledger
backup `artifacts/t8/study-ledger-after-conv49-incomplete.sqlite` and its receipt
`artifacts/t8/offline/post-failure-preservation.json` preserve this financial checkpoint; they never
replace or reset the cumulative live ledger.

Saved-result inventory: `artifacts/t8/blocked-collection-inventory/`. It retains incomplete conv-49 and
completed original conv-50 with their costs once; no selected-population condition is complete, and
no population quality/paired-difference table is presented. T5 issue#5 and T8 issue#8 remain open.
Langfuse project authentication was verified, but no new completed-population experiment exists to import.

Cost-only reforecast is USD44.183331 including all incurred charges and USD8 contingency. It retains
whole fresh-cell estimates for all eleven uncompleted cells, without crediting this partial build;
it is not an approved recovery cost or a guarantee. No new population decision or paid execution follows.

**Resolution proposed for review, not implemented/authorized:** extend the reviewed exact-state
checkpoint machinery to this conv-49 failure, preserving all413 notes, failed `D22:2`, counter411,
stale index and parent provenance. Start at `D22:3`:96 remaining turns plus196 QA entail584 logical
calls, at most1,752 attempts. Keep D9a4,000 and every other scientific setting unchanged. This avoids
rebuilding prior memories and would inherit degradation, but cap exhaustion can recur. The existing
checkpoint policy is conv-50-specific, so its approval cannot be reused for this lineage.
A fresh rebuild costs more and discards reuse without removing the cap risk. Raising the cap across
arms instead requires an explicit protocol amendment and a decision on comparability/recollection of
existing4,000-token baselines. No JSON repair, prompt shortening or silent cap increase is proposed.

All further paid collection is stopped pending the separate recovery/scientific decision required by
the frozen protocol. Unspent main-phase budget is not recovery authorization. PR#17 remains draft;
no T8 merge authority, balanced-study completion or submission readiness is asserted.
