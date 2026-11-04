# Run2 remaining-study affordability

4 November2026. BLK-009 remains **Open**. These are cost-only proposals, not a change to the
frozen population, order, model, scoring, conditions or paid authority. No remaining cell is authorized.
Read [the Run2 protocol](run2-protocol.md) and [reporting recovery](run2-reporting-recovery.md).

## Actual accounting and stage costs

| Phase | Known settled USD | Unknown reserved USD | Conservative exposure USD |
| --- | ---: | ---: | ---: |
| p0 |0.720433 |0.324404 |1.044837 |
| p1 |1.325173 |0 |1.325173 |
| p2 |1.796479 |0 |1.796479 |
| Lineage |3.842085 |0.324404 |4.166489 |

Count each physical attempt once, using its original ledger row. Attempt454 remains unknown/null
usage/fullUSD0.324404 reserved; successful retry455 does not reconcile its billing. There are1,666
logical/1,667 physical calls,1,666 settled and one unknown. Run1USD8.530133 is separate and unchanged.
The reporting recovery has zero model cost. OriginalUSD5 cell remainderUSD0.833511; theUSD42 planned
pool hasUSD37.833511 remaining;USD8 contingency remains protected. USD45.833511 remains under the
USD50 ceiling, of whichUSD8 is unavailable for planned execution. Langfuse incremental study fees
must fit the planned pool unless explicitly allocated elsewhere; the existingUSD29 subscription is separate.

| Stage | Logical / physical | Settled USD | Reserved USD | Conservative mean USD / logical call |
| --- | ---: | ---: | ---: | ---: |
| Metadata |675 /675 |0.228311 |0 |0.000338239 |
| Shared decision |675 /676 |2.284381 |0.324404 |0.003864867 |
| Query keywords |158 /158 |0.025470 |0 |0.000161203 |
| Answer |158 /158 |1.303923 |0 |0.008252677 |

Construction:USD2.512692 settled +USD0.324404 reserved =USD2.837096, orUSD0.004203105 per turn.
QA:USD1.329393, orUSD0.008413880 per question. The conservative construction mean deliberately
spreads the one unknown reservation across675 decisions; it is not measured metered usage.

## Nine ablations and two missing baselines

Only Full conv-44 has completed collection. Nine ablations **plus two missing Full baselines** remain
for the original12-cell design. They cannot be conflated: running only nine ablations would leave
Full results missing for conv-49/50, preventing balanced three-conversation comparisons.

| Future condition | conv-49 USD | conv-50 USD | conv-44 USD | Total USD |
| --- | ---: | ---: | ---: | ---: |
| Full |3.788501 |4.103796 |already incurred |7.892297 |
| Neither |3.788501 |4.103796 |4.166489 |12.058786 |
| Linking Only |3.788501 |4.103796 |4.166489 |12.058786 |
| Evolution Only |3.788501 |4.103796 |4.166489 |12.058786 |
| Nine ablations | | | |36.176358 |
| All eleven future cells | | | |44.068655 |

Future construction/QA respectively: conv-49USD2.139381/1.649121; conv-50USD2.387364/1.716432;
conv-44USD2.837096/1.329393. Stage components and cell totals are individually rounded upward to
microUSD; rounding components may sum one microUSD above the once-rounded cell total. Forecasts
use exact rational stage means. All unmeasured conditions use the Full-stage proxy: local action
suppression saves no generation call and may change later contexts/costs in either direction.

## Langfuse service forecast

