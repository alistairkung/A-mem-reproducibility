# T5 baseline readiness — conv-50 pilot incomplete

## Current status — BLK-014 blocks pilot completion

The user authorized one conv-50 pilot from the D9a plan (USD10 / 1,544 logical calls / 4,632 attempts).
It ran on merged PR #13 source `c659856` and is **incomplete**: 263 notes/index rows retained, zero
of 204 QA, 526 physical requests and USD0.739432 conservative charge. A normally finished shared
decision contained malformed JSON at 970 output tokens, below its unchanged 4,000-token allowance.
The durable halt blocked the next transmission. No retry, recovery or scoring result was fabricated.

Study total is USD0.806717; USD41.193283 remains usable while preserving USD8 contingency. Missing
QA and later construction coverage prevent a defensible full/fallback cost forecast. The original
population target remains unchanged. BLK-014 is Open; the successful small fixture remains valid
historical evidence, not proof of long-run provider reliability. All phase approvals are consumed.
See the [pilot report](t5-pilot-conv50-d9a-20261101.md) for immutable artifacts and socket-disabled replay.
Stop before further paid execution, the full benchmark or T6–T8.

Checkpoint engineering and offline tests are now separately authorized. The
[recovery runbook](checkpoint-recovery.md) describes the parent-bound child, exact stale-index restore
and new approval/preflight gates. This does not authorize paid continuation or resolve the provider defect.

## Historical checkpoint — functional compatibility verified; pilot approval pending

The authorized phase `compatibility-d9a-20261101` completed the frozen 18-turn/four-question fixture
under D9a and `canonical-index-strings-v1`. Its status is **degraded solely by approved, fully audited
integer-string deviations**. There were no other processing, metric or provider failures.

