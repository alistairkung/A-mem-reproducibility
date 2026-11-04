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


### Final third-key access grant — 4 November2026# Approved study decisions

Recorded 1 November 2026, Hong Kong time. Status: accepted, subject to the explicit validation and
execution gates below. [experimental-protocol.md](experimental-protocol.md) is the consolidated
operational specification; this log preserves the decisions and their rationale.

## D1 — Frozen author baseline

Freeze f9a173d and test_advanced.py. Describe the work as a controlled reproduction against arXiv v11,
documenting released-code/data differences. Collect the original full-mode baseline, establish replay,
refactor action gates, prove full-mode equivalence, reconstruct the two missing ablations, then add
evolution-only. This provides a concrete preservation target despite uncertain historical artifacts.

## D2 — Controlled DeepSeek substitution

Use DeepSeek across the original algorithm baseline and every ablation, with identical stage settings.
Keep the algorithm/evaluator intact and isolate provider adaptation. Compare with GPT-4o-mini findings
as a cross-model reproduction, without treating absolute scores as directly comparable. Estimate usage
and obtain approval before paid requests; credentials remain private.

## D3 — Provisional strict-function compatibility

Use deepseek-flash with thinking explicitly disabled and a minimal isolated strict-function adapter.
Preserve messages, schemas, parsing, memory behavior and scoring; validate all four schemas offline.
Return arguments to the original parser without executing tools or adding a generation turn. Preserve
the OpenAI backend. Semantic schema changes require review. This is a protocol approval, not proof of
live compatibility or permission to implement/run it.

## D4 — Full released-data target

Use all ten complete conversations (5,882 turns, 1,986 QA) across all four conditions, subject to budget.
Use the separate 18-turn/four-question fixture only for functional checks. Preserve history and all
included questions. D10a supplies a conditional fallback; it does not immediately replace this target.

## D5 — Isolated caches and canonical memory snapshots

Isolate each configuration and independent build repetition with provenance fingerprints, complete
note/index state and completion markers. Reject incomplete/mismatched caches. Preserve ordered notes,
link indices/mappings, metadata and evolution outcomes for inspection. Distinguish fresh construction,
cached QA and recorded-response replay; repeated QA is not an independent build trial.

## D6 — Fixed retrieval and observational measurements

Fix answer k=10 and construction neighbors=5, with immediate index refresh disabled and no evaluation
tuning. Document these as released defaults rather than verified paper-specific settings. Capture
initial/expanded retrieval counts (including duplicates), documented context-token counts and API
prompt usage, without truncation, deduplication or context-budget changes. Use identical questions
and model settings across conditions.

## D7 — Existing action boundaries

Independently gate strengthen and update_neighbor while retaining initial metadata, shared decision
logic and prompts. Strengthen includes new-note tag rewriting, so linking-only does not isolate graph
links from enrichment. Cover all four decision action sets across all configurations. Label these
as reconstructed operational ablations, not verified copies of unavailable author code.

## D8 — Decision-driven counter and consolidation

Preserve increments on every valid positive decision, even with disabled actions; negative decisions
and the original failure result do not increment. Consolidate every 100 positives without changing
embedding content, timing or refresh policy. Test disabled-action positives, failures and 99 to 100.
This retains control overhead intentionally. Charge joint generation once and report action execution
and suppressed decisions explicitly.

## D9 — Original generation settings and two kinds of evidence

Preserve temperature 0.7 for metadata/decision/query and category 1–4 answers, 0.5 for category 5, and
1,000 output tokens for each completion. Explicitly disable thinking and record endpoint, identifier,
version, parameters and fingerprint. Replay proves equivalence; independent live repetitions measure
variability. The subsequently approved frozen specification also fixes serial non-streaming transport,
a 120-second timeout setting and at most two SDK retries without semantic repair.

## D10 — Progressive USD 50 budget

The proposed USD 250 ceiling and three full-dataset repetitions were rejected. Adopt an initial
USD 50 total ceiling including contingency, provisional USD 1–2 compatibility/functional testing
and USD 5–10 pilot allocations. Three independent full builds per condition are an optional extension,
not the initial target. Determine affordability using measured usage and fixed, performance-independent
scope selection; paid execution remains separately gated.

## D10a — Exact conditional fallback and initial repetition count

Primary target remains all ten conversations and one independent build per conversation per condition.
If cost evidence excludes full scope, the approved fallback is exactly conv-49, conv-50 and conv-44:
sort by turn count/ID, strata 3/3/4, sequential draws with a separate Random(42), without redraws.

Freeze both manifests with original IDs/indices; pass offline contracts; obtain separate fixture and
pilot approvals; measure tokens/retries/context/cost. Forecast incurred plus remaining four-condition
cost with USD 8 contingency. Choose scope using cost evidence alone before comparative performance
inspection. If neither scope fits USD 50, stop for a revised decision. Preserve all selected questions,
context and model/retrieval settings. Additional repetitions require separate budget approval.

## D11 — Corrected primary and historical secondary scoring

Use current corrected author scoring as primary, per-category F1/BLEU-1 headlines and separate
category-5 adversarial_correct. Retain other author metrics/aggregation. Calculate the labelled legacy
view from identical immutable predictions/IDs/reference data without new model calls; higher historical
adversarial overlap is not better factual quality. Include scoring-policy IDs in every result surface
and test that rescoring cannot call a model or modify predictions.

## D12 — Transparent failure classification and recovery gates

Preserve original fallbacks and record run/build/question failures/retries. Distinguish failed-metric
zeros from actual zeros; never remove difficult cases or retry low-quality valid answers. Use a fixed
documented transport policy. Classify complete/degraded/incomplete runs, retain partial artifacts and
costs, and disclose limitations/exclusions without automatically discarding degraded runs. Paid recovery
requires approval. Test classification, metric-failure reporting and output preservation offline.

## D13 — Assignment requirements and discovery completion

The user supplied the authoritative requirements: deadline 13 November 2026 at midnight (Hong Kong time);
reproduce at least one result/behavior from a runnable agentic repository; make one isolated measurable
modification; meaningful subsets and controlled DeepSeek substitution are permitted. Three to five
stochastic trials are recommended, not unconditional. Submit a <=10-page report, reproducible GitHub
repository with commits and a <=15-minute recorded presentation. The current scope is accepted subject
to executing and documenting it. Conclude discovery and prioritize the smallest implementation.

## Approval to persist the plan and create tickets

After reviewing the frozen specification, the user authorized saving protocol/decisions in this repo
and creating GitHub issues T1–T8 with acceptance criteria and dependencies. This authorizes documentation
and tracker changes only. Implementation, commits and paid API calls remain unauthorized. Retain this
boundary in every ticket so a future agent does not infer execution permission from issue existence.


## T1–T4 implementation and commit authorization

The user subsequently authorized T1–T4 implementation and deterministic offline tests, preserving
frozen source and scientific decisions. The final branch instruction is one integration branch,
feature/reproducibility-foundation, with logically scoped T1/T2/T3/T4 commits and a consolidated PR.
Run ticket tests after each ticket and the complete offline suite at the end. Stop for review before
T5. No paid API calls or merge into main are authorized. Earlier parallel drafts are incorporated by
file review/copy; no branch merges are needed. The earlier separate-authorization requirement for
pushing is retained until explicitly resolved; prepare the local PR description before requesting it.

## PR #9 focused follow-up review

The user requested reviewability and safety corrections before merge. Compact version-2 selection
manifests replace duplicated dataset records while preserving the full dataset hash, original identities,
selection rules and exact expanded-manifest hashes. This changes representation, not the D4/D10a population.
Standalone AST loaders now verify frozen bytes, and direct uninstrumented/instrumented scoring parity is
tested. Optional reporting requires complete study identity. Default live execution is disabled until T5
has reviewed, durable phase/request/attempt/USD limits; a Boolean alone cannot enable paid execution.
No paid calls or T5 execution are authorized by these corrections.

## T5 fixture authorization and first compatibility result

The user subsequently authorized T5 implementation/preflight and then explicitly approved only the
USD2 compatibility fixture (44 logical calls, at most 132 physical attempts). Pilot, main execution,
recovery and branch pushing were excluded. See [the attempt report](t5-compatibility-20261101.md).

The first attempt stopped after ten physical requests because DeepSeek returned string connection
indices under the unchanged integer schema despite strict mode. The conservative ledger cost is
USD0.005851, with no unknown charges. The run is incomplete and is not compatibility acceptance or
a baseline result. This is observed evidence, not a revision of D3: preserve the contract and outputs,
and obtain a separate decision before paid recovery or any semantic/protocol change.

## D3a — BLK-007 validation-copy compatibility policy

On 1 November 2026, after the offline investigation, the user explicitly approved implementation and
offline testing of `canonical-index-strings-v1`. The default remains `strict-original-v1`.

Only `shared_decision.suggested_connections[*]` may admit strings matching ASCII `0|[1-9][0-9]*`
that Python `int` can parse. This is narrower than the frozen `as_index` tolerance. Validate an integer
copy against the unchanged complete schema, then return the original argument string byte-for-byte.
Do not convert booleans, signed/padded/Unicode/decimal strings, other fields or other schemas. Do not
filter unshown indices, reorder/deduplicate links, rewrite prompts, alter parsers or add semantic retries.
Original `as_index` and shown-neighbor checks retain those responsibilities.

