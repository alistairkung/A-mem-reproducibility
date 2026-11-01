# Approved study decisions

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
