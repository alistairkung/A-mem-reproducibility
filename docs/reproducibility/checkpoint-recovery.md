# BLK-014 checkpoint recovery

Implementation/offline testing and PR preparation are authorized. **Paid continuation is not.**
The parent remains immutable and incomplete; BLK-014 remains Open because this change does not fix
the provider's malformed JSON. The [investigation](blk-014-offline-investigation.md) explains why
syntax repair would alter the memory trajectory.

## Bound continuation

`--checkpoint artifacts/runs/pilot-conv50-d9a/phase.json` selects the exact conv-50 prefix:
263 notes/outcomes, counter261, 263×384 float32 embedding matrix, saved corpus/document map and
original note order/IDs. It resumes at offset263 / `D15:8`, without regenerating metadata or the
rejected shared decision. Existing stale embeddings remain stale until original consolidation.
Nominal remaining work: 1,018 logical calls, at most 3,054 physical attempts.

The verifier checks parent inventory, partial-state identity, original manifest/config, runtime assets,
compatibility provenance, source migration, prefix/outcomes and settled parent accounting. Any unknown
study charge blocks recovery. Scientific/provider/scoring files must match the parent; the only
permitted source migration files are `amem_repro/{checkpoint,runner,phases,forecast,budget}.py`.
Their current hashes and the changed-file list bind to the new approval; old hashes stay intact.

A new child run ID, approval ID, output directory and lineage-specific cache identity are required.
The ledger durably claims the parent receipt once, even if the child is interrupted before its first
request. A second child cannot silently retry the same prefix; another recovery then requires a new
reviewed decision. The old halted permit is never reopened. Existing conservative reservations,
settlement stops, retry policy, global USD42 usable allowance and stage limits remain enforced.

Parent failure/deviation records are inherited as checkpoint-origin records, with original run IDs
and stable failure indices. They are not new model calls. Local child events and costs remain separate;
a completed child stays degraded. The parent stays incomplete. The composite cost-only forecast reads
parent physical generations once (including the rejected billed decision), excludes the zero-attempt
blocked event, adds child generations and checks full 1,544-call coverage. Neither a partial child nor
unknown charges can select scope. Only the verified parent failure is admitted for cost accounting;
this is not acceptance of malformed output in the adapter.

The low-level runner can subsequently locate the completed recovered build for `cached_qa` using the
same verified checkpoint lineage and source identity. It loads the complete cache, not the partial
snapshot. This is a dependent QA rerun requiring its own paid authorization; no live cached-QA phase
is added or executed here.

## Offline preparation commands

Run after the final reviewed source is fixed; use new paths if these already exist:

```sh
.venv/bin/python -m amem_repro.phases preflight \
  --assets artifacts/assets --output artifacts/checkpoint-recovery-preflight.json
.venv/bin/python -m amem_repro.phases plan --phase pilot \
  --run-id pilot-conv50-checkpoint-child \
  --assets artifacts/assets --preflight artifacts/checkpoint-recovery-preflight.json \
  --compatibility artifacts/runs/compatibility-d9a-20261101/phase.json \
  --checkpoint artifacts/runs/pilot-conv50-d9a/phase.json \
  --provider-contract-policy canonical-index-strings-v1 \
  --output artifacts/checkpoint-recovery-plan.json
```

The generated plan is `approved:false`, with 1,018/3,054 request limits and a provisional USD10 cap.
It is not spending authority or an extension of the consumed pilot allocation. Review the requested
dollar ceiling separately, including USD0.806717 already incurred and USD8 contingency. An eventual
approved copy must bind the final source, preflight, parent receipt/snapshot/events and explicit limits.

The future execution entrypoint is the existing `execute` command with the same `--checkpoint`,
`--compatibility`, assets and preflight, plus a separately authorized approval file. Credentials are
supplied privately through the environment. No execution command has been run during implementation.
Optional saved-QA exports remain separate; local events/state/scoring/ledger are authoritative.

## Review and limits

Recovery tests use deterministic mocks and deny sockets. They must verify restore without encoding,
stale index/duplicate links, interrupted versus uninterrupted construction/consolidation, inherited
failures after later aborts, strict malformed-output rejection, one-shot claims, original QA order,
dual scoring and one-time parent accounting. Provider recurrence remains possible. This continuation
is one dependent memory build; it is not an additional stochastic trial or a fresh build under new code.
