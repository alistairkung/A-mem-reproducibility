# T5 baseline readiness — blocked by output truncation

Checked 1 November 2026, Hong Kong time. **The conv-50 pilot is not ready to execute.** The one
authorized fresh compatibility phase is incomplete. Its authorization is consumed; no additional
paid recovery, pilot or full benchmark has been authorized. See BLK-013 and the pending protocol
decision below. T5 stays open; T6–T8 are unstarted.

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

## Decision needed before another paid phase

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
