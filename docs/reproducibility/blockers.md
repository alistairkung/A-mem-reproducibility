# Reproducibility blockers and resolutions

Last reviewed: 1 November 2026. Scope: the FTEC5660 controlled reproduction defined in the
[protocol](experimental-protocol.md), [decisions](decisions.md) and [tickets](implementation-tickets.md).
This tracker records evidence and investigation history; it grants no execution or protocol-change approval.

| ID | Blocker | Status | Affected phase | Evidence |
| --- | --- | --- | --- | --- |
| [BLK-001](#blk-001) | Original structured-output contract needs provider adaptation | Mitigated | T2, T5 | D2–D3; PR #9; BLK-007 |
| [BLK-002](#blk-002) | Published ablation runners are missing from the frozen release | Open | T6–T8 | Table 3; issue #7; `_evolve` |
| [BLK-003](#blk-003) | Paper and released benchmark populations differ | Accepted Limitation | T1, T5, T8, report | Paper §4.1; dataset hash; full manifest |
| [BLK-004](#blk-004) | Historical adversarial overlap scores reward a different reference | Mitigated | T4, T5, T8 | Author fix `b31a1dd`; scoring tests |
| [BLK-005](#blk-005) | Original cache provenance cannot isolate the planned study | Mitigated | T3, T5–T8 | Runner cache keys; cache rejection tests |
| [BLK-006](#blk-006) | Local runtime readiness required verified assets and active lock markers | Resolved | T5 local preflight | Initial/final preflight receipts; local T5 commit |
| [BLK-007](#blk-007) | DeepSeek strict function returned string connection indices | Investigating | T5 compatibility; downstream T6–T8 | Archived response; [offline policy tests](blk-007-compatibility-review.md) |
| [BLK-008](#blk-008) | Local tokenizer equivalence to hosted DeepSeek is unverified | Open | T4, T5, T8 token reporting | Pinned tokenizer recipe; final preflight receipt |
| [BLK-009](#blk-009) | Four-condition affordability lacks representative pilot evidence | Open | T5 scope decision, T8 | D10/D10a; counts; conservative spending ledger |
| [BLK-010](#blk-010) | Released retrieval default differs from paper category settings | Accepted Limitation | T5, T8, interpretation | D6; runner default; paper Table 8 |
| [BLK-011](#blk-011) | T5 execution is not connected to Langfuse tracing/export | Open | T5, T8 observability | Runtime call-path audit; verified synthetic trace |
| [BLK-012](#blk-012) | Failed usage settlement triggers SDK regeneration | Resolved | T5 and later paid phases | Terminal settlement guard; SQLite fault/retry regressions |

Before a paid run: **BLK-007 currently prevents compatibility acceptance and pilot progression**.
BLK-001's query/answer contracts have not been exercised live. BLK-008 limits token-count claims;
BLK-009 still requires a separately approved representative pilot and cost-only scope decision.
BLK-011 requires actual runner wiring; a successful connection probe alone does not enable it.
BLK-012's terminal settlement guard is verified offline; this does not authorize paid recovery.
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
- **Final resolution or limitation:** Adapter mechanics are mitigated, not end-to-end compatibility. Query/answer remain untested live; no alternative parser or schema was introduced.
- **Verification:** PR #9 records four offline contracts and the 44-call mocked original-agent slice. The actual fixture supplies only partial live evidence; BLK-007 remains a paid-run gate.
- **Research significance:** A provider-compatible request interface does not establish equivalent structured-output guarantees or equivalent benchmark behavior.

## BLK-002

- **ID:** BLK-002
- **Title:** Published ablation runners are missing from the frozen release.
- **Status:** Open
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
- **Final resolution or limitation:** Reconstruction is planned, not executed. Archive the original baseline and prove full-mode replay before T7.
- **Verification:** Required but pending: 16 action/configuration combinations, failure/counter boundaries and full-mode replay. No proposed test is reported as passed.
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
- **Final resolution or limitation:** Scoring interpretation is mitigated through explicit policies; historical results/predictions and completed live QA are unavailable.
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
- **Status:** Investigating
- **First observed:** 2026-11-01, T5 `compatibility-20261101`, completed at 06:33:12 UTC with incomplete status.
- **Category:** Provider compatibility
- **Expected behaviour:** The unchanged schema requires `suggested_connections` items to be integers, including under strict-function translation.
- **Observed behaviour:** The fifth decision returned `"suggested_connections": ["2", "3"]`. HTTP 200, `finish_reason=tool_calls`, 640 completion tokens under max_tokens=1,000: the JSON was complete but violated the requested integer contract. The request used `strict:true`, the beta endpoint and the exact original schema.
- **Evidence:** Safe local `artifacts/compatibility-20261101-reproducer.json` contains exact redacted request/response and violations; `artifacts/runs/compatibility-20261101/events.jsonl`, `phase.json`, `summary.json` and `partial-memory.json` retain the run. Report/regression: `dad8908:docs/reproducibility/t5-compatibility-20261101.md`, `dad8908:tests/test_contracts.py`. [Frozen schema/parser](../../memory_layer.py); [provider strict-mode guide](https://api-docs.deepseek.com/guides/tool_calls/).
- **Root cause:** **Unknown.** Confirmed provider-contract violation; server-side cause is not established. The prompt's quoted neighbor-ID example may influence generation (**hypothesis**), but does not explain strict-mode enforcement. Existing `as_index` accepts numeric strings; that does not make the returned JSON schema-valid.
- **Impact:** Compatibility failed before query/answer generation; T5 cannot progress to pilot, and T6–T8 remain downstream. This is not a baseline or accuracy result.
- **Options considered:** Preserve evidence and stop. Coercion, weakening the schema, skipping validation, changing prompts/settings or switching pipelines were not implemented and require explicit decisions. Repeating the request is paid recovery, not covered by the unspent cap.
- **Resolution attempts:**
  - 2026-11-01, approved fixture: ten physical requests, no retries; five metadata/four decision payloads valid and one decision invalid. Next metadata event was blocked before transmission, not an eleventh request.
  - 2026-11-01, offline investigation: verify serialized strict/beta/schema settings and independently confirm both type errors with `Draft202012Validator`; add rejection/unchanged-input regression.
  - 2026-11-01, archive check: artifact hash inventory verifies; follow-up suite records 132 tests/71 subtests passed. No recovery request or proposed repair was executed.
  - 2026-11-01, focused offline investigation: reconstruct the exact pre-decision prompt and pass the raw response to the original parser. Its state and embedding documents match an integer-only control; both counters advance 3→4, while strict rejection stays 3. Added 38 characterization tests; branch suite 92 tests/32 subtests passes. See the [proposal and schema audit](blk-007-offline-investigation.md). A field-scoped validation-copy policy is proposed only; no adapter fix or model request was made. All nine original evidence files remain byte-identical.
  - 2026-11-01, user-approved D3a implementation/offline tests (`48bc2d1`): add opt-in `canonical-index-strings-v1` for canonical ASCII strings in this field only. Validate a copy and return raw arguments unchanged; retain strict default, record hashes/type violations and mark affected runs degraded. Full offline suite: 238 tests/71 subtests passed, including the 44-call mocked phase and frozen-parser state/retrieval/counter comparisons. SDK MockTransport replay of the exact failing response preserves the serialized request and argument bytes. See [implementation evidence and remaining gate](blk-007-compatibility-review.md). Twenty historical evidence files remain byte-identical; no model requests, recovery or pilot occurred.
- **Final resolution or limitation:** **Unresolved.** Five notes/index rows preserved, zero of four QA completed; conservative peak-rate ledger cost USD0.005851, with no unknown charges. Response alias `deepseek-flash`, fingerprint `bc19ba97cbe016479903222bb1578db6`; immutable served weights not independently verified.
- **Verification:** Rejection/spending stop and the approved validation-copy policy are verified offline. Hosted compatibility is not. Future resolution needs a separately authorized live test with the unchanged wire schema and explicitly selected policy, recording residual reliability limits. Offline replay cannot resolve the blocker or erase the provider-contract violation.
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
- **Title:** Four-condition affordability lacks representative pilot evidence.
- **Status:** Open
- **First observed:** 2026-11-01, budget discovery/D10–D10a.
- **Category:** Cost
- **Expected behaviour:** Demonstrate that incurred plus remaining four-condition cost and USD8 contingency fit the USD50 ceiling before choosing scope or main execution.
- **Observed behaviour:** The USD250/three-full-repetition proposal was rejected. One full-data build per arm entails 62,944 nominal calls; the fallback entails 18,480. No conv-50 cost pilot has run. Affordability is unmeasured, not a confirmed budget overrun.
- **Evidence:** D10/D10a and [protocol budget table](experimental-protocol.md), [population manifests](../../manifests/full.json), [T5 / #5](https://github.com/alistairkung/A-mem-reproducibility/issues/5), local `artifacts/study-budget.sqlite`/phase receipt, `502b376:amem_repro/budget.py`, `502b376:amem_repro/forecast.py` and their tests.
- **Root cause:** Confirmed missing representative usage evidence. Token growth, retries and condition-specific evolution prevent converting call counts or tiny-fixture costs directly into a reliable study total.
- **Impact:** Full versus approved fallback remains undecided; additional repetitions and pilot/main/recovery require their separate approvals.
- **Options considered:** Adopt progressive caps and exact performance-independent fallback. Three repetitions are optional; dropping difficult questions, tuning on results or changing settings to fit the cap was excluded.
- **Resolution attempts:**
  - 2026-11-01, D10/D10a: approve conditional scope and one initial build per arm, not USD250 spending.
  - 2026-11-01, local T5: test durable per-transmission reservations, cumulative USD42 usable allowance and cost-only forecasts offline.
  - 2026-11-01, first fixture: retain conservative USD0.005851 for ten requests, including the invalid response; no pilot or scope decision followed.
- **Final resolution or limitation:** Spending controls mitigate runaway execution, not study affordability. Unknown charges retain reservations; forecasts remain estimates, and full-mode pilot cost is not a bound on every arm.
- **Verification:** Offline cap/retry/restart tests exist; live contract failure stops further transmission. Representative cost forecast and main-scope acceptance are pending.
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
- **Status:** Open
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
- **Final resolution or limitation:** Connectivity is verified; automatic paid-run tracing remains unwired. Keys/connection values are absent from records and `.env` is unchanged. No paid execution is authorized by this setup.
- **Verification:** Synthetic observation `56d4b434cfe14653` is visible as `A-MEM/langfuse-configuration-smoke`, environment `configuration-preflight`. Verification of actual model-call capture, failure finalization and study-identity exports remains pending.
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
