# Reproducibility blockers and resolutions

Last reviewed: 4 November 2026. Scope: the FTEC5660 controlled reproduction defined in the
[protocol](experimental-protocol.md), [decisions](decisions.md) and [tickets](implementation-tickets.md).
This tracker records evidence and investigation history; it grants no execution or protocol-change approval.

**Current GPT-4o-mini state:** BLK-025 is Mitigated for one native metadata request
using the third user-supplied key. The fourth actual POST returns HTTP200; independent
OpenRouter generation readback confirms the exact dated model/OpenAI provider, strict
metadata schema and USD0.00006765 charge. All three earlier403 phases/halts and full
USD0.058950 unknown reservation remain unchanged. Conservative campaign exposure is
USD0.059018. No baseline, fifth request or old-charge settlement is released; remaining
compatibility and scientific release gates are outstanding. See
[verified access](gpt4omini-third-key-access-verified-20261104.md).

**Current Run2 state:** Full conv-44 is fully verified as a **Degraded completed lineage** via a
separate reporting acceptance supplement. PR#33 merged `513b44e`; one fresh16-span import and
actual readback verify316 question/view items/4,494 exact scores. Runtime5,097 observations/1,336
traces verify across all three phases. All675 notes/158 questions, original Incomplete receipts,
failed claims/partial scores, both ledgers and1,741 historical files remain unchanged. BLK-024 is
Resolved. Run2USD4.166489 includes unknown454/fullUSD0.324404 reservation; no new model cost or
Langfuse overage. BLK-009 remains Open: original scope pointUSD48.235144 provider cost exceedsUSD42
before service fees. No remaining paid cell, population/order change or contingency use is authorized.
Read [verified completion](run2-conv44-reporting-complete-20261104.md) and
[cost-only alternatives](run2-ablation-affordability-20261104.md).

**Historical collection/export stop:** PR#31 merged as `66d3ffa`; the single authorized p2 collected all675
notes/counter673 and158 QA, but the sealed phase is **Incomplete** on BLK-024: Langfuse dropped
both oversized Experiment span batches and Experiment visibility did not verify. All1,771 runtime
observations/623 traces verify; original import claim/IDs/receipt/halt are preserved. P2 added534
requests/USD1.796479, with zero new malformed outputs or unknown charges. Total Run2 exposure is
USD4.166489, including unknown454's fullUSD0.324404 reservation. BLK-014 is Mitigated at the narrow
verified author-fallback boundary, not repaired at the provider. BLK-009 is reopened Open: measured
Full-stage sensitivity projectsUSD48.235144 provider cost, aboveUSD42 usable before service fees.
No re-import, paid recovery, next cell or contingency use is authorized. Read
[the verified collection/export outcome](run2-conv44-collected-export-blocked-20261103.md).

**Historical Run2 stop:** GateA/GateB and the reviewed freeze passed; PR#26 is merged.
The first Full conv-44 cell is Incomplete at227 notes/zero QA after BLK-022 (HTTP200 body-read
failure, valid SDK retry, unresolved first usage). USD0.720433 settled plus USD0.324404 retained
reservation =USD1.044837 exposure. No later cell/recovery ran. BLK-009 also needs service-fee
allocation after the user's Core upgrade. [Stopping report](run2-first-cell-incomplete-20261103.md).
The approved financial exception retains unknown454 and full exposure. The new grant permits one
exact D10:11 child after release checks; rotated credentials/current-source cloud GateB are verified.
BLK-009 is Mitigated for this bounded cell, while whole-campaign affordability remains conditional.
BLK-023 is Resolved. No extra cell, recovery child, service allocation or contingency use is authorized.
Read [the current observation/recovery release](run2-observation-policy.md).

