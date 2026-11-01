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
The reviewed D9a fixture succeeded with audited D3a degradation. The subsequent authorized conv-50
pilot is incomplete after a malformed provider response (BLK-014); both approvals are consumed.
Read `docs/reproducibility/t5-pilot-conv50-d9a-20261101.md` before further T5 work. Preserve its raw
artifacts, partial state and charges. Full/fallback affordability remains unmeasured without pilot QA.
Further paid execution or recovery requires a new explicit decision; stop before full benchmark/T6–T8.
Checkpoint recovery implementation and offline tests are now authorized, with strict validation
unchanged. Follow `docs/reproducibility/checkpoint-recovery.md`; prepare a PR and stop before paid execution.
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