Record raw schema invalidity, the affected field/items, validation-copy transformation, raw/returned
argument hashes, canonical original/copy hashes and policy ID. Accepted deviations mark a completed
run degraded; aborted/missing-output runs remain incomplete. Count affected completions separately
from transformed items and inherited cache deviations. Bind policy to approval, cache and reporting
identity; every experimental arm must use the same reviewed policy. The integer wire schema, author
algorithm, generation settings and scoring remain unchanged.

Preserve the rejected response and incomplete run. BLK-007 remains Investigating until a separately
authorized live compatibility test succeeds; offline success does not establish provider compliance.
No paid recovery, resumed fixture, conv-50 pilot, push or merge is authorized by this decision.
See [implementation and offline verification](blk-007-compatibility-review.md).

## Authorization — autonomous T5 baseline readiness

The user subsequently authorized remaining T5 implementation, offline verification, specialist reviews,
commits/pushes and merging PR #11 after all required checks pass. Resolve BLK-012 and other material
engineering defects before paid execution; preserve frozen author behavior and D3a. This does not
authorize T6–T8 or changes to algorithms, prompts, schemas, parsing/scoring, populations or settings.

Exactly one **fresh** compatibility phase is authorized under `canonical-index-strings-v1`: the frozen
18-turn/four-QA fixture, up to 44 logical calls, at most three attempts each and USD2 **additional**
spending including failures/retries, within the study ceiling and USD8 contingency. Up to four extra
schema probes are permitted if required; the planned fixture itself covers every schema, so the
existing 44-call/132-attempt limits are retained and no probes are planned. Record a new immutable
approval/source/preflight/run identity; never resume or overwrite the first failed fixture.

Compatibility may succeed with degradation solely from fully audited D3a deviations. Investigate any
other degradation; an incomplete/failed phase consumes this one authorization. Offline fixes may
continue, but another paid phase needs a separate decision. After successful compatibility, verify
runtime/assets/manifests/caches/results and prepare the exact unapproved 1,544-call conv-50 pilot plan
and command. **Stop before the pilot or full benchmark**; both remain separately gated.

## Execution record — fresh D3a phase incomplete

PR #11 merged as `167470b` after BLK-012 correction, 247 offline tests/71 subtests and clear repeat
Standards/Spec reviews. The authorized fresh phase `compatibility-d3a-20261101` then made 12 physical
requests, charged a conservative USD0.008316 and completed zero QA. One D3a response was correctly
admitted with unchanged input; the sixth evolution decision exhausted the frozen 1,000-token output
limit and returned incomplete JSON (BLK-013). The phase halted, preserving all evidence and charges.

The single fresh-phase authorization is consumed. No further paid recovery, pilot or full benchmark
is authorized. A larger output limit would amend D9 and needs explicit approval; a retry under unchanged
settings still needs separate paid-phase approval. The proposed change in the [readiness report](baseline-readiness.md)
is pending, not an approved decision or implemented setting. Preserve both failed runs as historical evidence.

## D9a — Approved shared-decision output allowance and one fresh verification phase

After the blocked-readiness record was merged in PR #12 (`5078459`), the user explicitly approved a
controlled generation-setting deviation: raise **only** shared-decision maximum output from 1,000 to
4,000 tokens. Metadata, query-keyword and answer generations remain at 1,000; all temperatures,
prompts, schemas, parsers, retrieval, memory actions and scoring stay unchanged. Apply these stage
limits identically across all four experimental arms. Preserve the original author files and label
the deviation in every future run under output policy `d9a-shared-decision-4000-v1`.

The frozen configuration records the output-policy ID; its configuration hash and the explicit
stage-cap map bind phase approval and run/cache provenance. Request validation/reporting use
`metadata:1000`, `shared_decision:4000`, `query_keywords:1000`, `answer:1000`.
The reviewed pricing bound is `pricing.max_output_tokens:4000` while each actual request still obeys
its own stage cap. At the existing peak rates, reserve 319,373 microUSD for a shared decision
and 315,773 microUSD for each other-stage attempt before transmission. The USD2 phase hard cap,
USD42 cumulative usable allowance and USD8 contingency within USD50 are unchanged. Keep the existing
SDK retry policy and terminal accounting-failure guard.

Exactly **one further fresh compatibility phase** is authorized after implementation, full offline
tests, Standards/Spec review and refreshed runtime preflight. It uses the frozen 18-turn/four-question
fixture, D3a `canonical-index-strings-v1`, at most 44 logical calls and 132 physical attempts (three per
logical call), and at most USD2 **additional** expenditure including failures/retries. No extra schema
probes are planned. Create a new immutable phase/run identity and explicit approval artifact only
after those gates pass; do not reuse either consumed phase's identity, approval, cache or artifacts.
All prior charges remain in the same durable study ledger.

At this decision, the D9a phase has **not** run and has no approved execution plan. A higher cap is not
proof of compatibility or sufficient output space for the fixture/pilot. BLK-013 remains Investigating
and BLK-007 remains Investigating until supported by the fresh live result. If this single phase fails,
preserve it and investigate offline; another paid recovery needs a new explicit decision. The ongoing
baseline-readiness task permits T5 engineering, commits/pushes and reviews; the conv-50 pilot, full
benchmark and T6–T8 remain unauthorized.

## Execution record — D9a fixture verified; pilot approval pending

The authorized phase `compatibility-d9a-20261101` completed all 18 turns and four original questions
under reviewed D9a implementation `4e7f82b`, source bundle
`02dc368e77f1a1e36d7d2deeffe1e6b0c9a7e8de9e715864852566e704ad7285`. It made 44 logical/physical
requests with zero retries or unknown charges. Conservative phase charge: USD0.053118; cumulative
study charge: USD0.067285 across 66 physical requests, retaining both earlier failed phases.

Status is **degraded solely by seven audited D3a completions/19 string indices**. All 44 original
argument strings, schema/stage settings and relevant hashes verify. All 18 notes/outcomes and 18×384
index rows are preserved; evolution counter 17. Both scoring views use the same four saved predictions
without metric failures. Maximum shared-decision output was 1,572 tokens; this verifies the fixture,
not a guarantee that 4,000 will suffice throughout the pilot. This functional fixture is not a quality
benchmark. BLK-007 is Mitigated; BLK-013 is Resolved for this fixture under D9a; BLK-012 stays Resolved.

The D9a phase authorization is now consumed. The user approved PR #13 for merge after its successful
verification; no PR #13 merge commit is claimed at this checkpoint. Offline suite: 268 tests/92 subtests,
with clear independent Standards/Spec reviews. See [readiness evidence](baseline-readiness.md) for
artifacts and the exact pilot command.

`artifacts/pilot-conv50-d9a-plan.json` is a verified **unapproved** plan: complete conv-50, 568 turns,
204 original QA, 1,544 logical calls, at most 4,632 physical attempts and USD10 cap. No pilot cache,
run or execution exists. Obtain separate explicit pilot authorization and record a new approved file
before execution. The full benchmark, further paid recovery and T6–T8 remain unauthorized. T5 remains
open until its later approved pilot/baseline acceptance criteria are fulfilled.

## Authorization — one conv-50 D9a pilot and cost-only forecast

On 1 November 2026 the user explicitly authorized one pilot using the frozen
`artifacts/pilot-conv50-d9a-plan.json`: full-mode conv-50, all 568 turns/204 questions,
USD10 cap, 1,544 logical calls and at most 4,632 physical attempts including SDK retries.
Preserve the reviewed D3a/D9a settings, source/preflight/compatibility bindings and fresh-build
identity. Record approval in a new file without overwriting the unapproved plan. Retain every
result, failure, partial artifact and incurred or reserved charge in the shared study ledger.

After the pilot, use measured usage/cost to forecast remaining four-condition expenditure with
already incurred costs and USD8 contingency. Inspect cost evidence for that decision, not comparative
quality. A failed/incomplete pilot does not authorize automatic recovery or a forecast that assumes
complete representative coverage. Stop before the full benchmark or T6–T8; neither those phases
nor another paid pilot/recovery phase is authorized by this instruction.

### Outcome — pilot incomplete; approval consumed

`pilot-conv50-d9a` executed on merged main `c659856` with the approved immutable binding. It retained
263 notes/outcomes and a 263×384 index before a shared-decision response failed JSON parsing.
The response finished with `tool_calls` at 970/4,000 tokens; a missing outer array bracket makes this
BLK-014, distinct from BLK-013 output-cap exhaustion. No repair or retry was applied. The following
metadata event was blocked before transmission by the durable halt.

The phase made 526 logical/physical requests, no retries, and answered zero of 204 questions.
Conservative charge: USD0.739432; study total USD0.806717/592 requests, with zero unknown charges.
Remaining balance is USD49.193283 including contingency, or USD41.193283 while preserving USD8.
These are ledger balances, not approval for new spending or full/fallback affordability estimates.
The existing cost forecaster rejects this incomplete pilot; no population change is made.

All raw phase artifacts and historical ledger rows verify unchanged. The approved D3a deviations
(176 completions/661 indices) survive the later failure; incomplete status takes precedence.
The [pilot report](t5-pilot-conv50-d9a-20261101.md) records exact evidence and offline replay.
This authorization is consumed. No further paid phase, full benchmark or T6–T8 was started.

## Authorization — BLK-014 checkpoint engineering only

The user approved implementation/offline tests and a PR for checkpoint recovery, preserving all 263
notes, the failed evolution, stale index and parent provenance. Strict validation remains unchanged.
No JSON repair or raw-malformed-response acceptance exception is approved. Paid continuation is not
authorized; T6–T8 and main benchmark remain gated.

