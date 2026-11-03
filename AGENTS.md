## Agent skills

### Issue tracker

Issues and specs live in GitHub Issues for `alistairkung/A-mem-reproducibility`.
Before reading or publishing tickets, read `docs/agents/issue-tracker.md`.

### Triage labels

Use the five default triage labels.
Before assigning a triage state, read `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: root `GLOSSARY.md` and `docs/adr/`.
Before exploring domain concepts or design decisions, read `docs/agents/domain.md`.

## Reproducibility study

Before planning or executing study work, read `docs/reproducibility/experimental-protocol.md`
and `docs/reproducibility/decisions.md`. Follow `docs/reproducibility/implementation-tickets.md`
for issue dependencies. The approved protocol and ticket creation do not authorize implementation,
commits, pushes or paid API execution; those require separate user authorization.

Current work is T5 through baseline readiness; PR #11 is merged. Before execution, read the latest
authorization in `docs/reproducibility/decisions.md` and the phase's immutable approval/artifacts.
PR #14 is merged as `ca6c68f`. The authorized child `pilot-conv50-checkpoint-child` completed conv-50:
568 notes, 204 QA, degraded with inherited BLK-014 failure and audited D3a deviations. Read
`docs/reproducibility/t5-conv50-baseline-20261101.md` before further T5 work. Preserve the immutable
incomplete parent, completed child/cache, raw outputs and cumulative USD3.025799 study ledger.
All paid approvals are consumed. The cost-only forecast recommends the frozen three-conversation
fallback; remaining T5 collection, further paid execution/recovery and T6–T8 need separate approval.
T6 now provides the offline replay gate using that completed lineage. Before T7 changes or replay
verification, read `docs/reproducibility/t6-replay.md` and run its regression commands. Preserve fixed
fixtures/oracles and original artifacts; inject the candidate full-mode implementation for equivalence
checks. T7's four action gates now pass the full-mode equivalence gate and offline reviews (PR #16).
Before changing action gates or preparing T8, read
`docs/reproducibility/t7-action-gates.md`. T8, paid requests and further collection require separate approval.
The user has now separately authorized T8 implementation and paid main execution within the existing
USD50 ceiling/USD8 contingency. Before T8 work or paid transmission, read the latest decision and
`docs/reproducibility/t8-execution.md`; require reviewed, phase-bound immutable approvals. Finish the
two missing full-mode fallback baselines before ablations. Recovery/repetitions still need separate
approval; the T8 skill ends with a PR ready for review, without inferred merge authorization.
Preserve the frozen author files; add support code separately. A consumed phase approval cannot be reused.
Before any paid phase, read `docs/reproducibility/baseline-readiness.md` for the verified fixture,
historical plans and consumed approvals. Additional paid execution requires a new decision.

## Run 2 campaign

Before Run2 engineering, observability verification, paid execution or recovery, read
`docs/reproducibility/run2-protocol.md` and the latest authorization in
`docs/reproducibility/decisions.md`.
Run1 is immutable exploratory evidence; keep its USD8.530133 ledger/results/caches unchanged.
Run2 uses separate artifacts/accounting and requires GateA, real-runner Langfuse GateB, reviewed
offline checks and a frozen affordable approval before paid cells. Follow the Run2 protocol's
bounded recovery/stop rules; historical Run1 approvals cannot authorize or seed Run2 cells.
PR#26 is merged as `207eac0`. The first Run2 cell stopped at227 notes/zero QA with BLK-022:
HTTP200 body-read failure, successful SDK retry and one retained unknown-charge reservation.
Read `docs/reproducibility/run2-first-cell-incomplete-20261103.md`; no later paid cell/recovery may
start until the financial/recovery decision is resolved. Preserve the consumed root and ledger.

## Reproducibility Blocker Tracking

Before coding or research work affecting reproduction, experimental integrity, model compatibility,
data validity, costs or interpretation, read `docs/reproducibility/blockers.md`.

- Match the current issue to an existing blocker before assigning a new stable ID. Track material
  reproducibility issues, not every ordinary coding mistake.
- Record new blockers promptly with observed evidence. Separate confirmed facts from assumptions,
  hypotheses and untested solutions; keep credentials, headers and sensitive environment values out.
- Append dated fix attempts with commits, tests and outcomes. Preserve unsuccessful attempts and
  rejected alternatives. Resolve a blocker only after documented verification succeeds.
- Before submitting a PR investigating or resolving a blocker, update its entry and summary index.
  Reference applicable blocker IDs in PR descriptions and implementation reports.
- Preserve the approved protocol and scientific meaning. Never modify the experimental protocol or
  weaken a schema, metric or validation rule merely to make a blocker disappear; report the conflict
  and obtain the required explicit decision instead.
