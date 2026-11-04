# GPT-4o-mini Full baselines

## Conv-44 acceptance

PR #36 merged normally as `61d527a4edbc2d2f4d542e322dd347ab4d54ab4d`.
The original 675 turns and 158 questions completed in order, in one fresh build.
All 1,666 baseline requests settled. Independent audits matched all 675 float32
embedding rows against the saved corpus and preserved the original stale index,
including 43 rows whose indexed text differs from current memory text. The
evolution counter finished at 675. The implementation emitted no baseline
provider failure, original fallback, scoring failure or recovery. The Phase A
classification is **Degraded** under its accepted compatibility history.

| View | Overall F1 | Overall BLEU-1 | Category 5 correct |
| --- | ---: | ---: | ---: |
| Corrected | 39.50% | 34.52% | 18/35 |
| Historical | 38.58% | 33.70% | 18/35 |

Langfuse readback verified 3,710 observations on 836 runtime traces and 316
reporting items with 4,494 scores and 158 original QA trace associations. The
first item readback had 4,059 visible scores. A later GET verified all values
without further export or inference.
[Corrected Experiment](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=b4a39a3e02e2f361)
and [historical Experiment](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=bd8af7375fe2248e).

Baseline model charges were US$0.39390465. Key and account usage moved by exactly
this amount. The campaign had US$0.39965355 in individually verified charges after
compatibility, with US$0.459417 conservative exposure including the US$0.058950
permanent historical reservation. Available prepaid credits were US$49.58869545.
All 1,671 settled generation IDs and upstream responses were independently verified.

The measured-stage model scenario gives US$0.332656 for Full / conv-49 and
US$0.364510 for Full / conv-50. Nine ablations at the same Full stage rates project
to US$3.275642. The whole-study model estimate including compatibility exposure
is US$4.432225. Doubling remaining model costs and allowing 16,000 service units
per remaining cell gives a combined sensitivity of US$17.20 against US$42 usable.
These are cost scenarios. Future action settings can change prompt and output lengths.
Phase A used 9,988 included Langfuse units. The observed organization count reached
33,906. The service allocation for the next baseline fits within 100,000 included units.

## Remaining Full cells

Each cell has a separate physical runs directory, cache, source-bound approval,
opening financial snapshot and reconciliation. Financial admission checks the
US$5 cap for its conversation, the US$15 total of the three caps and the US$42
usable campaign ceiling. The original US$0.25 compatibility sublimit and three
retained reservations stay allocated to conv-44. An accepted predecessor seal,
exact SQL history, positive independent audits, reconciled charges and an affordable
whole-study forecast precede the next admission. Full / conv-49 precedes Full /
conv-50. Both use the same scientific configuration and exact restored-state policy.