The child must have a new immutable approval and phase identity, with the same shared study ledger
and an exclusive durable claim on its parent checkpoint. Restore the exact saved prefix and begin at
`D15:8`; do not regenerate note263 or its failed decision. New support-code/preflight fingerprints
must remain explicit: the reviewed migration permits only checkpoint/runner/phase/forecast/budget
support changes, while author files, provider adapter, scoring and scientific settings match the parent.
Retain inherited failures/deviations and charges once; child completion is degraded and the parent
remains incomplete. See the [recovery runbook](checkpoint-recovery.md).

## Authorization — merge PR #14 and one paid checkpoint child

On 1 November 2026 the user explicitly authorized merging reviewed PR #14 after the complete offline
suite and normal check gates. The exact reviewed head `77afc36` passed 287 tests/92 subtests. GitHub
reported no required checks or branch rules; the normal merge produced
`ca6c68f0f109b474a5206f59085474b683a4f9ca`, now local `main`. Frozen author/provider/schema/scoring/
retrieval/configuration files remain unchanged.

Exactly one paid child of `pilot-conv50-d9a` is authorized under `blk014-checkpoint-v1` and
`canonical-index-strings-v1`, model `deepseek-flash`: restore 263 notes, failed evolution, original
stale index and counter261; resume at `D15:8`; process 305 remaining turns and all 204 original QA.
Hard additional cap USD10, at most 1,018 new logical calls / 3,054 physical attempts, with existing
per-call retry limits. Use a new bound approval/run identity and the existing shared ledger, retaining
all USD0.806717 prior charges and preserving USD8 contingency within USD50. No output repair or
scientific-setting change is authorized.

After completion, verify all 568 turns/204 questions, both scoring views, complete cache, inherited
failures/deviations and degraded classification; forecast full versus predefined fallback using cost
evidence only. If a new malformed response, contract violation or spending/provenance failure stops
the phase, preserve partial evidence/charges and investigate offline. No second paid phase/restart/
recovery, full benchmark or T6–T8 is authorized. Stop at completed reporting/forecast or a material blocker.

### Outcome — completed degraded conv-50 lineage and cost-only recommendation

`pilot-conv50-checkpoint-child` completed all 305 remaining turns and 204 original QA on merged main
`ca6c68f`, restoring the exact 263-note prefix and resuming at `D15:8`. Final cache: 568 notes/outcomes,
568×384 index, counter566. The parent remains immutable and Incomplete; the completed lineage is
Degraded with the original failed evolution and all compatibility audits retained. No JSON repair,
new acceptance exception, scientific change or unexpected new failure occurred.

Child calls: 1,018 logical/physical, zero retries/unknown charges, USD2.219082 conservative charge.
Combined baseline: 1,544 calls / USD2.958514. Cumulative study, including prior compatibility phases:
1,610 calls / USD3.025799. The sole child authorization is consumed; no further paid request is approved.
All accepted argument bytes, QA identities/order, complete cache, historical ledger rows and both
saved-prediction scoring views verify. The full pre-merge suite passed 287 tests/92 subtests.

The forecast was generated before inspecting quality summaries. At one build per conversation/arm,
all ten conversations project USD127.391486 total; the frozen fallback projects USD42.762234,
each including incurred spending and USD8 contingency, crediting this baseline once. Recommend
`conv-49`, `conv-50`, `conv-44` under D10a's cost-only rule; no further execution followed. The fallback's
2× remaining-cost diagnostic is USD74.498668, so it is not a guaranteed bound. Review/approval and
ongoing cost reconciliation are required for further collection. No performance-based selection occurred.

See [baseline outcome and evidence](t5-conv50-baseline-20261101.md). Before T6, review the degraded
baseline and scope recommendation, separately approve remaining selected-scope T5 full-mode work
(two other conversations for fallback) and T6 itself. T6–T8 and further paid phases are unstarted.

## Authorization — T6 deterministic replay on the completed conv-50 lineage

On 2 November 2026 the user explicitly authorized T6 implementation/offline tests, documentation,
commits/push, focused PR, Standards/Spec review and merge after acceptance. The completed conv-50
parent/child lineage is the replay reference; this authorizes offline T6 before the still-gated
remaining selected-conversation T5 collection. It does not close T5 or change the population.

Preserve frozen author/provider/scoring/configuration and all raw evidence. Replay exact captured
response strings and request identities; distinguish approved D3a deviations and rejected outputs.
Normalise only incidental UUID identities/wall-clock access fields in comparison copies. Historical
per-insertion snapshots/query vectors are unavailable, so retain that limitation and use labelled
portable fixtures plus frozen-author-derived comparison hashes, verified against recorded checkpoints,
requests, outcomes, retrieval and scores. This is not new historical evidence or independent live trials.
No paid model calls, T7 switches, new compatibility policy or additional benchmark experiment is approved.

## Authorization — T7 independent action gates

On 2 November 2026 the user authorized issue #7 implementation, deterministic tests, Standards/Spec
reviews, routine corrections, documentation/blocker updates, commits/push, a focused PR and merge
after all tests and full-mode candidate replay pass. Use merged T6 (`87f34d7`) as the fixed oracle;
run both the frozen reference and the actual T7 candidate against it. Preserve the author source,
all baseline evidence, scientific settings and D3a/D9a policies. Independently gate only the released
strengthen and update_neighbor action execution under D7/D8; positive decisions still count even
when all actions are disabled. This authorizes no paid calls, T8 implementation or ablation collection.

### Verified T7 outcome

Implementation `84ec320`, observational review correction `a591ea8`, PR #16. All96 action tests,
mandatory103-test T6 portable gate and complete429-test/92-subtest offline suite pass. Standards
and Spec re-reviews are clear. The final frozen-reference and actual T7 full-mode candidate each
match1,544 requests,568 fixed state hashes/outcomes,204 QA, both scoring views and376 logical
failure/audit records; both remain Degraded. Direct receipts differ only by implementation label,
and both run source fingerprints match current source. Original run/cache/ledger hashes are unchanged;
no paid calls or ablation experiments occurred. See [T7 evidence and commands](t7-action-gates.md).
BLK-002 is Mitigated by operational reconstructions; unavailable historical ablation code and BLK-015's
recording/runtime limits remain explicit. T8 and further paid collection still need separate approval.

## Authorization — T8 implementation and paid main execution

On 2 November 2026, after T7 merge `577a1e3`, the user invoked `implement-spec T8` and explicitly
authorized paid execution. This authorizes T8 implementation/offline tests/reviews, the skill's
integration branch/commits/push/draft PR workflow, and the frozen one-build-per-conversation/condition
study within the existing USD50 total ceiling including USD8 contingency. It is not permission to
increase the ceiling, add repetitions, change scientific settings or automatically recover paid failures.
The skill ends with a PR ready for review; no new T8 merge authorization is inferred.

D10a's predefined fallback is activated using the existing completed-pilot cost-only forecast:
full scope USD127.391486 does not fit; fallback USD42.762234 including incurred spending/contingency
does. Population remains exactly conv-49, conv-50, conv-44, all turns/questions, across four conditions.
The archived full-mode conv-50 lineage is credited once. Complete full-mode conv-49/conv-44 (T5)
before the remaining nine ablation cells (T8); do not duplicate the existing baseline or claim T5 closed
before its remaining selected-scope collection verifies.

At authorization, the read-only cumulative ledger verifies1610 settled attempts / USD3.025799,
zero unknown charges, SHA256 `dcdb729c7f291da2d07949b374bdebc18952668548f691802f744da2ea1141c2`.
Thus at most USD38.974201 additional is usable while preserving the USD8 contingency. Remaining
nominal workload is16936 logical calls, at most50808 physical attempts, partitioned into eleven fresh
complete-conversation phases. Each needs a fresh immutable approval bound to its exact condition,
action flags, population partition, repetition0, current source/preflight and unchanged provider policy.
Use the same durable study ledger; all earlier approvals remain consumed and historical artifacts immutable.

Verify/review the main-phase controls and compatibility-source migration offline before transmission.
Retain DeepSeek/D3a/D9a, original prompts/schemas/parsing/retrieval/scoring and T7 action implementation;
financial/report support changes cannot redefine that scientific reference. Reconcile measured usage
and cost-only affordability between phases. On a provider/contract, provenance or spending failure,
preserve all evidence/charges and stop paid collection; recovery/reruns require a separate decision.
No tuning, dropped questions, context truncation, silent repairs or quality-based retries are authorized.

Issue #8 also authorizes saved-result local exports and Langfuse comparisons using the existing
author metrics and pinned SDK5.1.0, without model/LLM-judge calls. Local artifacts remain authoritative
if optional reporting fails. See [T8 execution record](t8-execution.md) for exact plans and outcomes.

## Execution hold — T8 conv-49 cap exhaustion (BLK-013 reopened)

On2 November2026 the authorized first T8 cell `t8-full-conv49-r0-20261102` stopped Incomplete at
`D22:2`: HTTP200/`finish_reason=length` at the frozen D9a4,000-token shared-decision cap. Preserve
413 notes, counter411, failed evolution, stale413-row index,270 audited D3a deviations/1,066 items
and all raw evidence. The next metadata call was blocked without transmission. All826 actual attempts
settled conservative USD1.413246; cumulative study cost is USD4.439045/2,436 attempts, zero unknown.
The exact approval is consumed. Conv-44/ablations/recovery remain unexecuted.

