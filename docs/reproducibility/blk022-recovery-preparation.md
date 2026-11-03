# BLK-022 — conservative adjudication and checkpoint preparation

3 November 2026. This is preparation for review, **not paid continuation authority**.
The existing Run2 cell remains Incomplete at227 notes/counter226, with zero QA.
The original [incident report](run2-first-cell-incomplete-20261103.md), consumed approval,
raw outputs, ledger rows, checkpoints and Langfuse records remain unchanged. Run1 remains
separate exploratory evidence (USD8.530133;557 protected files).

## Financial finding and authorized intervention

Physical454 received HTTP200, then a body-read `RemoteProtocolError`; its first response body,
usage and provider request ID were not captured. Physical455 was the permitted SDK transport
retry and completed logical454 at `D10:10`. Its valid output finished note227. No evidence
establishes whether454 was billed or unbilled. The provider console requires sign-in; an
aggregate balance, retry usage or Langfuse's partial usage cannot settle that first attempt.
No new provider request was made to investigate it. The underlying network/provider/proxy
cause remains a hypothesis; the lost-body/unknown-charge boundary is confirmed.

| Accounting at preparation | USD |
| --- | ---: |
| Known metered conservative cost,454 settled attempts |0.720433 |
| Unknown first-attempt exposure, retained in full |0.324404 |
| Conservative charged-or-reserved total |1.044837 |
| Original cell allocation, unchanged |5.000000 |
| Maximum remaining cell allocation |3.955163 |

These are peak-rate conservative accounting amounts, not an invoice. No charge is confirmed
unbilled. The user's latest grant permits a **financial-only**, incident-specific upper-bound
adjudication. It does not authorize requests, resume the phase or merge this PR.

`amem_repro/run2_blk022.py` fixes the admission exception to attempt454, its campaign/root
receipt, exact original ledger-row hashes, request/body hashes, unknown status, null usage
and324404-microUSD reservation. The standalone receipt records `unknown_attempts:1` and
`unadjudicated_unknown_attempts:0`; it never rewrites the unknown as settled or zero.
All cell/campaign spending sums still include its full charge. Every other pending/unknown
attempt blocks the next logical admission, including an interrupted request in the new child or
a later cell. Existing bounded genuine transport retries within the same logical call remain
unchanged, each with its own reservation counted against conservative exposure.
Default execution without this exact receipt retains the original blanket unknown-charge stop.

Immutable local preparation:

- `artifacts/blk022-recovery/provider-reconciliation.json`: evidence availability/classification.
- `financial-plan.json`, `financial-approval.json`, `financial-receipt.json` in that directory:
  the plan stays unapproved; the approved copy is explicitly financial-only with
  `paid_execution_authorized:false`. Approval ID `53840a65-ae46-4ecb-b47a-f1c8810727ab`.
- `preservation-before.json`: inventories all332 pre-existing Run2 files and557 Run1 files.

## Exact recovery boundary

The reviewed migration permits changes only to `amem_repro/run2.py` and the new incident module.
It verifies every fingerprinted source against an explicit full Git commit, a fresh network-disabled
runtime preflight, original asset hashes and the unchanged scientific configuration. Author source,
prompts, schemas, parsing, adapter, model/generation policy, action gates, retrieval, index refresh
and scoring bytes stay pinned. The old campaign/source receipt is retained as the parent reference.

The checkpoint verifier checks the sealed archive, all original ledger rows and attempt journal,
227 ordered notes/outcomes, counter226, the exact227×384 float32 stale index and original identity.
It also proves `D10:11` metadata was blocked with zero physical attempts. The already successful
`D10:10` decision is preserved and never regenerated. One-shot checkpoint ownership, leaf matching
and remaining cell/campaign quotas retain the existing duplicate-processing/charging guards.

`artifacts/blk022-recovery/child-plan-v2.json` prepares `run2-full-conv-44-r0-p1`:

| Child property | Value |
| --- | --- |
| Parent | `run2-full-conv-44-r0-p0` |
| Recovery policy | `run2-blk022-exact227-state-v1` |
| Next turn / remaining turns | `D10:11` /448 |
| Questions, original order |158 |
| New logical / physical maxima |1,212 /3,636 |
| Remaining cell cap |USD3.955163 |
| Paid approval | **False** |

No child run directory or checkpoint claim is created by preparation. The original root remains
halted. This exception supports this one preserved prefix; a new unknown charge or another failure
does not inherit an adjudication or authorization. BLK-013 recovery after this exceptional child
requires further reviewed support; it is not silently generalized by this change.

