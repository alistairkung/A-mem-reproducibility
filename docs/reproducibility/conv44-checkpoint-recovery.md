# Exact conv-44 checkpoint recovery

The user authorized implementation, offline tests, independent Standards/Spec reviews, merge after
all required checks and **one** bounded paid child. See the
[current decision](decisions.md#authorization--exact-conv-44-checkpoint-engineering-merge-and-one-child).
This engineering record grants no additional spending or ablation. At preparation, no child has run.

## Pinned state and continuation

Parent: `artifacts/runs/t8-full-conv44-r0-20261103/phase.json`, canonical receipt SHA256
`dad7f09f944e0de792787cf40f48f22a19af955353601d48f1c16c12fe62d45b`.
The original failed phase remains immutable and Incomplete. Verify its inventory and settled848-call,
USD1.415538 cost against the cumulative ledger; later spending cannot mask a lost historical prefix.

Recovery policy: `blk013-conv44-checkpoint-v1`. Restore424 notes/outcomes with their exact keys,
content, metadata, links and ordering; counter422;424×384 float32 embeddings, corpus and document map.
Preserve intentionally stale embeddings. Restore through the existing snapshot interface without
encoding, metadata generation or index refresh. Keep the failed `D18:21` evolution and original
fallback; it increments no counter and changes no neighbours. Start only at `D18:22`.

The suffix contains251 turns and all158 original questions in frozen order:818 logical calls,
at most2,454 physical attempts under the existing retry rules. Consolidation occurs only at original
positive-decision thresholds, including500/600 if reached naturally. Do not pre-consolidate restoration.

Use the existing checkpoint, phase, permit, manifest runner and saved-result comparison interfaces.
Only the two explicitly pinned full-mode study parents (conv-49 and conv-44) are eligible; this is
not arbitrary recovery or a child-of-child chain. Keep the old conv-49 eligibility and completed
conv-49/conv-50 evidence intact. Scientific/provider files cannot change during source migration;
the permitted support files are `amem_repro/{checkpoint,budget,phases,study,comparison}.py`.

## Safeguards and approval

Create a new run/approval identity and lineage-specific isolated cache. Atomically claim the exact
parent once and transfer its existing cell ownership to the child while retaining the historical
parent edge/halt. A crash, failed settlement, interrupted request or failed child cannot release
another attempt allowance or permit an automatic restart. Unknown charges block execution.

The immutable approval binds parent receipt/snapshot/events/source, reviewed current source,
dataset/configuration, assets/preflight, model/fingerprint, D3a policy and D9a stage limits. The child
has a **USD3 hard additional cap**,818 logical calls and2,454 maximum attempts. It uses the existing
`artifacts/study-budget.sqlite`, USD42 usable cumulative limit and USD8 reserve within USD50. The
before-recovery ledger holds USD7.705436/3,868 settled calls, zero unknown charges; do not reset it.

Retain original DeepSeek Flash, disabled thinking, temperatures, prompts, schemas/parsing, retrieval,
action gates and scoring. D3a remains `canonical-index-strings-v1`; shared decisions remain4,000
tokens, all other stages1,000. No provider output is repaired or retransmitted for semantic failure.

## Offline preparation and execution

Run from the repository root after final reviewed source is fixed, using new output paths rather
than overwriting previous receipts:

```sh
.venv/bin/pytest -q
.venv/bin/python -m amem_repro.phases preflight \
  --assets artifacts/assets --output artifacts/t8/conv44-recovery-preflight-20261103.json
.venv/bin/python -m amem_repro.study plan \
  --receipt artifacts/t8/conv44-recovery-preflight-20261103.json --assets artifacts/assets \
  --condition full --conversation conv-44 --run-id t8-full-conv44-checkpoint-child \
  --checkpoint artifacts/runs/t8-full-conv44-r0-20261103/phase.json \
  --output artifacts/t8/conv44-recovery-plan-20261103.json
```

Planning creates `approved:false` and does not claim a permit. Independently verify actual restore/
export equality and embedding bytes, historical hashes/ledger rows, parent ownership and absent child
claim. After verified merge and post-merge preflight, materialize a fresh approved copy under the
explicit user grant. Credentials enter privately through the process environment, never this document.
Execute the existing CLI exactly once with that approval:

```sh
.venv/bin/python -m amem_repro.study run \
  --receipt artifacts/t8/conv44-recovery-preflight-20261103.json --assets artifacts/assets \
  --checkpoint artifacts/runs/t8-full-conv44-r0-20261103/phase.json \
  --approval artifacts/t8/approvals/t8-full-conv44-checkpoint-child-20261103.json
```

The example approval path is not itself permission or a claim that execution occurred. The controller
and durable ledger enforce the recorded grant before each transmission. On any new provider/output,
provenance or spending failure, retain partial state/raw evidence/charges and stop; no second child
or recovery is authorized.

## Acceptance and limitations

Verify675 original turns exactly once across parent/child,158 unique ordered QA, consistent final
memory/index and a complete cache bound to the lineage. Copy all inherited failures/deviations with
original identifiers, including after memory, question or postprocessing failures. Completed lineage
status must be Degraded. Save corrected/historical author scoring views from identical predictions,
report per-category F1/BLEU-1 and separate adversarial correctness; no extra model calls for rescoring.

Reconcile parent/child generations, usage and conservative charges once; retain the rejected parent
call. Reforecast remaining balanced costs before quality comparisons. Optional Langfuse reporting
must not gate authoritative local results. This remains one dependent memory build, not an independent
trial. BLK-013 remains Open: checkpoint completion cannot guarantee future outputs fit4,000 tokens.
Stop after verified completion/reporting or another material blocker. No ablation is authorized.

## Verified engineering checkpoint

Implementation `563e8f4` passes146 focused tests/60 subtests across old/new checkpoints, budgets,
SDK-budget handling and saved-result comparisons. The actual parent restores/exports identically,
including embedding SHA256 `04c1848cfa7e9ffb2158e9ce48503dc218be882dcc2fd52ae085bcfbe1195630`.
All43 protected files and the study ledger remain unchanged; unapproved execution rejects before
client/claim creation. Current-source runtime preflight passes with sockets disabled, source
`eea7acf5953ecea73deb7fdd5b406c77171f76ef6a4544e5c149346b5e89e6c4`.
Evidence: `artifacts/t8/offline/conv44-checkpoint-verification.json` and
`artifacts/t8/conv44-recovery-preflight-20261103.json`. Full-suite/final reviews and merge are pending
at this engineering checkpoint; the plan remains unapproved and no child has run.

Final integrated gates for PR#20: **570 tests/92 subtests pass** (16 intentional SDK metadata warnings),
both independent reviews are clear and the source fingerprint above remains unchanged. Full/focused
test and review receipts are preserved under `artifacts/t8/offline/conv44-recovery-*`. All runtime,
actual-parent and finance-readiness checks pass. Merge and the single live child are still pending
at this recorded checkpoint; no paid request is implied by the unapproved plan.
