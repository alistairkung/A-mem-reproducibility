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
checks. T7, paid requests and additional benchmark collection require separate authorization.
Preserve the frozen author files; add support code separately. A consumed phase approval cannot be reused.
Before any paid phase, read `docs/reproducibility/baseline-readiness.md` for the verified fixture,
historical plans and consumed approvals. Additional paid execution requires a new decision.

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