Offline preparation commands (repository root; outputs must be new immutable paths):

```bash
.venv/bin/python -m amem_repro.run2_blk022 verify-adjudication \
  --root "$PWD" --campaign artifacts/run2/frozen/campaign-approval.json \
  --financial-approval artifacts/blk022-recovery/financial-approval.json \
  --output artifacts/blk022-recovery/financial-receipt-REVIEW.json

.venv/bin/python -m amem_repro.run2_blk022 plan-child \
  --root "$PWD" --campaign artifacts/run2/frozen/campaign-approval.json \
  --financial-approval artifacts/blk022-recovery/financial-approval.json \
  --preflight artifacts/blk022-recovery/current-source-preflight-v2.json \
  --assets artifacts/assets \
  --support-reference c8759986745840fe700a6b68ad6f6cd1a2420476 \
  --output artifacts/blk022-recovery/child-plan-REVIEW.json
```

The pinned source fingerprint is
`b423c0cfa4417339def6d8c9302c982d0942fdb69acd43ef14aac3b0970a60d9`.
Any production change requires a new reviewed reference/preflight/plan. These commands expose
planning/verification only. Keep the child unapproved until all remaining gates below are satisfied.
The initial plan/preflight remain preserved as superseded preparation. Review found and fixed one
P2 approval/runtime pin-comparison gap for later fresh cells in `c875998`; four regressions prove
tampered source/preflight pins fail before permit, output or client creation. V2 pins that correction.
The historical `scripts/run2-cell.py` stays frozen as a BLK-013-only launcher; it does not consume
this financial receipt or authorize this recovery. The reviewed executor API is exercised offline.
A separately reviewed, phase-bound launch command is still required with any future paid approval;
do not use the old launcher or alter its frozen hash to start this child.

## Langfuse costs: measured options, no adopted reduction

