# Conv-44 recovery — second output exhaustion, Incomplete

PR#19 merged as `11685b228f75e508d763be5417af5a5cef2a6d26`. Recovery PR#20 merged normally as
`3d0e04ac3054266cce8a82c3408d734de76a0fda` after570 offline tests/92 subtests,146 focused tests/60
subtests and clear independent Standards/Spec reviews. Local main was synchronized before execution.
No required check failed and no branch protection was bypassed. Production fingerprint remains
`eea7acf5953ecea73deb7fdd5b406c77171f76ef6a4544e5c149346b5e89e6c4`.

## Outcome

The single authorized child `t8-full-conv44-checkpoint-child` is **Incomplete**. It processed186
of251 assigned turns before another BLK-013 truncation, leaving the lineage at610 of675 notes,
counter607 and **zero of158 QA**. F1, BLEU-1 and adversarial correctness are **unavailable**, not zero.
Neither scoring view exists for this cell. A completed Degraded lineage cannot be claimed.

| Segment | Status | New turns | QA | Logical / physical calls | Conservative USD |
| --- | --- | ---: | ---: | ---: | ---: |
| `t8-full-conv44-r0-20261103` | Incomplete parent |424 |0 |848 /848 |1.415538 |
| `t8-full-conv44-checkpoint-child` | Incomplete child |186 |0 |372 /372 |0.702421 |
| Preserved lineage | Incomplete |610 |0 |1,220 /1,220 |2.117959 |

The child restored all424 original notes/outcomes, counter422 and the exact424×384 stale float32
index without encoding or regenerating the prefix or failed `D18:21` response. It resumed `D18:22`.
Original consolidation occurred naturally at counter500 (`D21:7`, overall note502) and600 (`D26:10`,
note602). Later normal neighbour evolution changed242 original-prefix contexts and243 tag lists;
their IDs/order, content, links and other attributes remain intact. The archived parent itself is
unchanged. These later updates and periodic consolidations are original algorithm behaviour, not
checkpoint refresh or historical repair.

## Confirmed failure and offline investigation

The186th new shared decision at `D26:18` returned HTTP200, `finish_reason=length`,4,000 completion
tokens and5,566 prompt tokens. Request ID `fb87d9c6-26e5-47e4-9a29-f9d2fca78d3b`; raw argument SHA256
`34c0c645fa306274c597b1af10e6bde40071d49e1db588158d51984123c96a0a`.
Its19,240-character inner JSON ends after a comma in a neighbour tag list. Outer response JSON is
valid; wire-decoded and SDK argument strings agree. The exact request retains strict mode, original
prompt/schema, temperature0.7, disabled thinking and unchanged D9a4,000-token cap. No serialization
or compatibility-layer truncation was found. Provider internal causes remain unknown; the immediate
failure is exhaustion of the frozen allowance, not BLK-014's normal-completion malformed JSON.

The original fallback retained note610, made no neighbour changes for this failed decision and kept
counter607 unchanged. The durable phase halt rejected the following metadata call before transmission.
No output repair, semantic retry, paid restart, second child or ablation was attempted. There were
zero retries and zero unknown charges. The next unprocessed original turn is `D26:19`;65 turns and
all158 questions remain. The parent's original failed evolution also remains in the lineage.

Exact saved-response replay through the real SDK/HTTPX MockTransport reproduces rejection with one
identical mock transmission and sockets disabled. It preserves the response and unchanged schema.
All371 accepted child argument strings match provider/transport arguments byte-for-byte. All274
inherited failure records survive with original provenance;131 new D3a deviations/536 transformations
are retained alongside271 inherited deviations/1,055 transformations. Lineage totals:402 approved
deviations/1,591 transformations and two distinct rejected length completions. Strict validation and
the approved validation-copy exception remain unchanged.

The final partial snapshot validates and restores/exports identically:610 ordered notes/outcomes,
counter607 and finite610×384 float32 retrieval state. There is no complete cache or completed cell.
All51 protected historical/new phase files verify, including the original parent and both completed
conv-49/conv-50 baselines/caches. All3,868 historical attempt/logical rows, eight old phase rows,
earlier checkpoint claims/recovery edges and prior completed-cell ownership remain unchanged.
The original conv-44 cell is owned by its halted child through exactly one reviewed recovery edge.

