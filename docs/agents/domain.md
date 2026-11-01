# Domain docs

This repository uses a single-context layout. All paths are relative to
the repository root.

## Before exploring

- Read `GLOSSARY.md` when present.
- Read decisions in `docs/adr/` relevant to the area being explored.

If these files are absent, proceed silently. The `/domain-modeling` skill
creates them when terms or decisions are resolved.

## Layout

- `GLOSSARY.md`: shared domain vocabulary.
- `docs/adr/NNNN-short-title.md`: numbered architecture decision records.

## Vocabulary and decisions

Use glossary terms consistently in issue titles, proposals, hypotheses
and test names. When a needed concept is missing, reconsider the wording
or note the gap for `/domain-modeling`.

If a proposal contradicts an ADR, identify that ADR and explain why the
decision should be reopened.