Read-only billing UI metadata reports Core and2,245 consumed units in the3 November–3 December
period; reporting can lag about an hour. The5,959-unit daily bucket is a different scope. The first
paid phase already contributes1,508 campaign units (1,278 observations +230 traces); subtract that
once when forecasting remaining work. No scores are available because no QA has completed.
[Core pricing](https://langfuse.com/pricing) includes100K units, with advertised additional usage at
USD8/100K. [Billable units](https://langfuse.com/docs/administration/billable-units) count traces,
observations and scores, including SDK-generated Experiment evaluator observations.

The actual pinned SDK5.1.0 was tested offline using production `export_experiments`, an in-memory
exporter, two saved questions and both scoring views. Current imports emit72 observations/4 traces/
58 scores; a scoped filter for successful import-evaluation bookkeeping emits8/4/58. Every score's
value, retained subject/root, experiment identity, prediction/reference and failure provenance are
verified. Injected import errors and generation request/output/usage/retry evidence survive.
This is not fresh cloud GateB evidence, and no production reporting policy changed.

| Opportunity | Explanation and why | Same-volume saving | Effort | Risk |
| --- | --- | ---: | --- | --- |
| One callback returning all existing evaluations | Avoid per-metric callback spans; retain all values |62,496 units /USD5.00 | Small | Error/score association verification needed |
| Scoped successful import-evaluation filter | Keep task/item roots and every error; omit local saved-value bookkeeping |71,424 units /USD5.71 | Small | A broad filter could hide required evidence |
| Suppress future duplicate original Score objects | Values remain in question/scoring outputs and both complete Experiments |31,732 units /USD2.54 | Small | Original trace loses its third score-column copy |
| **Recommend filter + duplicate suppression** | Preserve all original generation/action/retrieval/retry/checkpoint observations and both metric views |103,156 units /USD8.25 | Small focused follow-up | Requires frozen export policy and fresh cloud verification |
| Native one-span import | Removes another SDK wrapper |OnlyUSD0.36 beyond recommended option | Medium | Extra identity/import maintenance; rejected for minimal scope |

Alternatives are not additive except the combined recommendation. Sampling, dropping metrics,
disabling generation tracing and deleting history are rejected. No model calls, metrics, scoring
semantics, scientific settings or authoritative local records would change under the recommendation.

Normal full-campaign forecast: existing design221,508–235,524 units (USD9.72–10.84 overage);
recommended design118,352–132,368 (USD1.47–2.59). Anchoring to current displayed usage and subtracting
the already-exported1,508 once gives119,089–133,105 units / **USD1.53–2.65**. The current provider
point forecastUSD39.056674 already includesUSD1.044837 exposure. Provider + protectedUSD8 + the
usage-anchored recommended service estimate totals **USD48.583794–49.705074** before taxes,
rounding, unrelated/lagged traffic or added recovery/fixture overhead. The upper normal scenario
leaves onlyUSD0.294926; it is not an affordability guarantee. One/two structural continuations per
cell can raise the total aboveUSD50. Keep BLK-009 Investigating.

Recommendation: a separate narrow prospective reporting-policy change and explicit service-fee
allocation decision, followed by secured real-runner GateB/readback and a new cost forecast before
paid execution. No overage allocation, extra ingestion, reduction or cost-policy amendment is
approved or implemented in this PR. Detailed reproducible offline calculations live in
`artifacts/blk022-recovery/langfuse/{options.md,options.json,reproduce.py,reproduce.log,current-usage.json}`.

## Credential security — user action required

Safe masked-key/lifecycle metadata identifies the original unnamed1-November project key pair as
still listed with **No expiration**. Treat it as active and potentially compromised. No authentication
using the exposed value, rotation, replacement-secret access, raw browser snapshot or credential
copy was performed. `artifacts/blk022-recovery/credential-lifecycle-metadata.json` stores only
allowlisted non-secret facts. This is [BLK-023](blockers.md#blk-023).

The user must create a replacement in the project's Settings → API Keys, privately update only
the Langfuse values in local `.env`, verify the correct project using read-only metadata, then
delete the original unnamed1-Nov pair and confirm it is absent. Do not paste secrets into chat,
terminal output, screenshots or commits. Deletion invalidates a key immediately; Langfuse only
shows a newly generated secret once ([official key lifecycle](https://langfuse.com/docs/administration/rbac)).
Use short expiry where appropriate. Rotation is not authorized to the agent by this task.

The operator-only `scripts/safe_service_audit.py` defaults to no network. Its opt-in post-rotation
check invokes only a pinned read-only project-list command against allowlisted official HTTPS hosts,
with a restricted child environment and allowlisted output (`status`, `project_match`, `error_type`).
Untrusted stdout/stderr/errors never reach tool output. Its redactor is for operator copies only;
authoritative requests/responses remain unchanged. For browser work, inspect in-memory DOM data
through allowlisted fields/redaction before tool emission; raw key/settings snapshots remain unsafe.
After privately replacing the values, verify with `.venv/bin/python scripts/safe_service_audit.py
--check-auth --expected-project-id PROJECT_ID`, using the intended project ID from its URL.
Only then delete the original pair and confirm its absence; this task does not run that auth check.

## Verification and remaining gates

Regression evidence covers exact fixed-ledger admission, unchanged unknown charge, refusal of
another unknown, altered prefix/config/source/receipt rejection, duplicate claims, original stale
index bytes and non-repetition of the accepted decision. An isolated copy of the real checkpoint
finishes448 mock turns/158 QA in1,212 mock calls, retaining parent hashes and Degraded lineage,
and carries the same conservative charge into next-cell planning. It is not a paid completion.

Actual-archive tests require private local artifacts and skip in a clean checkout without them:

```bash
AMEM_BLK022_EVIDENCE_ROOT="$PWD" .venv/bin/pytest \
  tests/test_run2_blk022.py tests/test_run2.py \
  tests/test_adapter_budget.py tests/test_budget.py -q
AMEM_BLK022_EVIDENCE_ROOT="$PWD" .venv/bin/pytest -q
```

Final suite/replay/review and preservation evidence is recorded under
`artifacts/blk022-recovery/verification-final.json`: **755 tests/92 subtests pass** in823.04s,
with17 expected warnings. The final operator-helper recheck passes4 tests. Both complete archive
replays at source `b423c0c…` reproduce1,544 requests/568 notes/204 QA and all scientific comparisons
exactly, differing only in implementation label. Standards and Spec reviews are clear after the
two P2 corrections. All557 Run1 and332 pre-existing Run2 files remain byte-identical; the primary
ledger remains454 logical/455 physical calls with no child claim or new paid request.

Before paid continuation: obtain explicit PR
merge authorization; resolve BLK-023; decide/freeze Langfuse cost policy and service-fee allocation;
complete any required fresh visible GateB verification; independently review current-source preflight,
financial receipt and unapproved child plan; obtain a separate phase-bound paid approval. Neither
the old consumed approval nor this financial-only receipt authorizes a transmission.