Post-failure checkpoint, output-limit and compatibility regressions pass **97 tests**. The actual
ablation planner still rejects incomplete full conv-44, and a child-of-child checkpoint proposal
rejects as unsupported, without client creation, approval claim or ledger change. These are safe
failure controls, not resolution of output-cap exhaustion. No scientific/production changes followed
the paid failure; BLK-013 remains **Open**.

## Spending and cost-only forecast

| Child stage | Calls | API input tokens | API output tokens | Conservative USD |
| --- | ---: | ---: | ---: | ---: |
| Metadata |186 |104,617 |26,562 |0.063340 |
| Shared decision |186 |582,769 |386,806 |0.639081 |
| Total |372 |687,386 |413,368 |0.702421 |

Parent and child are counted once, including both rejected billed responses. Cumulative study:
**USD8.407857 /4,240 settled logical and physical requests**, zero unknown charges. USD33.592143
remains usable under USD42, preserving USD8 within USD50. The child's immutable USD3/818-call/
2,454-attempt approval `ad09fe3d-5401-4898-a64e-294491a6dc64` is consumed; unused allocation is not
permission to continue. Charges use the unchanged conservative peak rates, not invoice totals or
assumed cache/off-peak discounts. [Provider pricing](https://api-docs.deepseek.com/quick_start/pricing/).

The existing whole-fresh-cell scenario totals **USD48.096559**: incurred USD8.407857 + remaining
USD31.688702 + USD8 reserve. The remainder includes hypothetical fresh full conv-44 USD3.255215 and
nine ablations USD28.433487. It grants no restart authority and cannot reclaim the consumed cell.
The point estimate leaves USD1.903441 forecast headroom;2× remaining costs exceed the ceiling.

For decision support only, preserving the610-note state would leave446 logical calls/1,338 maximum
attempts (65 turns/158 QA). Child memory-stage means and completed conv-49/50 QA means yield a
conditional suffix estimate USD1.344443; combined with nine ablations, incurred costs and reserve,
USD46.185787. **A further recovery chain is unsupported and unauthorized.** This arithmetic is not
an executable plan, spending grant or upper bound. Neither scenario uses observed quality or revises
the frozen population/settings; another4,000-token failure remains possible.

## Stopping boundary and evidence

Stop at the user's material-blocker boundary. Both existing baselines remain verified, but full
conv-44 and first-ablation readiness are blocked. No balanced558-question condition aggregate is
reported. A further recovery or a uniform generation-policy amendment needs an explicit decision
and reviewed safeguards; the latter would also require assessing comparability with existing4,000-
token baselines. Do not silently drop conv-44, score a partial memory build, increase the cap or
introduce output repair. This report implements none of those options.

Safe local, Git-ignored evidence (not public download links):

- `artifacts/runs/t8-full-conv44-r0-20261103/` and `artifacts/runs/t8-full-conv44-checkpoint-child/`:
  exact raw requests/responses, original failures, approval/preflight/checkpoint, partial memory/index,
  run/summary and phase inventories.
- `artifacts/t8/conv44-recovery-incomplete-20261103/`: `verification.json`, `child-stage-costs.json`,
  `cost-only-forecast.json` and `selected-population-inventory/` with explicit incomplete coverage.
- `artifacts/t8/offline/conv44-child-length-{reproduce.py,reproducer.json}`,
  `conv44-child-length-replay-20261103.log` and `conv44-child-postfailure-tests-20261103.txt`.
- `artifacts/t8/conv44-recovery-{pre-execution-20261103.json,preservation-before-20261103.json}`,
  main preflight/plan, immutable approved copy and before/after SQLite backups. The actual ledger
  remains `artifacts/study-budget.sqlite`; it was never reset or replaced.
- Engineering/full/focused/review evidence: `artifacts/t8/offline/conv44-recovery-*` and
  `conv44-checkpoint-verification.json`; live/error logs under `artifacts/t8/live/`.

Local collection remains independent of optional Langfuse; no new cloud import/tracing claim is made.
The result demonstrates repeated output-bound failures despite successful short-fixture validation
and exact-state recovery. It does not establish that the memory algorithm, provider strictness or
generation policy is universally reliable, or that a partial conversation reproduces quality metrics.
