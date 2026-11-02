# T5 conv-50 baseline — verified degraded checkpoint lineage

Completed 1 November 2026, 12:56:57 UTC (20:56:57 Hong Kong). This is the original full-mode memory
algorithm under the approved DeepSeek/D3a/D9a substitution, on one complete conversation. It is not
the full benchmark or a four-condition comparison. No T6–T8 work or additional paid phase was started.

## Merge and execution authority

[PR #14](https://github.com/alistairkung/A-mem-reproducibility/pull/14) merged normally as
`ca6c68f0f109b474a5206f59085474b683a4f9ca`, from reviewed head `77afc36`; local `main` was synchronised
before execution. The fresh pre-merge suite passed **287 tests / 92 subtests**, including the 19
checkpoint regressions and spending/SDK retry tests. Required checks/branch rules were absent;
none was bypassed. Standards/Spec findings had been corrected and independently rechecked.
Source bundle: `a0f43a95bf523d8194908ec10612e97ce28daf5700754f651e95c53e0afad8e2`.
Frozen author files, adapter/contracts, scoring, scientific configuration and retrieval were unchanged.

The user's single-child approval capped additional spending at USD10, 1,018 logical calls and 3,054
attempts. A fresh immutable approval `7f9512c9-b1d3-4f49-ad8f-763de64e7b62` binds the current source,
preflight, original dataset/configuration and pinned parent receipt. It is now consumed.
No restart, further paid recovery or additional experiment is authorized.

## Checkpoint and completion verification

| Item | Verified result |
| --- | --- |
| Parent / child | `pilot-conv50-d9a` / `pilot-conv50-checkpoint-child` |
| Recovery / provider policy | `blk014-checkpoint-v1` / `canonical-index-strings-v1` |
| Parent receipt SHA256 | `a3d90514404a454cb894e9c716ffaccb26a1b054364aa8c8f3cd1f4509d7a231` |
| Restored prefix | Exactly 263 notes/outcomes, counter 261, original corpus/document map and float32 embeddings |
| First child turn | `D15:8`; no prefix regeneration or retry of the failed decision |
| Child / complete lineage | 305 new turns / all 568 original turn IDs, ordered |
| Final state | 568 notes/outcomes, 568×384 float32 index, evolution counter 566 |
| QA | All 204 unique original question IDs/data, in order; no dropped questions |
| Classification | **Degraded**; parent remains immutable and Incomplete |
| New unexpected processing / metric failures | Zero / zero |
| Model / observed fingerprint | `deepseek-flash` / `bc19ba97cbe016479903222bb1578db6` |

Pre-execution restore/export matched the entire archived state exactly, including embedding bytes.
The 227 stale prefix index documents were preserved on restoration. Subsequent original evolution
and consolidation may legitimately update old contexts/tags and index rows. The final cache retains
the original 263 note IDs, content, keywords, links, timestamps and exact prefix outcomes. This does
not freeze memories against later normal A-MEM evolution. All parent artifact hashes and historical
ledger rows are unchanged. The ledger has exactly one child claim for this checkpoint.

The inherited malformed decision remains rejected and its note unevolved: no JSON repair was applied.
All 179 parent failure records survive (176 D3a notices, one evolution failure, and two provider-completion
records: one rejected response plus the subsequent zero-attempt blocked event). The child adds 198
approved D3a notices, not new unexpected failures. Across the lineage, 374 completions / 1,470 integer
strings have complete validation-copy audits. All 1,543 accepted argument strings match provider output
bytes; the rejected 1,544th string is preserved without being returned as an accepted decision.
These audit counts explain degradation; they are not extra API requests.

The longest new shared-decision output was 3,851 tokens under the unchanged 4,000 cap, with no new
truncation. Metadata/query/answer caps remain 1,000; thinking remains disabled and original temperatures
remain unchanged. All four original schemas and request settings verify for every generation.

## Evaluation

Values are author-defined per-question means on a 0–1 scale, with unchanged category aggregation.
Both policies use identical saved predictions, original QA data and question order. Only reference/
scoring policy differs. Secondary author metrics and exact match remain in the saved views and tables.

| Category | QA | Corrected F1 | Corrected BLEU-1 | Historical F1 | Historical BLEU-1 |
| --- | --- | --- | --- | --- | --- |
| 1 | 32 | 0.298754 | 0.220344 | 0.298754 | 0.220344 |
| 2 | 32 | 0.317726 | 0.347131 | 0.317726 | 0.347131 |
| 3 | 7 | 0.095223 | 0.059462 | 0.095223 | 0.059462 |
| 4 | 87 | 0.561929 | 0.489568 | 0.561929 | 0.489568 |
| 5 | 46 | 0.632229 | 0.600825 | 0.344821 | 0.319523 |
| Overall | 204 | 0.482178 | 0.435322 | 0.417370 | 0.371892 |

Primary policy: `author-corrected-v1`; historical view: `author-legacy-c5-v1`.
Category-5 `adversarial_correct` is **29/46 = 0.630435**, reported separately. Overall corrected exact
match is 0.250000; historical exact match is 0.186275. Historical adversarial overlap is not evidence
of factual answer quality. Scorer revision SHA256:
`2f4303ff0775b67f2c328fa5df88af36172596b064ea2f661924730a355fcd3c`.
There were no metric-computation failures or prediction changes during rescoring/export.

Retrieval initially selected 10 notes for every question. Expanded entries including duplicates ranged
39–58 (mean 48.7647), without deduplication or truncation. Local retrieved-context counts ranged
14,291–27,939 tokens (mean 20,028.1373). Method: pinned DeepSeek-V4.1-Flash `tokenizer.json`, revision
`314113f8a7dadb388215396ba5fbee2c610a04d6`, tokenizers0.23.3, `add_special_tokens=False`.
Hosted parity is unverified (`token_count_exact:false`); API prompt usage remains authoritative.

## Calls, usage and conservative spending

All charges below use reviewed peak rates with per-attempt upward rounding, not a provider invoice.
All attempts have known usage; there were zero retries, unknown charges or pending reservations.

| Scope | Logical / physical calls | Conservative USD |
| --- | --- | --- |
| Parent pilot | 526 / 526 | 0.739432 |
| Child | 1,018 / 1,018 | 2.219082 |
| Combined conv-50 baseline | 1,544 / 1,544 | 2.958514 |
| Earlier compatibility phases | 66 / 66 | 0.067285 |
| Entire study incurred | 1,610 / 1,610 | **3.025799** |

| Baseline stage | Calls | Input tokens | Output tokens | Ledger USD |
| --- | --- | --- | --- | --- |
| Memory metadata | 568 | 321,255 | 81,356 | 0.194269 |
| Shared decision | 568 | 1,507,940 | 852,829 | 1.476040 |
| Query keywords | 204 | 70,536 | 9,431 | 0.032572 |
| Answers | 204 | 4,152,406 | 8,182 | 1.255633 |

Strengthening/neighbour updates execute locally after the shared decision; no additional model calls
are attributed to them. Their observational action records remain in the raw events. Stage latency
sums are in the final verification receipt. Current usable balance after reserving USD8 contingency
is **USD38.974201**; unused child allocation is not authorization for further spending.

## Cost-only population forecast

The forecast was generated after completion/identity verification and **before inspecting quality
summaries**. It uses all parent/child physical usage once, including the rejected billed decision,
and credits the completed full-mode conv-50 baseline once. It does not credit independent repeats.

| Four configurations, one build each | Remaining calls | Remaining estimate USD | Total including incurred + USD8 | 2× remaining-cost sensitivity |
| --- | --- | --- | --- | --- |
| All 10 conversations | 61,400 | 116.365687 | **127.391486** | 243.757173 |
| Frozen fallback: conv-49, conv-50, conv-44 | 16,936 | 31.736435 | **42.762234** | 74.498668 |

Recommend the predefined fallback under D10a's cost-only rule. Its point forecast fits USD50 with
USD7.237766 planning headroom after the separate USD8 contingency. Its 2× diagnostic exceeds the
ceiling; this is not a confidence interval or measured bound. One full-mode conversation does not
bound other conversations/conditions. Reconcile new usage against the forecast and retain hard caps.
No additional population or configuration was executed, and no performance-based population tuning
was performed. Main execution still requires separate approval.

## Local evidence and next gates

These ignored artifacts are local study evidence, not public download links. Preserve them with the
ledger; a fresh clone contains the protocol/tests but not the raw run. Credentials/headers are excluded.

- `artifacts/runs/pilot-conv50-d9a/`: unchanged incomplete parent and raw failing response.
- `artifacts/runs/pilot-conv50-checkpoint-child/`: bound approval, preflight, checkpoint lineage,
  original generations/retrieval/predictions/references, summary, both scoring views and final inventory.
- `artifacts/cache/73f7c8f11549f969cc6ca4223cbac99a0e0e49e4e12d5e6cff32a2cf5b29a2d2/`:
  verified completed memory/index cache, including inherited failures.
- `artifacts/checkpoint-child-{preexecution-20261101,memory-verification,completion-checks,final-verification}.json`:
  source/restore/ledger, full memory, prediction identity and final contract/scoring audit receipts.
- `artifacts/checkpoint-child-cost-forecast.json`: cost-only recommendation and assumptions.
- `artifacts/checkpoint-child-tables/`: unchanged-view JSON, question/aggregate metric CSV exports.
- `artifacts/study-budget.sqlite` and `artifacts/checkpoint-child-ledger-{before,after}.sqlite`:
  durable accounting and snapshots. `artifacts/pr14-premerge-offline-suite.txt` retains test output.

BLK-014 is Mitigated by verified checkpoint completion, not a repaired provider guarantee. BLK-007
remains Mitigated; BLK-009 is Mitigated by a representative cost forecast. BLK-013 remains Resolved
for D9a on this conversation, with broader cap adequacy unproven. BLK-008 tokenizer parity and BLK-011
automatic Langfuse tracing remain Open; local results are authoritative and complete. No new live
Langfuse tracing was introduced during the run.

Before T6: review/accept this degraded baseline and cost recommendation; separately authorize any
remaining selected-scope T5 full-mode baseline collection and T6 itself. The frozen fallback still has
two uncollected full-mode conversations (conv-49 and conv-44). Do not treat this pilot as completion
of all selected-conversation baseline work, or as independent stochastic evidence. Prompts/parsers/
schema/settings changes, new recovery phases, T6–T8 and further paid execution remain unauthorized.
