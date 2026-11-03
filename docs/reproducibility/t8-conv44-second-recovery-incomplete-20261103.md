# Conv-44 second recovery — third output exhaustion, Incomplete

Recovery PR[#22](https://github.com/alistairkung/A-mem-reproducibility/pull/22) merged normally as
`5ddc96ef8653bcf8997f2d7840435c4630826e09`. Before execution,613 offline tests/92 subtests,
189 focused tests/60 subtests and both independent Standards/Spec reviews passed. Each reviewer
also ran62 focused tests; final factual documentation readbacks were clear. No failed required
check or branch protection was bypassed. Frozen author files, prompts, schemas/parser, DeepSeek
settings, D3a/D9a, retrieval and scoring were unchanged. Production fingerprint:
`0341a2a579842725c9ac6a18a110e2816a2896c32e07cf883fd36e2ef1ab681f`.

## Outcome and preserved lineage

The single authorized second continuation, `t8-full-conv44-checkpoint-grandchild`, is **Incomplete**.
It processed26 of65 assigned turns, then stopped at `D26:44`. The lineage preserves636 of675 notes,
counter632 and **zero of158 QA**. Corrected/historical F1, BLEU-1 and adversarial correctness are
**unavailable**, not zero. No complete memory cache or scoring view exists for this cell. A completed
Degraded baseline cannot be claimed.

| Segment | Status | New turns | QA | Logical / physical calls | Conservative USD |
| --- | --- | ---: | ---: | ---: | ---: |
| `t8-full-conv44-r0-20261103` | Incomplete root |424 |0 |848 /848 |1.415538 |
| `t8-full-conv44-checkpoint-child` | Incomplete first child |186 |0 |372 /372 |0.702421 |
| `t8-full-conv44-checkpoint-grandchild` | Incomplete second child |26 |0 |52 /52 |0.122276 |
| Preserved lineage | Incomplete |636 |0 |1,272 /1,272 |2.240235 |

Fresh network-disabled preflight on merged main verified both pinned ancestors, all610 ordered
notes/outcomes, counter607, stale610×384 float32 index and all408 inherited failure records.
All51 protected files and the USD8.407857 historical ledger were unchanged before transmission.
Approval `a35ef8a2-78f1-44c6-9f67-1c36d605b2c2` bound that lineage, current source/preflight/assets,
dataset/configuration, model/provider policy and USD3/446-call/1,338-attempt caps. The new phase
resumed exactly `D26:19`; no prefix, failed decision or embedding was regenerated.

The ordered root424 + first-child186 + new26 outcomes exactly cover the first636 original turns,
without duplication/omission. The partial state restores/exports identically. Its636×384 float32
index is finite, SHA256 `06951b2f0e4b1ef05567077f15c937bafc8a0c79ecaa38dcf32b1e353506e49d`.
The first610 embedding bytes and corpus entries remain exact. No consolidation threshold was reached.
Original successful actions changed77 prefix contexts and77 tag lists; IDs/order, content, links
and other attributes remain intact. Those lawful later updates do not alter either archived ancestor.

## Confirmed failure and offline investigation

The26th new shared decision returned HTTP200, `finish_reason=length`, exactly4,000 output tokens
and5,638 input tokens. Request ID `633454cd-c049-4132-9754-f9ba24ea63bf`; raw argument SHA256
`f8bcf69f4e8beacec49bcc87d2eac84af432f80512e3d0941cf366f45a4a5eb9`.
The19,058-character /19,074-byte argument string ends inside an unfinished neighbour tag. The outer
response is valid JSON; wire-decoded and SDK argument strings agree. Exact request metadata verifies
the original schema/strict flag/prompt, temperature0.7, disabled thinking and unchanged4,000-token cap.
The immediate cause is output allowance exhaustion. Provider internals remain unknown; no adapter
or serialization shortening was found. This is BLK-013, distinct from BLK-014's normally finished
malformed response and BLK-007's accepted index-type deviation.

The adapter rejects the incomplete completion marker before schema parsing. The original author
fallback retains note636 and its generated metadata, with no new links or neighbour updates and
counter632→632. The next metadata call, for `D26:45`, is rejected by the durable halt before logical
admission/transmission. Its journal event has zero attempts; it is not an extra billed request.
All52 transmitted requests settled once, with zero SDK retries or unknown charges. No JSON repair,
semantic retry, output-cap change, further continuation or ablation occurred.

An exact saved-response replay through the real SDK and HTTPX MockTransport reproduces rejection
with one identical mock transmission and sockets disabled. Both historical truncated responses and
their original fallbacks remain unchanged. All51 accepted new response strings equal provider
arguments byte-for-byte;15 new approved D3a deviations/63 validation-copy transformations are retained.
The408 inherited records preserve original origin IDs/indices, including402 prior deviations/1,591
transformations. Combined lineage:417 approved deviations/1,654 transformations and three rejected
length completions. Other schemas and the approved exception remain unchanged.

Post-failure focused regressions pass **62 tests**. Root read-only verification checks all59 protected
historical/new files, the old4,240 attempt/logical rows, nine historical phases, existing claims/edges,
and completed conv-49/conv-50 caches unchanged. The exact two-edge chain retains both ancestor
claims and one halted leaf owner; no extra independent trial is counted. The actual planner rejects
an ablation while full conv-44 is incomplete and rejects a third recovery checkpoint. Independent
failure verification passed and is recorded separately; no successful full-baseline assertion follows from
passing software tests. BLK-013 remains **Open**; BLK-019/020 remain Resolved at their tested control
boundaries.

## Spending and cost-only forecast

All three conv-44 segments count once, including each rejected billed response. Cumulative study:
**USD8.530133 /4,292 settled logical and physical requests**, zero unknown charges. USD33.469867
remains usable under USD42, preserving the USD8 contingency within USD50. The second continuation's
approval is consumed; its unused allocation is not permission for recovery. Costs use the frozen
conservative peak rates and API usage, not invoice totals or assumed cache/off-peak discounts.

| Entire conv-44 lineage stage | Calls | API input tokens | API output tokens | Conservative USD |
| --- | ---: | ---: | ---: | ---: |
| Memory metadata |636 |356,698 |89,882 |0.215159 |
| Shared evolution decision |636 |1,889,928 |1,214,847 |2.025076 |
| QA |0 |0 |0 |0 |
| Total |1,272 |2,246,626 |1,304,729 |2.240235 |

The existing whole-fresh-cell planning scenario totals **USD48.218835**: incurred USD8.530133 +
remaining USD31.688702 + USD8 reserve. Remaining estimates include a hypothetical fresh full
conv-44 USD3.255215 and nine ablations USD28.433487. This deliberately whole-cell scenario is not
an executable restart plan or permission to reclaim the consumed cell. Forecast headroom is
USD1.781165;2× remaining costs exceed the ceiling.

For decision support only,39 remaining turns and158 questions imply394 logical calls and at most
1,182 attempts. The latest26-turn memory costs and completed conv-49/50 QA means estimate a suffix
at USD1.282387; conditional balanced total USD46.246007 including incurred costs, nine ablations
and the reserve. **A third recovery is unsupported and unauthorized.** These point estimates are
not upper bounds, paid approvals or evidence that another4,000-token output will fit. No population
selection or quality result influenced the forecast.

## Stopping boundary and artifact inventory

Stop at the user's explicit provider-failure boundary. The next original turn is `D26:45`;39 turns
and all158 questions remain. Full conv-44 and first-ablation readiness are blocked. No balanced
558-question Full aggregate is reported. A new recovery or controlled protocol amendment requires
an explicit user decision and reviewed safeguards. Raising a cap would also require assessing
comparability with existing4,000-token baselines; no such amendment is made here.

Safe local, Git-ignored evidence (not public download links):

- `artifacts/runs/t8-full-conv44-{r0-20261103,checkpoint-child,checkpoint-grandchild}/`:
  immutable raw requests/responses, approvals, preflights, checkpoint bindings, partial states,
  run journals, summaries and phase inventories; all three distinct failures retained.
- `artifacts/t8/conv44-second-incomplete-20261103/`: `verification.json`, `lineage-stage-costs.json`,
  `cost-only-forecast.json`, independent failure audit and `selected-population-inventory/`.
- `artifacts/t8/offline/conv44-grandchild-length-{reproduce.py,reproducer.json}`,
  length-replay log, post-failure62-test log and read-only failure-verification logs.
- `artifacts/t8/conv44-second-{preservation-before-20261103.json,pre-execution-20261103.json}`,
  fresh `*-preflight-main-*` / `*-plan-main-*`, the immutable grandchild approval and before/after
  ledger backups. The actual ledger remains `artifacts/study-budget.sqlite`, never reset/replaced.
- Engineering evidence under `artifacts/t8/offline/conv44-second-*`: full/focused suites, red/green
  control proofs, exact restoration and independent final review receipts; live/redacted error logs
  under `artifacts/t8/live/`.

Local evidence collection remains authoritative; no new Langfuse tracing/import claim is made.
Repeated bounded continuations preserve research history and costs but do not resolve output growth
or guarantee complete-conversation execution. A short successful fixture is insufficient evidence
that every full-build shared decision fits the frozen allowance.
