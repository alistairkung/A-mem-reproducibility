# T7 independent memory action gates

Authority: [issue #7](https://github.com/alistairkung/A-mem-reproducibility/issues/7), D7/D8 and
[2 November authorization](decisions.md#authorization--t7-independent-action-gates).
Reference: T6 merged in PR #15 (`87f34d7`), with fixed fixtures/oracles in [the replay gate](t6-replay.md).
No paid calls, T8 implementation or ablation collection is authorized by T7.

## Intervention

| Condition identifier | Strengthening | Neighbour updates |
| --- | --- | --- |
| `neither` | Disabled | Disabled |
| `linking_only` | Enabled | Disabled |
| `evolution_only` | Disabled | Enabled |
| `full` | Enabled | Enabled |

`amem_repro/actions.py` reads verified `f9a173d` source and extracts `_evolve`. Its only AST changes are
two Boolean guards: `action == "strengthen" and <flag>` and `action == "update_neighbor" and <flag>`.
Each original guard must occur exactly once. Tests remove those two additions and compare the entire
method AST, including source locations, to the original. The derived method is bound per instance;
the reference class and author source file remain unchanged. Flags are fixed at factory construction.

The shared call, prompt, schema, JSON parsing, pre-action validation, action order/bodies and return
value remain original. Note construction, generated metadata, `add_note`, counter increments,
consolidation, retrieval and scoring remain original. Valid positives count even when no action
executes; negatives/original failed processing do not count. Consolidation still occurs every100
positive decisions, including in `neither`. Stale embeddings and index refresh policy are preserved.

Strengthening includes directed links **and new-note tag updates**. Linking-only is therefore not a
pure graph-link ablation. Neighbour updates change existing-note context/tags. These are our operational
implementations of the published conditions, not verified copies of unavailable author ablation code
(BLK-002). Evolution-only is the fourth, novel condition. Retained shared-decision calls are control
overhead; the existing generation ledger charges them once. Passive action measurements record only
executed branches and zero separate API calls for those local operations.

## Binding and provenance

Use `make_action_agent_factory` through the existing agent/controller seam:

```python
from amem_repro.actions import make_action_agent_factory

factory = make_action_agent_factory(
    repo_root, condition="linking_only",
    controller_factory=controller_factory, token_counter=token_counter,
)
# Pass the same condition to run_manifest(..., condition="linking_only", agent_factory=factory).
```

`run_manifest` rejects condition/factory mismatches before construction and verifies the returned
agent's configuration before processing. Ablations require the matching gate factory. All four still
make the original metadata/shared-decision/query/answer calls. Existing `make_agent_factory` remains
the auditable frozen full-mode reference.

Every new run-start record and cache identity includes `condition`, `memory_actions`, action-policy
identifier `released-action-boundaries-v1` and `action_implementation` (`frozen-author` or
`t7-action-gates`), alongside existing source/data/configuration/repetition/provider fingerprints.
Evolution outcomes retain raw proposed decisions, list configured enabled actions and identify
proposed disabled actions on successful positive decisions (verified by the original counter increment).
Rejected raw proposals remain recorded with their failure and are not labelled gate-suppressed.
These observations do not rewrite the response or affect counting.

Different conditions require independent builds. Exact cache identities and completion hashes prevent
cross-condition reuse; cached QA can reuse only its matching verified build and is not a new build
trial. Existing T5 caches/receipts are unchanged and are not silently migrated into T7's identities.
The historical full-mode checkpoint is expressly rejected for any ablation. A positive decision or
malformed response is never repaired to make an ablated action executable.

## Required T8 regression commands

Run from the repository root; use fresh archive output directories on later invocations:

```sh
.venv/bin/pytest tests/test_replay.py tests/test_checkpoint.py tests/test_type_compatibility_characterization.py -q
.venv/bin/pytest tests/test_actions.py -q
.venv/bin/pytest -q
.venv/bin/python -m amem_repro.replay_baseline \
  --assets artifacts/assets --output artifacts/replays/t8-reference-check
.venv/bin/python -m amem_repro.replay_baseline \
  --assets artifacts/assets --output artifacts/replays/t8-full-mode-candidate \
  --full-mode-candidate
```

The first archive command uses the frozen implementation. The second binds the actual T7 full-mode
candidate through T6's `factory_builder` seam; its receipt labels `implementation: t7-action-gates`.
Both must independently match the **unchanged** T6 per-insertion oracle and historical observations,
including all failure/audit records and Degraded classification. No tolerance, response substitution
or golden regeneration is permitted. Existing output directories are refused.

These are offline regression commands, not permission to collect T8 data. The existing paid phase
CLI remains scoped to the full-mode compatibility/pilot workflow. T8 must separately implement/review
condition-bound phase approvals and spending controls before any ablation collection; a direct runner
call or available credential is not paid authorization. Remaining selected-scope T5 baseline collection,
T8 implementation/execution, population decision and new phase budgets still require user approval.

## Verification

T7's96 portable tests cover all4 proposed action sets ×4 configurations ×positive/negative decisions
×counters0/99, original rejected-output fallbacks, metadata/shared-call preservation, unchanged reference
class, captured opening golden states, exact AST delta, all4 independent cache builds/cached-QA reuse,
disabled-action measurement/provenance, rejected cross-condition/checkpoint reuse and rejected-positive
JSON being reported as failure rather than suppression.
The mandatory103-test T6 portable gate and complete429-test/92-subtest offline suite pass. Standards
and Spec re-reviews are clear after `a591ea8` fixes an observational rejection/suppression distinction;
its regression first reproduced three failing ablated cases and then passed all four conditions.
Both the first and final reviewed-code archive pairs pass. Final evidence, local and ignored by Git:

- `artifacts/replays/t7-reviewed-reference/verification.json`: frozen-author receipt SHA256
  `552b0e86057c9da7d2e0d03ac04a5b4db1c26e6ca25abaf5cec8878655d5d4d1`.
- `artifacts/replays/t7-reviewed-candidate/verification.json`: actual gated candidate receipt SHA256
  `3bcf45c32a874f12850df6ab509c8983c13d49a7011af4598b163212762ecdc6`.
- Each independently matches all1,544 captured requests,568 insertion hashes/outcomes, historical
  full states at263/568, five consolidations, all204 retrieval contexts/predictions/primary scores,
  both rescoring views and376 logical failure/audit records. Classification remains Degraded.
- `artifacts/t7-equivalence-comparison.json`: all verification fields match between reference/candidate
  except the explicit implementation label. Both run-start source fingerprints equal the current source,
  fingerprint `2206fa3f23e6f9b36f3721a4e6d75383f3a0db21081d5ed6308313f5cbb237d3`.
  Sockets were denied, paid calls were zero, and protected original run/cache/ledger hashes match.
- Logs: `artifacts/t7-reviewed-{reference,candidate}.log`, `artifacts/t7-reviewed-action-tests.txt`,
  `artifacts/t7-mandatory-portable-tests.txt`, `artifacts/t7-reviewed-offline-suite.txt`.
  The reproduced review failure is preserved in `artifacts/t7-review-suppression-red.txt`.

[PR #16](https://github.com/alistairkung/A-mem-reproducibility/pull/16) supplies the implementation and
verification record. BLK-002 is Mitigated by these operational gates, not recovery of historical author
ablation code. BLK-015's recording/runtime limitations still apply; offline equivalence is not evidence
of stochastic ablation performance. T8 and paid collection remain unauthorized.
