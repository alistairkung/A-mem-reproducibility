# Linking Only / conv-44: conditional recovery investigation

7 November 2026. Base: PR #47, `ec968e6a34e189fa195ca6aee7bb4ecca1badbb2`.

**Paid continuation remains stopped.** The frozen author code supports an unevolved-note fallback for this transport exception, and the paid metadata is recoverable. However, the unfinished note's historical UUID and wall-clock `last_accessed` were not saved. The exact 231-note checkpoint can be restored; the complete in-flight object cannot. The user's explicit requirement to stop when the partial-turn boundary cannot be restored exactly therefore applies. A narrowly disclosed reconstruction is a proposal requiring a further decision, not an implemented recovery.

The eleven accepted cells and [their population-specific analysis](gpt4omini-linking44-transport-stop.md#available-matched-results) remain valid. Linking Only / conv-44 remains Incomplete at 231/675 notes and 0/158 answers. There is no complete 558-question four-condition comparison or interaction estimate, and no missing result is imputed.

## Findings at the partial-turn boundary

| Question | Verified finding |
|---|---|
| Is the paid metadata preserved? | Yes: attempt 17285, raw response bytes, parsed generation event, usage and provider ID are retained. Its reported charge is US$0.0001086; conservative charge is US$0.000109. |
| Could its output be reused without another generation? | Yes, as the same pending turn's recorded metadata. This establishes output availability, not exact recovery of every field of the temporary note constructed afterwards. |
| Did failed attempt 17286 reach OpenAI or incur a charge? | Unknown. No HTTP status, response body, usage or provider ID was returned. The prior read-only account close has zero unexplained aggregate movement, which does not settle this request. Its full US$0.021044 reservation stays held. |
| Does the frozen author define a transport fallback? | Yes. `process_memory` catches ordinary `Exception` around `_evolve`, including its shared-decision call, and returns `(False, note)`. `RemoteProtocolError` qualifies. No JSON output or invented decision is needed for that catch. |
| Why did the actual phase not insert the note? | `OpenRouterController` records the transport error, halts the ledger and raises `BudgetStop`, which inherits `BaseException`. It bypasses the author's ordinary-exception catch. That financial stop is intentional. |
| What would the original fallback do? | Insert the metadata note unevolved, append its retrieval document/vector, leave the counter at 231, apply neither strengthening nor neighbour updates, and perform no consolidation at that turn. This is a counterfactual source result, not an event that occurred in the parent. |
| Can the stopped partial turn be restored exactly? | The 231 committed notes, stale vectors, mappings and counter can. The uninserted note's UUID and `last_accessed` cannot be established from retained evidence. |
| Does existing checkpoint infrastructure admit this parent? | No. The executor requires a sealed recoverable-length parent; this parent is terminal. Its fallback guard requires a settled decision. Neither rule is changed by this investigation. |

Frozen source is revision `f9a173dec325d84fcc97e7828775c7b241c33466`, verified byte-for-byte by `verified_author_bytes`. Relevant code is [MemoryNote construction and author fallback](../../memory_layer.py), [native transport and durable accounting](../../amem_repro/openrouter.py), and [current checkpoint/fallback eligibility](../../amem_repro/gpt4omini_campaign.py). Scientific support-source fingerprint remains `817d3d06017d8d119c80eae3b487b482c0977ee6b8e383f8bd080d9c2c35b17d`.

## Exact state versus reconstruction

`MemoryNote` generates its UUID and access timestamp after metadata analysis and before `_evolve`. Neither is part of the metadata response or shared-decision prompt. No action executes at the failed call, so the action observer does not capture the temporary note. The partial-memory archive contains only inserted notes. Generation/turn traces preserve the input, metadata, request and failure, not this uninserted object's full attributes.

The accepted [T6 replay policy](t6-replay.md#reference-data-and-normalisation) maps UUIDs to insertion indices and removes wall-clock access times **only in comparison copies**. This permits a behavioural-equivalence comparison; it does not restore unavailable historical values or authorise replacing them in a recovered execution artifact. The original dataset timestamp is preserved and is distinct from the missing wall-clock access timestamp.

An offline characterization proves the information gap: two different pending UUIDs can produce the identical committed snapshot when `BudgetStop` interrupts before insertion. Thus the snapshot cannot uniquely determine the missing UUID. This does not establish that a replacement UUID would change scores; the blocker is the current exact-restoration/provenance requirement. The algorithm's fallback and financial affordability alone do not satisfy that requirement.

## Minimal proposal requiring a further decision

Permit reconstruction of **only the uncommitted D10:15 note's UUID and wall-clock `last_accessed`**, assigning and preserving explicit new values without representing them as recovered historical values. All 231 existing note attributes and index rows must remain exact. The original dataset timestamp, content and paid metadata must remain unchanged.

If that exception is explicitly approved, a reviewed implementation could consume the saved metadata once, reproduce the recorded ordinary transport exception at the author-call boundary without network transmission, and let the frozen author catch insert the note unevolved. It must record the distinction between replaying an observed failure and obtaining a new provider decision. It must not resend attempt 17286, fabricate output, release its reservation or overwrite the terminal parent.

The resulting state would contain 232 notes with counter 231, zero actions for D10:15, unchanged prior stale rows and one newly encoded row. A separately sealed reconstruction supplement would bind the new note fields, evidence and original fallback transition. Only then could a fresh one-shot child continue at D10:16: 443 remaining turns and 158 questions, normally 1,202 new generation requests. The original 464 attempts plus those requests total the original 1,666-request cell allocation, including the unresolved failed attempt. No additional metadata generation is needed for D10:15.

This proposal changes the recovery representation policy, not prompts, action gates, retrieval, scoring or model settings. It offers normalized algorithmic equivalence rather than a claim of byte-exact historical partial-object restoration. A completed lineage would remain Degraded. Implementation, full offline regression, independent reviews, normal merge, fresh provider/balance/service checks and a source-bound approval would still be required. No part of this proposal is implemented or paid-admitted here.

## Financial position and preservation

The independently rechecked sealed parent consumes US$0.107623 conservative settled model cost, US$0.021044 reserved unknown exposure and US$0.092400 service upper bound: **US$0.221067 combined**. Remaining headroom under the same US$5 cell cap is **US$4.778933**: US$3.791333 model and US$0.987600 service (12,345 units under the original allocation). These are arithmetic limits, not a fresh completion forecast or financial release.

No model request, remote reporting import, new financial approval, reservation release or ledger mutation was made during this investigation. Last verified campaign model/service exposure remains US$8.296465, with US$33.703535 of the planned allocation remaining and the US$8 contingency untouched. Last observed prepaid credit was US$46.20182925; this investigation does not assert a new live balance reading. All four unknown reservations total US$0.079994 and remain retained. The historical two-unit service allowance also remains separately accounted for as in PR #47.

The terminal phase file remains `65d8f6a672863bdfbc2a5d5a6d5d95b3fd25c0a2b9b2dfd8cbef53032c80917b`, SQL seal `97dbd9f331503b15d97a73d7b3f210a0c4ed13363b0bfe33e63fedbc4e2b32aa`, and ledger file `9f425359b58c0f8167eeb5446b7ad5d0063e94ebd02b350259491829e5b28d46`. Prior Full, conv-49, expansion and DeepSeek evidence is preserved. Existing Langfuse readback remains the parent evidence; no final-cell Experiments exist because no questions were answered.

## Investigation diary and verification

1. Read the conditional grant, frozen protocol, previous stop and BLK-022 history. Kept paid execution closed.
2. Distinguished the outer author exception catch from the inner JSON parser and from the financial `BudgetStop`. Independent investigators confirmed the distinction.
3. Checked metadata, charge, committed-state restoration, missing temporary-note attributes and current checkpoint exclusions. Identified the exactness blocker before implementing a recovery path.
4. Added nine network-free characterization cases across all four action gates. They distinguish ordinary-transport fallback from financial stop, verify counter/index behaviour, and demonstrate the missing identity cannot be inferred from the committed snapshot.
5. Ran those cases with existing action, OpenRouter and executor regressions: **162 passed in 28.24 seconds**. No production support source changed. A new full paid-release suite was not run: the mandatory scientific eligibility gate failed before implementation, and no paid-release gate is claimed.

Independent Spec inspection searched 940 sealed or adjacent execution/cache/service files. It found the 231 committed note UUIDs and a separately identified Langfuse service-instance UUID, but no pending-note identity or access time. Its four offline cases distinguish author fallback, gated fallback, native-controller stop and comparison-only normalization. The appended vector in that harness is explicitly synthetic. Independent Standards inspection additionally uses local CPU embeddings with the actual retained prefix: restored rows stay exact, the reconstructed note reproduces the failed prompt, and supplied metadata requires no new generation. Neither harness produces an operational recovery checkpoint.

Evidence paths below are relative to `artifacts/gpt4omini/verification/`:

| Evidence | SHA-256 |
|---|---|
| `linking44-transport-eligibility-spec/eligibility-spec.json` | `d8e8a8f5551605e90ad6bca8e90fe0e54baaf0f713e253b951d9e8da7ff91cd1` |
| `linking44-recovery-assessment/standards-boundary-assessment.json` | `5135fbca88cb544572ff7feb7fbb6316f3f1fa67ffd98564f421f6ae99abdadd` |
| `blk027-release/finance-linking44-conditional-recovery-headroom.json` | `7d4d7f2eedb350f32bd1c767dafa600b968c4aca6741ed489eae089441f7d231` |
| `linking44-recovery-investigation/focused-tests.txt` | `577ff156e86d71dd53f16e0e8b413e2b2a7021a442db094dadd82e2e90e28121` |

BLK-022 remains Open. The reduced-scope report is ready to use with its explicit missing-cell limitation; a completed twelve-cell coursework claim is not supported.