| ID | Blocker | Status | Affected phase | Evidence |
| --- | --- | --- | --- | --- |
| [BLK-001](#blk-001) | Original structured-output contract needs provider adaptation | Mitigated | T2, T5 | D2–D3; PR #9; BLK-007 |
| [BLK-002](#blk-002) | Published ablation runners are missing from the frozen release | Mitigated | T6–T8 | [T7 gates and full-mode proof](t7-action-gates.md); PR #16 |
| [BLK-003](#blk-003) | Paper and released benchmark populations differ | Accepted Limitation | T1, T5, T8, report | Paper §4.1; dataset hash; full manifest |
| [BLK-004](#blk-004) | Historical adversarial overlap scores reward a different reference | Mitigated | T4, T5, T8 | Author fix `b31a1dd`; scoring tests |
| [BLK-005](#blk-005) | Original cache provenance cannot isolate the planned study | Mitigated | T3, T5–T8 | Runner cache keys; cache rejection tests |
| [BLK-006](#blk-006) | Local runtime readiness required verified assets and active lock markers | Resolved | T5 local preflight | Initial/final preflight receipts; local T5 commit |
| [BLK-007](#blk-007) | DeepSeek strict function returned string connection indices | Mitigated | T5 compatibility; downstream T6–T8 | Archived violations; audited complete D9a fixture |
| [BLK-008](#blk-008) | Local tokenizer equivalence to hosted DeepSeek is unverified | Open | T4, T5, T8 token reporting | Pinned tokenizer recipe; final preflight receipt |
| [BLK-009](#blk-009) | Four-condition affordability needs measured cost control | Open | Remaining Run2 campaign | [Measured-stage cost sensitivity](run2-conv44-collected-export-blocked-20261103.md#spending-and-remaining-study-forecast) |
| [BLK-010](#blk-010) | Released retrieval default differs from paper category settings | Accepted Limitation | T5, T8, interpretation | D6; runner default; paper Table 8 |
| [BLK-011](#blk-011) | T5 execution is not connected to Langfuse tracing/export | Resolved | Run2 runtime/Experiments; Run1 limitation retained | [Actual8K runner/cloud verification](run2-observability-verification.md) |
| [BLK-012](#blk-012) | Failed usage settlement triggers SDK regeneration | Resolved | T5 and later paid phases | Terminal settlement guard; SQLite fault/retry regressions |
| [BLK-013](#blk-013) | Shared decision exhausts frozen output allowance, including D9a4,000 | Open | T8 conv-44 second child incomplete; ablations blocked | [third conv-44 exhaustion](t8-conv44-second-recovery-incomplete-20261103.md); all failed phases retained |
| [BLK-014](#blk-014) | Normally finished strict function contains malformed JSON | Mitigated | Verified Run2 author fallback; provider reliability remains limited | [Reviewed fallback and exact continuation](run2-conv44-collected-export-blocked-20261103.md) |
| [BLK-015](#blk-015) | Historical intermediate states/query vectors were not recorded | Mitigated | T6–T7 replay claims | [Replay gate and oracle provenance](t6-replay.md) |
| [BLK-016](#blk-016) | Index text keys trigger credential-field rejection | Resolved | T8 conv-49 artifact persistence | Exact real-cache byte/state proof;519-test suite |
| [BLK-017](#blk-017) | Critical faults can be hidden behind tolerated failure paths | Resolved | Run2 recovery eligibility; Run1 guards retained | Verified715-test suite, independent audits and preserved red/green proofs |
| [BLK-018](#blk-018) | Paid frontier ignores a prior failed/unconfirmed completion | Resolved | Run2 phase admission; Run1 guards retained | Verified715-test suite, independent audits and preserved red/green proofs |
| [BLK-019](#blk-019) | Recovery provenance can accept altered ancestry or unchecked edges | Resolved | Run2 immutable receipt seal; Run1 guards retained | Verified715-test suite, independent audits and preserved red/green proofs |
| [BLK-020](#blk-020) | Failed attempt admission enters SDK retry handling | Resolved | Paid-request admission | Terminal reservation boundary; real-SDK faults/genuine retries verified |
| [BLK-021](#blk-021) | Run2 ledger path can alias immutable Run1 accounting | Resolved | Run2 storage isolation | Verified715-test suite, independent audits and preserved red/green proofs |
| [BLK-022](#blk-022) | HTTP200 body-read failure leaves an unknown charge after a successful SDK retry | Mitigated | Run2 Full conv-44 lineage | [Full reservation retained through p2](run2-conv44-collected-export-blocked-20261103.md) |
| [BLK-023](#blk-023) | Langfuse project credential exposed in a tool snapshot | Resolved | Secure Run2 observability/continuation | Replacement authentication/readback; original pair absent |
| [BLK-024](#blk-024) | Full-cell Experiment export exceeds local OTLP batch size | Resolved | Run2 Full conv-44 reporting | [Exact recovered readback and acceptance](run2-conv44-reporting-complete-20261104.md) |
| [BLK-025](#blk-025) | OpenRouter rejects first dated GPT-4o-mini compatibility request with HTTP403 | Mitigated | Third-key metadata access only; baseline not started | [One actual native success; all previous failures retained](gpt4omini-third-key-access-verified-20261104.md) |

**Run1 final status (3 November 2026):** PR#22 merged as `5ddc96e` after613 offline tests/92 subtests
and clear independent Standards/Spec reviews. The single authorized second conv-44 continuation
stopped Incomplete at `D26:44`, another HTTP200/`length`/4,000-token BLK-013 failure. It added26 turns:
636 notes/counter632, zero of158 QA. New52 requests/USD0.122276; entire conv-44 lineage1,272/
USD2.240235; cumulative USD8.530133/4,292 settled requests, zero unknown charges. Original fallback
and all inherited failures/audits remain intact; next metadata transmission was blocked. Root and
independent offline audits verify exact stale index/prefix, both ancestors, old ledger rows and
unchanged conv-49/conv-50 baselines.62 post-failure tests pass. All grants are consumed;39 turns and
158 QA remain. A third recovery, restart, ablation or scientific change is unsupported/unauthorized.
First-ablation readiness remains blocked. See the
[verified second-continuation failure and forecast](t8-conv44-second-recovery-incomplete-20261103.md).
BLK-019/020 remain Resolved at their verified software boundaries; BLK-013 remains Open.

**Historical engineering status:** PR#20 merged as `3d0e04a`; the single USD3-authorized conv-44
child also stopped Incomplete, at `D26:18`:186 new turns,610 total notes/counter607, zero of158 QA.
BLK-013 recurred with HTTP200/`length` and4,000 output tokens. Child372 requests/USD0.702421;
full conv-44 lineage1,220 requests/USD2.117959; cumulative USD8.407857/4,240 settled requests,
zero unknown charges. All274 inherited failure records and402 total D3a deviations remain intact.
Both failed responses/partial states and completed conv-49/conv-50 baselines are preserved.
The two previous grants are consumed. A subsequent grant now permits exactly one second continuation
after engineering/review/merge and preflight, under USD3/446 logical/1,338 physical limits. See the
[latest authority](decisions.md#authorization--second-pinned-conv-44-continuation). At this engineering
checkpoint support is implemented and offline-verified; merge, fresh immutable approval and live
execution remain pending. First-ablation planning still rejects.
No third recovery, restart, ablation or scientific change is authorized. See the
[verified child failure and cost-only forecast](t8-conv44-recovery-incomplete-20261103.md).
BLK-019/020 corrections pass613 tests/92 subtests and independent reviews. They are Resolved at
the software-control boundaries; BLK-013 provider output exhaustion remains Open. No new paid
continuation has executed at this engineering checkpoint.

**Historical bounded grant:** the user authorized recovery engineering/review/merge and one
USD3/818-logical/2,454-attempt child. That grant funded only the failed child above and cannot be
reused. See [consumed authority](decisions.md#authorization--exact-conv-44-checkpoint-engineering-merge-and-one-child).

**Historical paid hold (2 November2026):** T8 full conv-49 exhausted D9a's4,000-token shared-decision
allowance at `D22:2`. BLK-013 is reopened. The incomplete run preserves413 notes/counter411,
zero QA,826 settled requests/USD1.413246,270 D3a deviations/1,066 transformations. Cumulative study
cost is USD4.439045/2,436 settled attempts, zero unknown charges. Its consumed approval cannot
authorize recovery; no conv-44 or ablation phase has started. A separate recovery/protocol decision
is required before any further paid collection. [Investigation and evidence](t8-execution.md#paid-hold--blk-013-recurrence).

Historical readiness checkpoints, retained chronologically below: the checkpoint child completed conv-50 (568 notes/204 QA), Degraded, with
the original failed evolution and all D3a deviations retained. The parent remains immutable and
Incomplete. All approvals are consumed; cumulative study cost is USD3.025799. BLK-009 is Mitigated
by the cost-only fallback forecast (USD42.762234 including USD8), with uncertainty still requiring
cost monitoring. BLK-014/BLK-007 are Mitigated, not restored provider guarantees. BLK-013 is resolved
under D9a for this conversation; other contexts may exceed the cap. BLK-008 limits token-count claims
and BLK-011 tracing remains optional/unwired. BLK-012's terminal guard remains verified. See the
[baseline outcome](t5-conv50-baseline-20261101.md) before further decisions. T6's offline gate is
implemented; T7's four gates and full-mode equivalence are verified in [PR #16](https://github.com/alistairkung/A-mem-reproducibility/pull/16).
T8 and further paid collection remain unstarted and separately gated.
Latest authority: T8 engineering/paid main collection is now authorized within the existing ceiling;
see [T8 record](t8-execution.md). No T8 transmission has occurred at this checkpoint. BLK-016 was
found offline and must pass final tests/review before paid collection. Recovery remains separately gated.
Pre-paid review also found BLK-017: injected provider-identity/journal failures allowed subsequent mock
transmissions. Paid collection is held until terminal handling, failure evidence and independent rechecks pass.
BLK-018 additionally requires receipt publication and SQL frontier release to be coordinated before
any next-phase transmission; a green non-concurrent fault suite is insufficient.
Verified update: T8 source `ae23e291` resolves BLK-016/017/018;519 tests/92 subtests, final runtime
preflight and both independent reviews pass. The original ledger/cache remain unchanged before
transmission. Historical hold records above are retained; see [the paid execution record](t8-execution.md)
for current phase approvals and actual outcomes.
Issue closure, mitigation or unspent allocation is not permission for a paid run or recovery.

## Maintenance and evidence conventions

Keep IDs stable; append dated events under **Resolution attempts**, preserving earlier outcomes and
rejected alternatives. Update the index whenever a status changes. Use **Open** for an unresolved gap,
**Investigating** when evidence is being examined, **Mitigated** for a verified control with remaining
limitations, **Resolved** only for the explicitly verified failure, and **Accepted Limitation** only
where an approved decision bounds the claim. A successful mock is not proof of live compatibility.
State missing evidence explicitly. Keep long logs and secrets out of this document.

Published implementation evidence is in [PR #9](https://github.com/alistairkung/A-mem-reproducibility/pull/9),
merged as `f02c798b439feaf314333f716080a843e851c7db`. Safe local artifact paths below are relative to the
repository root, ignored by Git, and **not public download links**. Their presence and recorded hashes
were checked during this backfill. Preserve them with the study; a fresh clone alone does not contain them.

Two verified local commits are not yet published and therefore have no GitHub links:

- `502b376d331dffcddcb325785dfefad154074242`: T5 preparation, assets, spending controls and offline tests.
- `dad8908cbae546db02d8c74e925b1f2caf253b11`: first compatibility report and observed-failure regression.

References such as `502b376:amem_repro/preflight.py` identify Git objects, retrievable with `git show` in
this research workspace. Do not treat their absence from a fresh clone as published implementation evidence.
Historical discovery dates below are backfilled from the 1 November decision record; finer timestamps
are unavailable unless an experiment receipt supplies them.

## BLK-001

- **ID:** BLK-001
- **Title:** Original structured-output contract needs provider adaptation.
- **Status:** Mitigated
- **First observed:** 2026-11-01, discovery/D2–D3 and T2.
- **Category:** Provider compatibility
- **Expected behaviour:** Preserve the four original JSON schemas, prompts and parser inputs while substituting DeepSeek.
- **Observed behaviour:** The original OpenAI path uses `response_format=json_schema`; DeepSeek's documented response-format options do not expose that contract directly. Forced strict functions require a separate adapter. Mechanical submission works, but enforcement failed in BLK-007.
- **Evidence:** [Original controller and schemas](../../memory_layer.py), [answer/query schemas](../../test_advanced.py), [adapter](../../amem_repro/adapter.py), [contracts tests](../../tests/test_contracts.py), D3, [DeepSeek API reference](https://api-docs.deepseek.com/api/create-chat-completion/), PR #9.
- **Root cause:** Confirmed API-interface difference. This does not establish why the provider later violated a submitted schema.
- **Impact:** T5 cannot equate offline translation with reliable live output; model substitution remains a cross-model reproduction.
- **Options considered:** Adopted an isolated strict-function translation returning original argument strings. JSON-only output weakens schema guarantees; the robust pipeline changes the baseline. Neither is an approved substitute. Original OpenAI support was retained.
- **Resolution attempts:**
  - 2026-11-01, T2 `82692f7`: extract frozen contracts and test unchanged request/argument semantics offline; passed.
  - 2026-11-01, approved T5 fixture: five metadata and four decision outputs passed; the next decision violated the integer contract. See BLK-007.
  - 2026-11-01, authorized D9a fixture: all 18 metadata, 18 shared-decision, four query and four answer calls completed. Seven shared decisions needed the approved D3a validation-copy policy; other fields/contracts remained strict and all original argument strings verify.
  - 2026-11-01, authorized conv-50 pilot on `c659856`: the 263rd shared decision has malformed JSON despite HTTP200 / `tool_calls` and output below its cap. It is rejected and the phase halts; see BLK-014. Small-fixture success does not establish long-run reliability.
  - 2026-11-01, merged PR #14 and authorized checkpoint child: all 568 turns/204 QA complete in a degraded lineage. All four contracts/settings and 1,543 accepted argument strings verify unchanged; the historical malformed decision remains rejected and preserved, not accepted as strict compliance. See [baseline outcome](t5-conv50-baseline-20261101.md).
- **Final resolution or limitation:** Functional provider compatibility is verified for the full smoke fixture under explicit D3a/D9a controls. Strict-provider enforcement itself remains unreliable; no alternative parser or schema was introduced. This is not full-pilot or benchmark validation.
- **Verification:** PR #9 supplies offline contracts; `artifacts/runs/compatibility-d9a-20261101/` and `artifacts/compatibility-d9a-verification.json` now supply complete live fixture evidence. Query/answer generation and both saved-prediction scoring views succeeded without metric failures.
- **Research significance:** A provider-compatible request interface does not establish equivalent structured-output guarantees or equivalent benchmark behavior.

## BLK-002

- **ID:** BLK-002
- **Title:** Published ablation runners are missing from the frozen release.
- **Status:** Mitigated
- **First observed:** 2026-11-01, architecture discovery/D1 and D7.
- **Category:** Reproduction fidelity
- **Expected behaviour:** Runnable author configurations corresponding to Table 3's neither, linking-only and full conditions.
- **Observed behaviour:** The reviewed `f9a173d` tree supplies original/robust runners, not independently configurable author ablations. The original `_evolve` shares one decision and executes both action types; strengthening also rewrites new-note tags.
- **Evidence:** [Paper Table 3](https://arxiv.org/html/2502.12110v11), [frozen memory implementation](../../memory_layer.py), [original runner](../../test_advanced.py), D7–D8, [T7 / #7](https://github.com/alistairkung/A-mem-reproducibility/issues/7).
- **Root cause:** Confirmed omission in the reviewed frozen release. Whether historical ablation code exists elsewhere is unresolved; no claim of an exhaustive search of all author repositories is made.
- **Impact:** We cannot claim exact reconstruction of unavailable author ablation code or isolate pure graph links from metadata enrichment.
- **Options considered:** D7 adopts gates at existing strengthening/neighbor-update boundaries after baseline/replay. Removing shared decisions, optimizing counters or substituting robust code would change the controlled experiment and was excluded.
- **Resolution attempts:**
  - 2026-11-01, discovery: traced shared decisions, action boundaries and counter/consolidation semantics; D7–D8 approved.
  - 2026-11-01, ticket review: T6/T7 remain open; no ablation gates or equivalence results exist.
  - 2026-11-02, separately authorized T7 engineering after T6 merge `87f34d7`: derive only two Boolean guards from the verified frozen `_evolve` AST, bind per instance, retain parsing/validation/action bodies/counting/consolidation, and record condition/actions in run and cache provenance. Initial90 offline tests pass; mandatory reference/candidate archive replays and independent reviews are in progress. No paid ablation has run.
  - 2026-11-02, Spec review of `84ec320`: find P2 observational mislabelling of rejected valid-JSON positive responses as gate-suppressed. Reproduce deterministically (three ablated cases fail, full case passes), then condition suppression reporting on the original successful positive counter increment. Retain raw proposals and provider/evolution failures; change no acceptance, parsing or memory logic. Regression/re-review results will be appended after verification.
  - 2026-11-02, correction `a591ea8`: all96 action tests, mandatory103 T6 portable tests and complete429-test/92-subtest offline suite pass. Standards and Spec re-reviews report no remaining findings. First frozen-reference and actual full-mode candidate archive replays independently match all1,544 calls/568 states/204 QA/both scoring views/376 failure records. Final reviewed-code replay receipts are pending; no paid or ablated live run occurred.
  - 2026-11-02, final reviewed-code fresh processes: `artifacts/replays/t7-reviewed-{reference,candidate}/verification.json` independently pass unchanged T6 oracles, all requests/states/consolidations/checkpoints/retrieval/predictions/scoring and376 logical failure/audit records. Direct receipt comparison differs only by implementation label and verifies both run source fingerprints equal current source (`artifacts/t7-equivalence-comparison.json`). Both are Degraded, with zero network/paid calls and unchanged original run/cache/ledger hashes. See [runbook and evidence](t7-action-gates.md), PR #16.
- **Final resolution or limitation:** Mitigated by our four operational action gates and verified full-mode equivalence, preserving the frozen author reference. The historical author ablation implementation remains unavailable; these are not verified copies. No paid ablation or comparative performance claim exists yet; T8 is separately gated.
- **Verification:** All16 action/configuration combinations, valid negatives, disabled-action positives, failures and99→100 are covered within96 action tests. Mandatory T6 gate103 tests; complete suite429 tests/92 subtests. Both final full archive gates and direct receipt/current-source comparison pass, with clear Standards and Spec re-reviews. Local logs: `artifacts/t7-reviewed-action-tests.txt`, `artifacts/t7-mandatory-portable-tests.txt`, `artifacts/t7-reviewed-offline-suite.txt`.
- **Research significance:** A published ablation table does not uniquely specify its executable intervention; operational definitions must disclose coupled metadata changes.

## BLK-003

- **ID:** BLK-003
- **Title:** Paper and released benchmark populations differ.
- **Status:** Accepted Limitation
- **First observed:** 2026-11-01, dataset discovery/T1.
- **Category:** Data
- **Expected behaviour:** A traceable mapping from the paper's evaluated population to released conversation/question identities.
- **Observed behaviour:** Paper §4.1 describes 7,512 LoCoMo QA pairs; the checked-in file contains 10 conversations, 5,882 turns and 1,986 QA. The historical evaluated question mapping is unavailable.
- **Evidence:** [Paper §4.1](https://arxiv.org/html/2502.12110v11), [released dataset](../../data/locomo10.json), [full manifest](../../manifests/full.json), [manifest tests](../../tests/test_manifests.py), D1/D4/D10a. Dataset SHA256: `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4`.
- **Root cause:** Confirmed discrepancy; the historical selection/release process causing it is unknown. Do not assume the paper evaluated exactly this file.
- **Impact:** Exact population matching and direct attribution of score differences to the algorithm alone are unsupported.
- **Options considered:** Approved released-data reproduction with fixed original IDs; conditional stratified fallback selected independently of performance. Replacing data or reconstructing unverified historical splits was not adopted.
- **Resolution attempts:**
  - 2026-11-01, T1 `5aaa5f6`: freeze counts/hash, original indices and full/fallback/smoke/pilot selections.
  - 2026-11-01, review `6c2439b`: replace duplicated records with compact manifests; tests reproduce all four original expanded hashes.
- **Final resolution or limitation:** D1/D4 accept a controlled released-data reproduction, not recovery of the historical population. D10a fallback remains conditional, not activated by this tracker.
- **Verification:** Dataset hash/counts rechecked during backfill; manifest regeneration/selection tests and PR #9 preserve identities. Historical equivalence remains unverified.
- **Research significance:** Dataset version and question identities define the experiment as much as method names do.

## BLK-004

- **ID:** BLK-004
- **Title:** Historical adversarial overlap scores use a different reference.
- **Status:** Mitigated
- **First observed:** 2026-11-01, scoring audit/D11; upstream repair already present in the frozen release.
- **Category:** Evaluation
- **Expected behaviour:** Adversarial answer quality rewards correct abstention from unsupported facts.
- **Observed behaviour:** The author fix describes older category-5 evaluation against the trap answer. Current `QA.reference` uses the abstention reference; legacy mode deliberately restores the old reference. Higher legacy overlap need not indicate better factual quality.
- **Evidence:** [Author repair `b31a1dd`](https://github.com/alistairkung/A-mem-reproducibility/commit/b31a1dddf56f87ec762cce3539418602d7e2ffb1), [QA.reference](../../load_dataset.py), [score_prediction](../../utils.py), [dual rescoring](../../amem_repro/scoring.py), [scoring parity tests](../../tests/test_scoring.py), D11.
- **Root cause:** Confirmed reference-policy change in author source/history. The author's statement connecting legacy mode to paper results is not independent verification against historical saved predictions.
- **Impact:** Category-5 overlap scores and paper comparisons can be misinterpreted; failed metric computations must also remain distinguishable from genuine zeros.
- **Options considered:** Adopted corrected primary and separately labelled legacy views from identical predictions; retain `adversarial_correct` separately. Optimizing for legacy overlap or replacing the evaluator was rejected.
- **Resolution attempts:**
  - Upstream `b31a1dd`: introduce corrected reference, legacy flag and adversarial diagnostic.
  - 2026-11-01, T4/review: add immutable dual rescoring, failure notices and original/instrumented metric parity tests; passed offline.
  - 2026-11-01, completed conv-50: both saved-output views use identical 204 predictions/QA IDs without metric failures or new model calls. Corrected overall F1/BLEU-1 0.482178/0.435322; historical 0.417370/0.371892. Category-5 adversarial correctness is separately 29/46. These local results do not recover historical author predictions.
  - 2026-11-02, T8 pre-paid review: a re-sealed synthetic archive with a changed scoring-wrapper hash was accepted because only the underlying author scorer was checked. Correction `84d354a` pins the wrapper and runtime/asset/dependency sources plus bound preflight, without rescoring predictions. Thirty-one comparison regressions and the final519-test/92-subtest suite pass; actual original204-QA import remains unchanged.
- **Final resolution or limitation:** Scoring interpretation is mitigated through explicit policies. Completed local conv-50 QA and both views are now available; the authors' historical saved predictions remain unavailable.
- **Verification:** PR #9 verifies unchanged author math, aggregates and saved predictions without model calls. The failed fixture completed no QA, so it adds no live scoring evidence.
- **Research significance:** Reproducing a numerical score can reproduce a scoring defect; factual quality and historical compatibility require distinct views.

## BLK-005

- **ID:** BLK-005
- **Title:** Original cache provenance cannot isolate the planned study.
- **Status:** Mitigated
- **First observed:** 2026-11-01, cache audit/D5 and T3.
- **Category:** Reproduction fidelity
- **Expected behaviour:** Reuse only complete state from the exact population, configuration, condition and independent memory-build repetition.
- **Observed behaviour:** Original cache paths use backend/model/refresh and sample index, with a memory-version warning. They do not verify the study's full provenance. This is a demonstrated design risk, not evidence that an actual experiment was contaminated.
- **Evidence:** [evaluate_dataset cache handling](../../test_advanced.py), [CacheStore/build_identity](../../amem_repro/artifacts.py), [runner](../../amem_repro/runner.py), [cache rejection tests](../../tests/test_artifacts.py), D5, [T3 / #3](https://github.com/alistairkung/A-mem-reproducibility/issues/3).
- **Root cause:** Confirmed insufficient original cache identity/completion checks for the proposed multi-condition study.
- **Impact:** Reused or partial state can change causal comparisons and construction-cost estimates; cached QA repetitions are not independent memory builds.
- **Options considered:** Adopt isolated fingerprints, complete note/index bundles, completion markers and rejection on mismatch. Reusing author filenames alone or treating cached QA as new builds was excluded.
- **Resolution attempts:**
  - 2026-11-01, T3 `70646d7`: add atomic verified caches, canonical snapshots and complete/degraded/incomplete records; offline roundtrip/tamper/mismatch tests passed.
  - 2026-11-01, T5 failure: preserve five notes/index rows in an explicitly partial artifact, not a completed reusable build.
- **Final resolution or limitation:** Offline provenance controls are in place. Four-condition live isolation remains to be exercised after T7; no contamination incident has been established.
- **Verification:** Named tests reject incomplete/mismatched/duplicate builds and preserve links/index/counters. T5's incomplete phase is unusable for progression.
- **Research significance:** Cache reuse is an experimental intervention; provenance and build independence must be part of the design.

## BLK-006

- **ID:** BLK-006
- **Title:** Local runtime readiness required verified assets and active lock markers.
- **Status:** Resolved
- **First observed:** 2026-11-01, T5 local preflight; resolution is scoped to the tested local environment.
- **Category:** Infrastructure
- **Expected behaviour:** The locked Python 3.11 environment loads original embeddings/metrics from verified local files with network disabled.
- **Observed behaviour:** The initial receipt falsely expected NumPy 2.5.4 while the active lock correctly installed 2.4.6. Metadata-only model pins were also insufficient proof of runtime readiness. An import-time LiteLLM price-map request was encountered during socket-denied checking.
- **Evidence:** Local `artifacts/preflight-initial.json` (exact version mismatch), `artifacts/preflight-final.json` (ready/runtime OK, 257 verified files), `502b376:amem_repro/preflight.py`, `502b376:tests/test_preflight.py`, `502b376:config/assets.json`, locked `uv.lock`. The earlier import traceback was observed in the session but not archived as a standalone file.
- **Root cause:** Confirmed inactive lock entry overwrote the active version; local assets needed explicit preparation. LiteLLM's import can fetch a price map and load dotenv in development mode; package settings control these side effects.
- **Impact:** False readiness rejection, uncontrolled setup downloads or missing metrics could block execution or produce failure-derived zeros.
- **Options considered:** Adopt active-marker checks, exact HF/NLTK recipes and offline/import environment controls. Silent metric substitution or claiming dependency metadata alone proved runtime success was excluded.
- **Resolution attempts:**
  - 2026-11-01, initial preflight: rejected valid NumPy environment; no runtime verification occurred.
  - 2026-11-01, local T5 implementation/review: fix marker selection, verify files/dependencies and disable incidental network/dotenv initialization; offline regressions passed.
  - 2026-11-01, final real preflight: original embedding/search and every author metric passed with sockets disabled.
- **Final resolution or limitation:** Resolved for macOS arm64/Python 3.11.17, using the prepared assets. Portability to another environment requires its own preflight; model-loader warnings were retained, not hidden by changing metrics.
- **Verification:** Final receipt records CPU embeddings shape 2×384, no metric failures, self-match F1/BLEU-1=1 and BERTScore/SBERT≈1. Hosted tokenizer parity is a separate unresolved blocker (BLK-008).
- **Research significance:** A lockfile and model repository revision are prerequisites, not evidence of an executable offline evaluation environment.

## BLK-007

- **ID:** BLK-007
- **Title:** DeepSeek strict function returned string connection indices.
- **Status:** Mitigated
- **First observed:** 2026-11-01, T5 `compatibility-20261101`, completed at 06:33:12 UTC with incomplete status.
- **Category:** Provider compatibility
- **Expected behaviour:** The unchanged schema requires `suggested_connections` items to be integers, including under strict-function translation.
- **Observed behaviour:** The fifth decision returned `"suggested_connections": ["2", "3"]`. HTTP 200, `finish_reason=tool_calls`, 640 completion tokens under max_tokens=1,000: the JSON was complete but violated the requested integer contract. The request used `strict:true`, the beta endpoint and the exact original schema.
- **Evidence:** Safe local `artifacts/compatibility-20261101-reproducer.json` contains exact redacted request/response and violations; `artifacts/runs/compatibility-20261101/events.jsonl`, `phase.json`, `summary.json` and `partial-memory.json` retain the run. Report/regression: `dad8908:docs/reproducibility/t5-compatibility-20261101.md`, `dad8908:tests/test_contracts.py`. [Frozen schema/parser](../../memory_layer.py); [provider strict-mode guide](https://api-docs.deepseek.com/guides/tool_calls/).
- **Root cause:** **Unknown.** Confirmed provider-contract violation; server-side cause is not established. The prompt's quoted neighbor-ID example may influence generation (**hypothesis**), but does not explain strict-mode enforcement. Existing `as_index` accepts numeric strings; that does not make the returned JSON schema-valid.
- **Impact:** The original failure blocked compatibility before query/answer generation. The completed D9a fixture now verifies the approved mitigation; remaining provider-contract deviations must stay visible in every future run. This is not a baseline or accuracy result.
- **Options considered:** Preserve evidence and stop. Coercion, weakening the schema, skipping validation, changing prompts/settings or switching pipelines were not implemented and require explicit decisions. Repeating the request is paid recovery, not covered by the unspent cap.
- **Resolution attempts:**
  - 2026-11-01, approved fixture: ten physical requests, no retries; five metadata/four decision payloads valid and one decision invalid. Next metadata event was blocked before transmission, not an eleventh request.
  - 2026-11-01, offline investigation: verify serialized strict/beta/schema settings and independently confirm both type errors with `Draft202012Validator`; add rejection/unchanged-input regression.
  - 2026-11-01, archive check: artifact hash inventory verifies; follow-up suite records 132 tests/71 subtests passed. No recovery request or proposed repair was executed.
  - 2026-11-01, focused offline investigation: reconstruct the exact pre-decision prompt and pass the raw response to the original parser. Its state and embedding documents match an integer-only control; both counters advance 3→4, while strict rejection stays 3. Added 38 characterization tests; branch suite 92 tests/32 subtests passes. See the [proposal and schema audit](blk-007-offline-investigation.md). A field-scoped validation-copy policy is proposed only; no adapter fix or model request was made. All nine original evidence files remain byte-identical.
  - 2026-11-01, user-approved D3a implementation/offline tests (`48bc2d1`): add opt-in `canonical-index-strings-v1` for canonical ASCII strings in this field only. Validate a copy and return raw arguments unchanged; retain strict default, record hashes/type violations and mark affected runs degraded. Full offline suite: 238 tests/71 subtests passed, including the 44-call mocked phase and frozen-parser state/retrieval/counter comparisons. SDK MockTransport replay of the exact failing response preserves the serialized request and argument bytes. See [implementation evidence and remaining gate](blk-007-compatibility-review.md). Twenty historical evidence files remain byte-identical; no model requests, recovery or pilot occurred.
  - 2026-11-01, separately authorized fresh phase `compatibility-d3a-20261101` on merged PR #11: the fifth shared decision's string indices were admitted with raw/copy hashes and unchanged parser input. One completion/two items were audited and retained after later failure. The sixth decision truncated at the frozen output limit (BLK-013), so the run is incomplete and BLK-007 remains Investigating. No automatic recovery or pilot followed.
  - 2026-11-01, authorized `compatibility-d9a-20261101`: all 18 turns/four original QA completed; seven shared-decision responses/19 items needed D3a. Every raw/returned argument string and audit hash verifies. Run status is degraded solely by those approved deviations, with no other failures, 44 requests/no retries and USD0.053118 conservative phase charge. Safe evidence: `artifacts/compatibility-d9a-verification.json` and the immutable run directory.
  - 2026-11-01, authorized conv-50 pilot: 176 accepted deviations/661 string indices are fully audited; all 525 accepted argument strings match provider output bytes. These audits and partial memory survive the later malformed-JSON abort (BLK-014). The run is Incomplete rather than successful/degraded, and no exception was extended to malformed JSON.
  - 2026-11-01, completed conv-50 child: 198 new shared-decision deviations/809 indices plus 176 inherited deviations/661 indices remain audited. All accepted argument strings are unchanged; completed lineage is Degraded and no other schema field was relaxed.
- **Final resolution or limitation:** **Mitigated, not a restored provider guarantee.** The approved narrow policy works in the complete D9a fixture while strict integer-schema violations still occur. The original five-note/zero-QA failure and its USD0.005851 charge remain unchanged, as does the subsequent truncation failure. Hosted weights/future reliability remain unverified; all future arms must retain the same explicit controls and degraded classification for accepted deviations.
- **Verification:** Complete live fixture evidence now supplements offline parser-equivalence tests: 18 notes/outcomes, four ordered original questions, unchanged arguments on all 44 calls and both scoring views from identical predictions without metric failures. Source bundle `02dc368e77f1a1e36d7d2deeffe1e6b0c9a7e8de9e715864852566e704ad7285`; no benchmark or pilot success is inferred.
- **Research significance:** A documented strict API contract and HTTP success do not establish reliable schema compliance; preserving rejected outputs is essential to an honest reproduction diary.

## BLK-008

- **ID:** BLK-008
- **Title:** Local tokenizer equivalence to hosted DeepSeek is unverified.
- **Status:** Open
- **First observed:** 2026-11-01, T1 asset discovery and T5 tokenizer preparation.
- **Category:** Evaluation
- **Expected behaviour:** Retrieved-context token counts have a verified relationship to the hosted model's tokenizer; API prompt usage is distinguished from local observations.
- **Observed behaviour:** A pinned HF tokenizer loads locally, but hosted parity is unproven. The asset record reports nine added-special-token differences against the official downloadable archive; this does not identify which tokenizer the hosted model uses.
- **Evidence:** `502b376:config/assets.json`, `502b376:amem_repro/preflight.py`, local `artifacts/preflight-final.json`, [token measurements](../../amem_repro/measurements.py), D6, [official token-usage documentation](https://api-docs.deepseek.com/quick_start/token_usage/).
- **Root cause:** Unknown hosted tokenizer/version and prompt serialization. Recorded file comparisons do not independently verify hosted behavior; a standalone raw comparison log was not retained.
- **Impact:** Local context counts cannot be described as exact hosted/billed token counts. This does not justify altering context or retrieval.
- **Options considered:** Implemented pinned local estimates labelled `exact=False`, retaining API usage separately. Claiming parity from repository names or changing context to fit an estimated budget was excluded.
- **Resolution attempts:**
  - 2026-11-01, T1: pin tokenizer candidate metadata; no live parity evidence.
  - 2026-11-01, T5: verify/load candidate bytes and record official-archive comparison limitations; final preflight passes. Ten actual requests supplied API usage, but no QA retrieval was reached.
- **Final resolution or limitation:** Estimates are available; hosted equivalence remains open. Fixture approval acknowledged uncertainty and did not revise the protocol's token-count claims.
- **Verification:** Local tokenizer loading/counting tests pass. No documented hosted-context parity test has succeeded.
- **Research significance:** Reproducible local tokenization and provider-authoritative usage are different measurements; report their scope explicitly.

## BLK-009

- **ID:** BLK-009
- **Title:** Four-condition affordability needs measured cost control.
- **Status:** Open
- **First observed:** 2026-11-01, budget discovery/D10–D10a.
- **Category:** Cost
- **Expected behaviour:** Demonstrate that incurred plus remaining four-condition cost and USD8 contingency fit the USD50 ceiling before choosing scope or main execution.
- **Observed behaviour:** The USD250/three-full-repetition proposal was rejected. One full-data build per arm entails 62,944 nominal calls; the fallback entails 18,480. The original pilot stopped on BLK-014; its authorized child now supplies complete representative usage. All 10 conversations project above USD50; the frozen fallback fits the point estimate, not the 2× sensitivity diagnostic.
- **Evidence:** D10/D10a and [protocol budget table](experimental-protocol.md), [population manifests](../../manifests/full.json), [T5 / #5](https://github.com/alistairkung/A-mem-reproducibility/issues/5), local `artifacts/study-budget.sqlite`/phase receipt, `502b376:amem_repro/budget.py`, `502b376:amem_repro/forecast.py` and their tests.
- **Root cause:** Confirmed missing representative usage evidence. Token growth, retries and condition-specific evolution prevent converting call counts or tiny-fixture costs directly into a reliable study total.
- **Impact:** Run2 retains its frozen three-conversation/four-condition design. This cell spentUSD4.166489 conservatively, leavingUSD37.833511 of theUSD42 execution pool andUSD8 protected. A cost-only sensitivity based on all actually collected Full stages projectsUSD48.235144 provider total before Langfuse fees, exceeding usable funding byUSD6.235144. Other conditions are unmeasured; do not silently resize the population, consume reserve or treat the older proxy estimate as renewed affordability evidence.
- **Options considered:** Adopt progressive caps and exact performance-independent fallback. Three repetitions are optional; dropping difficult questions, tuning on results or changing settings to fit the cap was excluded.
- **Resolution attempts:**
  - 2026-11-01, D10/D10a: approve conditional scope and one initial build per arm, not USD250 spending.
  - 2026-11-01, local T5: test durable per-transmission reservations, cumulative USD42 usable allowance and cost-only forecasts offline.
  - 2026-11-01, first fixture: retain conservative USD0.005851 for ten requests, including the invalid response; no pilot or scope decision followed.
  - 2026-11-01, authorized conv-50 pilot: retain USD0.739432/526 requests, including the malformed response. Cumulative USD0.806717 leaves USD41.193283 usable after USD8 contingency. No QA or late-construction usage exists; the original forecast command rejects the incomplete inventory. Preserve partial stage measurements without extrapolating them into a full/fallback scope decision; see [pilot budget record](t5-pilot-conv50-d9a-20261101.md#budget-status-and-forecast-limitation).
  - 2026-11-01, completed checkpoint lineage: full 568-turn/204-QA usage and known costs support the cost-only forecast before quality inspection. Credit conv-50 once; retain 1,610 study requests/USD3.025799. Recommend the frozen fallback with one build per arm and no scope tuning. No further execution occurred. See `artifacts/checkpoint-child-cost-forecast.json`.
  - 2026-11-02, separately authorized T8: activate D10a's fixed fallback and credit full conv-50 once. Eleven remaining one-shot cells have a pooled additional ceiling USD38.974201, per-phase ceiling USD10 and unchanged usable study ceiling USD42; caps are not additive authority. Close an unused unbound baseline-permit path, retain global-cap/concurrency assertions through valid historical pilot fixtures, and verify archived main approvals/claims so an older ledger cannot reset spending. Cost-only just-in-time plans reconcile all remaining balanced cells. Final519 tests/92 subtests, preflight and independent reviews pass before paid transmission.
  - 2026-11-03, new Run2 planning: deduplicated Run1 stage costs provide an initial USD38.764609 execution point estimate under a separate USD42 allowance/8 reserve. An offline candidate regression shows forecasts must replace the4K proxy with observed Run2 Full stage means once available, then use each measured condition's own means; preserve `artifacts/run2/offline/forecast-red.txt`. Implementer corrected this priority and is verifying it before paid execution. No primary quality result informs affordability or population choice.
  - 2026-11-03, Run2 capacity check while the first bounded cell is active: official Langfuse pricing counts traces, observations and scores. The normal14-metric design generates93,744 score units alone (hard minimum80,352 if every result used the12-metric empty-answer fallback), before traces/observations and extra category5 correctness. Initial authenticated UI showed Hobby50K; the user then changed to Core, independently verified in the billing UI with a new3 November–3 December period and zero displayed consumption (usage refresh lags about60minutes). Core includes100K units; published excess rate isUSD8/100K. Actual incremental fees remain unmeasured and must enter the post-cell affordability check before later cells; no agent upgrade, fee authorization or contingency use is inferred. Preserve `artifacts/run2/observability-capacity.json`; the current cell retains itsUSD5 provider limit.
  - 2026-11-03, corrected offline Core capacity forecast: actual SDK5.1.0 imports create an observation for every metric evaluator, including a no-value callback. Offline SDK/memory-exporter and real-runner counts verify221,508–235,524 normal campaign units, aboutUSD9.72–10.84 incremental usage beyond100K, excluding subscription/tax/rounding. Two continuations per cell give a structural249,788-unit/USD11.98 scenario, not a bound. These fees plus the initialUSD38.764612 provider estimate exceedUSD42 usable if charged together. Core itself was upgraded by the user; overage allocation remains unapproved. Reopen affordability for a precise financial decision; do not drop metrics, spans, conversations or reserve to hide it. Evidence: `artifacts/run2/langfuse-unit-forecast.{md,json}` and its offline script/log. Current Run2 stops separately on BLK-022 with no extra service fee asserted.
  - 2026-11-03, BLK-022 follow-up: current-period read-only UI reports2,245 units (lagged), versus1,508 already-exported paid campaign units. Actual SDK offline import comparison verifies all58 fixture scores and retained root/subject/identity/error associations under a proposed scoped successful-import-evaluation filter. Suppressing future third-copy original Score objects while retaining question/scoring outputs and both complete Experiments gives a normal usage-anchored119,089–133,105-unit/USD1.53–2.65 overage forecast. Provider point estimate +USD8 reserve +service estimate totalsUSD48.583794–49.705074 before extra recovery/fixture/tax/other traffic, leaving insufficient safety margin for a completion guarantee. No reporting change, extra ingestion, fee grant or sampling is implemented. A new frozen policy, secured real-runner cloud verification and explicit fee-allocation decision remain necessary. Evidence: `artifacts/blk022-recovery/langfuse/` and [preparation report](blk022-recovery-preparation.md).
  - 2026-11-03, separately authorized essential-export policy: implement `run2-audit-essential-v1`, retain every scientific generation/action/retrieval/error observation and both complete Experiments, suppress successful import-evaluator bookkeeping and third-copy original Scores, and replace only the redundant wire envelope with a hash/local locator. Actual source265094c0… GateB verifies131 success/18 failure observations and112 scores; deterministic equivalence and both independent audits pass. A30K original-observation fail-closed ceiling bounds this one child below included100K capacity (conservative79,833 units including imports/existing/verification allowance). Its remaining provider pointUSD2.584628 fits residualUSD3.955163. Updated normal whole-campaign provider/service/reserve pointUSD48.731314–49.798114 is conditional with little headroom; no next cell, extra service allocation or contingency use is authorized. See [policy/recovery release](run2-observation-policy.md) and `artifacts/run2-observed-recovery/cost-policy-forecast-final.json`.
  - 2026-11-03, sole observed child consumed:678 settled requests/USD1.325173; total Run2 exposureUSD2.370010 including the originalUSD0.324404 unknown. Readback verifies2,048 observations/483 traces, billing shows5,166 lagged-period units/USD0 draft usage; no added service commitment. Unchanged cost-only forecast givesUSD39.257657 provider total, withUSD1.460438 proxy for534 remaining calls in this cell. Carrying the preceding normal-service range plusUSD8 reserve givesUSD48.932297–49.999097, excluding any new recovery and other growth. This historical-service scenario is not a refreshed bound or completion guarantee. Whole-campaign affordability remains conditional; no subsequent cell or recovery is authorized. [Outcome and evidence](run2-conv44-recovery-incomplete-20261103.md).
  - 2026-11-03, consumed566-note p2: all109 remaining turns/158 QA collect withinUSD1.796479/534 attempts. Full lineageUSD4.166489 includes the original unknown. Measured Full-stage sensitivity givesUSD48.235144 provider total,USD56.235144 including protected reserve before service fees. Read-only Core UI shows8,657 lagged-period versus16,878 daily-bucket units andUSD0 draft usage; counters have different scopes and are not summed or treated as an invoice. Reopen affordability; no population choice used quality, no new service allocation/contingency/further cell. [Outcome and evidence](run2-conv44-collected-export-blocked-20261103.md).
- **Final resolution or limitation:** Reopened Open after full local model collection. Provider cost sensitivity alone exceeds the usableUSD42 pool; service fees/recovery growth are additional uncertainties. The official frontier remains Incomplete on BLK-024 and cannot silently promote this cell. A separate cost-only scope/budget decision is necessary before any further paid cell.
- **Verification:** Release784 tests/92 subtests, independent financial audit and immutable ledger reconcileUSD3.842085 settled plusUSD0.324404 unknown/full-reserved. `artifacts/run2-fallback-recovery/measured-stage-cost-sensitivity.json` uses675 metadata/675 decisions/158 queries/158 answers, and separately recordsUSD44.068655 remaining11-cell proxy cost. The current official forecast remains preserved as an Incomplete-frontier/Run1-proxy view; neither estimate is an upper bound.
- **Research significance:** Construction, QA, retries and failed attempts all consume budget; controlling spending and estimating scientific study feasibility are separate problems.

## BLK-010

- **ID:** BLK-010
- **Title:** Released retrieval default differs from paper category settings.
- **Status:** Accepted Limitation
- **First observed:** 2026-11-01, retrieval audit/D6.
- **Category:** Reproduction fidelity
- **Expected behaviour:** Identify retrieval settings actually used for the published ablation comparison.
- **Observed behaviour:** The released runner defaults to `retrieve_k=10`; paper Table 8 lists GPT-4o-mini category values 40/50. The paper does not explicitly bind those values to Table 3. Actual context also includes linked entries and duplicates.
- **Evidence:** [Runner arguments/retrieval](../../test_advanced.py), [paper §4.2 and Table 8](https://arxiv.org/html/2502.12110v11), D6, [passive retrieval observations](../../amem_repro/measurements.py), [measurement tests](../../tests/test_measurements.py).
- **Root cause:** Confirmed documented/default difference; exact historical Table 3 retrieval settings remain unknown.
- **Impact:** A released-default reproduction cannot claim verified retrieval-setting equivalence to published GPT-4o-mini results; k alone is not a context-token budget.
- **Options considered:** D6 fixes k=10 across arms, construction neighbors 5 and refresh disabled, with observational expansion/token reporting. Category tuning, deduplication and truncation were excluded.
- **Resolution attempts:**
  - 2026-11-01, discovery: compare paper settings with runner defaults; approve D6's explicit released-default deviation.
  - 2026-11-01, T4: test passive counts/context preservation in the mocked original-agent fixture. The failed live fixture reached no QA retrieval.
- **Final resolution or limitation:** Accepted deviation, not historical-setting recovery. All future arms retain identical approved settings.
- **Verification:** Configuration/bridge tests verify k=10 and disabled refresh; retrieval tests preserve context and duplicate expansion. No evidence establishes the paper's exact Table 3 settings.
- **Research significance:** Matching an algorithm name and a nominal k does not guarantee matching the model's effective context or published experimental setting.

## BLK-011

- **ID:** BLK-011
- **Title:** T5 execution is not connected to Langfuse tracing/export.
- **Status:** Resolved
- **First observed:** 2026-11-01, user review of the incomplete T5 fixture.
- **Category:** Infrastructure
- **Expected behaviour:** The next approved run records construction failures and later QA experiments in the configured Langfuse project, without changing model/evaluation behavior.
- **Observed behaviour:** No trace was sent by the first fixture. T4 has an optional saved-QA importer, but the T5 entrypoint invokes neither that exporter nor phase/generation tracing. The fixture produced no QA rows.
- **Evidence:** [Reporting code](../../amem_repro/reporting.py), `502b376:amem_repro/phases.py`, [readiness record](langfuse-readiness.md), safe local `artifacts/blk007-offline-investigation/langfuse-verified.json` and synthetic trace `a8e18a92ccdc5a873f595010f1e3c283`.
- **Root cause:** Confirmed missing runtime connection. Private project credentials are present and authentication/ingestion succeed; this is not an authentication-failure finding.
- **Impact:** Local records remain available, but Langfuse cannot show actual construction/generation failures until the runner is wired. A future successful QA export alone would still omit pre-QA failures.
- **Options considered:** Recommend an explicit observation-only phase/generation wrapper at existing seams plus the existing saved-QA exporter. Credentials alone, automatic SDK replacement during compatibility investigation, or fabricated historical traces were not adopted.
- **Resolution attempts:**
  - 2026-11-01: privately load the project's Langfuse settings; verify no different-project environment shadowing and successful CLI authentication.
  - 2026-11-01: send/flush one synthetic configuration span with SDK 5.1.0; read it back and verify name, type, input/output and empty model usage. No LLM was invoked and no old benchmark data was exported.
  - 2026-11-01: document the minimal runner connection and its offline checks for review. That runtime change is not implemented.
  - 2026-11-01, successful D9a fixture: verify the existing saved-QA exporter with both scoring views. Eight question traces were imported and read back with correct identities/policies, saved predictions, original status/deviation count and cost metadata; no model requests or local artifact/ledger changes. See [reporting verification](langfuse-readiness.md). This mitigates missing experiment results after successful QA, while pre-QA/automatic construction tracing remains unwired.
  - 2026-11-02, T8 preparation: configured project CLI authentication/readback succeeds (HTTP200). An isolated temporary npm cache avoids an unrelated local cache-permission failure. Filtered evidence `artifacts/t8-langfuse-project-readback.json` retains no headers/credentials. No new result export or live generation tracing is claimed by this authentication check.
  - 2026-11-03, Run2 candidate implementation `e3a598a`/wire-input correction `3e99da7`, integrated at `01debed`: passive actual-runner lifecycle/generation/action/retrieval/scoring/failure hooks, complete safe wire request, exact raw argument wrapper and explicit cloud-verification receipt.164 regressions/12 subtests and23 latest observer/reporting tests/5 subtests pass. A preliminary18-turn/four-Q real-runner fixture with actual local assets and44 HTTPX-mocked generations emits130 cloud observations and56 score IDs, with zero network LLM calls. Modern CLI observes all130; a session-score query returns zero even after delay, while exact-ID query returns all56. Preserve both readbacks rather than inferring failed score delivery; the server's internal filtering explanation is unverified. Scope score verification to bounded exact IDs. Evidence: `artifacts/run2/gate-b/engineering-4k-20261103/`. This preliminary check uses Run1's4K profile and is explicitly not the final8K/source-bound Run2 gate; failure capture, saved-result Experiments import and final replay/readback review remain pending.
  - 2026-11-03, final8K GateB attempts: the first actual-executor fixture verifies two retained length failures/recoveries and all observations, then rejects Experiments because the API's experiment `name` is SDK `run_name`, distinct from SDK logical `name`. Preserve attempt1 unchanged. Correction `414b97b` records both names and compares the exact run name; old incomplete receipts reject without guessing/reimport. All four fully indexed saved snapshots pass offline characterization and two partial snapshots still reject. A fresh attempt2 completes24 synthetic turns/one QA across three phases,50 MockTransport calls, with all observations and both Experiments independently fetched. A separate real-assets18-turn/four-Q fixture verifies130 observations/56 scores, exact traced/untraced ordered replay, raw argument preservation and unchanged results under tracing failure. Both bind source `184544748e86f608286a031a86bd53519e5c95b7f6b3eee0ffae8e2ba2e6e2fe`; no billable LLM request or primary Run2 ledger exists. See [verification report](run2-observability-verification.md) and `artifacts/run2/gate-b/{executor-8k-20261103-attempt2,real-assets-8k-20261103-attempt1}/`. Final independent audit/full-suite/archive replay remain pending.
  - 2026-11-03, final Run2 verification: source184544748e86f608286a031a86bd53519e5c95b7f6b3eee0ffae8e2ba2e6e2fe passes715 offline tests/92 subtests (17 expected warnings), both complete original/full-candidate archive replays and clear independent Standards/Spec audits. Current-source runtime preflight passes with sockets disabled. No paid Run2 call or Run1 artifact change occurred. Final evidence: `artifacts/run2/offline/final-full-suite-20261103.txt`, `archive-equivalence.json`, `{spec,standards}-final.md`; GateB source-bound raw proof is separately preserved.
  - 2026-11-03, observed recovery gate: preserve an initial wrong-directory fixture and a second cloud readback failure caused by an absent optional nested journal ID. Keep the verifier strict; use proper immutable source-specific Run2 directories and omit only that absent export-only ID (paid IDs remain). Final265094c0… gate matches all131 successful/18 simulated-length-error observations, eight items/112 scores and source/policy identities. Traced/replay/tracing-failure memory/results match, with zero network LLM calls. Every original request/response/local journal remains unchanged; the passive policy is now verified end-to-end. Evidence: `artifacts/run2/observed-recovery/gate-b/265094c0a6484105b3922862633b7063fd5a4f917663349fdf720658e0864fbf/`.
  - 2026-11-03, full-cell readback: p2 verifies all1,771 actual runtime observations/623 traces. Final158-question saved-result import fails because two local OTLP batches exceed64MiB; track distinct scaling failure BLK-024 rather than undoing verified runtime wiring or claiming full Experiment visibility. No automatic re-import.
- **Final resolution or limitation:** Runtime wiring is verified for Run2 at source184544748e86f608286a031a86bd53519e5c95b7f6b3eee0ffae8e2ba2e6e2fe: real-assets traced/untraced replay, actual executor with two successive checkpoint continuations, exact remote observations/Experiments and independent factual audits all pass. Run1 remains historically unwired; no retrospective traces or primary results are fabricated. Every paid Run2 phase must still verify actual cloud visibility before release.
- **Verification:** Source-bound GateB receipt and122-file hash inventory are preserved under `artifacts/run2/gate-b/`; final offline suite715 tests/92 subtests passes, both complete568-note/204-Q archive replays match and Standards/Spec audits independently verify six actual cloud proofs. See [verification](run2-observability-verification.md).
- **Research significance:** Valid credentials and an installed observability SDK do not establish that the executed research path emits traces, especially when it fails before evaluation.

## BLK-012

- **ID:** BLK-012
- **Title:** Failed usage settlement triggers SDK regeneration.
- **Status:** Resolved
- **First observed:** 2026-11-01, final narrow review of [PR #11](https://github.com/alistairkung/A-mem-reproducibility/pull/11), head `cc0b36c`.
- **Category:** Cost
- **Expected behaviour:** A local accounting failure after a received response preserves its maximum reservation and raw output, stops execution without another model request, and prevents unapproved continuation. Transport retries must not become semantic retries caused by local ledger failures.
- **Observed behaviour:** Fault injection into the first settlement SQL update or commit after HTTP200 makes the SDK send a second request. It returns the second generated output; the phase remains unhalted and accepts a subsequent logical generation. The first maximum reservation is retained: no unsafe charge release was observed.
- **Evidence:** [Transport settlement](../../amem_repro/adapter.py), `_recording_transport` line399 at `cc0b36c`; [SQLite transaction/settlement](../../amem_repro/budget.py); `test_failed_settlement_retains_charge_and_stops_without_sdk_regeneration` in [SDK budget tests](../../tests/test_adapter_budget.py). Safe local review artifacts: `artifacts/pr11-final-review/focused-pytest.txt` and `settlement-reproducer.json`.
- **Root cause:** **Confirmed.** An ordinary `sqlite3.OperationalError` escapes the transport's `finally` block. The SDK interprets it as a connection failure and retries a generation whose response was already received. The exception bypasses the transport's error-recording handler; successful retry leaves no terminal phase stop. SQLite rollback itself conservatively preserves the original reservation.
- **Impact:** Before correction, an unexpected second model output replaced the first, incurred another charge and changed the effective generation/failure process. Unknown reservations still counted toward the caps; no ceiling overrun was observed. This blocked paid execution and PR readiness until verified.
- **Options considered:** Proposed only: retain the reservation/raw response, turn settlement failure into non-retryable `BudgetStop`, and prevent continued use of the permit even if persisting the stop fails. Retrying the completed generation or releasing its reservation is inappropriate. No production fix was made during the review.
- **Resolution attempts:**
  - 2026-11-01: inspect existing interruption, restart, unknown-usage, cap and SDK retry tests before adding cases. Independently reproduce both direct settlement-write failure and actual failed SQLite commit using HTTPX MockTransport; no live service or model request.
  - 2026-11-01: add two failing fail-closed regressions. Both observe two transmissions where one is required; the initial charge remains reserved. Separate memory/question-abort tests and strengthened postprocessing assertions verify BLK-007 deviation persistence without modifying production code.
  - 2026-11-01, approved focused P1 correction: `PhasePermit.settle` rolls back failed accounting, latches a terminal state, separately persists the halt and raises `BudgetStop` outside the SDK's `Exception` retry machinery. Attempt records retain the received payload plus error classes. No provider request policy or author code changed.
  - 2026-11-01: both original update/commit regressions pass. Additional halt-write/commit fault cases reject continuation and old-approval restart even while SQLite cannot persist the halt; once writes recover, the original reason persists. Genuine 429/503/read-error retries still succeed under unchanged SDK limits and retain unknown reservations. Full offline suite: 247 tests and 71 subtests passed. Safe evidence: `artifacts/blk012-fix/{red.txt,focused.txt,full-pytest.txt}`.
  - 2026-11-01, correction commit `d0e0bf9`: repeat Standards and Spec reviews independently found no remaining actionable defect. Independent safety subsets passed 26 tests and 111 tests/39 subtests respectively. Author source, contracts, scientific configuration and dependency lock remain unchanged; review covered spending, raw/strict contracts and persistence after later errors.
- **Final resolution or limitation:** Terminal accounting failures cannot regenerate a response or reuse the permit. The original reservation and response evidence survive; phase halt is committed separately. If SQLite remains unwritable, an irreversible local latch and the already-durable one-shot phase claim prevent continuation/restart; summaries explicitly report `halt_persisted:false` and the persistence error type. This does not pretend a failed halt write succeeded. Historical initial reproducer (two attempts, USD0.315785, no halt) and original paid-run evidence remain unchanged.
- **Verification:** Update/commit fault tests prove one transmission, USD0.315773 retained reservation, original response, durable halt and denied continuation/restart. Halt-write/commit failure tests verify the local fallback and truthful persistence diagnostics; genuine transport/provider retry tests remain green. SQLite transaction and SDK integration tests run with sockets disabled; no paid request was used to verify the fix.
- **Research significance:** Durable cost reservation and correct retry classification are separate requirements. A financially conservative ledger can still cause scientifically uncontrolled resampling when local accounting exceptions enter a provider's retry machinery.

## BLK-013

- **ID:** BLK-013
- **Title:** Shared decision exhausts the frozen output allowance (historical1,000; D9a4,000).
- **Status:** Open
- **First observed:** 2026-11-01, fresh authorized T5 phase `compatibility-d3a-20261101`, merged source `167470b`.
- **Category:** Provider compatibility
- **Expected behaviour:** Complete original-schema output within frozen stage limits: historical D9 fixture and, after D9a, full selected-conversation builds with all designated QA.
- **Observed behaviour:** The sixth shared decision returned HTTP200, `finish_reason=length`, exactly 1,000 output tokens and incomplete tool-argument JSON ending inside a neighbor-tag string. Twelve physical requests were charged; the next metadata attempt was blocked before transmission. Six notes were preserved, zero QA completed.
- **Evidence:** [Readiness report](baseline-readiness.md); safe local `artifacts/runs/compatibility-d3a-20261101/` and `artifacts/compatibility-d3a-20261101-truncation-reproducer.json`. The exact request retains max_tokens=1000, temperature 0.7, disabled thinking, original schema/prompt. Failed arguments hash `26708080e3e5a0edb08a3f62d9e4265d3eebab088015c6b45526e88211037a9e`.
- **Root cause:** **Confirmed immediate cause:** output allowance exhausted before valid JSON completion. **Supported explanation, not a universal guarantee:** fuller neighbor payloads and repeated metadata enrichment increase output demand; observed decision token counts were 149, 262, 409, 569, 778, 1000 for zero through five neighbors. No adapter truncation or altered generation cap was found. This differs from BLK-007's complete-but-wrong-type response.
- **Impact:** Historical truncation charges remain intact. D9a completed the fixture/conv-50; conv-49 completed only through a separately approved degraded checkpoint lineage. The original full conv-44 phase and both authorized continuations exhausted4,000 tokens before QA. T5 selected-scope completion and T8 balanced comparison remain blocked; no conv-44 quality/population conclusion follows from its636-note partial build.
- **Options considered:** Proposed controlled D9 amendment: raise only shared-decision output allowance uniformly across arms, with updated hard reservations and a separately approved fresh phase. An unchanged-settings retry also requires separate approval and may recur. Prompt/schema/parser repair or automatic semantic retries are outside the approved protocol and were not attempted.
- **Resolution attempts:**
  - 2026-11-01: retain full received request/response, partial memory/index, settled costs and audited D3a deviation. Verify phase inventory, original 19 historical files and the first ten ledger attempts/charge.
  - 2026-11-01: exact offline SDK MockTransport replay confirms identical request, truncated response preservation, rejection, terminal halt and blocked subsequent transmission. Pilot planning against the incomplete receipt rejects before execution.
  - 2026-11-01: independent offline source/output audit confirms output growth and original max_tokens=1000. Prepare a proposed 4,000-token shared-decision amendment plus one further USD2 phase for explicit decision; neither change nor new phase has been executed.
  - 2026-11-01, approved D9a implementation `4e7f82b`: shared-decision-only 4,000-token wire limit, exact stage-cap approval bindings, stage-specific reservations/settlement checks and forecast bounds. Full suite passes 268 tests/92 subtests. Independent Standards (71 tests/60 subtests) and Spec (132 tests/60 subtests) reviews found no material defect. Fresh network-disabled runtime preflight passes. The new live phase is still pending at this checkpoint; no outcome is inferred from offline success.
  - 2026-11-01, D9a approved after PR #12 merge (`5078459`): implement output policy `d9a-shared-decision-4000-v1`, raising only shared decisions to 4,000 tokens and retaining 1,000 elsewhere uniformly across arms. Preserve prompts/schemas/parsers/temperatures. Bind stage caps and update conservative reservations to 319,373 microUSD for shared decisions / 315,773 for other attempts; retain the USD2 hard phase and USD42 usable study caps. One fresh 44-call/132-attempt phase is authorized after offline verification, review and preflight; no extra probes planned. New live verification has not occurred and no approved execution plan exists yet.
  - 2026-11-01, authorized D9a live verification: `compatibility-d9a-20261101` completed 18 shared decisions, with maximum observed output1,572 tokens and no `length` finish or rejected response. All 44 physical/logical calls completed, with zero retries/unknown charges; stage bounds and original parser input verify. Full state and both scoring views are retained. The phase cost USD0.053118 and cumulative study cost USD0.067285/66 requests remain in the durable ledger. The exact conv-50 plan is prepared as `approved:false`, not executed.
  - 2026-11-01, authorized checkpoint child on merged PR #14: all remaining 305 shared decisions complete without truncation, maximum output 3,851 under 4,000; combined conv-50 reaches 568 notes/204 QA. The original below-cap malformed response is BLK-014, not length exhaustion. D9a adequacy is now verified for this conversation, not all other conversations/conditions.
  - 2026-11-02, authorized T8 run `t8-full-conv49-r0-20261102` on reviewed source `ae23e291` (launch commit `881b35d`): the413th shared decision, request `8b6bea1e-bc8e-40bf-8b38-22627f0edf4a`, returns HTTP200/`finish_reason=length`,4,000 completion tokens,6,551 prompt tokens and unfinished JSON in a neighbor tag. Saved wire/SDK arguments agree (SHA256 `51be35f7cefb5a2da8623dcf23ea54bdb8fdc3f8e7f4c3c5d2e2d1e66cd1b962`). No request/prompt/schema/adapter truncation was found. This is length exhaustion, not BLK-014's normally finished malformed output.
  - 2026-11-02, offline saved-response replay: identical SDK request, unchanged frozen schema and exact raw response reproduce terminal rejection with one mock transmission and zero network requests. All825 accepted argument strings match provider bytes;270 D3a deviations/1,066 transformations survive. The author fallback retains the413th note/failed `D22:2` evolution with counter411 and no neighbor changes; the next metadata call is blocked before transmission. Partial413-row stale index and phase inventory verify;826 real attempts settle USD1.413246, zero retries/unknown charges. Preserve `artifacts/runs/t8-full-conv49-r0-20261102/`, `artifacts/t8/live/full-conv49-r0.log` and `artifacts/t8/offline/conv49-length-{reproduce.py,reproducer.json}`. No recovery, output repair or later cell was executed.
  - 2026-11-03, separately approved engineering only, implementation `1ffa184`/integration `a5695be`: add a pinned conv-49 verifier and one-shot child ownership using existing checkpoint/phase/permit/import interfaces. Restore413 notes/counter411 and the exact stale index, retain the failed evolution, resume only at `D22:3`, and account for parent/child once. The 26 focused tests and related119-test/60-subtest group pass; actual-parent read-only restoration leaves the ledger byte-identical. Full integrated checks/reviews and the final unapproved plan remain pending at this checkpoint. No paid continuation or schema/cap change is authorized.
  - 2026-11-03, final engineering verification: **545 tests/92 subtests pass**; both independent reviews are clear, each re-running26 focused tests. Current-source preflight passes with sockets disabled, source `0b2287b19626da56d7bd567c6073ac15000a4f73c98e9b3510ca18d5ba6faaa9`. `artifacts/t8/offline/conv49-checkpoint-verification.json` proves exact real-state restoration and unchanged parent/ledger bytes; unapproved execution rejects before client/claim/schema creation. `artifacts/t8/conv49-checkpoint-plan.json` is an **unapproved** USD3/584-call/1,752-attempt proposal. Cumulative spending stays USD4.439045, zero new paid calls. Safe continuation support is verified offline; output-cap exhaustion is not resolved and paid recovery remains unauthorized.
  - 2026-11-03, user-authorized merge and one USD3 child: PR#17 merged normally as `78ac46b`; fresh545 tests/92 subtests and64 focused tests pass, final Standards/Spec reviews clear, no failed required check or rule bypass. New parent-bound approval `a550491a-d027-4752-a959-3b6bcdc1e0f6` restored413 notes/counter411/stale embeddings and resumed `D22:3`. Child `t8-full-conv49-checkpoint-child` completed96 turns and196 QA,584 requests/USD1.850853, zero retries/unknown charges. It added only72 D3a deviations/276 transformations and no new processing/metric failure. Final lineage509 notes/counter507, Degraded; original natural consolidation500 occurred at `D25:13`. All historical rows/parent/conv-50 hashes verify unchanged; costs combine once. See `artifacts/t8/conv49-baseline-20261103/{verification,additional-integrity}.json` and [the outcome](t8-conv49-baseline-20261103.md). No further paid phase ran.
  - 2026-11-03, one explicitly authorized Full conv-44 phase after PR#18 merge `f78215e`: fresh preflight/provenance/cache/ledger gates pass. Run `t8-full-conv44-r0-20261103` stops at424th decision/`D18:21`, HTTP200, `finish_reason=length`,4,000 output and3,633 prompt tokens, request `4368db7f-c980-429d-aaec-ed36c55ee7e5`. Exact wire/SDK arguments agree (SHA256 `955c9f38b5d56d459ca2f0bc8cb7214572490dca4ba365d5fb97427cdcf9f108`); unchanged schema/request and one MockTransport replay reproduce rejection with sockets disabled. Preserve424 notes/counter422, failed evolution and424×384 float32 stale index; next metadata blocked before transmission. All847 accepted argument strings,271 D3a deviations/1,055 transformations, original baselines and3,020 historical ledger rows verify unchanged. All848 real attempts settle USD1.415538, zero retries/unknown charges; cumulative USD7.705436/3,868. No QA or quality metrics, no complete cache, and no recovery/ablation executed. See [outcome](t8-conv44-incomplete-20261103.md), `artifacts/t8/offline/conv44-length-reproducer.json` and `artifacts/t8/conv44-incomplete-20261103/verification.json`. The one-phase grant is consumed.
  - 2026-11-03, subsequent explicit engineering/merge/one-child authorization: implementation `563e8f4` extends the existing support seams to the second fixed parent under `blk013-conv44-checkpoint-v1`, without author/provider/config/scoring changes. It pins424 notes/counter422 and exact stale state, resumes only `D18:22`, and bounds the child to USD3/818 calls/2,454 attempts. The old conv-49 path remains supported. Existing exclusive-parent rejection now occurs before inserts, including after child completion; a safe SQLite uniqueness exception found by a regression was replaced by the expected terminal rejection. Combined old/new checkpoint, budget, SDK-budget and comparison checks pass146 tests/60 subtests. Real-parent restore/export and embedding bytes verify exactly,43 protected files/ledger remain unchanged, and unapproved execution rejects before client/claim creation. Fresh network-disabled preflight passes under source `eea7acf5953ecea73deb7fdd5b406c77171f76ef6a4544e5c149346b5e89e6c4`. See [recovery gates](conv44-checkpoint-recovery.md) and `artifacts/t8/offline/conv44-checkpoint-verification.json`. Complete suite/final reviews/merge remain pending at this checkpoint; no child has executed.
  - 2026-11-03, final integrated engineering verification for PR#20:570 offline tests/92 subtests pass (16 intentional SDK metadata warnings), plus146 focused tests/60 subtests. Both independent Standards/Spec reviews are clear after correcting obsolete detailed tracker wording. Source remains `eea7acf5953ecea73deb7fdd5b406c77171f76ef6a4544e5c149346b5e89e6c4`; actual-parent restore/preflight and the unapproved USD3/818/2,454 plan verify,43 protected files and the USD7.705436 ledger remain unchanged. Evidence: `artifacts/t8/offline/conv44-recovery-{full-suite-20261103.txt,focused-legacy-20261103.txt,spec-review.md,standards-review.md}` and `conv44-checkpoint-verification.json`. Merge and the single approved live child remain pending at this checkpoint; no provider-cap resolution is claimed.
  - 2026-11-03, authorized live child after PR#20 merge `3d0e04a`: post-merge preflight passes and fresh approval `ad09fe3d-5401-4898-a64e-294491a6dc64` executes once. Exact424-note/counter422/stale-index restore resumes `D18:22` and processes186 new turns, preserving all274 inherited failure records. Natural consolidation500/600 occurs at `D21:7`/`D26:10`. Shared decision `D26:18` then returns HTTP200/`length`,4,000 completion/5,566 prompt tokens, request `fb87d9c6-26e5-47e4-9a29-f9d2fca78d3b`; raw argument SHA256 `34c0c645fa306274c597b1af10e6bde40071d49e1db588158d51984123c96a0a`. Original fallback retains note610/counter607; next metadata transmission is blocked. Child372 calls/USD0.702421, zero retries/unknown charges; cumulative USD8.407857/4,240. Exact offline MockTransport replay reproduces rejection with unchanged request/schema and no network. All371 accepted child strings,131 new D3a deviations/536 transformations, original parent/baselines and3,868 old ledger rows verify unchanged. The finite610×384 partial index restores/exports exactly; no QA, scoring view or complete cache exists.97 post-failure regression tests pass; nested recovery and ablation planners reject without writes. See [verified outcome](t8-conv44-recovery-incomplete-20261103.md), `artifacts/t8/offline/conv44-child-length-reproducer.json` and `artifacts/t8/conv44-recovery-incomplete-20261103/verification.json`. No second paid phase was launched; the one-child grant is consumed.
  - 2026-11-03, second-continuation engineering under the new explicit user grant: feature `f49da9a`, BLK-019 correction `acefbfa` and BLK-020 correction `59ab9ae`, integrated at `7211a4a`, pass613 tests/92 subtests,189 focused/60 and both independent62-test groups. Actual610-note/counter607/stale-index restore verifies both pinned ancestors and408 inherited failure records; all51 protected files and the USD8.407857 ledger stay unchanged. Fresh network-disabled runtime preflight and unapproved USD3/446-call/1,338-attempt plan pass under source `0341a2a579842725c9ac6a18a110e2816a2896c32e07cf883fd36e2ef1ab681f`. Software controls are verified; merge and the single new immutable approval/live phase remain pending. No provider-cap fix or new paid success is claimed.
  - 2026-11-03, authorized second continuation after PR#22 merge `5ddc96e`: fresh main preflight verifies610 notes/counter607/stale index and both pinned ancestors; approval `a35ef8a2-78f1-44c6-9f67-1c36d605b2c2` executes once under USD3/446/1,338 limits. After26 new turns, `D26:44` returns HTTP200/`length`,4,000 completion/5,638 prompt tokens, request `633454cd-c049-4132-9754-f9ba24ea63bf`; raw arguments SHA256 `f8bcf69f4e8beacec49bcc87d2eac84af432f80512e3d0941cf366f45a4a5eb9`. Wire/SDK agree;19,058 characters end inside a neighbour tag. The unchanged adapter rejects before schema parsing; original fallback retains note636/counter632 with no links/neighbour changes. Next metadata blocks before transmission.52 calls/USD0.122276, zero retries/unknown charges; full conv-44 lineage1,272/USD2.240235, cumulative4,292/USD8.530133. Exact offline MockTransport replay reproduces rejection with unchanged request/schema and zero network. Root and independent audits verify partial636×384 index/restoration, exact610-row prefix, all408 inherited records,15 new D3a deviations/63 transformations, original baselines/ancestors and4,240 historical ledger rows.62 post-failure regressions pass. No QA, scoring view or complete cache exists; third-recovery and ablation planners reject. See [outcome](t8-conv44-second-recovery-incomplete-20261103.md), `artifacts/t8/conv44-second-incomplete-20261103/{verification,independent-verification}.json` and `artifacts/t8/offline/conv44-grandchild-length-reproducer.json`. Grant consumed; no third recovery or ablation executed.
  - 2026-11-03, separately authorized Run2 GateA: current official documentation permits1–393,216 output tokens with disabled thinking and no separate4K strict-function limit; direct OpenAI2.54.0 MockTransport sends8,192/16,384/393,216 unchanged (three mock/zero network calls). Deduplicated Run1 analysis counts1,708 accepted shared decisions (median1,642.5, p99≈3,570, max3,987), three conv-444,000-token failures and two other rejected decisions. Neighbour context/tag fields dominate95.7% of serialized field characters. Recommend8,192 for all12 new Run2 cells, retain1,000 elsewhere and all other scientific settings. Run1 defaults/replay/evidence remain unchanged. See [GateA report](run2-output-limit-investigation.md), `artifacts/run2/gate-a/{analysis,shared-decision-records,provider-sdk-check,run1-preservation}.json`. No hosted >4K probe or Run2 benchmark call occurred; GateB/final freeze/preflight remain pending.
- **Final resolution or limitation:** **Open: repeated output exhaustion despite exact-state recovery.** All three Run1 conv-44 phases remain Incomplete; preserve636 notes/counter632, three rejected decisions and all failure/cost evidence.39 turns/158 QA remain, next `D26:45`. Its second continuation grant is consumed; no further Run1 recovery is authorized. The new Run2 campaign may use a supported larger cap only after both gates/freeze/review; it cannot retrospectively repair or complete Run1. Do not repair outputs or reuse consumed grants. Run1's4,000-token limit remains operationally unreliable; no hosted8K success is inferred from offline evidence.
- **Verification:** D9a passed 268 tests/92 subtests and independent reviews before the successful live phase. `artifacts/compatibility-d9a-verification.json` verifies stage settings, unchanged arguments, complete state, scoring identity and phase/cache integrity. Historical truncation/replay evidence remains immutable. The separately approved child now supplies complete conv-50 evidence; broader adequacy remains unverified.
  The T8 recurrence's `artifacts/t8/offline/conv49-length-reproducer.json` independently verifies the preserved request/response, inventory, accepted argument identities, partial state and settled ledger. It verifies safe rejection, not resolution of cap exhaustion.
  The conv-44 recurrence is independently reproduced in `artifacts/t8/offline/conv44-length-reproducer.json`; its artifact/state/ledger audit and rejected ablation-readiness check are in `artifacts/t8/conv44-incomplete-20261103/`. These verify safe stopping, not a provider fix or complete baseline.
  Post-failure adapter-budget/phase/study/comparison tests pass120/120 (16 intentional SDK metadata warnings); pre-paid control tests passed48 tests/60 subtests. Both independent outcome reviews are clear. See `artifacts/t8/offline/conv44-failure-regressions-20261103.txt`. BLK-013 remains Open.
  The second-continuation failure has separate root/independent state, audit and ledger verification; original catch-boundary replay preserves `(False, original note)` and632→632. Its exact wire-response MockTransport replay and62 post-failure tests confirm safe rejection, not output-cap adequacy. All original failure evidence remains immutable.
- **Research significance:** Preserving a paper's nominal generation cap under a model substitution can make the released structured-output algorithm operationally infeasible. Output growth, provider representation compatibility and spending safety are separate reproducibility constraints.

## BLK-014

- **ID:** BLK-014
- **Title:** Normally finished strict function contains malformed JSON.
- **Status:** Mitigated
- **First observed:** 2026-11-01, authorized T5 pilot `pilot-conv50-d9a`, source `c659856`.
- **Category:** Provider compatibility
- **Expected behaviour:** A forced strict function returns valid original-schema JSON so the unchanged parser can process every pilot turn and reach all 204 QA.
- **Observed behaviour:** The 263rd shared decision returned HTTP200 / `finish_reason=tool_calls` with 970 output tokens under the 4,000 cap, but its final `}` closes the object before the outer `new_tags_neighborhood` array is closed. JSON parsing fails at offset4075/column4076. This is not token-limit truncation or an integer-string exception. The adapter rejected it; original evolution failure/fallback was retained and the next metadata event was blocked before transmission.
- **Evidence:** [Pilot report](t5-pilot-conv50-d9a-20261101.md), immutable local `artifacts/runs/pilot-conv50-d9a/{events.jsonl,phase.json,partial-memory.json}`, exact request/schema/response/argument files in `artifacts/pilot-conv50-d9a-offline-replay/`, and `artifacts/pilot-conv50-d9a-verification.json`. Provider request ID `440d0fe0-4152-4e64-b4bd-df4e0c479993`; argument SHA256 `e4343dbdcc385261cff04faac6b4f8e101ffe2b8b64fbb2c072c4befb95f2ece`.
- **Root cause:** **Confirmed immediate cause:** the returned function-argument string is syntactically invalid JSON. Wire request and saved response verify the original schema, strict flag, beta endpoint, unchanged settings and missing bracket; no adapter shortening was found. Why provider generation/strict-mode enforcement produced it is **unknown**. Normal finish and low token usage distinguish this from BLK-013.
- **Impact:** Provider malformed outputs remain historical scientific limitations. PR#31 verifies a narrowly scoped original-fallback continuation without accepting/repairing rejected JSON. The p2 restores566 notes and collects all675 turns/158 QA with no new malformed generation. The outer phase remains Incomplete for independent Experiment export failure BLK-024; original inherited failures, D3a deviations and charges persist.
- **Options considered:** Retain strict rejection under the current approved policy. Automatic JSON repair, prompt/schema changes and semantic retries are outside D3a; none was executed. A different compatibility intervention or new live recovery needs a separate decision. Raising the cap is unsupported by this observed failure, which finished normally below the current limit.
- **Resolution attempts:**
  - 2026-11-01: preserve immutable phase files and partial state, settle all 526 requests with zero unknown charges, and verify the next event has zero HTTP attempts. All 176 accepted D3a audits/661 transformed indices survive the later failure; original/historical ledger rows remain intact.
  - 2026-11-01: reproduce with exact safe request/response through the real SDK and HTTPX MockTransport, sockets disabled, in a separate synthetic ledger. One identical mock transmission reproduces rejection; original arguments are retained and a following call is denied by a persisted halt. No paid retry or production change.
  - 2026-11-01: existing malformed-output, strict-field, SDK retry, spending, phase and cost-forecast tests pass: 159 tests/67 subtests. The original forecast CLI rejects the incomplete inventory, rather than selecting scope from partial early-turn usage or the smoke fixture.
  - 2026-11-01, focused offline recovery investigation: transport-decoded arguments, SDK arguments and adapter output are identical. Outer response JSON is valid; the inner argument string is malformed before adapter validation. Raw HTTP bytes were not retained, so provider internal generation/enforcement causes remain unknown. Exact raw output through the frozen parser yields the saved failure fallback. A diagnostic single-bracket insertion instead creates four links, updates four neighbours and returns a positive decision: it is not behaviour-preserving. See [investigation and proposals](blk-014-offline-investigation.md).
  - 2026-11-01: partial snapshot restore/export is exact, including all float32 embedding bytes. Eight frozen-search comparisons with fixed cached-row query vectors pass. 227 intentionally stale corpus rows would change if re-embedded. Retained prefix ends at `D15:7`; next is `D15:8`, with 1,018 nominal calls remaining. Existing runner/phase/forecast interfaces do not support this recovery lineage; no continuation was attempted. Proposed checkpoint support must preserve note263's failure, counter 261, all inherited audits/costs and the halted parent.
  - 2026-11-01: 176 existing tests/7 subtests pass across artifact, parser, adapter, compatibility, SDK-budget, phase and forecast modules. New characterization script verifies all parent phase-file and study-ledger hashes unchanged. Full interrupted-versus-uninterrupted recovery/consolidation tests remain proposed, not passed. No paid calls or production changes.
  - 2026-11-01, separately approved engineering: implement a parent-bound child continuation with exact restore, original failure retention, exclusive durable checkpoint claim, unchanged strict adapter and inherited failure/deviation records. Composite forecasting includes the rejected parent's known usage once, without accepting its malformed output. New preflight/source hashes are explicit; scientific/provider/scoring changes are rejected. See [recovery runbook](checkpoint-recovery.md). No paid recovery is authorized or executed; test/review evidence will be appended after verification.
  - 2026-11-01, implementation `45db8af`, review corrections `ead5a43`/`44461cd`: 19 portable checkpoint tests pass, including mock 305-turn/204-QA continuation, cached-QA reuse, inherited audits after memory/QA/postprocessing aborts, exact stale-state restore, unchanged malformed-output rejection and 99→100/299→300 consolidation equivalence. Standards review found and verified the recovered-cache lookup correction. Spec review independently reproduced missing historical charges and later-spend masking; exact frozen ledger-prefix reconciliation now rejects both. Both axes report no remaining material findings. Actual network-disabled runtime preflight and unapproved real-parent 1,018/3,054 plan pass; no child run/claim or paid execution exists.
  - 2026-11-01, explicit paid-child authorization after PR #14 merge `ca6c68f`: `pilot-conv50-checkpoint-child` restores all 263 notes/counter 261 and exact original float32 index, resumes `D15:8`, and completes all 305 new turns/204 QA. All568 outcomes verify; final counter 566. Child USD2.219082/1,018 requests, no retries/unknown charges or new unexpected failures. All179 inherited failure records and198 new D3a notices persist. Final cache, parent hashes, historical ledger rows, original argument bytes and both scoring views verify; status Degraded. See [verified outcome](t5-conv50-baseline-20261101.md) and `artifacts/checkpoint-child-final-verification.json`.
  - 2026-11-03, separately authorized Run2 child on merged PR#29 (`afcecdb`): resume the exact227-note prefix and process339 new turns. AtD24:12, request `0d1fd874-a744-4be4-af5b-10983cfc41d4` returns HTTP200/normal `tool_calls`,3,016 completion tokens under8,192, but inner JSON fails at column7053/offset7052. Raw arguments SHA256 `3e3db33fd88fe5adfdb736d8c86d0b283eb6cdebcb4cadf2376ff769dc9d47f8` are retained; no JSON repair or compatibility-copy transformation applies. Original fallback preserves note566/counter564; zero QA. All678 child attempts settle once (USD1.325173), then a durable halt prevents further transmission. Strict cloud readback verifies2,048 observations/483 traces, including failure/fallback. The lineage is Incomplete, not a completed degraded cell. Reopen this blocker: Run1 mitigation did not establish provider contract reliability. See [verified outcome](run2-conv44-recovery-incomplete-20261103.md), immutable `artifacts/run2/runs/run2-full-conv-44-r0-p1/` and independent offline audits. Existing financial recovery supports only the consumed227-note prefix; no extra paid child is authorized.
  - 2026-11-03, new user-authorized remediation: independently verify that the frozen author catches the actual malformed shared decision and keeps the original note/counter; fatal phase stopping came from the adapter wrapper. A counterexample proves raw JSONDecodeError alone is unsafe: wrapped positive JSON is parseable by the author's cleanup. Implement only object-delimited normal shared-decision syntax rejection with unchanged strict validation/bytes and a pending gate until exact fallback/state/settlement proof. Other failures remain fatal. Existing actual566-note checkpoint verification succeeds without recomputing the historical launcher's hash from today's file. Initial red regression reproduces unconditional stop; focused offline successive malformed/length/unsafe-wrapper and failure-precedence tests are being verified. No new paid request yet. See [design and grant](run2-author-fallback-recovery.md); preserve `artifacts/run2-fallback-recovery/` attempts.
  - 2026-11-03, reviewed source `7921b15`/fingerprintfc5fc67e…: exact malformed-response replay, successive fallback decisions, unsafe wrappers (including original-strip control characters), other-stage failures, corrupt state/pending admission, copied566-note completion, two length descendants and original untraced equivalence pass. Complete suite784 tests/92 subtests, exact1,544-request archive replays and network-disabled preflight pass. Independent reviews/cloud audits verify75 gate hashes,130 actual-new-executor observations/two fallback proofs and both saved-result Experiments. Legacy smoke helper metadata is explicitly synthetic; actual new executor manifest identity matches. One candidate-classifier storage-fault escape found in review is terminally corrected and regressed. Cost scenarioUSD2.604027 fitsUSD2.629990; immutable p2 plan is still unapproved at this release checkpoint. Provider reliability is not claimed repaired; paid completion remains unverified.
  - 2026-11-03, PR#31 merged66d3ffa and sole authorized p2 consumed: exact566-note/counter564 restore resumesD24:13;109 turns/158 QA complete locally, final675 notes/counter673. Zero new malformed/rejected generations or retries,80 new D3a deviations, original arguments unchanged; all352 inherited failures retained once. USD1.796479/534 requests within limits. Runtime1,771 observations/623 traces verify. Experiment export then fails independently on BLK-024; do not call the sealed Incomplete phase completedDegraded. Both original failures/artifacts and unknown-charge reservation remain unchanged.
- **Final resolution or limitation:** Mitigated at the wrapper/verified original-fallback boundary by `run2-original-evolution-fallback-v1` (PR#31, merge66d3ffa). Normal shared-decision syntax rejection stays strict, the unchanged author fallback runs, and state/index/counter/settlement/journal/tracing must verify before another request. Other fields/stages/transport/storage/accounting faults stay terminal. The provider bug is not repaired; no JSON repair, parser substitution, semantic retry or scientific-setting change. Paid p2 had no new malformed outputs, so successive live fallback is not claimed.
- **Verification:** Exact saved malformed-response offline replay, successive malformed decisions, failure-precedence/pending-admission cases, instrumented/uninstrumented equivalence, two length descendants,784 tests/92 subtests, exact full archive replay and independent Standards/Spec reviews pass. Source-bound real-runner GateB verifies two malformed fallback observations/proofs with zero network LLM calls. P2 exact state and all675 notes/158 QA verify locally, retaining inherited failures once. See [release](run2-author-fallback-recovery.md) and [actual outcome](run2-conv44-collected-export-blocked-20261103.md).
- **Research significance:** Passing a short compatibility fixture and requesting strict mode do not establish long-run structured-output reliability. A normal completion marker cannot replace parser/schema validation, and rare failures can prevent a costly memory build from reaching any benchmark QA.

## BLK-015

- **ID:** BLK-015
- **Title:** Historical intermediate memory states and query vectors were not recorded.
- **Status:** Mitigated
- **First observed:** 2026-11-02, T6 / issue #6 archive inspection.
- **Category:** Reproduction fidelity
- **Expected behaviour:** Replay captured responses with enough independent state evidence to compare memory/index transitions and final retrieval/scoring exactly.
- **Observed behaviour:** T5 retained all 1,544 transmitted completions, per-turn decisions/counters/changed IDs, final QA contexts/results and complete states at notes263/568. It did not retain every per-insertion full snapshot or query embedding. The parent's subsequent blocked metadata event has no response and is not an extra model completion.
- **Evidence:** Immutable `artifacts/runs/pilot-conv50-{d9a,checkpoint-child}/`, completed cache, [T5 report](t5-conv50-baseline-20261101.md), [T6 reference provenance](t6-replay.md), local `artifacts/replays/t6-conv50-20261102/verification.json` and the labelled `tests/fixtures/conv50-replay-state-hashes.json`.
- **Root cause:** **Confirmed:** the existing observational runner records outcomes and complete/abort snapshots, not per-insertion vector/state checkpoints or query vectors. This is a recording-scope limit, not missing LLM outputs or evidence of cache contamination.
- **Impact:** No independent historical numeric oracle exists for every intermediate state. Cross-platform local embedding differences cannot be resolved by silently normalising vectors or replacing retrieval. The two historical checkpoints plus recorded requests/outcomes/QA still support meaningful full replay.
- **Options considered:** Recollecting paid baseline telemetry is unnecessary and unauthorized. Inventing missing historical responses/vectors or substituting captured neighbour choices would weaken the test. Use pinned local CPU recomputation, verify all historical observations, and label frozen-author-derived per-insertion hashes separately. Small portable fixtures use clearly identified deterministic embedding/metric stubs.
- **Resolution attempts:**
  - 2026-11-02: inspect original implementation and immutable archives; find complete logical response coverage, including the malformed decision and accepted D3a audits.
  - 2026-11-02: first socket-denied full replay exactly matches all1,544 requests, 568 outcomes, historical states at263/568, all204 retrieval contexts/predictions and both original scoring views on the pinned CPU environment. No vector/metric tolerance was used; original run/cache/ledger files were read only.
  - 2026-11-02: freeze568 compact T6-derived per-insertion comparison hashes, anchored to parent/child receipts, author revision and dataset. Export only four exact opening responses for portable tests; label their 2D-stub comparison states as new offline characterization, not historical embeddings.
  - 2026-11-02, implementation `c6d7a57`: fresh-process replay matches all568 pinned hashes, historical checkpoints, requests, outcomes, retrieval/predictions and scoring without numerical tolerance. Explicit consolidation observations match notes101/201/302/402/502 at counters100/200/300/400/500. An injected first-row embedding mutation is rejected at insertion1 (`artifacts/t6-mutant-gate.txt`).
  - 2026-11-02, Spec review correction `d0c8168`: add exact ordered logical failure/audit comparison and Degraded classification, excluding only the explicitly verified historical zero-attempt stop notice. Negative regressions reject missing/extra/changed failures and a Boolean-schema/integer substitution. Standards and Spec re-reviews independently pass46 replay tests with no remaining findings; complete offline suite passes333 tests/92 subtests, portable T7 gate103 tests.
  - 2026-11-02, final reviewed-code fresh process: `artifacts/replays/t6-reviewed-20261102/verification.json` verifies all1,544 calls, 568 state hashes, five consolidations, both historical full states, all204 retrieval/prediction/scoring results, both scoring views, all376 logical failure/audit records and Degraded classification exactly. Parent/child artifacts, final cache and study-ledger hashes remain unchanged; sockets are denied and paid calls are zero.
- **Final resolution or limitation:** Mitigated for T6's regression purpose. Recorded facts and derived reference state remain distinct. Every future full-mode replay must match the fixed intermediate oracle as well as recorded checkpoints/outcomes/QA. Historical unlogged vectors are not claimed recovered independently; another runtime/device must fail or be investigated if exact recomputation differs.
- **Verification:** Final reviewed-code receipt above, fresh-process oracle-gated replay, explicit consolidation checks and mutation rejection pass; Standards and Spec reviews are clear. Test logs are `artifacts/t6-merged-candidate-suite.txt` and `artifacts/t6-portable-final-tests.txt`. No paid calls or baseline regeneration occurred.
- **Research significance:** Capturing model outputs enables logical replay, but does not alone supply independent evidence of every numerical state. A trustworthy regression gate separates recorded history, deterministic local computation and explicitly derived test oracles.

## BLK-016

- **ID:** BLK-016
- **Title:** Benign indexed document text is mistaken for a credential-field name.
- **Status:** Resolved
- **First observed:** 2026-11-02, T8 offline complete-conversation partition test for conv-49.
- **Category:** Infrastructure
- **Expected behaviour:** Preserve all original corpus text and its document-to-row index while rejecting actual credential fields in artifact/provenance structures.
- **Observed behaviour:** `snapshot_memory` raises `ValueError: Provenance contains a credential field` before a complete conv-49 build can be saved. One of509 source turns contains the ordinary word “secret”; the index uses complete corpus documents as dictionary keys. No paid run discovered this failure.
- **Evidence:** Frozen `data/locomo10.json` / conv-49, `amem_repro/config.py:reject_credentials`, `amem_repro/artifacts.py:snapshot_memory`; preserved local `artifacts/t8/offline/blk016-red.txt` (two failures), `artifacts/t8/offline/blk016-green.txt` (six passes).
- **Root cause:** **Confirmed:** recursive field-name validation treats arbitrary `retriever.document_ids` corpus text as structured credential-field names. Corpus text is already stored as ordinary string values; it is not a configuration key or authorization header.
- **Impact:** A paid build could complete its model calls but fail artifact persistence, preventing trustworthy reuse/reporting. The selected population includes this conversation, so offline readiness requires correction before transmission.
- **Options considered:** Dropping/redacting the turn, changing embedding text or weakening the global credential validator would alter data/security and are rejected. Validate only the known document-to-row map as data while retaining all other field-name checks.
- **Resolution attempts:**
  - 2026-11-02: reproduce through complete frozen conv-49 runner partition and a focused dynamic-document-key case; both fail before correction. Independently verify source population has509 turns and exactly one containing “secret”.
  - 2026-11-02: implement temporary validation view only after proving every map key equals its indexed corpus row and every row is a proper in-range integer. Keep raw/saved state unchanged, validate all other keys and retain global `reject_credentials`. Six narrow artifact/runner regressions pass, including credential-field and malformed-map rejection. Full-suite/source-migration review remains pending.
  - 2026-11-02, implementation `3948120`, integrated final source `ae23e291`: current-code real568-note cache load/serialization is byte-identical; restore/export preserves all notes, float32 embeddings/order, counter and outcomes. Original files/377 build-failure records remain intact. `artifacts/t8/offline/final-integrity-proof.json` verifies this with sockets denied and zero paid calls. Independent audit/reviews and final519-test/92-subtest suite pass.
- **Final resolution or limitation:** Resolved by the narrow typed-map validation view. Global credential checks and all stored scientific data are unchanged. No live T8 completion is inferred from the artifact fix.
- **Verification:** Red/green, current-code byte/state proof and complete-suite logs above; Standards/Spec reviews clear. Source fingerprint `42ee5de8ffb64090fbafa564bd4ea3e41fd042e846271349ff18b370991a9fe0`.
- **Research significance:** Applying secret-detection heuristics to arbitrary research data can make persistence fail despite a valid memory build. Structural provenance keys and text-keyed retrieval maps require distinct validation contexts without changing the experiment's data.

## BLK-017

- **ID:** BLK-017
- **Title:** Critical paid-run provenance faults can be hidden behind tolerated failure paths.
- **Status:** Resolved
- **First observed:** 2026-11-02, pre-paid T8 Spec review of integration `9fb0b86`.
- **Category:** Infrastructure
- **Expected behaviour:** A provider identity violation or failed durable generation record halts the phase before a subsequent transmission, retains costs/raw evidence where writable, and cannot yield a reusable completed run. Optional cloud reporting may remain best-effort.
- **Observed behaviour:** Two independent offline fault injections each permit all1,410 mock full-conv49 requests. (A) A list-valued `system_fingerprint` reaches set insertion, raises `TypeError`, and is swallowed as a reporting failure before the identity halt. (B) An `OSError` on the first durable generation record is swallowed by the adapter's best-effort observer boundary: only1,409 generation records persist, while the permit remains unhalted and the receipt usable. These are mock reproductions, not observed live provider or storage incidents.
- **Evidence:** `artifacts/t8/offline/review/identity-metadata-red.json` and `journal-red.json`; `amem_repro/phases.py:execute_phase` observer/controller seams, `amem_repro/runner.py:record`, and unchanged `amem_repro/adapter.py` best-effort notification boundary. Actual paid ledger remains at1,610 attempts/USD3.025799.
- **Root cause:** **Confirmed:** critical identity checks and local provenance persistence are incorrectly routed through handlers intended to tolerate observational failures. Provider SDK objects do not guarantee runtime metadata types, and set insertion precedes validation. Critical journal exceptions are caught without a durable phase halt.
- **Impact:** A run may consume its authorized workload after provenance loss, undermining identity/response evidence and incorrectly appear reusable. The monetary cap/one-shot claim still bound spending, but do not satisfy the requirement to stop paid collection on provenance failure.
- **Options considered:** Weakening metadata checks, treating missing records as harmless, or making all optional Langfuse errors fatal are rejected. Validate exact identity types/membership before set operations; wrap only the critical local recorder with terminal budget-stop handling. Preserve original prompts, schemas, argument strings and memory/scoring semantics.
- **Resolution attempts:**
  - 2026-11-02: independent Spec review reproduces both failures with real SDK/MockTransport, zero paid calls, preserved synthetic ledger evidence. Standards review separately reproduces a related completion-mark classification gap and an omitted scoring-wrapper provenance hash; both are assigned to the same implementer for narrow correction.
  - 2026-11-02: implementer is adding first/final-call invalid-metadata regressions, critical recorder/write-failure regressions, terminal halts and truthful incomplete receipts. Final fixes/tests/reviews are pending; no paid call is permitted at this checkpoint.
  - 2026-11-02, correction `84d354a`, final source `ae23e291`: exact provider identity validation precedes set insertion; the baseline critical-local-recorder wrapper persists a halt, retains a safe raw-event companion where writable and always raises terminal `BudgetStop`, including when fallback writing fails. Final-call journal failure preserves195 completed QA rather than falsely reporting zero. Optional cloud reporting remains separate; adapter/prompts/argument strings are unchanged.
  - 2026-11-03, Run2 candidate review (offline, uncommitted/undeployed): a genuine simulated8K shared-decision exhaustion followed by an injected halt-persistence exception still publishes `recoverable_length_failure:true`. Failing test `test_length_failure_cannot_hide_a_later_halt_persistence_fault`; preserved `artifacts/run2/offline/combined-halt-fault-red.txt`. The known provider fallback masks a secondary critical control failure in recovery eligibility. No live call, Run1 artifact or real ledger is affected. Reopen this critical-failure propagation class for a narrow eligibility/secondary-failure receipt correction; no automatic Run2 recovery or paid cell is permitted before verification.
  - 2026-11-03, additional candidate identity regression: a dict-valued returned model correctly halts further requests, but final identity-set aggregation raises `TypeError` and hides the Incomplete phase receipt. Preserve `artifacts/run2/offline/provider-identity-red.txt`. The implementer is preserving the raw invalid metadata while excluding non-string values only from summary sets, never weakening identity validation. No real provider request or Run1 write occurred; correction and independent verification remain pending.
  - 2026-11-03, final Run2 verification: source184544748e86f608286a031a86bd53519e5c95b7f6b3eee0ffae8e2ba2e6e2fe passes715 offline tests/92 subtests (17 expected warnings), both complete original/full-candidate archive replays and clear independent Standards/Spec audits. Current-source runtime preflight passes with sockets disabled. No paid Run2 call or Run1 artifact change occurred. Final evidence: `artifacts/run2/offline/final-full-suite-20261103.txt`, `archive-equivalence.json`, `{spec,standards}-final.md`; GateB source-bound raw proof is separately preserved.
  - 2026-11-03, original-fallback review: an initial candidate called its classifier/import outside the terminal guard, allowing a classifier OSError to reach the author's ordinary catch without a pending gate. Move the entire classification under terminal protection. Real-permit regression verifies persisted halt, four initial mock attempts and no subsequent transmission. Complete784-test/92-subtest suite and independent review pass at sourcefc5fc67e…; no paid request used the faulty candidate. Preserve `artifacts/run2-fallback-recovery/` review/fault tests.
- **Final resolution or limitation:** Run2 correction182dfe1/15176b2, integrated247a747, retains secondary control failures and forbids their recovery, including when a genuine length failure occurred first. Invalid provider metadata remains raw evidence; only string values enter summary sets, after strict identity enforcement. Critical journal, observation, transport-close, settlement and finalization faults cannot release another request/cell. Run1 guards remain unchanged.
- **Verification:** The original red proofs remain unchanged. Final715 tests/92 subtests, independent Standards/Spec audits and actual mock-only executor failure/continuation receipts verify terminal combined-fault and invalid-identity behavior. Both full archive replays preserve376 logical failure records exactly; no paid request was used.
- **Research significance:** Best-effort observability is appropriate for optional reporting, but cannot silently cover critical experiment identity or durable evidence. Request/cost caps alone do not establish experimental integrity.

## BLK-018

- **ID:** BLK-018
- **Title:** Completion exposes a paid-next-phase window before final receipt publication.
- **Status:** Resolved
- **First observed:** 2026-11-02, T8 correction Spec review of integration `b41d825`.
- **Category:** Cost
- **Expected behaviour:** A next study cell cannot claim/transmit until the preceding cell has a verified published receipt and committed completion; failed finalization blocks both new and already-claimed continuation.
- **Observed behaviour:** Offline interleaving commits conv-49's `complete=1`, claims a prevalidated conv-44 permit before receipt publication, then injects conv-49 publication failure. Although conv-49 is halted/incomplete, the new permit can still start/reserve another transmission (synthetic attempt1412). No live or paid call occurred.
- **Evidence:** `artifacts/t8/offline/review/finalization-concurrency-red.json`; `amem_repro/phases.py:_finalize_study_phase`, `amem_repro/budget.py:complete_study_job` and phase ownership checks.
- **Root cause:** **Confirmed:** SQL completion commits before filesystem publication, opening the serial frontier prematurely. A previously claimed permit validates only its own phase at transmission, so a later preceding-cell halt is not observed.
- **Impact:** Concurrent/prevalidated callers could continue paid collection after a provenance/finalization failure, contrary to the one-shot serial study protocol. Root's planned serial schedule does not substitute for enforcing this boundary.
- **Options considered:** Assuming callers never overlap is rejected. Simply swapping SQL/publication order without handling failure reintroduces the earlier false-success receipt problem. Coordinate publication with the SQL release and check shared study failure state before transmission; preserve failed-publication evidence and charges.
- **Resolution attempts:**
  - 2026-11-02, initial review of `9fb0b86`: SQL completion failure after writing a usable receipt left misleading status. Correction `84d354a` moved SQL completion before atomic publication and added truthful failure finalization; ordinary SQL/publication regressions passed.
  - 2026-11-02, independent correction review: deterministic interleaving exposes the resulting publication window. Same implementer is adding coordinated release, shared-failure checks and a concurrency/post-publication commit-failure regression. The earlier correction remains recorded rather than described as sufficient.
  - 2026-11-02, correction `022fd46`, integrated as `ae23e291`: hold `BEGIN IMMEDIATE` through atomic receipt publication/readback and completion commit. Before logical-call and physical-attempt admission, reject other failed/unfinished study cells; allow settlement of already incurred usage. Post-publication commit failures preserve the unconfirmed candidate and failure marker, halt and publish truthful Incomplete evidence; paid/report readers reject marked stale completion.
  - 2026-11-03, Run2 candidate review (offline, uncommitted/undeployed): a next-cell permit claimed while the preceding cell was complete still admits a new logical call after that prior completed phase is durably halted. Failing `test_preclaimed_next_cell_stops_if_prior_completion_becomes_halted`; preserve `artifacts/run2/offline/prior-completion-halt-red.txt`. Current-cell ownership alone is insufficient; every admission must reject failed/unconfirmed earlier completions, including after a post-publication commit fault. Reopen this same frontier control class for correction and regression. No physical provider call, Run1 artifact or real ledger was affected.
  - 2026-11-03, final Run2 verification: source184544748e86f608286a031a86bd53519e5c95b7f6b3eee0ffae8e2ba2e6e2fe passes715 offline tests/92 subtests (17 expected warnings), both complete original/full-candidate archive replays and clear independent Standards/Spec audits. Current-source runtime preflight passes with sockets disabled. No paid Run2 call or Run1 artifact change occurred. Final evidence: `artifacts/run2/offline/final-full-suite-20261103.txt`, `archive-equivalence.json`, `{spec,standards}-final.md`; GateB source-bound raw proof is separately preserved.
- **Final resolution or limitation:** Run2 correction182dfe1/15176b2 checks all earlier cell histories at every admission, not only the current claim; publication/sealing and SQL completion remain coordinated. Prior halts, unconfirmed/changed receipts and failed commits block even an already claimed next permit. Run1 publication controls remain unchanged.
- **Verification:** Final715 tests/92 subtests and both independent reviews pass, including the preserved prior-completion red regression, interleaving and failed-publication controls. Actual mocked executor receipts are sealed before continuation; no paid request was used.
- **Research significance:** Durable accounting and durable research artifacts span different resources. A completion flag alone is not evidence that the preceding experiment is safe to reuse or that a subsequent paid phase may start.

## BLK-019

- **ID:** BLK-019
- **Title:** Recovery provenance can accept altered ancestry or unchecked edges.
- **Status:** Resolved
- **First observed:** 2026-11-03, pre-merge second conv-44 continuation engineering.
- **Category:** Infrastructure
- **Expected behaviour:** A claimed leaf must reject transmission after any invalid edge touches its pinned ancestry. Migration records must list the actual support-file changes, and returned lineage data must not alias a verified parent's binding.
- **Observed behaviour:** A deterministic test inserts a foreign-study incoming edge into the original root after the synthetic grandchild permit is claimed; `start_logical('metadata')` still succeeds. Two further tests show a note-field loop shadowing the changed-file set (reporting an empty migration list despite enforced source checks), and mutable aliasing of `parent_checkpoint` into the loaded parent.
- **Evidence:** `artifacts/t8/offline/conv44-second-provenance-red.txt`; `tests/test_conv44_second_checkpoint.py` tests for cross-cell ancestor edges, migration-field accuracy and lineage-copy isolation. The original three tests fail deterministically before correction. Actual archived phases and the USD8.407857 ledger are unchanged; no new live phase exists.
- **Root cause:** **Confirmed in the candidate:** ownership traversal selects only same-cell edges and misses another edge touching an ancestor; the source-change variable is reused for note attributes; lineage embeds the parent's dictionary without copying it. These are support/provenance defects, not provider-output or memory-algorithm changes.
- **Impact:** Blocks review/paid readiness of the new second continuation. It could admit a request under corrupted ancestry or misreport migration metadata; no real study result or charge was affected.
- **Options considered:** Trusting callers not to alter the ledger and silently accepting incomplete migration metadata are rejected. Add bounded edge validation at admission, separate the source/note-field variables and copy the parent record. No generic graph/recovery framework or scientific change is needed.
- **Resolution attempts:**
  - 2026-11-03: reproduce all three failures with deterministic synthetic ledgers and zero network/model calls. Preserve the red log and actual-parent audit; the implementer is applying narrow corrections before integration.
  - 2026-11-03, correction `acefbfa`, integrated at `7211a4a`: validate every edge touching the bounded ancestry at admission, keep source-change and note-field sets separate, and deep-copy the verified parent lineage.37 new continuation cases pass; combined controls/checkpoint/import checks pass189 tests/60 subtests. Both independent reviews pass62 focused tests each. Actual archived610-note restore and accurate six-file migration metadata verify under source `0341a2a579842725c9ac6a18a110e2816a2896c32e07cf883fd36e2ef1ab681f`, with51 protected files and real ledger unchanged. Full-suite completion remains pending at this checkpoint; no paid continuation occurred.
  - 2026-11-03, final integrated verification:613 tests/92 subtests pass (16 intentional SDK metadata warnings), plus189 focused/60 and both independent62-test groups. Exact610-memory/embedding-byte restore and six-file migration record pass; all51 protected files and the real ledger stay unchanged. No new phase is claimed. Final evidence is `artifacts/t8/offline/conv44-second-full-suite-20261103.txt`, `conv44-second-checkpoint-verification.json` and the two review receipts.
  - 2026-11-03, Run2 candidate review (offline, undeployed): editing a synthetic partial state and recomputing its phase artifact inventory is accepted by the first recovery plan because the newly published phase lacks an independently sealed receipt hash. Preserve `artifacts/run2/offline/receipt-seal-red.txt`. The implementer is adding one immutable receipt hash column to the new Run2 phase ledger, sealed with publication and checked before recovery/admission; no generic recovery framework or Run1 change. Red proof affects synthetic temp artifacts only; real historical states/ledger remain unchanged. Correction and independent verification are pending.
  - 2026-11-03, additional candidate allocation-integrity test: altering the SQL phase-cap column alone can expand a session beyond its immutable approval (the global USD42 guard still holds). Preserve `artifacts/run2/offline/cap-integrity-red.txt`. Compare stored caps with the original approved value at every admission; correction `182dfe1` reports zero transmissions under the same mutation. Exact-tip tests and independent review remain pending. No real ledger or charge was affected.
  - 2026-11-03, final Run2 verification: source184544748e86f608286a031a86bd53519e5c95b7f6b3eee0ffae8e2ba2e6e2fe passes715 offline tests/92 subtests (17 expected warnings), both complete original/full-candidate archive replays and clear independent Standards/Spec audits. Current-source runtime preflight passes with sockets disabled. No paid Run2 call or Run1 artifact change occurred. Final evidence: `artifacts/run2/offline/final-full-suite-20261103.txt`, `archive-equivalence.json`, `{spec,standards}-final.md`; GateB source-bound raw proof is separately preserved.
- **Final resolution or limitation:** Run2 correction15176b2 adds a single immutable receipt hash seal to its phase ledger, published before any recovery/next-cell release. Every edge verifies that seal and the full archive. Correction182dfe1 also compares the SQL phase cap with its immutable authorization at every admission. Run1 bounded ancestry/migration/copy corrections remain unchanged.
- **Verification:**613 tests/92 subtests,189 focused tests/60 subtests, independent62-test groups, actual-parent proof and network-disabled preflight pass. The original failing evidence remains preserved.
- **Research significance:** Multi-phase reproducibility requires both graph ownership and accurate isolated provenance records. Safe single-hop behaviour does not establish correct ancestry handling after an extra recovery hop.

## BLK-020

- **ID:** BLK-020
- **Title:** Failed attempt admission enters SDK retry handling.
- **Status:** Resolved
- **First observed:** 2026-11-03, focused spending-control investigation before the second conv-44 continuation.
- **Category:** Cost
- **Expected behaviour:** A SQLite admission/reservation failure is terminal before HTTP transmission, preserving any uncertain reservation and durably halting the phase. Only genuine transport/provider failures use SDK retries.
- **Observed behaviour:** Injecting one `sqlite3.OperationalError` at `INSERT INTO attempts` through the real SDK rolls back that admission, then SDK retry succeeds and transmits once to HTTPX MockTransport. The call returns an answer and the synthetic phase is not halted, contrary to stop-on-control-failure policy.
- **Evidence:** `artifacts/t8/offline/conv44-second-admission-{reproduce.py,reproducer.json,red.txt}`. Reproducer runs with sockets denied, a fake key and temporary ledger: one mock transmission versus expected zero. Its synthetic12-microUSD charge is not study spending; actual USD8.407857/4,240 records are unchanged.
- **Root cause:** **Confirmed:** `reserve_attempt` lets the database `Exception` escape the transport boundary; the SDK treats it as a retryable connection failure. BLK-012 already made post-response settlement failures terminal, but admission lacked the equivalent boundary.
- **Impact:** Future paid calls could continue after a transient financial-control failure. No actual admission fault or incurred study charge is identified in preserved historical runs. Hold the newly authorized phase until fixed and reviewed.
- **Options considered:** Disabling SDK retries would alter the agreed genuine transport/provider policy. Swallowing the database error or releasing an uncertain reservation is rejected. Prefer a narrow terminal budget-admission wrapper outside its rolled-back transaction, retaining evidence/charges and the original adapter.
- **Resolution attempts:**
  - 2026-11-03: exact SQLite/SDK fault injection reproduces the incorrect retry/transmission with zero network requests and no real-ledger writes. The implementer is adding admission insert/commit and terminal-halt regressions before the correction.
  - 2026-11-03, correction `59ab9ae`, integrated at `7211a4a`: keep the reservation transaction in a private implementation and catch its database failures outside rollback in the public admission boundary. Latch/persist the stop and raise terminal `BudgetStop`; retain committed/uncertain reservations. Six real-SDK regression cases cover initial/retry admission, insert/commit failures and failed halt persistence; existing genuine provider/transport retries still pass. The root reproducer now gives zero mock transmissions, persisted halt and zero synthetic charge, with sockets denied; red/green artifacts remain separate. Combined189 tests/60 subtests and both independent62-test groups pass. No actual study rows/charges changed; full-suite completion remains pending.
  - 2026-11-03, final integrated verification:613 tests/92 subtests and189 focused/60 pass; both independent reviewers verify the terminal boundary and genuine retries. The unchanged root fault script, copied to a fresh green-output path, now produces zero mock transmissions/zero synthetic charge and a persisted `attempt_admission_failed` halt. The actual USD8.407857 ledger remains byte-identical and unclaimed by the new phase.
  - 2026-11-03, independent P1 review of the observed-child precheck: an initial override performed a SQLite query before the inherited terminal wrapper. Correction `b7a2207` moves it to protected `_reserve_attempt`, preserving the public wrapper. A real-SDK OperationalError injection produces zero transmissions, a durable halt and no reservation release; new unknown usage also blocks physical retransmission. Both focused financial regressions and independent reviews pass before any paid child. Original failed/partial tests remain in `artifacts/run2-observed-recovery/`; final source/test evidence supersedes runs invalidated by concurrent candidate edits.
- **Final resolution or limitation:** Resolved at the financial-admission boundary: local reservation failures are terminal and non-retryable by the SDK; committed/uncertain reservations remain retained. Genuine provider/transport retries are unchanged. This does not repair provider JSON or grant an additional phase.
- **Verification:** `artifacts/t8/offline/conv44-second-admission-{red.txt,green.txt,green-reproducer.json}` preserve before/after root proof; the red script is unchanged. Six real-SDK admission fault cases, genuine retry controls,613 tests/92 subtests and independent reviews pass. No real charge or historical artifact was altered.
- **Research significance:** A durable spending ledger is insufficient if its own storage errors become model transport retries. Accounting/control failures and provider/network retries require distinct terminal semantics both before and after transmission.

<a id="blk-021"></a>
## BLK-021

- **ID:** BLK-021
- **Title:** Run2 ledger path can alias immutable Run1 accounting before scope validation.
- **Status:** Resolved
- **First observed:** 2026-11-03, Run2 candidate offline storage-isolation test, issue#24.
- **Category:** Infrastructure
- **Expected behaviour:** New campaign accounting writes only its fresh Run2 ledger; Run1 bytes
  remain immutable, even when a proposed path aliases an older file.
- **Observed behaviour:** A synthetic `artifacts/run2/budget.sqlite` symlink targets a synthetic
  populated old ledger. The constructor rejects the foreign history, but only after SQLite DDL
  changes the target's bytes. No real Run1 ledger, artifact or paid request was affected.
- **Evidence:** `artifacts/run2/offline/ledger-scope-red.txt`;
  `tests/test_run2.py::test_run2_rejects_symlink_to_original_ledger_before_any_write` in the
  unmerged implementation candidate. Earlier557-file preservation remains unchanged.
- **Root cause:** **Confirmed:** the fixed lexical destination is opened/initialized before alias
  and foreign-ledger validation. Logical campaign separation does not establish filesystem isolation.
- **Impact:** A misconfigured alias could mutate exploratory accounting despite a subsequent safe
  execution rejection, violating Run1 preservation. Paid readiness is blocked until corrected.
- **Options considered:** Replacing/resetting the old ledger or accepting a populated foreign file
  is rejected. Validate path components and same-file aliases before mkdir/SQLite writes; retain
  the existing accounting/transport implementation rather than adding a storage framework.
- **Resolution attempts:** 2026-11-03: preserve the failing synthetic proof; implementer is adding
  pre-open symlink/component and same-file/hardlink rejection with byte-preservation regressions.
  - 2026-11-03, final Run2 verification: source184544748e86f608286a031a86bd53519e5c95b7f6b3eee0ffae8e2ba2e6e2fe passes715 offline tests/92 subtests (17 expected warnings), both complete original/full-candidate archive replays and clear independent Standards/Spec audits. Current-source runtime preflight passes with sockets disabled. No paid Run2 call or Run1 artifact change occurred. Final evidence: `artifacts/run2/offline/final-full-suite-20261103.txt`, `archive-equivalence.json`, `{spec,standards}-final.md`; GateB source-bound raw proof is separately preserved.
- **Final resolution or limitation:** Run2 correction182dfe1/15176b2 checks destination path components, symlinks, hardlinks and same-file aliases against preserved Run1 SQLite artifacts before opening or initializing SQLite, including subsequent transactions. Foreign history is never reset or adopted.
- **Verification:** Synthetic symlink/component/hardlink/backup-alias tests preserve the old target bytes and admit zero transmissions. Final715 tests/92 subtests and independent reviews pass. All557 actual Run1 files/ledger hashes independently match the GateA inventory; zero paid Run2 requests existed at verification.
- **Research significance:** Separate experiment names and database tables cannot protect a previous
  campaign if both paths reach the same file. Isolation must hold before initialization side effects.

## BLK-022

- **ID:** BLK-022
- **Title:** HTTP200 body-read failure leaves an unknown charge after a successful SDK retry.
- **Status:** Mitigated
- **First observed:** 2026-11-03, Run2 Full conv-44 `run2-full-conv-44-r0-p0`, shared decision at `D10:10`.
- **Category:** Cost
- **Expected behaviour:** A complete provider response supplies trustworthy usage. Genuine transport retries remain bounded, and potentially incurred charges without usage retain their full reservation and block further paid requests.
- **Observed behaviour:** Logical call454's first physical attempt454 receives HTTP200, then raises `RemoteProtocolError` during body read after60.529s, without a captured response body or usage. The agreed SDK retry455 succeeds after34.465s (3,611 input/2,822 output tokens). The original parser receives that valid retry argument string and finishes note227/counter226. The next `D10:11` metadata call is blocked before transmission. The final phase is Incomplete, not a completed Degraded baseline; no QA ran.
- **Evidence:** Immutable `artifacts/run2/runs/run2-full-conv-44-r0-p0/{approval.json,events.jsonl,phase.json,partial-memory.json,trace-capture.json,observability.json,failure-trace.json}`; ledger attempt454/455 and logical454 in `artifacts/run2/budget.sqlite`; derived `artifacts/run2/transport-incident.json`. The actual phase's1278 observations/230 traces verify remotely; the affected generation explicitly reports incomplete usage/cost and one unknown attempt. No first-response body, provider request ID or detailed exception message is available; do not invent them.
- **Root cause:** **Confirmed:** a response-body transport protocol error prevents usage capture; a subsequent SDK success does not resolve the earlier potentially incurred charge. The durable unknown-charge admission guard correctly stops the phase. The underlying provider/proxy/network reason is **unverified**. This is not an observed `ReadTimeout`, malformed JSON, settlement failure or output-token exhaustion. DeepSeek's [keep-alive documentation](https://api-docs.deepseek.com/quick_start/rate_limit/) explains that non-streaming HTTP connections can remain open before inference; it does not diagnose this60-second incident or prove it unbilled.
- **Impact:** Original attempt454 remains unknown with its fullUSD0.324404 reservation after p1/p2 continuation. All675 turns/158 QA are locally collected; combined1,666 logical/1,667 physical calls costUSD3.842085 known plusUSD0.324404 reserved =USD4.166489. The outer phase is Incomplete due to separate BLK-024. Run1USD8.530133 and all historical artifacts are unchanged.
- **Options considered:** Releasing the reservation, treating HTTP200 as completed usage, changing timeouts/streaming/prompts or silently allowing another phase is rejected. First seek request-level billing/usage evidence. If unavailable, the user must explicitly decide whether a narrowly scoped, fully charged upper-bound adjudication and exact-state continuation are acceptable; this would amend the financial/recovery protocol. A new build is more expensive and discards a usable prefix. Neither option is authorized by BLK-013's length-only continuation grant.
- **Resolution attempts:**
  - 2026-11-03: inspect the actual request/attempt records, sealed phase, index/state and durable ledger read-only. Verify the retry shares the exact original body, the first reservation remains intact and no `D10:11` transmission exists. Verify all557 protected Run1 files unchanged. No new model request or recovery occurs.
  - 2026-11-03: inspect official provider keep-alive/usage documentation. The provider console requires sign-in, so no authenticated request-level billing record is available to settle the unknown charge. Aggregate balance or an SDK retry success would not independently establish this attempt's cost. Focused synthetic HTTP200 body-read regression and independent state/cloud/ledger audit are being added; production retry/validation settings remain unchanged.
  - 2026-11-03, offline verification: test-only `326383e` (merged `ecd74e5`) reproduces an HTTP200 stream-read `RemoteProtocolError` followed by a valid SDK retry. Exact original arguments return; the full first reservation stays unknown and next logical admission makes zero transmissions.28 focused tests pass. Independent actual-phase audit verifies all1278 cloud observations/proofs,227 notes/counter226, exact index and sealed ledger. Original-note serialization roundtrip is byte-exact with no encoder/network. No production defect or setting change is identified; the final whole-suite run is pending. Preserve `artifacts/run2/offline/transport-review.md`, `transport-state-roundtrip.json` and `transport-ledger-archive.json`.
  - 2026-11-03, final post-incident verification:716 tests/92 subtests pass in661.43s with17 expected warnings. Separate Standards/Spec audits verify the sealed phase/cloud hashes, exact index/notes, unknown-charge row and absence of a later transmission; the capacity forecast is independently reproduced with the real SDK offline. The original full reservation and ledger-file hash remain unchanged. These checks establish correct stopping, not resolved provider usage or recovery authorization.
  - 2026-11-03, separately authorized offline mitigation: implement `run2-blk022-attempt454-upper-bound-v1` and `run2-blk022-exact227-state-v1` in `10784e8`, with suffix/next-cell regressions in `99bef89`. The exact original ledger prefix, fixed attempt454/status/null usage/charge/request/receipt hashes are verified; financial-only approval retainsUSD0.324404 and all original rows. Every later unknown still blocks. Exact227-note/counter226/stale-index restoration prepares nextD10:11 without repeating the valid decision; the child stays unapproved with1,212/3,636 call limits andUSD3.955163 remaining. An isolated-copy mock completion verifies448 additional turns/158 QA, inherited Degraded lineage and conservative charge carry to next-cell planning.31 new incident tests plus existing financial guards pass in the focused run; final whole-suite/replay/review evidence is linked in the PR/preparation report. Provider console access remains unavailable; no new paid request or charge reconciliation is claimed.
  - 2026-11-03, independent Spec review: identify a P2 gap for a later fresh cell: runtime verified the reviewed source migration but did not compare it with the immutable phase binding. Fix in `c875998` compares actual source/preflight and the full recomputed migration before permit/output/client creation; four source/preflight/valid-admission regressions pass independently. Preserve the first preparation and issue source-bound V2 preflight/child plan. Standards review has no findings; final Spec review has no remaining findings. No scientific setting or historical evidence changes.
  - 2026-11-03, final offline verification:755 tests/92 subtests pass in823.04s (17 expected warnings). Source-bound original/full-candidate archive replays match all1,544 requests/568 notes/204 questions, every insertion/index/context/prediction and both scoring views; only implementation label differs. Independent Standards/Spec reviews are clear after the pin-comparison and operator-redaction corrections. Network-disabled V2 preflight passes. All557 Run1 files and332 pre-existing Run2 files verify unchanged, with no new primary-ledger rows, checkpoint claim, cloud ingestion or paid request. Preserve `artifacts/blk022-recovery/verification-final.json`; merge and paid continuation remain unauthorized.
  - 2026-11-03, new one-child execution grant: PR#28 is merged as799d0b0. User authorizes exactly the227-note/counter226 D10:11 continuation,1,212 logical/3,636 physical maximum andUSD3.955163 residual original cell cap. The observed support migration pins the five named support files, new secured GateB/credential proof and Git-verified one-shot launcher; no extra recovery chain. Unknown454 remains unchanged/full-reserved. Final source265094c0… gate/preflight/reviews pass; whole offline suite/archive checks and normal merge remain release gates. No paid child has started at this engineering checkpoint.
  - 2026-11-03, merged PR#29 and one live child: the227-note checkpoint restores exactly and resumes atD10:11. Original SQL prefix and unknown454/fullUSD0.324404 reservation remain unchanged. The child adds678 settled attempts/USD1.325173 with no new unknown, stopping on a different malformed-output failure (BLK-014) at566 notes/counter564/zero QA. Total knownUSD2.045606 +reservedUSD0.324404 =USD2.370010; all1,133 physical attempts are accounted for once. This verifies the financial-only mitigation in execution, not that unknown usage is reconciled or the cell completed. The one-child approval is consumed; further recovery is unsupported/unauthorized. [Verified outcome](run2-conv44-recovery-incomplete-20261103.md).
  - 2026-11-03, PR#31/p2: retain p0/p1 receipt/ledger prefix and the exact unknown454 row through534 new settled requests/USD1.796479. The one-shot566-note continuation collects all109 turns/158 QA without retries/new unknown. CumulativeUSD4.166489 stays below originalUSD5 cap. The separate Experiment export failure leaves p2 Incomplete; original unknown is neither released nor relabelled zero. [Outcome](run2-conv44-collected-export-blocked-20261103.md).
- **Final resolution or limitation:** Mitigated by the explicit incident-specific retained-upper-bound adjudication, verified through p1 and p2. Original attempt454 remains unknown/full-reserved; its actual billing is unreconciled. Both paid grants are consumed; no future unknown inherits this exception. Local collection is complete, but sealed p2 remains Incomplete on BLK-024 and no next paid cell is authorized.
- **Verification:** Original ledger prefix, immutable parent receipts and unknown454/null usage/full reservation remain exact. All534 p2 attempts settle once with no new unknown; independent audit confirmsUSD3.842085 settled +USD0.324404 reserved. Exact checkpoint restore and runtime readback pass; this establishes conservative financial continuation, not missing-usage reconciliation or successful Experiment export.
- **Research significance:** A successful retry can produce usable memory while leaving an earlier charge unresolved. HTTP status, transport completion, model-output validity and financial completeness are distinct reproducibility facts. A larger generation cap does not remove transport/accounting failure modes.

## BLK-023

- **ID:** BLK-023
- **Title:** Langfuse project credential exposed in a browser-tool snapshot.
- **Status:** Resolved
- **First observed:** 2026-11-03, user-confirmed exposure during Run2 observability/cost investigation.
- **Category:** Infrastructure
- **Expected behaviour:** Credentials remain private; operator snapshots/logs expose only allowlisted metadata, with secure credentials available for required observability.
- **Observed behaviour:** A prior browser-tool snapshot exposed a project credential. Safe read-only lifecycle inspection still lists the matching original unnamed1-November pair with no expiry. Treat it as active and potentially compromised; actual misuse is not established.
- **Evidence:** `artifacts/blk022-recovery/credential-lifecycle-metadata.json` contains masked-match boolean/lifecycle facts only. The exposed value and raw snapshot are intentionally not repeated. [Preparation report](blk022-recovery-preparation.md#credential-security--user-action-required) records the user-only procedure; `scripts/safe_service_audit.py` provides restricted operator-copy redaction/read-only post-rotation checks.
- **Root cause:** Confirmed sensitive API-key UI content entered a tool-visible snapshot. The one-time display/masking behavior does not make an exposed credential safe. No evidence establishes third-party use.
- **Impact:** Secure Run2 Langfuse auditing and further ingestion should wait for replacement/revocation; immutable scientific artifacts and financial accounting are not changed by rotation.
- **Options considered:** User creates replacement, privately updates local configuration, verifies project and deletes old pair (recommended). Continued use of the exposed value or copying it into a diagnostic is rejected. Agent-driven rotation is outside this grant.
- **Resolution attempts:** 2026-11-03: inspect safe masked/lifecycle metadata in memory without emitting a raw snapshot or copying any key. Add operator-only redaction, allowlisted hosts/child environment/output and offline synthetic-secret regressions. No auth using the exposed value, rotation, replacement access or new cloud ingestion occurred.
  - 2026-11-03, user-performed rotation verified: new `.env` credentials authenticate to the intended project and read an existing trace (HTTP200). Authenticated administration lists only new key `rotate`, created3-Nov18:27:01; original1-Nov pair is absent. Revocation is verified from this inventory without testing the exposed value. The launcher clears inherited values and uses only current `.env`, intended host/project and fresh client. Safe helper succeeds with the existing isolated CLI cache; its default-cache failure cause is unverified. Evidence contains only allowlisted metadata: `artifacts/run2-observed-recovery/credential-{readback,rotation-verified}.json`. No agent rotation or credential disclosure occurred.
- **Final resolution or limitation:** Resolved by user-performed replacement/revocation and verified new access. Inventory establishes the old pair is absent; no old-key authentication or misuse-forensics claim is made. Browser tooling emits only allowlisted/redacted operator views; scientific artifacts are untouched.
- **Verification:** New project authentication and existing-trace read returnHTTP200; current helper returns `status:ok/project_match:true`; authenticated inventory lists only the3-Nov replacement. Safe receipts and source-bound actual ingestion/readback support closure.
- **Research significance:** End-to-end observability adds a credential-handling surface. Diagnostic evidence must retain scientific/audit detail while keeping operational secrets out of agent-visible logs.


## BLK-024

- **ID:** BLK-024
- **Title:** Full-cell Experiment export exceeds local OTLP batch size.
- **Status:** Resolved
- **First observed:** 2026-11-03, Run2 Full conv-44 p2 final saved-result Experiment export after all675 notes/158 QA were collected.
- **Category:** Infrastructure
- **Expected behaviour:** Both frozen scoring views import all158 question results into Langfuse Experiments and verify readback before phase acceptance, without altering local evidence or model behaviour.
- **Observed behaviour:** Runtime readback verifies1,771 observations/623 traces. The one saved-result import returns IDs `7adb9c90792cb287` (corrected) and `622ed0b34679ea04` (historical), but six bounded Experiment/item queries returnHTTP200/empty data. Exporter warnings report dropped serialized batches155,623,154B and155,624,770B above67,108,864B (64MiB). The phase seals Incomplete with `run2_experiments_not_verified`, usablefalse, after the author runner had completed with inherited Degraded status. Final persisted summary/phase are both Incomplete. No automatic re-import or paid restart occurs.
- **Evidence:** [Verified outcome](run2-conv44-collected-export-blocked-20261103.md); immutable `artifacts/run2/runs/run2-full-conv-44-r0-p2/{phase.json,experiments.json,langfuse-import-claim.json,langfuse-imported.json,scoring-views.json}` and bounded readbacks; `artifacts/run2-fallback-recovery/{paid-execution.log,experiment-drop-evidence.json,cli-readback-diagnostic.json}`; [one-shot import/readback](../../amem_repro/langfuse_verify.py) and [saved-result exporter](../../amem_repro/reporting.py).
- **Root cause:** **Confirmed immediate cause:** installed OTLP exporter rejects serialized pre-compression batches above64MiB before transmitting those batches. Actual SDK5.1.0 offline reproduction using the unchanged saved views produces two155.6MB default batches; individual spans remain below0.702MB. Large per-question `original_record` payloads accumulate within default batches. This is distinct from earlier CLI bulk-read timeouts. Whether any individual scores or other partial writes reached cloud remains **unknown**; empty Experiment queries do not prove no writes.
- **Impact:** Primary local predictions/metrics/memory/cache and all financial records are intact, but required Experiment visibility and fully observed acceptance fail. Sealed phase and downstream frontier stay closed. Re-running models would be unnecessary and would change the evidence; automatic re-import could duplicate partial writes.
- **Options considered:** Proposed minimal fix: reviewed `flush_at=16` batching with unchanged records/metadata/scores and existing64MiB guard, followed by separately authorized partial-write reconciliation and one reporting-only import/acceptance supplement. Reject raising/disabling size protection, deleting records/scores, JSON/prediction regeneration, overwriting import claim/phase seal, clearing the halt or silently re-importing. Compression alone cannot avoid the serialized-size guard.
- **Resolution attempts:**
  - 2026-11-03: preserve the sole import claim/IDs, two exporter warnings, all readbacks and sealed failure. Diagnose earlier CLI abort as timeout/empty stdout, not truncated JSON. No additional model request or import.
  - 2026-11-03, offline only: actual SDK/exporter with saved views and blocked network compares default vs16-span batches. Both emit632 spans/316 roots/4,494 score callbacks and retain each original record exactly. Default has two oversized batches;16-span batches produce40 batches, largest9,060,149B, zero above64MiB. Evidence: `artifacts/run2-fallback-recovery/export-characterization/{characterize.py,results.json,run.log}`. This is not a production change, live import or successful remote verification.
- **Final resolution or limitation:** Resolved on4 November2026 by the separately authorized one-shot16-span recovery and exact actual readback:316 question/view items,4,494 scores,316 reporting traces and158 original QA trace associations. Original partial writes/failed import/Incomplete phase remain immutable; acceptance is a separate Degraded lineage supplement. Initial Experiment-filter score reads were corrected through explicit item trace IDs, with independent reviews and59 focused tests; no second ingestion or model call. See [verified completion](run2-conv44-reporting-complete-20261104.md).
- **Verification:**4 November2026 exact cloud readback verifies316 question/view items,4,494 score IDs/names/values/subjects,316 reporting traces and158 original QA trace associations. The separate completion verifier rechecks675 turns/158 QA, all sealed receipts, all1,741 historical file hashes andUSD4.166489 exposure with unknown454/full reservation unchanged. Fresh runtime5,097 observations/1,336 traces and original strict IO proof hashes pass. Original pre-recovery failures and offline-only evidence remain preserved in the dated attempts below.
- **Research significance:** A small end-to-end tracing fixture does not establish full-benchmark export scalability. Successful local scoring, runtime ingestion, SDK-returned Experiment IDs and verified remote Experiment completeness are separate facts; reporting failure must remain visible without discarding sound scientific evidence.

### BLK-024 — 4 November2026 authorized reporting-only attempt

The user separately authorizes engineering/reviews/merge and one bounded saved-result import;
no model execution or future paid cell. [Recovery specification](run2-reporting-recovery.md).
Original cloud inspection discovers4,494 orphan scores despite0 Experiment/item results; preserve
and isolate these original subjects rather than assume no partial writes. New explicit import/run
identities,16-span batches and exact item/score/trace readback are implemented for review. Actual
SDK network-disabled reproduction retains632 spans/316 items/4,494 scores: default max155,613,589B,
bounded max9,059,941B, zero changed results/model calls. Interrupted claims resume reads only.
BLK-024 remains Open pending merged-source live readback; BLK-009 and all paid-cell holds remain.

### BLK-024 — 4 November2026 live score-filter reconciliation

The sole authorized import finishes with316 item traces. Initial readback catches indexing lag
(4,130 embedded scores); subsequent readback has all4,494. `scores --experiment-id` nevertheless
returns0, while explicit score IDs and trace IDs return identical expected sample scores/subjects.
Retain the consumed claim, SDK return, both failed read attempts and diagnostic evidence. Narrow
read-only correction uses bounded explicit item trace filters; no re-ingestion or model client.
Status remains Open until exact actual readback passes. See [live correction](run2-reporting-recovery.md#live-readback-correction--consumed-import-reads-only).

### BLK-024 — 4 November2026 verified resolution

PR#33 merged `513b44e` after809 tests/92 subtests and independent Standards/Spec reviews. Consumed
recovery `run2-full-conv-44-reporting-recovery-20261104-v1` creates corrected `0bb2cccf10432f3d`
and historical `b1402704f1fb57e3`. After the separately reviewed read-only filter correction,
actual readback verifies316 items/4,494 scores/316 traces with exact IDs/subjects/values/provenance.
The separate Degraded acceptance supplement rechecks675 turns/158 QA, all original receipt/inventory
hashes, the1,741-file preservation snapshot, fresh runtime5,097 observations/1,336 traces and original
strict proofs. Exposure remainsUSD4.166489 with unknown454/fullUSD0.324404 retained. Billing shows
exactly5,442 new reporting units andUSD0 draft usage fee. No ingestion/model execution repeated.

### BLK-009 — 4 November2026 measured forecast and alternatives

Status remains Open. Independent cost-only reviews confirm nine remaining ablationsUSD36.176358
plus two missing Full baselinesUSD7.892297; all-scope provider pointUSD48.235144 plus normal service
USD2.526080–3.485360 exceedsUSD42 planned, before protectedUSD8. Proposed balanced conv-44/49 four-arm
scope isUSD31.819960 provider point, normal serviceUSD0 forecast; combined growth/retry/unknown/
checkpoint stressUSD49.330258 including protectedUSD8. One-conversation four-arm and narrower
published three-arm alternatives are documented. Per-cellUSD5 still binds. No scope/order/budget or
paid-phase authorization is inferred. See [analysis](run2-ablation-affordability-20261104.md).

### BLK-017 / BLK-021 — 4 November2026 separate GPT-4o-mini transport review

Before any OpenRouter model transmission, independent Spec/Standards reviews of
`1ba4757` reproduce two existing control classes using synthetic ledgers only:
a settled invalid-provider response did not durably forbid a later caller, and a
symlinked ancestor/regular foreign SQLite destination could receive new tables.
Correction `4fe1733` adds terminal halts, process-owned exact approval checks,
read-only existing-ledger ownership validation before DDL, all-ancestor alias
rejection and per-transaction root/file identity checks. Review fault injection
verifies no second transmission even when halt persistence fails, no acceptance
of changed SQL approval/kind, and unchanged foreign-ledger bytes. The focused
85-test suite passes; independent Standards review passes. Preserve initial and
final review receipts under `artifacts/gpt4omini/verification/`. These are new
support-code defects in the same blocker classes, not changes to historical
Run1/Run2 evidence or their verified control status. Full baseline orchestration
and final campaign release remain separately subject to all handover gates.

The same review finds a financial anomaly edge: a provider-reported charge above
its original reservation must be retained in full, then stop. The correction
records the full known liability, rather than understating exposure as the lower
reservation; the trace also uses this known campaign amount rather than historical
DeepSeek rates. Synthetic faults and rejected alternatives remain preserved; no
live overcharge, financial exception or additional paid authority is asserted.

### BLK-005 / BLK-017 / BLK-019 / BLK-004 / BLK-011 — GPT baseline core review,4 November2026

Independent reviews of unexecuted native prototype `5470c49` reproduce material
control defects offline: a secondary summary OSError remains recoverable after a
length stop; mismatched parent identity/path repeats processed turns; arbitrary
Full cache selection accepts counter999 instead of actual675; post-run rescoring
failure leaves Complete status and escapes the verified observation capture.
No model network request or historical write occurs. Preserve the initial reviews,
actual-executor helpers and red proofs under `artifacts/gpt4omini/verification/`.

The prospective correction uses a distinct intentional length-stop type, requires
healthy mandatory artifacts with no secondary control fault, binds exact parent
path/identity/seal, rechecks all ancestor/leaf edges and immutable file signatures
at every admission after initial full hashes, and protects source/data/selection.
It loads only the exact cache identity/completion marker and compares its complete
state to the actual author agent; final cache/source checks follow reporting.
Rescore before capture, emit policy/question-scoped metric failures and classify
Degraded; preserve original predictions and author metric math. Transport attempts
are recorded before HTTP invocation so unknown body-read failures remain visible
as one attempt, with their original errors/reservations retained.

Production-executor regressions verify675 original turns/158 questions/1,666 mock
posts, exact cache identity/counter675 despite a foreign cache, two real sealed
checkpoint children, rejected wrong-parent paths/post-claim ancestor/leaf changes,
terminal secondary persistence failure and correctly observed Degraded rescoring.
Ten focused tests and the two full675/158 mock executions pass. Final source-bound
whole suite, fixed archive gates, real-cloud native gate and independent re-review
remain release requirements. These are new-engineering fixes in existing blocker
classes, not changes to Run1/Run2 evidence or additional paid authority.

### BLK-019 / BLK-005 — 4 November2026 historical source-alias preservation gate

Before the first OpenRouter model request, full preservation verification rejects
a changed shared observer visible through a synthetic historical workspace's
source symlink. No campaign ledger/client/transmission exists. A complete alias
audit identifies30 tracked-source links; some earlier inventory expansion occurred
after support edits and cannot substitute for the clean pre-task source commit.
Preserve both maps, the failed precheck and the alias audit.

Restore the original research checkout exactly to its clean pre-task `b8b3656`,
without editing any historical artifact or link. Isolate the new campaign in its
own checkout and physical ledger/cache namespace. The authoritative preservation
record combines the original file inventories with original Git bytes for the
tracked aliases; all1,534 older files verify. The initial29-alias count was
preliminary; the complete V2 audit verifies44 tracked-source aliases (30 support/
config plus14 frozen author/runtime) and61 exact symlink targets. Add legacy
checkout/file checks at paid work boundaries. This is restoration/isolation of
support source, not a waiver of changed evidence, financial adjudication, altered
experiment receipt or retroactive scientific change. The original unused approval
stays preserved/ineligible; a new reviewed source-bound plan is required.


<a id="blk-025"></a>
## BLK-025 — OpenRouter prohibits the first dated GPT-4o-mini compatibility request

- **Status:** Open.
- **Observed4 November2026,06:22:08 UTC:** the sole admitted metadata compatibility
  POST to `https://openrouter.ai/api/v1/chat/completions` returns HTTP403:
  “The request is prohibited due to a violation of provider Terms Of Service.”
  `provider_name` is null. No generation ID, response model, output or usage exists.
  Authentication, catalogue and credit GETs had succeeded. They do not prove access
  to actual model execution or identify the entity responsible for the denial.
- **Impact:** all four live native-schema contracts, actual dated serving identity,
  routing and output-cap suitability remain unverified. Full/conv-44 is unstarted;
  there are no scientific metrics or baseline Langfuse Experiments. This is a
  provider-access blocker, distinct from BLK-001's schema adaptation and BLK-022's
  historical HTTP200 body-read failure.
- **Financial boundary:** the new ledger contains one physical attempt, terminal
  phase/halt and one unknown full USD0.019650 reservation. No retry, second probe,
  fallback, continuation or baseline occurred. Read-only credit/key reads at06:26 UTC
  show USD50 and zero recorded usage; aggregate usage cannot settle this attempt.
  Preserve the original raw response/error, approval, receipt and every charge.
- **Confirmed preservation:** independent Standards and Spec outcome audits verify
  1,534 earlier files,61 links and the clean original `b8b3656` source anchor. Run1
  and Run2 ledgers/reservations remain unchanged. New artifacts are isolated.
- **Fix attempts / outcome:** PR#35 merged `c90d5af` for native transport/accounting;
  reviewed compatibility source `3fd147d` admits exactly one request and halts safely.
  Subsequent work is read-only accounting/audit and outcome documentation. No access
  workaround or semantic retry is attempted. Synthetic replay/cloud gates are not
  evidence that this provider accepts the actual request.
- **Unknown / release requirements:** cause, responsible entity and individual charge
  are unresolved. Do not infer a location/account/user violation or change route,
  model or credential. Provider/account clarification and request-level financial
  evidence are needed, then a fresh explicit decision and all outstanding release
  gates before any new transmission. The consumed approval cannot be reused.
- **Evidence:** [complete outcome](gpt4omini-openrouter-blocked-20261104.md);
  private `artifacts/gpt4omini/compatibility-v2/`, `budget.sqlite`, and source-bound
  independent outcome audits. Raw identifiers and credentials remain private.


### BLK-025 — separately authorized updated-key check,4 November2026

After the user privately updated the API key and explicitly requested another
attempt, free authentication/credit/key reads succeed. Independent Standards/Spec
PASS at `79e480b` covers exactly one original metadata payload with a fresh approval,
retained original ledger snapshot/seal/halt/reservation and cumulative caps.40 tests
pass, including the independently requested exact retained-request hash binding.
Offline actual-launcher success/denial checks verify one POST, preserved ancestry,
blocked reuse and no baseline release. No historical source/evidence is changed.

The new request at06:49:31 UTC returns the same HTTP403 prohibition, no generation
ID/output/usage/model and null provider name. Preserve `compatibility-v3/` raw000002
response, event, original error, approval/reviews, terminal receipt/seal and halt.
Both phases are consumed/terminal; exactly two admitted physical requests total,
no automatic retry, no further probe and no baseline. The original SQL rows match
the frozen pre-retest snapshot exactly. Both full USD0.019650 reservations remain
unknown, total USD0.039300. At06:50 UTC account/key readbacks still show USD50/zero
usage; no reservation is released or individual charge declared zero. BLK-025 stays
Open. The source is preserved in draft PR#36; baseline release remains blocked.


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


### Third-key access verified — 4 November2026,15:26 HKT (07:26 UTC)

The single fourth metadata POST succeeds at07:26:23 UTC: HTTP200, unchanged strict
native author schema valid, exact model `openai/gpt-4o-mini-2024-07-18`, provider
`OpenAI`, generation `gen-1793777183-1zYHckobPRQEm0FCPCbe`. Independent read-only
`/generation` confirms identity,299 native input/38 output tokens and USD0.00006765
cost; key usage and account aggregate reconcile with the USD0.011651 opening offset.
No semantic or transport retry, model/provider/route/schema change or JSON repair.

The phase is consumed/Complete for access only. All three previous terminal phases,
halts, raw errors and unknown reservations remain unchanged. The ledger records
four attempts: three unknown/full USD0.019650 each, one settled conservatively at
USD0.000068. Campaign conservative exposure USD0.059018, known reported cost
USD0.00006765, unknown USD0.058950. Account available credit USD49.98828135 includes
separate user testing; none of that external evidence is a study result or charge.
BLK-025 is Mitigated at this single successful access boundary; original denial
cause and old charges remain unresolved. Do not rewrite any earlier receipt.

This proves metadata access and serving identity for one request. It does not pass
all four contracts, validate shared-decision caps, fix the whole-suite source-context
failure or release a baseline. Original memory/question processing remains0/675 and
0/158; no baseline metric or Langfuse Experiment exists. The final one-request grant
is consumed; no fifth POST, baseline, ablation or old-charge settlement is inferred.
Read [the verified access supplement](gpt4omini-third-key-access-verified-20261104.md).