Current official [Core pricing](https://langfuse.com/pricing) includes100K units/month and charges
USD8/100K above that level. [Billable units](https://langfuse.com/docs/administration/billable-units)
include observations, traces and scores. The frozen essential policy retains required scientific
observations and both scoring views while omitting successful import-evaluator bookkeeping and
original duplicate Scores. It does not discard any required metric value.

A normal cell with T turns, Q questions and A adversarial questions has planning units
`4T +40Q +6 +2A` through `(5 + action_slots)T +40Q +6 +2A`, covering base runtime, reporting observations/traces,
28Q+2A imported scores, and up to one D3 observation plus zero/one/two action observations per turn for Neither,
Linking/Evolution, and Full respectively. Thus upper construction coefficients are5/6/7,
not a condition-independent6. The four-condition average coefficient is6. This matches the prior
118,352–132,368-unit12-cell essential-policy analysis. Actual future exceptional events can exceed
this normal range; it is not a hard upper bound.

Use the larger16,878 daily-bucket display rather than adding it to13,174 hourly-lagged period units,
then add the new5,442-unit recovery (632 observations/316 traces/4,494 scores). Conservative planning
base22,320 units includes old partial writes; never credit/delete their fees. All eleven future cells
produce an estimated131,576–143,567 total period units:USD2.526080–3.485360 additional usage fees.
For seven new balanced-two cells, normal usage remains below100K. The current recovery itself fits
included units and creates no overage authority. Other traffic, delayed counters, billing period
rollover, rounding/tax or new failures can change fees. No future overage is approved by this analysis.

## Planning alternatives

All totals below include the already incurred/reservedUSD4.166489 exactly once. Subsets are proposals
based on cost, frozen selection and original Full order, with no quality selection or population redraw.
Conv-44 was preselected first before primary quality inspection; retain it to use the collected baseline.
Conv-49 is the next original Full baseline and the lowest projected additional cost. Excluding conv-50
still requires explicit authorization and makes these new, smaller populations rather than the frozen fallback.

| Proposal | New cells | Provider total USD | Normal service USD | Total with protectedUSD8 |
| --- | ---: | ---: | ---: | ---: |
| Original:3 conversations ×4 conditions |11 |48.235144 |2.526080–3.485360 |58.761224–59.720504 |
| Balanced:conv-44/49 ×4 conditions |7 |31.819960 |0 forecast |39.819960 |
| Smaller balanced:conv-44 ×4 conditions |3 |16.665956 |0 forecast |24.665956 |
| Minimum:conv-44 ×Full/Neither/Linking Only |2 |12.499467 |0 forecast |20.499467 |

The original scope is viable only with a new larger financial grant: point planned cost is
USD50.761224–51.720504, exceedingUSD42 byUSD8.761224–9.720504, while retainingUSD8 reserve.
It is not viable within the current grant. Current point estimates fit individualUSD5 cells, but
future growth may trigger those independent caps even if the campaign scenario fits.

[Table3 and §4.4 of A-MEM v11](https://arxiv.org/html/2502.12110v11#S4.SS4) compare neither,
linking without evolution, and Full; they attribute improved category performance to linking and
additional evolution. Our scopes investigate those directional contrasts descriptively, not identical
published scores. Evolution Only is our added condition, supporting a fourth-arm/interaction comparison.

- **Original:** all558 questions/condition across three conversations support every reconstructed
  Table3 contrast, category analyses and the novel Evolution Only comparison. Cross-model/released-data/
  k=10/scoring differences and one stochastic build/cell still preclude exact historical replication
  or robust uncertainty claims.
- **Balanced two:**354 questions/condition across conv-44/49,1,184 turns; all four arms retain matched
  comparisons and the novel evolution-only/interaction contrast. Losing conv-50 drops a frozen
  population stratum, reduces category coverage (only20 Open Domain questions), and prevents claims
  about the original558-question fallback. Two conversations are not independent live repetitions.
- **Balanced one:** all158 conv-44 questions and675 turns under four arms investigate the same contrasts
  within one conversation, including Evolution Only. Seven Open Domain questions and single-conversation
  dependence sharply limit generalization; no claim of balanced three-stratum coverage.
- **Minimum useful:** Full/Neither/Linking Only on the same158 questions is a narrower reconstruction
  of the published ablation. It can investigate linking and the incremental Full-versus-Linking contrast
  locally; it cannot isolate evolution without linking or estimate the full2×2 interaction. Other
  single-conversation limitations remain. It is not the approved four-condition study until revised.

## Sensitivity, retries and continuation

| Scope | −20% future cost | Point | +10% | +20% | +50% |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original provider total USD |39.421413 |48.235144 |52.642010 |57.048875 |70.269472 |
| Balanced two provider total USD |26.289266 |31.819960 |34.585308 |37.350655 |45.646696 |
| Balanced one provider total USD |14.166063 |16.665956 |17.915903 |19.165850 |22.915690 |
| Minimum provider total USD |10.832872 |12.499467 |13.332765 |14.166063 |16.665956 |

Service andUSD8 reserve are additional. Multipliers are transparent sensitivity scenarios, not
confidence intervals; one Full cell supplies no statistical estimate of ablation/conversation variance.
Observed transport retry frequency is1/1,666 logical calls, with one unknown/full reservation.
One malformed shared decision used the verified original fallback; p2 had zero new retries/failures.
The conservative stage proxy already embeds that reservation pattern. Continuing a verified checkpoint
adds no repeated logical work; state restore is offline. New failed/retried attempts still cost and
unsupported failures halt. No new recovery authority or automatic repetitions are inferred.

A separate combined stress adds20% future-stage growth,1% additional settled-retry allowance,
one extraUSD0.324404 unknown reservation per future cell **beyond the embedded stage allowance**,
and two extra continuations per future cell at1,500 additional service units each (rounded planning
proxy from prior gate/recovery overhead, not a measured universal bound):

| Scope | Provider USD | Service USD | Total including protectedUSD8 |
| --- | ---: | ---: | ---: |
| Original |61.058006 |6.125360 |75.183366 |
| Balanced two |39.898018 |1.432240 |49.330258 |
| Balanced one |20.264057 |0 |28.264057 |
| Minimum |14.898201 |0 |22.898201 |

These aggregate scenarios do not override per-cellUSD5 caps. A conv-44 proxy grows toUSD4.999787
at20% before extra unknown exposure, leaving almost no cell headroom; a failure can stop it early.
Extra Langfuse fees, recoveries and any cap/budget revision still require explicit decisions. Never
spend the protected contingency to make a failing forecast appear affordable.

## Recommendation and reproducible evidence

Recommend the **balanced conv-44/49 four-condition scope**, subject to explicit revised population/
order and phase-bound paid approval. It retains the complete ablation design and has useful normal
financial headroom. Its combined stress is tight and future cell caps remain binding. If greater
campaign-level headroom and fewer new cells are preferred, choose conv-44 under all four conditions;
the three-condition minimum sacrifices the novel evolution-only comparison. Do not authorize the
original scope from a favorable low-cost sensitivity; its conservative point already exceeds budget.
Before the next paid cell, freeze the chosen scope/order and refreshed caps/fee allocation explicitly,
verify current Langfuse capacity, then execute only the next approved phase and reforecast from its
actual stage costs. No such paid phase is executed under this handover.

Read-only calculator: [forecast-run2-remaining.py](../../scripts/forecast-run2-remaining.py).
Evidence: `artifacts/run2/reporting-recovery/{forecast.json,forecast-final.log}` binds the original
ledger SHA256 and exact rational cost means; `forecast-decimal-rounding-audit.json` preserves an
early superseded rounding check. It is a planning artifact, never a phase approval or ledger update.
