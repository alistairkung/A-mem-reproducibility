# Issue tracker: GitHub

Issues and specs live in GitHub Issues for `alistairkung/A-mem-reproducibility`.
Use the `gh` CLI. Add `--repo alistairkung/A-mem-reproducibility` to every
`gh issue` command below so fork defaults cannot target the upstream repository.

## Conventions

- Create: `gh issue create --title "..." --body-file <file>`.
  Write multiline bodies to a temporary file with actual newlines.
- Read: `gh issue view <number> --json number,title,body,labels,comments`.
- List: `gh issue list --state open --json number,title,body,labels,comments`.
  Add label filters as needed.
- Sub-issues: `gh issue create --parent <parent> ...` or
  `gh issue edit <parent> --add-sub-issue <child>`.
  If unavailable, put `Part of #<parent>` at the top of the child body and
  link the child in the parent's task list.
- Dependencies: `gh issue edit <child> --add-blocked-by <blocker>`.
  If unavailable, put `Blocked by: #<number>` at the top of the child body.
  An issue is unblocked when every blocker is closed.
- Count open native blockers:
  `gh api repos/alistairkung/A-mem-reproducibility/issues/<number> --jq .issue_dependencies_summary.blocked_by`.
  For fallback dependencies, inspect each referenced issue's state.
- Comment: `gh issue comment <number> --body-file <file>`.
- Labels: `gh issue edit <number> --add-label "..."` or `--remove-label "..."`.
  Use the role mapping in `docs/agents/triage-labels.md`.
- Close: post the explanation with `gh issue comment`, then `gh issue close`.
  Post comments separately so explanations also reach already-closed issues.

## Pull requests as a triage surface

**PRs as a request surface: no.**

## Skill instructions

"Publish to the issue tracker" means create a GitHub issue.
"Fetch the relevant ticket" means read the referenced GitHub issue.

## Wayfinding operations

For `/wayfinder`:

- Map: one issue labelled `wayfinder:map`, with Notes, Decisions-so-far and Fog.
- Children: sub-issues labelled `wayfinder:<type>`, where type is
  `research`, `prototype`, `grilling` or `task`. Use the parent task-list
  fallback when sub-issues are unavailable.
- Frontier: choose the first open, unassigned child in map order with no
  open blockers.
- Claim: assign the child to `@me` before starting work.
- Resolve: comment with the answer, close the child, then add a short
  summary and link to the map's Decisions-so-far.
