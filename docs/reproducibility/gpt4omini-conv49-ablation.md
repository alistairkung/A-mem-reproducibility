# Four-condition GPT-4o-mini conv-49 ablation

Authority: the user's 5 November 2026 mission, recorded in `decisions.md`.
Reference: the independently accepted Full / conv-49 build (509 turns, 196 QA).
Execute exactly three fresh cells in this order: `evolution_only`, `neither`,
`linking_only`. Do not repeat Full or execute another conversation.

| Condition | Strengthening | Neighbour updates |
| --- | --- | --- |
| Full (accepted) | on | on |
| Evolution Only | off | on |
| Neither | off | off |
| Linking Only | on | off |

Use the existing T7 gates. Strengthening includes new-note links and tag updates;
neighbour evolution changes existing-note contexts and tags. Retain the original
shared evolution decision in every condition, original insertion, counter,
consolidation, stale index, prompts, native schemas and scoring. Freeze
`openai/gpt-4o-mini-2024-07-18` via OpenRouter, OpenAI only with fallbacks disabled,
temperature 0.7 (category 5 answers 0.5), output limits 1,000 / shared decision
4,096, retrieval k=10 and five construction neighbours.

Each cell processes the exact original 509 turn IDs and 196 question IDs, with
its own empty store/cache and run identity. Full memory/provider outputs cannot
seed an ablation. Exact-state children may resume only their own condition and
configuration after a settled supported shared-decision exhaustion. Preserve raw
failures, strict rejection and the original author fallback. No JSON repair,
semantic retry or regenerated processed turn is permitted. Normally finished
malformed shared decisions continue only after the existing fallback verification.
Affected completed cells are Degraded. Unsupported errors, route mismatches, new
unknown charges, lost provenance or critical observability stop paid execution.

Before payment: run all four gate/isolation tests, original versus Full replay,
exact dataset identity/cache isolation tests, successive checkpoint/fallback and
financial fault tests, full-size bounded SDK reporting proof, current-source cloud
readback, full offline suite and independent Standards/Spec reviews. Resolve material
findings and merge normally. Freeze each source-bound single-use approval only
after the preceding cell's independent scientific/cloud/financial acceptance.

Keep the existing campaign ledger, its US$1.147803 opening conservative exposure
and US$0.058950 historical upper bound. Each new cell is capped at US$5 including
recovery; the three new cells share at most US$15 additional spending. The US$42
planned allocation and US$8 protected reserve remain. Reforecast after each cell;
do not infer Langfuse overage permission. Essential observations, all original QA
trace associations and both complete scoring views must verify through remote
readback. Reporting recovery uses saved predictions only after independent review.

Report question-weighted corrected F1/BLEU-1 overall and by category, historical
scores separately, adversarial correctness, memory actions, failures, costs and
Experiment links. Match original question IDs for Linking−Neither,
Evolution−Neither, Full−Linking and Full−Evolution, plus
Full−Linking−Evolution+Neither. These are descriptive single-build contrasts.
Compare published Table 3 directions with population/retrieval limitations; the
Evolution Only condition is additional. Review and normally merge final outcomes.

Historical Full and DeepSeek receipts, approvals, caches, ledgers and research
evidence remain immutable. All work runs in the isolated GPT checkout, preserving
the original research checkout at `b8b3656` for its historical source aliases.

Completed 5 November 2026. All three new cells passed independent acceptance as
Clean. See the [four-condition results and matched question scores](gpt4omini-conv49-four-condition-results.md).