| Verification | Result |
| --- | --- |
| Reviewed implementation / PR | `4e7f82b`, [PR #13](https://github.com/alistairkung/A-mem-reproducibility/pull/13); user-approved for merge, merge not yet claimed here |
| Source/configuration bundle | `02dc368e77f1a1e36d7d2deeffe1e6b0c9a7e8de9e715864852566e704ad7285` |
| Fixture state | 18 notes, 18 evolution outcomes, 18×384 index, evolution counter 17 |
| QA identities/order | `conv-26:qa:0`, `conv-26:qa:1`, `conv-26:qa:2`, `conv-26:qa:4` |
| Logical / physical requests; retries | 44 / 44; zero retries and unknown charges |
| Audited degradation | Seven completions, 19 string indices; raw/returned argument hashes equal |
| Conservative phase / cumulative study charge | USD0.053118 / USD0.067285; 66 cumulative physical requests |
| Input / output tokens | 95,676 / 20,330 |
| Maximum observed output tokens by stage | Metadata 155; shared decision 1,572; query 49; answer 39 |
| Scoring | Corrected/historical views use the same four saved predictions; no metric failures |

All 44 original argument strings and schema/stage controls verify. Complete cache integrity and phase
inventory verify. The output policy remains `d9a-shared-decision-4000-v1`: shared decisions 4,000,
other stages 1,000; no prompts, schemas, parsers, temperatures, retrieval or scoring were changed.
Offline suite: **268 tests and 92 subtests passed**; independent Standards/Spec reviews and the
refreshed network-disabled runtime preflight are clear. This fixture verifies functionality, not
benchmark accuracy or long-conversation robustness.

BLK-007 is **Mitigated**: provider strict-schema violations remain real and audited, while the
approved boundary policy works in the fixture. BLK-013 is **Resolved for this fixture under D9a**;
4,000 tokens are not guaranteed sufficient for the full pilot. BLK-012 stays Resolved. Hosted tokenizer
parity (BLK-008), representative affordability (BLK-009) and live Langfuse tracing (BLK-011) remain Open.
Optional reporting does not block authoritative local result collection.

The existing saved-result exporter was then verified against the configured Langfuse project:
two experiments (corrected and historical), four questions each, with all eight question traces
read back through the current Observations API. Run/condition/population/repetition, scoring and
provider/output policy IDs, original degraded status, seven deviations, original cost metadata and
saved predictions match. This is **import timing**, not original inference timing; no model calls or
new ledger charges occurred. Automatic construction-time tracing remains unwired (BLK-011).
Receipts: `artifacts/compatibility-d9a-langfuse-export.json` and
`artifacts/compatibility-d9a-langfuse-verified.json` (headers/SDK key attributes excluded).

- [Corrected scoring experiment](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=a2ca1a936b9b2427)
- [Historical scoring experiment](https://cloud.langfuse.com/project/cmvxd2aby005wad0ei7wt2d5o/experiments/results?baseline=f00c6621e4195c75)

Preserved local evidence:

- `artifacts/runs/compatibility-d9a-20261101/`: immutable approval/preflight, raw events, four predictions,
  complete summary/phase inventory and both scoring views.
- `artifacts/cache/2dccf21427d0df63137bb9911fe9cce085bfe5aac0f1b90f2e54ac7db38fba63/`:
  verified complete memory/index build.
- `artifacts/compatibility-d9a-verification.json`: raw-argument, cache, outcome and dual-scoring checks.
- `artifacts/compatibility-d9a-preflight.json` and `artifacts/pilot-conv50-d9a-plan.json`:
  matched runtime evidence and the exact **unapproved** pilot plan.

The D9a phase authorization is consumed. The pilot plan selects all 568 turns and 204 original QA
of conv-50, 1,544 logical calls and at most 4,632 physical attempts, with a USD10 hard cap. It is
`approved:false`; no pilot cache, run or execution exists. Separate explicit authorization and a new
`artifacts/pilot-conv50-d9a-approved.json` approval artifact are required. API credentials must come
privately from the process environment; the CLI never loads `.env`. The exact future command is
**not executed**:

```sh
.venv/bin/python -m amem_repro.phases execute \
  --assets artifacts/assets \
  --preflight artifacts/compatibility-d9a-preflight.json \
  --compatibility artifacts/runs/compatibility-d9a-20261101/phase.json \
  --approval artifacts/pilot-conv50-d9a-approved.json
```

T5 remains open; stop before that pilot, the full benchmark or T6–T8. The following checkpoints
preserve earlier pending and failed states; their consumed approvals cannot be reused.

## Historical checkpoint — D9a approved; fresh verification pending

After PR #12 merged this failure record (`5078459`), the user approved
[D9a](decisions.md#d9a--approved-shared-decision-output-allowance-and-one-fresh-verification-phase):
4,000 output tokens for shared decisions and 1,000 for every other stage, with original temperatures,
prompts, schemas and parsers retained. The uniform all-arm output policy is
`d9a-shared-decision-4000-v1`; approvals bind its configuration hash and explicit stage-cap map. Pricing must
allow the 4,000-token bound while reservations remain stage-specific: 319,373 microUSD for a shared
decision and 315,773 for another stage. The USD2 phase hard cap and USD42 usable study allowance
(preserving USD8 contingency) are unchanged.

Exactly **one further fresh** 18-turn/four-question phase is authorized after offline tests, review and
new runtime preflight: 44 logical calls, at most 132 physical attempts including SDK retries, no extra
probes planned, and at most USD2 additional expenditure. That phase has not been executed and no
approved execution plan exists yet. BLK-013 remains Investigating; BLK-007 remains Investigating.
A 4,000-token limit is not a guarantee of fixture or full-pilot completion. The conv-50 pilot remains
unready and unauthorized; full benchmark and T6–T8 are also outside this task's execution authority.

The D9a offline suite passes **268 tests and 92 subtests**, including stage-specific SDK requests,
usage/reservations, rejection of missing/incorrect limits, failed settlements and genuine SDK retries.
Live verification still requires the final reviewed source and refreshed runtime preflight.

D9a implementation `4e7f82b` has clear independent Standards/Spec reviews (71 tests/60 subtests and
132 tests/60 subtests respectively). Refreshed network-disabled runtime preflight passes under source
bundle `02dc368e77f1a1e36d7d2deeffe1e6b0c9a7e8de9e715864852566e704ad7285`.
These gates permit preparing the newly authorized phase; they do not establish live compatibility.

## Historical checkpoint — consumed 1,000-token phase

Checked 1 November 2026, Hong Kong time. **At this checkpoint the conv-50 pilot was not ready to
execute.** The one authorized fresh compatibility phase was incomplete and its authorization consumed;
no further paid phase was then authorized. The following failure evidence and decision request are
preserved as history. T5 stays open; T6–T8 are unstarted.

## Engineering and merge evidence

[PR #11](https://github.com/alistairkung/A-mem-reproducibility/pull/11) was marked ready and merged as
`167470b514a7e97d097a647e6e1a12972860ff5e`. BLK-012 was corrected in `d0e0bf9`; both previously
failing settlement regressions pass. Full offline suite: **247 tests and 71 subtests passed**.
Repeat Standards and Spec reviews found no actionable safety defect; independent focused runs passed
26 tests and 111 tests/39 subtests respectively. GitHub reported no failing required checks.

Actual offline runtime preflight passes with sockets disabled, verified assets and author metrics.
Asset audit: 257 pinned files and 24 locked packages. All four manifests expand and hash correctly.
Frozen author source, prompts, schemas, retrieval, generation configuration and scoring are unchanged.
Source/configuration bundle SHA-256:
`74aec8da2fd001597c6f41772644aeb3e9ef3800bef787c328bae224c67ad45c`.

## Fresh compatibility outcome

| Measurement | Observed value |
| --- | --- |
| Run | `compatibility-d3a-20261101` |
| Executed source | Merged main `167470b` |
| Approval | One fresh fixture; 44 logical / 132 physical maximum; USD2 additional cap |
| Policy | `canonical-index-strings-v1` |
| Status | **Incomplete** |
| Physical / logical requests; retries | 12 / 12; zero retries |
| Original fixture turns | Six notes/index rows retained out of 18 target turns |
| QA | 0 of 4; no quality result |
| Metadata / shared decisions | Six calls each |
| Input / output tokens | 11,683 / 4,005 |
| Conservative phase charge | **USD0.008316**; zero unknown charges |
| Cumulative study charge | **USD0.014167**, 22 physical requests; includes original failed fixture |
| Approved deviations | One completion, two string indices; original and returned hashes equal |
| Returned model / fingerprint | `deepseek-flash` / `bc19ba97cbe016479903222bb1578db6` |

The fifth decision's `['2', '3']` strings passed the approved validation-copy policy, with full audit
data and unchanged parser input. A later failure did not erase that deviation. **BLK-007 remains
Investigating** because the complete fixture has not succeeded.

The sixth decision reached `completion_tokens=1000`, `finish_reason=length`. Its 4,537-character
function-argument string ends inside an unclosed neighbor-tag string, so it is incomplete JSON.
The request still used the original prompt/schema, thinking disabled, temperature0.7 and max_tokens1000.
It was correctly rejected; a subsequent metadata event was blocked before transmission. That event
is not a thirteenth paid request. The halt is persisted, all received usage is settled, and the
partial memory counter remains 4. No completed reusable build or scoring views were fabricated.

## Offline diagnosis and preserved evidence

As the original construction neighborhood grew from zero to five notes, decision output tokens were
149, 262, 409, 569, 778 and 1,000. Generated neighbor-context characters grew from 0 to 2,802; complete
neighbor-tag totals were 0, 6, 18, 30, 49, followed by at least 62 tags in four complete lists before the
fifth list truncated. Metadata remained 132–155 tokens. The author requests full neighbor context/tags
and stores them for later prompts. This supports output growth from evolving metadata; it does not
establish that any particular larger cap will always suffice. No adapter shortening was found.

Exact failed argument SHA-256:
`26708080e3e5a0edb08a3f62d9e4265d3eebab088015c6b45526e88211037a9e`.
Offline SDK MockTransport replay reproduces rejection with one identical request, preserves the
partial arguments and blocks a following request. Existing length/malformed-output regressions remain
applicable; the correct rejection is not an implementation bug to bypass.

Safe ignored local evidence:

- `artifacts/runs/compatibility-d3a-20261101/`: immutable approval/preflight, fsynced events, summary,
  phase inventory and partial memory/index state.
- `artifacts/compatibility-d3a-{plan,approved,preflight}.json`: fresh provenance and explicit authority.
- `artifacts/compatibility-d3a-20261101-truncation-reproducer.json`: exact safe request/response.
- `artifacts/compatibility-d3a-{offline-replay,verification}.json`: no-network replay/integrity checks.
- `artifacts/blk012-fix/`: red/green/full tests and runtime preflight log.
- `artifacts/pilot-conv50-blocked-plan.log`: incomplete-phase provenance rejection; no pilot plan created.

The phase's artifact inventory verifies. Nineteen protected historical files are byte-identical.
The shared ledger necessarily gained the authorized phase; its original ten attempts and USD0.005851
charge remain intact. Raw artifacts and credentials are not committed.

## Historical decision request before D9a approval

The request below was subsequently approved as D9a; it does not itself record a successful live test.

The frozen D9 cap is 1,000 tokens for every generation. Increasing it is an experimental amendment,
not a routine repair. Proposed minimum: change **only shared-decision** maximum output to 4,000, keep
all other stages at 1,000, preserve prompts/schemas/parsers/temperatures, and use identical stage limits
across all four arms. Update bindings/reservations and regression tests before another live request.
At the reviewed peak rates, the maximum per-attempt reservation would be USD0.319373 instead of
USD0.315773; the phase's USD2 hard cap and study/contingency controls would remain intact. This is a
proposal, not an implemented change or a guarantee of sufficient output space.

Alternatives: separately authorize one new phase at the unchanged 1,000-token limit, accepting the
risk of recurrence; or retain the frozen protocol and stop paid work. Any new phase needs separate
explicit approval, even though the prior phase spent less than its USD2 cap.

## Pilot and Langfuse gates

The pilot manifest remains complete conv-50: 568 turns, 204 original QA, 1,544 logical calls,
at most 4,632 physical attempts and a separately approved cap up to USD10. Planning against the new
incomplete receipt correctly fails `Incomplete phase artifact inventory`. There is **no valid approved
pilot plan** and no pilot was executed. A successful compatibility receipt under the final unchanged
source/preflight/policy is required first; then prepare the plan and seek pilot approval.

Langfuse project authentication and synthetic ingestion/readback were verified previously with the
pinned SDK 5.1.0. Reporting is optional and local collection is independent. Live runner tracing remains
unwired (BLK-011); the saved-QA exporter cannot import a run with zero QA. No historical trace or
benchmark quality result has been fabricated. Reaching baseline readiness requires the compatibility
decision/test first; the optional tracing limitation must remain explicit.
