# T8 conv-44 — incomplete full-mode baseline

On 3 November 2026, documentation PR #18 merged normally as
`f78215e3a6e127d19001df73011b27c273b1f65d`. Standards/Spec reviews were clear,
GitHub reported a clean merge with no failed required check, and local main was synchronized.
Production source remains `0b2287b19626da56d7bd567c6073ac15000a4f73c98e9b3510ca18d5ba6faaa9`;
the frozen author files, configuration, prompts, schemas, parser, retrieval and scoring are unchanged.

## Observed outcome

The single authorized run `t8-full-conv44-r0-20261103` is **Incomplete**, not a completed degraded
baseline. It retains424 of675 original turns/notes, evolution counter422 and the exact424×384
finite float32 retrieval index, including original stale embeddings. **Zero of158 questions were
answered. F1, BLEU-1 and adversarial correctness are unavailable, not zero.** Neither scoring view
exists for this incomplete phase. The original conv-49 and conv-50 completed baselines remain unchanged.

BLK-013 recurred on the424th shared decision at `D18:21`: HTTP200, `finish_reason=length`,
4,000 output tokens and unfinished JSON inside a neighbour tag. Request ID:
`4368db7f-c980-429d-aaec-ed36c55ee7e5`. Raw argument SHA256:
`955c9f38b5d56d459ca2f0bc8cb7214572490dca4ba365d5fb97427cdcf9f108`.
The original wire request has strict mode, the unchanged shared-decision schema, temperature0.7,
disabled thinking and the approved D9a4,000-token limit. Wire-decoded and SDK argument strings agree.
This is output exhaustion, not BLK-014's normally finished malformed JSON or a new serialization defect.

The author's failure fallback retained the424th note without changing neighbours or incrementing
the counter. The phase durably halted; the next metadata request was rejected **before transmission**.
The failed output was neither repaired nor regenerated. The next unprocessed turn would be `D18:22`.
No recovery, restart, ablation or other paid phase was launched.

## Gates, accounting and verification

Before transmission, current-source runtime preflight passed with network disabled. All36 protected
historical run/cache files verified, the new cache was absent, and no conv-44 cell claim existed.
The immutable approval `295e4e88-5bd8-479f-951a-fbb4d4ef56e6` bound675 turns/158 questions,
USD5 additional,1,666 logical calls and4,998 maximum attempts. Its grant is now consumed.

| Stage | Logical / physical calls | API input tokens | API output tokens | Conservative USD |
| --- | ---: | ---: | ---: | ---: |
| Metadata |424 /424 |237,700 |59,799 |0.143267 |
| Shared decision |424 /424 |1,208,744 |757,884 |1.272271 |
| Total |848 /848 |1,446,444 |817,683 |1.415538 |

All848 attempts settled, including the rejected response; there were no retries or unknown charges.
Cumulative study spending is **USD7.705436 /3,868 logical and physical calls**, leaving USD34.294564
usable under USD42 and preserving the USD8 contingency. Charges use the existing conservative peak
rates, not provider invoices or assumed cache discounts.

All847 accepted argument strings are byte-identical to provider arguments. All271 approved D3a
deviations/1,055 validation-copy transformations survive. The failure inventory also retains one
rejected completion, its evolution-failure notice and the next untransmitted metadata-block notice.
All42 protected files (36 historical plus six newly inventoried phase artifacts), all3,020 historical
attempt/logical rows, seven prior phase rows and prior ownership/checkpoint records verify unchanged.
The partial snapshot passes state validation; there is no complete cache marker or completed cell.

Exact real-SDK replay through HTTPX MockTransport, with sockets disabled, sends one identical mock
request and reproduces rejection while preserving the response. No offline model calls or output
repair occurred. All120 existing adapter-budget/phase/study/comparison regressions pass (16 warnings
from intentional SDK malformed-metadata fixtures), recorded in
`artifacts/t8/offline/conv44-failure-regressions-20261103.txt`; pre-paid controls passed48 tests/60
subtests. Independent Standards and Spec/factual reviews are clear. No production changes or new
compatibility policy were needed.

## Cost-only forecast and next decision

The existing planner does not credit incomplete cells as completed builds. Its whole-fresh-cell
scenario is **USD31.688702 remaining + USD7.705436 incurred + USD8 reserve = USD47.394138**.
It includes a hypothetical fresh conv-44 cell (USD3.255215) plus nine ablation cells (USD28.433487).
This is a planning scenario, **not authorization to restart**; the consumed cell cannot be reclaimed.
The estimate is not an upper bound, and a2× remaining-cost sensitivity exceeds USD50.

A supplemental, non-executable checkpoint scenario would retain all424 notes, failed `D18:21`,
counter422 and stale index, then start at `D18:22`:251 remaining turns/158 questions,818 logical calls
and at most2,454 attempts. Using this prefix's measured memory cost and completed conv-49/50 QA
means gives **USD1.936945** for that suffix. With the same nine-ablation estimate, incurred charges
and reserve, the conditional total is **USD46.075868**. Future output/context growth and another
failure can invalidate this estimate. Neither forecast uses quality results or changes the population.

Recommend separately reviewing exact-state conv-44 checkpoint support before considering a bounded
paid continuation, preserving the failed decision rather than retrying it. That support is **not
implemented or approved here**, and the4,000-token cap can fail again. A larger cap or prompt/schema
change would require a separate scientific/comparability decision; none was made.

**First-ablation readiness: blocked.** The existing Neither-conv49 planner still rejects while full
conv-44 is incomplete, with no client, approval claim or ledger change. T5 selected-scope collection
and T8 remain incomplete. Keep BLK-013 Open and stop before further paid execution. No recovery,
repeat, ablation or protocol amendment is authorized by this report.

## Preserved evidence

All paths below are safe local, Git-ignored artifacts, not public download links:

- `artifacts/runs/t8-full-conv44-r0-20261103/`: immutable approval/preflight, raw events/request/response,
  partial memory/index, summary and complete incomplete-phase file inventory.
- `artifacts/t8/approvals/t8-full-conv44-r0-20261103.json` and
  `artifacts/t8/conv44-preflight-20261103.json`.
- `artifacts/t8/conv44-incomplete-20261103/`: `verification.json`, `stage-costs.json`,
  `cost-only-forecast.json`, `ablation-gate.json` and `selected-population-inventory/`.
- `artifacts/t8/offline/conv44-length-{reproduce.py,reproducer.json}` and
  `conv44-length-replay-20261103.log`; `artifacts/t8/live/full-conv44-r0-20261103.log`.
- `artifacts/t8/conv44-preservation-before-20261103.json` and immutable
  `conv44-ledger-{before,after}-20261103.sqlite` backups. The actual cumulative ledger remains
  `artifacts/study-budget.sqlite`; it was never reset or replaced.

Provider internals remain unknown; the immediate failure is verified cap exhaustion. Local collection
does not depend on Langfuse, and no new cloud import/tracing claim is made. This recurrence shows why
a successful short fixture and completed conversations cannot establish a general output-size bound.
