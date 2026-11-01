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

Current implementation scope: T1–T4 and offline tests are authorized on
`feature/reproducibility-foundation`, with separate commits per ticket and a consolidated PR for review.
T5 and paid execution remain gated. Preserve the frozen author files; add support code separately.

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