This is an observed hold under the existing protocol, **not** a new setting or execution approval.
Offline saved-response replay confirms identical request/schema/raw response and correct terminal
rejection, with zero network requests. Remaining scope must not continue automatically after failure.
See [T8 evidence and proposed choices](t8-execution.md#paid-hold--blk-013-recurrence).
Checkpoint continuation would need a new conv-49 lineage policy/approval, preserving this exact state
and starting `D22:3` (96 turns/196 QA;584 logical calls, at most1,752 attempts). Raising the cap instead
would require an explicit protocol amendment and treatment of existing4,000-token baseline evidence.
Neither is authorized or implemented by this hold record. T5/T8 remain open and PR#17 remains draft.

## Authorization — BLK-013 conv-49 checkpoint engineering only

On3 November2026 the user approved implementing and offline-testing exact-state checkpoint recovery
for `t8-full-conv49-r0-20261102`, keeping the frozen D9a4,000-token shared-decision cap. Preserve all
413 notes, counter411, failed `D22:2` evolution, stale index, parent provenance, raw output and charges;
resume at `D22:3` only under a future separately approved paid phase. Remaining scope is96 turns plus
all196 original questions,584 logical calls and at most1,752 physical attempts.

This authorizes narrow support code, deterministic offline tests, documentation and review on existing
T8 PR#17. It grants no paid continuation/recovery, new main cell, cap/prompt/schema/parser/scoring/
retrieval/model change or merge. Reuse existing checkpoint/phase/permit/runner/result-import seams;
retain one-shot parent claims, cumulative ledger history, immutable evidence and inherited degradation.
Keep BLK-013 Open: engineering verification cannot resolve the observed output-cap limitation.

### Verified conv-49 checkpoint engineering outcome

Implementation `1ffa184`, integrated as `a5695be`, passes545 offline tests/92 subtests and clear
independent Standards/Spec reviews. Network-disabled current-source preflight and exact real-parent
restoration pass, with unchanged parent artifacts and cumulative USD4.439045/2,436-attempt ledger.
Unapproved execution rejects before client creation, phase claim or schema migration. Frozen author,
provider, scoring, retrieval, model/settings and benchmark inputs remain unchanged.

Prepared `artifacts/t8/conv49-checkpoint-plan.json` stays `approved:false`: proposed USD3 ceiling,
584 logical calls and at most1,752 attempts, source
`0b2287b19626da56d7bd567c6073ac15000a4f73c98e9b3510ca18d5ba6faaa9`.
Its historical-cost estimate is USD1.566190, not an upper bound or spending grant. No approved child
artifact exists and no paid recovery was executed. BLK-013 remains Open because truncation can recur;
PR#17 remains draft and unmerged. Separate paid approval after review is still required.

## Authorization — PR17 merge and one conv-49 recovery child

On 3 November 2026 the user explicitly authorized merging PR#17 into main after fresh complete and
focused offline tests, required checks and Standards/Spec reviews pass, then executing exactly one
fresh checkpoint child for `t8-full-conv49-r0-20261102` under `blk013-conv49-checkpoint-v1`.
Restore413 notes/outcomes, counter411, failed `D22:2` and the exact stale413×384 float32 index;
resume `D22:3`, process96 remaining turns and all196 original QA in frozen order. Preserve D3a,
D9a4,000, original algorithm/prompts/schemas/parsers/retrieval/scoring/model/settings and all evidence.

The hard additional ceiling is USD3,584 logical calls and at most1,752 physical attempts under the
existing SDK retry rules. Use the existing cumulative ledger, USD50 total/USD8 contingency and a new
immutable parent/source/preflight-bound approval; do not reuse consumed approvals or reset history.
No other experimental cell, child restart, second recovery chain or repetition is authorized.
On any new provider/contract, provenance or financial failure, halt further paid transmission, retain
all partial results/charges and investigate offline. Non-scientific engineering corrections may be
made/reviewed autonomously, but no paid restart is implied.

After successful completion, verify509 unique turns/196 ordered QA, complete cache/index, both
scoring views, inherited Degraded classification and once-only parent/child accounting. Verify original
conv-50 unchanged, reforecast the remaining balanced fallback using cost evidence and prepare the next
phase for separate approval, prioritizing a paired Full/Neither comparison subject to the existing
baseline dependencies. Stop after that preparation or a material blocker; do not execute another cell.

### Verified PR17 merge and conv-49 child outcome

PR#17 merged as `78ac46b57fd3b89bbf75a315565c945fbb9713be` after fresh545 tests/92 subtests,
64 focused tests, clear final Standards/Spec reviews and no failed required checks or rule bypass.
The new immutable child approval `a550491a-d027-4752-a959-3b6bcdc1e0f6` executed once on synchronized
main. `t8-full-conv49-checkpoint-child` completed96 turns/196 QA with584 logical/physical requests,
USD1.850853, zero retries/unknown charges. Original failed `D22:2`, parent state/evidence, old ledger
rows and original conv-50 remain unchanged. Completed lineage509 notes/counter507 is Degraded.

Combined conv-49 cost is USD3.264099; cumulative study USD6.289898/3,020 settled requests. The child
approval is consumed. No other cell or paid recovery was executed. BLK-013 remains Open: the unchanged
4,000-token cap is not guaranteed adequate elsewhere. Corrected/historical scoring views and all
predictions/observations are saved; [verified outcome](t8-conv49-baseline-20261103.md).

The remaining balanced fixed-population point forecast is USD45.978600 including incurred spending
and USD8 contingency, with USD35.710102 usable actual budget remaining. This is not an upper bound.
The next unapproved full-conv44 plan proposes USD5/1,666 logical/4,998 attempts. Prioritize paired
Neither-conv49 after the existing full-conv44 baseline prerequisite; running it first would require an
explicit sequencing amendment and new reviewed plan. No such gate/population change or further paid
approval is made by this outcome record. T5/T8 remain open for the uncollected scope.

## Authorization — PR18 merge and one Full conv-44 phase

On 3 November 2026 the user authorized review/merge of documentation PR#18 if checks pass and exactly
one fresh Full A-MEM conv-44 phase under the existing frozen protocol. Scope: all675 turns/158 original
questions, maximum USD5 additional,1,666 logical calls and4,998 physical attempts under the existing
SDK retry policy. Use the cumulative ledger and preserve USD50 total/USD8 contingency, both completed
conv-49/conv-50 baselines, original algorithm, DeepSeek/D3a/D9a settings, retrieval and scoring.

Verify current-source preflight, immutable provenance, isolated fresh cache and spending controls
before transmission; create a new scope-bound immutable approval. Routine non-scientific engineering,
offline tests, blocker/documentation updates and scoped commits may proceed autonomously. On output,
provider, provenance or financial failure, preserve partial evidence/charges, investigate offline and
stop before any paid recovery. No ablation, repeat, restart, second recovery or other paid phase is
authorized. Stop after all three full-mode baselines verify, or a material blocker prevents continuation;
report conv-44 quality/status/cost, cumulative budget/forecast and readiness for the first ablation.

## Outcome — Full conv-44 stopped; BLK-013 remains Open

PR#18 merged as `f78215e3a6e127d19001df73011b27c273b1f65d` after clear reviews/checks;
production fingerprint remains `0b2287b19626da56d7bd567c6073ac15000a4f73c98e9b3510ca18d5ba6faaa9`.
Fresh preflight/provenance/cache/spending gates passed. Immutable approval
`295e4e88-5bd8-479f-951a-fbb4d4ef56e6` funded only `t8-full-conv44-r0-20261103` under USD5,
1,666 logical/4,998 physical ceilings. That single approval is consumed.

The424th shared decision (`D18:21`) exhausted unchanged D9a4,000 output tokens, HTTP200/`length`.
The original failure fallback,424 notes/counter422 and exact stale index are preserved. Zero of158
questions completed; F1/BLEU-1/c5 correctness are unavailable. All848 actual requests settled
USD1.415538 with zero retries/unknown charges. Cumulative study cost is USD7.705436/3,868 attempts;
USD34.294564 remains usable while preserving USD8. Prior baselines, historical ledger rows and raw
response evidence remain unchanged. Offline exact-request MockTransport replay reproduces rejection;
the subsequent metadata transmission and the Neither-conv49 planner are blocked.

The whole-fresh-cell cost-only scenario totals USD47.394138 including incurred costs and USD8 reserve;
it is neither an upper bound nor authority to restart. A non-executable exact-state checkpoint suffix
would require251 turns/158 QA,818 logical calls/2,454 maximum attempts; its conditional estimate is
USD1.936945 (balanced total USD46.075868). Conv-44 checkpoint support and paid continuation require
separate decisions/review. No output repair, cap/prompt/schema change, recovery or ablation was
implemented or executed. BLK-013 remains Open; T5/T8 and first-ablation readiness remain blocked.
See [verified outcome and evidence](t8-conv44-incomplete-20261103.md). Stop at the authorized failure
boundary; unused budget is not permission for another phase.

## Authorization — exact conv-44 checkpoint engineering, merge and one child

On 3 November 2026 the user explicitly authorized autonomous conv-44 checkpoint implementation,
offline tests, Standards/Spec review, scoped commits/pushes and merge after all required checks pass.
Documentation PR#19 may also merge after review; it merged as `11685b228f75e508d763be5417af5a5cef2a6d26`.
This supersedes the previous paid hold only for the single child described here; it grants no ablation.

Recover only parent `t8-full-conv44-r0-20261103`, canonical receipt SHA256
`dad7f09f944e0de792787cf40f48f22a19af955353601d48f1c16c12fe62d45b`.
Preserve424 notes, links/metadata, counter422, failed `D18:21` and its original fallback, and exact
stale424×384 float32 index. Resume `D18:22`, process251 remaining turns and all158 original QA.
Do not regenerate the prefix/rejected decision, refresh embeddings, repair JSON or change scientific
settings. Use the existing DeepSeek Flash, D3a and D9a policies, prompts/schemas/parser/retrieval/scoring.

Exactly one new immutable child approval may authorize **USD3 additional,818 logical calls and2,454
physical attempts**, including the existing permitted SDK retries. Bind the exact parent, current
reviewed source, dataset, assets/preflight, model and provider policy. Retain the existing cumulative
USD50 study ledger, USD8 reserve, pre-request reservations, durable halt and one-shot checkpoint
ownership. Do not reopen the parent, reuse an approval or reset historical accounting.

After verified merge/preflight/safeguards, execute this single phase without further confirmation.
If provider truncation/contract violation or provenance/spending failure recurs, halt, preserve partial
state/raw responses/charges and investigate offline. No second paid recovery or automatic restart is
authorized. On success verify675 ordered turns/158 unique QA, final memory/index, inherited degradation,
both scoring views and separate adversarial correctness, once-only parent/child costs and a cost-only
affordability forecast. Stop after verified completion or a material blocker. No ablation or further
paid phase is authorized by this grant. BLK-013 remains Open until the evidence supports a narrower
mitigation claim; checkpoint completion would not prove output-cap adequacy generally.

### Verified conv-44 recovery engineering before merge

Implementation `563e8f4` and PR#20 pass570 offline tests/92 subtests,146 focused tests/60 subtests
and clear independent Standards/Spec reviews. Source fingerprint:
`eea7acf5953ecea73deb7fdd5b406c77171f76ef6a4544e5c149346b5e89e6c4`.
Current-source preflight and exact real-parent restore/export pass; all43 protected files and the
cumulative USD7.705436/3,868-request ledger remain unchanged, zero unknown charges. Unapproved
execution rejects before client/claim creation. The prepared plan remains `approved:false`, exactly
USD3/818 logical/2,454 physical,251 new turns/158 QA. The existing user grant permits merge and one
fresh approved child after final gates, but no child has executed at this checkpoint. No scientific
or provider policy changed; BLK-013 remains Open. No ablation or second recovery is authorized.

## Outcome — authorized conv-44 child stopped; all grants consumed

PR#20 merged normally as `3d0e04ac3054266cce8a82c3408d734de76a0fda`; post-merge preflight and exact
parent/current-source/ledger/cache checks passed. New approval `ad09fe3d-5401-4898-a64e-294491a6dc64`
funded only `t8-full-conv44-checkpoint-child`, USD3/818-logical/2,454-attempt ceilings. It restored424
notes/counter422/stale index and resumed `D18:22` without regenerating the prefix or failed decision.

After186 new turns, `D26:18` exhausted the unchanged4,000-token cap, HTTP200/`length`. Original
fallback/failed decision,610 total notes/counter607 and610×384 partial index are retained. Natural
original consolidations at500/600 are observed; no refresh occurred during restoration. Zero of158
QA completed, so corrected/historical metrics and adversarial correctness are unavailable. Status is
Incomplete, not a completed Degraded baseline. No second recovery/restart or ablation was executed.

Child372 settled requests/USD0.702421; parent+child1,220/USD2.117959; cumulative USD8.407857/4,240,
zero retries in the child and zero unknown charges. All274 inherited failure records,131 new/271
inherited D3a deviations and all original parent/baseline hashes/old ledger rows verify. Exact offline
SDK replay reproduces rejection;97 post-failure regressions pass. The child is durably halted and
its grant consumed. No complete cache, new question result or scoring view exists for conv-44.

The whole-fresh-cell cost-only scenario totals USD48.096559 including incurred costs and USD8
reserve. A hypothetical further suffix (65 turns/158 QA,446 calls/1,338 attempts) estimates
USD1.344443, conditional balanced total USD46.185787; another recovery chain is unsupported and
unauthorized. These are planning arithmetic, not bounds or spending approvals. BLK-013 remains Open;
T5/T8 and first-ablation readiness remain blocked. Stop at the explicit provider-failure boundary.
See [verified outcome](t8-conv44-recovery-incomplete-20261103.md). No population, schema, prompt,
model, generation limit, scoring, retrieval or memory change is approved by this outcome record.

## Authorization — second pinned conv-44 continuation

On 3 November 2026 the user explicitly authorized the smallest implementation, focused/full offline
tests, independent Standards/Spec reviews, commits/pushes and merge for one additional conv-44
continuation, plus a separate reviewed/merged outcome-documentation PR. No intermediate approval is
required after the safeguards pass. This supersedes the previous hold only for this one continuation.

Immediate parent: `t8-full-conv44-checkpoint-child`, canonical phase SHA256
`fb730968fc1eec7cd4df4bcae5dc89baa7ff507dc111c5c1868319f5106d7fd9`.
Verify its full lineage to original `t8-full-conv44-r0-20261103`, canonical phase SHA256
`dad7f09f944e0de792787cf40f48f22a19af955353601d48f1c16c12fe62d45b`, including both immutable
snapshots, approvals, source/configuration and all ledger prefixes. Preserve both original failures
(`D18:21`, `D26:18`) and their unchanged fallbacks; restore610 ordered notes/metadata/links,
counter607 and exact stale610×384 float32 retrieval state without re-embedding. Resume `D26:19`,
process65 original turns, then all158 original QA in frozen order. Do not repeat historical requests.

One new single-use approval may authorize **USD3 additional,446 logical calls and1,338 physical
attempts**, including permitted SDK retries. The workload is130 memory calls plus316 question calls.
Bind exact parent/root lineage, reviewed current source, dataset/configuration, assets/preflight,
model and provider policy. Keep the existing USD8.407857/4,240-request cumulative ledger, USD50
ceiling and USD8 reserve; do not reset accounting or reuse earlier grants. Enforce one-shot chain
ownership and charge all three phases once. Permit only this named second continuation, not an
arbitrary chain or third recovery. Support policy: `blk013-conv44-second-checkpoint-v1`.

Frozen algorithm/prompts/schema/parser/model, temperatures, D3a policy,4,000-token shared-decision
cap, retrieval, index policy and scoring remain unchanged. Preserve existing origin IDs when copying
inherited failure records across the second hop. A support-only runner annotation correction is
within scope; no memory algorithm change is permitted. All prior raw artifacts and completed
conv-49/conv-50 baselines stay immutable.

After offline validation, reviews, merge and exact-state preflight, execute this phase once. On new
invalid/truncated provider output or provenance/spending-control failure, halt paid transmission,
preserve partial state/responses/charges and investigate offline. Apply only original fallbacks;
no JSON repair, cap increase, semantic retry or third paid recovery is authorized. Stop on another
material blocker or verified675-turn/158-QA completion. A completed lineage must be Degraded with
all inherited failures/audits, dual author scoring and separate adversarial correctness. Reconcile
costs without duplication and reforecast by cost evidence alone. No ablation or other paid phase is
authorized. BLK-013 stays Open unless evidence supports a narrower mitigation claim.

### Verified second-continuation engineering

Feature `f49da9a`, provenance fix `acefbfa` (BLK-019) and terminal admission fix `59ab9ae` (BLK-020),
integrated at `7211a4a`, pass613 offline tests/92 subtests (16 intentional SDK metadata warnings),
189 focused tests/60 subtests and two clear independent62-test reviews. Source fingerprint:
`0341a2a579842725c9ac6a18a110e2816a2896c32e07cf883fd36e2ef1ab681f`.
Actual610-note/counter607/stale-index restore/export matches exactly, with both ancestor pins and
408 failure records verified; all51 protected files and the real ledger stay unchanged. Fresh runtime
preflight passes with sockets disabled; unapproved execution rejects before client/claim creation.
The root SDK admission-fault replay now halts with zero transmissions and retained reservations;
genuine transport/provider retries remain unchanged. BLK-019/020 are Resolved; BLK-013 stays Open.
PR#22, final merge and the new single-use approved copy/live continuation are pending at this checkpoint.
The unapproved plan binds USD3/446 logical/1,338 physical limits; no new paid phase has executed.

## Outcome — second conv-44 continuation stopped at the paid boundary

On 3 November2026, PR#22 merged normally as `5ddc96ef8653bcf8997f2d7840435c4630826e09` after
613 offline tests/92 subtests,189 focused tests/60 subtests and clear independent Standards/Spec
reviews. Current-main runtime preflight and exact610-note/counter607/stale-index verification passed
with both pinned ancestors and unchanged historical ledger/baselines. The fresh single-use approval
`a35ef8a2-78f1-44c6-9f67-1c36d605b2c2` executed once under USD3/446-call/1,338-attempt limits.

Grandchild `t8-full-conv44-checkpoint-grandchild` resumed `D26:19`, then stopped after26 new turns
at `D26:44`: HTTP200/`length`,4,000 output/5,638 input tokens, request
`633454cd-c049-4132-9754-f9ba24ea63bf`. BLK-013 recurred. Original fallback retains note636,
counter632 and no new links/neighbour changes for that decision; next metadata is blocked before
transmission. The entire lineage is **Incomplete**, not completed Degraded:636/675 notes,0/158 QA.
Both scoring views and adversarial correctness are unavailable. Preserve all original failures,
408 inherited records,417 total D3a deviations/1,654 transformations and exact stale index history.

The new52 logical/physical calls cost conservative USD0.122276, zero retries/unknown charges.
Conv-44 totals1,272 requests/USD2.240235; cumulative study4,292/USD8.530133, zero unknown charges.
All prior artifacts/ledger rows and completed conv-49/conv-50 baselines verify unchanged. Exact
offline MockTransport replay and independent original catch-boundary replay reproduce the failure;
62 post-failure tests and separate root/independent state/audit/accounting checks pass. This verifies
safe stopping, not provider-cap adequacy. BLK-019/020 remain Resolved; BLK-013 remains Open.

The consumed grant cannot fund another phase.39 turns and158 QA remain, next `D26:45` (394 logical
calls/1,182 maximum attempts hypothetically). Third recovery is unsupported and unauthorized; actual
third-recovery and ablation planning reject without a transmission. No further recovery, restart,
ablation, cap/compatibility/schema change or population revision is approved by this record.

Cost-only whole-fresh-cell point scenario: USD48.218835 including incurred costs and USD8 reserve.
Hypothetical preserved-suffix estimate: USD1.282387, conditional balanced total USD46.246007 with
nine ablations and reserve. These are not upper bounds, executable plans or spending grants. No
accuracy result influenced them. Stop at the material provider-failure boundary; no further paid
execution occurred. See [verified outcome and inventory](t8-conv44-second-recovery-incomplete-20261103.md).

## Authorization — Run 2 fully observed campaign

On3 November2026 the user authorized a new campaign, after output-limit investigation (GateA) and
verified real-runner Langfuse observability (GateB). Track [issue#24](https://github.com/alistairkung/A-mem-reproducibility/issues/24).
All existing runs remain immutable exploratory Run1 evidence, including the USD8.530133/4,292-request
ledger, completed conv-49/50 and incomplete conv-44 lineage. Do not overwrite/relabel them or pool
their predictions with Run2 primary evaluation. Run2 has a separate USD50 conservative ceiling:
USD42 usable, USD8 protected reserve; Run1 spending remains separately recorded.

Engineering, offline tests, focused PRs/reviews/merges and all12 fresh Run2 cells are authorized once
both gates, frozen configuration, independent reviews/preflight and affordability pass. Preserve the
four action conditions, all questions from conv-49/50/44, model, prompts/schemas/parsers, temperatures,
disabled thinking, k=10/five neighbours, index/counter/action/scoring semantics. A documented supported
larger shared-decision allowance may be selected/frozen uniformly before any Run2 benchmark call.
GateA recommends8,192 with1,000 elsewhere; [evidence](run2-output-limit-investigation.md). Hosted
long-output reliability remains untested; official support and offline SDK serialization are distinct
from a paid probe. No exploratory paid probe is implicitly authorized or charged to experimental cells.

Run2 may automatically continue sequential BLK-013 checkpoints within each original cell's allocation,
retaining original failed output/fallback, exact ordered notes/counter/stale embeddings, immutable
lineage and cumulative charges. Never repeat/repair a failed semantic decision or reset cell quotas.
At least two successive simulated failures must pass before execution. Other provider/transport,
provenance/scientific, observability or spending failures stop; no schema/compatibility changes,
contingency top-up or silent population reduction are authorized.

GateB must exercise the real instrumented runner with offline responses, fetch actual observations
from the configured project, verify all stage/action/retrieval/QA inputs/outputs/usage/failures/IDs,
import saved question results into Experiments, prove instrumented/uninstrumented replay equivalence
and zero extra model calls, and simulate output exhaustion/tracing failure. Authentication or a
standalone synthetic trace is insufficient. Local immutable artifacts remain authoritative.

Execute one bounded verified cell at a time, reconcile cost/observations and reforecast before each
next cell. Stop on an unsatisfied gate/material scientific change or unaffordable continuation;
otherwise proceed autonomously. At this authorization checkpoint no Run2 code or paid benchmark
execution exists. Final generation policy, live observability gate and campaign preflight are pending.

### Run2 verified freeze before primary execution

On3 November2026, GateA PR#25 and the reviewed PR#26 implementation establish the frozen
`run2-shared-decision-8192-v1` policy:8,192 shared-decision output tokens,1,000 at every other stage,
identical across all12 fresh cells. Official maximum support and real SDK offline serialization
are verified; no exploratory paid probe or hosted reliability guarantee is claimed. Preserve the
Run1 default4K profile, original author source/prompts/schemas/parsers/model/temperatures/retrieval/
index/counter/scoring semantics and D3a unchanged.

Source fingerprint `184544748e86f608286a031a86bd53519e5c95b7f6b3eee0ffae8e2ba2e6e2fe` passes715
offline tests/92 subtests (17 expected warnings), current-source network-disabled runtime preflight
and both complete568-note/204-Q archive replays. All1,544 recorded requests, per-insertion memory/
index, retrieval, predictions, scoring, consolidation and376 logical failure records match between
original and full candidate; only the implementation label differs. An explicit immutable reviewed
support-source reference permits named support deltas without relaxing author/schema/scorer/assets/
config pins, raw evidence or fixed behavioral oracles. Legacy Run1 execution still rejects Run2 source.

GateB's actual8K real-assets18-turn/four-Q fixture has130 visible observations/56 scores and both
saved scoring-policy Experiments verified by exact readback. Traced/untraced ordered replay and
simulated tracing failure preserve memory/index/predictions/scoring, with zero network LLM calls.
The actual campaign executor separately completes two successive mocked length-failure recoveries,
50 mock calls and final QA/Experiments in an isolated fixture ledger. Independent Standards/Spec
audits verify raw proof/readback hashes and exact values; no auth-only or standalone trace substitutes.
BLK-011 is Resolved for Run2; Run1 remains historically unwired. BLK-017/018/019/021 corrections also
pass final tests/reviews. BLK-013 remains Open as a provider reliability risk.

The frozen [Run2 protocol](run2-protocol.md) and local `artifacts/run2/frozen/manifest.json`
(`5ebd46fd99635d1f74f16935648856de1e5e3c0dc2d6c35ae8b8fef581a7c1c6`) bind source, compact
population, configuration, assets, preflight, gates, reviews, cost forecast and the independently
reviewed one-cell script (`b86e7471d76b73ad81564911f166dd92806658ee8c9efaa3a692b648b3ad37a1`).
Final campaign preparation is unapproved until the final factual audit and normal PR merge pass;
then the user's existing grant authorizes an immutable approved copy and phase-bound single-use
approvals. The superseded draft plan stays unapproved and cannot be reused.

Cost-only initial execution forecastUSD38.764612 plus protectedUSD8 =USD46.764612; three extra
microUSD relative to GateA result from per-cell rounding. Run2 enforcesUSD42 usable, an originalUSD5
maximum per cell and18,480 logical/55,440 physical campaign maxima. Recoveries share the original
cell allocation and remaining quotas. Execute in frozen order (Full44/49/50, then Neither49/50/44,
Linking49/50/44, Evolution49/50/44), reconcile each cell and reforecast from measured Run2 stage costs
before the next. No quality-based selection, extra provider policy, semantic retry, JSON repair,
contingency use or automatic top-up is authorized. All557 Run1 artifacts and USD8.530133 ledger bytes
verify unchanged. No paid Run2 request existed at this freeze checkpoint.

### Run2 outcome — first cell stopped on unknown transport usage

PR#26 merged normally as `207eac03fb92e32fb4d0571cd67359da6875463d`; the final independent freeze
audit passed and only approval metadata changed in the approved copy. Cell0
`run2-full-conv-44-r0-p0` then executed once under itsUSD5/1,666-logical/4,998-attempt limits.

At `D10:10`, shared logical454's first physical attempt454 returned HTTP200 but raised a body-read
`RemoteProtocolError` after60.529s, with no captured body/usage. The permitted SDK transport retry455
returned valid arguments after34.465s (3,611 input/2,822 output tokens); those unchanged arguments
completed note227/counter226. The first charge remains unknown and retains its fullUSD0.324404
reservation. Next-turn `D10:11` metadata was rejected before transmission by the durable financial
guard. This is not BLK-013, a confirmed timeout, malformed JSON or a settlement-retry defect.

The phase is **Incomplete**:227/675 notes, exact227×384 float32 stale index, zero/158 QA,
454 logical/455 physical calls. Known settled conservative costUSD0.720433 plus retained reservation
=USD1.044837 exposure. All1,278 real paid observations/230 traces verify in Langfuse, with partial
usage/cost explicitly labelled.140 D3a deviations/521 transformations and all original arguments
are retained. No `length` occurred; maximum successful shared output3,512 does not establish that
the larger cap fits later growth. Run1's557 files and USD8.530133 ledger remain byte-identical.

No continuation or later cell ran. BLK-022 is Investigating; a valid retry cannot establish that the
first attempt was unbilled. Exact state serialization restores offline without model/embedding calls,
but the current approval only permits automatic BLK-013 recovery and unknown-charge guards forbid
paid admission.448 turns/158 QA (1,212 logical/at most3,636 physical calls) remain hypothetically.
Seek request-level billing/usage first; if unavailable, a narrowly scoped upper-bound financial
adjudication and exact-state continuation require an explicit decision. Never edit the historical
attempt to fabricate usage, release its reservation or silently reuse the consumed phase.

The provider-only point forecast remainsUSD39.056674 including exposure, plusUSD8 protected reserve
=USD47.056674; incomplete Run2 stages still use Run1 cost proxies. It is not recovery authority.
Separately, the user upgraded Langfuse to Core, verified in the billing UI for a new3 November–
3 December period. Actual SDK offline capacity analysis projects221,508–235,524 normal campaign
units and approximatelyUSD9.72–10.84 incremental overage beyond100K included units; two continuations
per cell give a structural scenario nearUSD11.98. Scores are not the whole bill: SDK imports create
per-metric evaluator observations even when returning no value. Fees, discounts/tax, future failure
volume and allocation of service charges need a separate financial decision; no agent upgrade or
incremental overage grant is inferred. If these fees shareUSD42, the current whole campaign forecast
does not fit. Preserve the population, model, settings and reserve while resolving the budget.

See [the stopping report](run2-first-cell-incomplete-20261103.md),
[BLK-022](blockers.md#blk-022), the immutable first phase and
`artifacts/run2/transport-incident.json`. Corrected/historical quality metrics and published-ablation
comparisons are unavailable; no partial or Run1 result substitutes for a complete Run2 condition.

Final post-incident verification: the test-only HTTP200 body-read regression and full offline suite
pass716 tests/92 subtests (17 expected warnings). Independent Standards/Spec audits confirm correct
SDK retry/unknown-charge stopping, exact state/cloud proof and the SDK unit forecast. PR#27 records
the outcome. Neither verification nor its merge settles the unknown usage or grants a new paid phase.

### Authorization — BLK-022 one-off retained-upper-bound adjudication and offline recovery preparation

On3 November2026 the user authorized an isolated-branch PR to investigate BLK-022 and prepare
continuation, explicitly excluding new paid requests, automatic merge and additional Langfuse
spending. The unknown first physical454 may be adjudicated only by retaining its fullUSD0.324404
exposure and unknown status, with an explicit incident-specific financial record. Confirmed metered
conservative charges remainUSD0.720433; total conservative exposureUSD1.044837. The originalUSD5
cell cap, USD42 usable campaign allocation and protectedUSD8 remain unchanged. A valid retry is
not proof of unbilled usage; no authoritative first-attempt reconciliation was found.

Implement fixed `run2-blk022-attempt454-upper-bound-v1` admission, preserving all original rows,
raw response/phase evidence and cost sums. A financial-only receipt distinguishes the one retained
adjudicated unknown from every future blocking unknown; it must never become paid authority.
Prepare `run2-blk022-exact227-state-v1`:227 ordered notes/counter226, exact stale float32 index,
successful D10:10 decision retained, next turnD10:11,448 turns/158 QA remaining. The child plan
stays unapproved and bounded by1,212 new logical/3,636 physical calls and residualUSD3.955163.
The current support migration is restricted to the two reviewed Run2 incident/control modules;
all scientific files/assets/settings and the historical source receipt remain pinned.

Investigate lower-cost Langfuse observation/export options without dropping required auditability.
The existingUSD9.72–10.84 normal overage forecast has a possible offline-verified reduction to
approximatelyUSD1.53–2.65 after the current displayed-period usage adjustment. This is a proposed
prospective export policy, not an adopted change, cloud GateB proof, budget allocation or guarantee.
No additional cloud ingestion or service fee is authorized. A displayed unexpired original project
key is potentially compromised; document safe user-only replacement/revocation steps and redacted
operator tooling. No agent rotation or use of the exposed value is authorized or performed.

Keep Run1/Run2 archives and ledgers immutable; no model, prompt, schema, parsing, retrieval, action,
counter, scoring, generation or population change is permitted. Current scope ends at reviewed PR
and offline readiness evidence. See [recovery preparation](blk022-recovery-preparation.md),
[BLK-022](blockers.md#blk-022), [affordability](blockers.md#blk-009) and
[credential security](blockers.md#blk-023) for implementation, costs and remaining gates.

### Authorization — essential Run2 observations and one BLK-022 paid child

On3 November2026 the user confirmed PR#28 merged and private Langfuse rotation, then authorized
engineering, independent reviews, normal merge, exactly one paid checkpoint continuation and an
outcome-documentation PR/merge. Preserve all historical Run1/Run2 artifacts and the original ledger.
The grant supersedes the earlier preparation-only boundary for this child; it grants no later cell,
additional paid recovery, top-up, contingency use or scientific change.

Verify new project authentication/existing-trace access and old-key revocation with safe evidence;
do not regenerate keys. Adopt the smallest verified observability cost policy retaining generations,
usage/latency/errors, identities, actions, retrieval/answers, complete question-level Experiments,
checkpoint/degradation and authoritative local journals. Freeze `run2-audit-essential-v1`, successful
import-bookkeeping filtering, omission of duplicate original Scores and redundant wire envelopes,
and a30K original-observation fail-closed phase ceiling. Preserve prompts/schema/raw argument strings,
all metric values and original algorithm/settings. Offline equivalence and actual cloud GateB must
pass, with source-bound preflight and independent Standards/Spec reviews before paid execution.

Authorize child `run2-full-conv-44-r0-p1` from exactly227 ordered notes/counter226/stale index, nextD10:11:
448 turns and all158 questions; maximum1,212 new logical calls/3,636 attempts andUSD3.955163 new
conservative spending. Retain knownUSD0.720433 plus unknownUSD0.324404 =USD1.044837 exposure, original
USD5 cell, fresh Run2 USD50 ceiling/USD8 protected reserve and all historical accounting. Generate a
new single-use approval bound to the merged source, dataset/model, secured policy gate and exact
checkpoint. A forecast above the remainder prohibits transmission. Never repair/regenerate history.

New unknown usage, authentication/ingestion, provenance or financial-control failure stops. Use only
already reviewed recovery capabilities; this financial lineage has no further supported child, and
the one-shot launcher never loops. Any length exhaustion therefore preserves fallback/evidence and
stops without inventing another continuation. No semantic retries or scientific-setting changes.

For this child the policy's structural capacity check fits included Langfuse units without extra
overage: at most79,833 units including conservative original/import/existing/verification capacity.
No additional service charge or upgrade is committed. Normal whole-campaign provider/service/reserve
pointUSD48.731314–49.798114 remains conditional and tight; reforecast from this completed cell before
requesting another scope. Stop after verified completion or a material failure, preserve incurred
charges and failures, update blockers/report/forecast and merge the outcome documentation.
See [release specification and evidence](run2-observation-policy.md).

### Outcome — sole BLK-022 observed child consumed, Run2 stopped on BLK-014

PR#29 merged as `afcecdbbfddbc6bc06bdbd4f2524dd58692dedac` after764 tests/92 subtests, exact
original/full-candidate archive replays, source-bound real-runner GateB and independent Standards/Spec
reviews. Rotated credential authentication/readback and original-pair absence are verified without
exposing or retesting the old key. The essential policy is frozen and the financial exception remains
limited to original unknown attempt454/fullUSD0.324404 reservation.

The fresh approval `8854d11c-3202-4c38-948b-409c4be350f4` authorized exactly child
`run2-full-conv-44-r0-p1`. It restored227 notes/counter226/stale index and resumedD10:11. AtD24:12,
a normally finished shared decision (`tool_calls`,3,016 output tokens below8,192) returned malformed
JSON. Strict rejection/original fallback are preserved; no semantic retry or repair occurred.
The child stops Incomplete at566 notes/counter564, zero of158 QA. BLK-014 is reopened Open; this is
not BLK-013 output exhaustion. All2,048 child observations/483 traces verify in Langfuse, including
the failure. No primary quality scores or Experiments exist.

New678 logical/physical calls costUSD1.325173. Combined1,132 logical/1,133 physical attempts have
knownUSD2.045606 +retained unknownUSD0.324404 =USD2.370010 exposure. Cell remainderUSD2.629990;
Run1's USD8.530133 and all previous evidence remain unchanged. Cost-only provider pointUSD39.257657
for the full campaign still uses documented proxies (no completed Run2 cell); carrying the old
normal-service range andUSD8 reserve givesUSD48.932297–49.999097 before any new recovery or other
growth. This does not establish safe affordability. No contingency or extra Langfuse fee is committed.

The sole paid grant is consumed. Next turnD24:13;109 turns and158 questions remain (534 logical
calls). Existing financial recovery supports only the consumed227-note prefix. A new exact566-note
checkpoint extension and another bounded paid phase require a separate decision; neither is
authorized or implemented here. No later cell may start. The separately authorized outcome-
documentation PR/merge records this material stop without changing the scientific protocol.
Read [the complete verified outcome](run2-conv44-recovery-incomplete-20261103.md).

### Authorization — original evolution fallback and one exact566-note Run2 continuation

On3 November2026 the user authorized investigation, narrow implementation/offline tests, independent
reviews, normal merge and one new paid continuation from p1, plus an outcome-documentation PR/merge.
Verify the author's supported fallback before changing experiment-level fatality. Do not repair or
accept invalid JSON, retry a semantic decision, weaken schemas, or change scientific settings.

The verified scope is `run2-original-evolution-fallback-v1`: only normal, correctly identified strict
shared-decision syntax errors whose object-delimited text also fails the unchanged author cleanup.
Keep strict rejection/AdapterError and original fallback; verify complete memory/index/counter and
settled accounting before another transmission. Other stages, schema types, wrappers, length,
transport, storage, provenance, observability and financial failures stay terminal. A completed cell
with these failures is Degraded. This replaces excessive wrapper fatality for a supported author
fallback while preserving its effective algorithm and all prior Run2 state.

Authorize exact566-note/counter564/stale-index recovery from `run2-full-conv-44-r0-p1` atD24:13,
with both ancestors and all inherited failures/charges. Permit the smallest sequential checkpoint
extension, exclusive ownership, cumulative budgets and single-use approval. Historical sources are
validated against their own archived bindings; only the new candidate uses current release pins.

Exactly one fresh p2 paid phase:109 turns/158 questions,534 logical calls,1,602 physical attempts,
maximumUSD2.629990 additional conservative exposure. OriginalUSD5 cell and Run2USD50 ceiling/8
protected reserve remain; unknown454 retainsUSD0.324404 and existing exposureUSD2.370010 is not
reset. Require all offline/cloud/review/merge/preflight and conservative affordability gates before
transmission. No further actual recovery, later cell, additional budget or contingency use is granted.
See [verified design and execution boundary](run2-author-fallback-recovery.md).


### Outcome — exact566-note p2 consumed; local collection complete, Experiment release blocked

PR#31 merged as `66d3ffa6af82560d50658a9077439becc01681ba` after784 tests/92 subtests,
exact original/full-candidate archive replays, source-bound real-runner cloud GateB, network-disabled
preflight and clear independent Standards/Spec reviews. `run2-original-evolution-fallback-v1`
keeps strict rejection and the unchanged author catch, then verifies state/settlement/tracing before
further transmission; provider malformed-output reliability is not repaired.

Fresh approval `94021561-b115-4e79-83db-de93e3464c4f` is consumed. Sole p2 restores566 notes/counter564,
resumesD24:13 and collects109 new turns plus158 QA: final675 notes/counter673. All534 logical/physical
requests settle once, zero retries/new malformed outputs/new unknown;80 new D3a deviations retain
original argument strings. Inherited failures/unknown charges and all historical artifacts persist.
P2USD1.796479 is withinUSD2.629990. Total Run2USD3.842085 known +USD0.324404 retained unknown
=USD4.166489; originalUSD5 cell remainderUSD0.833511. Run1 remains separateUSD8.530133.

All1,771 runtime observations/623 traces verify, but the sole saved-result Experiment export drops
two serialized155.6MB batches above64MiB. Both scoring views/readbacks fail visibility; partial
remote writes are unknown. The sealed phase is Incomplete (`run2_experiments_not_verified`),
not completedDegraded; do not change its receipt/halt/claim or silently release another cell.
BLK-014 is Mitigated at the tested fallback boundary; BLK-024 is Open for reporting-only recovery.
Offline SDK batching16 spans preserves all316 result roots/4,494 score callbacks and metadata,
with max9.06MB/zero oversized batches; it is a proposal, not implemented/live-verified recovery.

Measured Full-stage cost sensitivity projectsUSD48.235144 provider total (remaining11USD44.068655),
exceedingUSD42 execution allowance byUSD6.235144 before service fees. BLK-009 is reopened Open;
no population/design/settings/budget decision is inferred from quality. USD8 contingency is protected.
No further paid phase, additional import or frontier release is authorized. A separate explicit
reporting-only recovery/partial-write/acceptance decision and later cost-only budget decision are
needed. Read [complete evidence and local scores](run2-conv44-collected-export-blocked-20261103.md).

### Authorization — BLK-024 reporting-only recovery and cost reforecast

On4 November2026 the user authorized the smallest bounded Experiment exporter fix, offline tests,
independent Standards/Spec reviews, implementation PR/normal merge, one reporting-only import and
actual readback, followed by an outcome-documentation PR/merge. No DeepSeek request, regenerated
prediction/scoring, scientific change, additional cell, contingency or Langfuse overage is authorized.
The fresh import is `run2-full-conv-44-reporting-recovery-20261104-v1`; consumed original Experiment
IDs, all phase claims/receipts/halt, authoritative results/checkpoints/caches/source and ledgers remain
immutable. Preserve and explicitly isolate old cloud writes; stop on unresolved ambiguity, provenance
or new service charges. A separate verified supplement may classify the completed lineage Degraded;
it cannot rewrite the original Incomplete receipt or release a paid frontier. Reforecast all nine
ablations plus the two missing Full baselines, with scope alternatives requiring a new user decision.
See [recovery specification and evidence](run2-reporting-recovery.md).

### Outcome — Run2 conv-44 reporting complete; affordability decision remains open

On4 November2026 PR#33 merged normally as `513b44e11ff846035add3b5aefe32043cbd960a6` after809 tests/
92 subtests (17 expected warnings) and independent Standards/Spec PASS. Original scientific source
fingerprint remains `fc5fc67e0a0276948b1c8ac38ec4bbd0fab2fa09b44badc4c2a517cee3503fa7`.
The sole reporting claim `run2-full-conv-44-reporting-recovery-20261104-v1` is consumed. Both scoring
views preserve158 questions each; new Experiment IDs are corrected `0bb2cccf10432f3d` and historical
`b1402704f1fb57e3`. Original4,494 orphan scores and failed IDs/claim/receipt remain unchanged.

Readback first caught indexing lag, then a score endpoint Experiment-filter discrepancy. Explicit
score IDs/trace IDs match; a separately independently reviewed59-test correction reads bounded item
trace IDs, with no ingestion client or modified consumed approval. Actual complete readback verifies
316 items/4,494 scores/316 reporting traces, all identities/values/subjects and original158 QA traces.
Runtime5,097 observations/1,336 traces and original strict proofs also verify. A separately sealed
lineage supplement classifies675 notes/158 QA **Degraded**, preserving original p0/p1/p2 Incomplete
receipts/halt and ledger frontier. No model request, regrading or scientific change occurred; import callbacks only returned saved metric values.
Corrected overallF1/BLEU-1 are54.06%/48.37%; historical42.05%/36.24%; adversarial correctness27/35.

BLK-024 is Resolved. All1,741 historical files, Run1USD8.530133 and Run2 ledger are unchanged. Run2
knownUSD3.842085 +unknown454/fullUSD0.324404 =USD4.166489; cell remainderUSD0.833511, plannedUSD42
remainderUSD37.833511, protectedUSD8 untouched. Reporting adds5,442 included Langfuse units; current
draft usage chargeUSD0, no overage commitment. The read-only recovery creates no new model charge.

BLK-009 stays Open. Nine ablations costUSD36.176358, plusUSD7.892297 for two missing Full baselines;
provider pointUSD48.235144 exceedsUSD42 before serviceUSD2.526080–3.485360. Cost-only balanced
conv-44/49 four-condition proposalUSD31.819960 provider and combined stressUSD49.330258 including
protectedUSD8 retains more comparisons; individualUSD5 caps still bind. One-conversation four-arm
and narrower published three-arm alternatives are also recorded. No smaller population/order,
budget revision, later paid cell, extra recovery or contingency use is authorized here. The outcome
PR/normal merge is within the existing explicit user grant. See [completion](run2-conv44-reporting-complete-20261104.md)
and [affordability](run2-ablation-affordability-20261104.md).

### Authorization — independent GPT-4o-mini OpenRouter Full / conv-44 baseline

On4 November2026 the user separately authorized engineering, complete offline tests,
independent Standards/Spec reviews, focused PRs/normal merges and autonomous paid
execution of exactly one fresh GPT-4o-mini Full / conv-44 baseline lineage. This is
a new campaign; all DeepSeek campaigns/results/ledgers/reservations remain unchanged
exploratory evidence. Keep the three preselected conversations/four conditions, but
do not execute the other eleven cells. See [campaign specification](gpt4omini-baseline.md).

Use OpenRouter's exact dated `openai/gpt-4o-mini-2024-07-18`, OpenAI-only routing,
fallbacks disabled/required parameters, original native strict JSON schemas, prompts,
algorithm, stale index and scoring. Verify authentication/actual route/limits/pricing;
investigate and freeze stage caps prospectively. The private existing credential must
never be printed, regenerated or committed. All compatibility/equivalence/checkpoint/
accounting/real-runner observation/Experiments gates and independent reviews precede
baseline execution. Preserve every original artifact and failed attempt.

New campaign ceilingUSD50 including protectedUSD8; this cell including compatibility
and any permitted recovery has a hardUSD5 allocation. A compatibility phase may spend
at mostUSD0.25. Durable per-transmission reservation/usage accounting and a fresh
documented cost forecast are mandatory; stop before transmission if unaffordable.
Bounded exact-state sequential recovery is authorized only for verified supported
failures within the same original allocation, without repair/semantic retry/repeated
processed work. Unknown exposure, unsupported transport, scientific inconsistency,
broken provenance or budget exhaustion stop. Complete observed lineages containing
provider failures are Degraded. No top-up, later cell or contingency use is granted.
Use the verified small-batch Langfuse policy and actual readback; merge outcome
documentation and report metrics/links/spending/remaining-cell forecast afterwards.


### Outcome — GPT-4o-mini compatibility denied; baseline not started

On4 November2026 the first actual completion of the separately reviewed native
compatibility phase returns HTTP403 with a provider Terms Of Service prohibition.
No generation ID, model/provider identity, output or usage is returned. The sole
phase is terminal/Incomplete on BLK-025 after one physical request, zero retries.
The six-probe approval is consumed; no second probe, recovery, baseline or ablation
may run. Root cause and denying entity remain unconfirmed.

The isolated campaign ledger retains the full USD0.019650 unknown reservation.
Read-only account/key evidence shows USD50 remaining/zero recorded usage, which
cannot adjudicate an individual attempt. Preserve all raw errors/responses and
approvals, both old campaigns and their ledgers/reservations. Independent outcome
Standards/Spec audits confirm preservation and the safe material stop.

PR#35 merged `c90d5afb5f8a41cf6da9ca1aeed5552fa4851bc5` for native provider/accounting.
Later baseline core remains unmerged engineering, with no baseline freeze or final
release. Outcome documentation/normal merge stays within the user's existing grant.
No additional paid probe, access workaround, cell, top-up or contingency use is
inferred. Provider-access clarification, request-level financial resolution and a
fresh explicit decision are required before further transmission. Read the
[full stopping report](gpt4omini-openrouter-blocked-20261104.md).


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
