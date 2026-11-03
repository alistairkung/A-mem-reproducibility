# Run2 original evolution fallback and exact566-note continuation

3 November2026. This records the user's separate engineering/merge and one-phase paid grant.
It supersedes the consumed227-note continuation's stopping boundary for this new scope only.
Historical Run1 and Run2 phases, labels, snapshots, responses, receipts and charges stay immutable.

## Scientific finding

**Yes, the frozen author treats the observed malformed evolution JSON as a recoverable per-turn
failure; our adapter's unconditional phase halt was stricter than that algorithm requires.**
`memory_layer.py:AgenticMemorySystem._evolve` catches JSONDecodeError and returns `(False,note)`;
`process_memory` also catches ordinary evolution exceptions. `add_note` retains metadata, stores the
note/index row and does not increment the counter or consolidate on this failure. The real saved
D24:12 response reproduces that fallback offline, unchanged. Provider generation produced invalid
inner JSON; strict schema parsing rejects it; the author catch supplies fallback; the experiment
wrapper previously escalated that supported fallback into phase termination. These are separate facts.

This does not authorize ignoring every bad response. Wrapped text can fail raw JSON parsing while
the author's existing cleanup parses a positive decision. Treating that as fallback would change the
counter. Therefore `run2-original-evolution-fallback-v1` requires normal HTTP200/`tool_calls`, one
correct forced function, unchanged request/schema/settings, expected model/fingerprint and trusted
usage. Only syntax-invalid object-delimited shared-decision text is eligible: the frozen cleanup is
then a no-op and also fails. Strict validation continues raising AdapterError; rejected bytes never
become an accepted output, and nothing is repaired, returned cleaned or regenerated.

Metadata/query/answer failures, valid JSON with wrong schema/types, nonfinite constants, wrapped or
otherwise uncharacterized text, length exhaustion, transport, persistence, tracing, provenance and
financial faults remain terminal. BLK-013 keeps its separate checkpoint protocol. A new actual paid
child beyond the single grant is not authorized even if engineering supports a later continuation.

## Verification before the next transmission

A phase-bound opt-in and an in-process pending gate prevent new logical or physical requests after
eligible rejection. Every attempt must already be settled with matching usage; the sole historical
BLK-022 unknown remains fully reserved. An interrupted process cannot reuse its consumed approval;
an unsealed or unverifiable phase cannot seed a new child. No durable halt is cleared or restarted.

After the unchanged author catch completes, compare complete before/after notes and exact float32
stale index rows. Require unchanged existing notes/links/metadata/counter, unchanged new-note
metadata, no new links/actions, and exactly one appended note/document/embedding. Record a durable
`original_evolution_fallback` failure with raw-argument/state hashes and policy identity, verify
tracing health and journal/accounting, then release the pending gate. Any proof/control failure halts.
This is execution-policy remediation, not a new A-MEM memory or provider-acceptance algorithm.

The original supported fallback and resulting state match uninterrupted original-author replay.
Paused ancestors can therefore remain part of this lineage with inherited degradation. No completed
Run2 comparison is relabelled or mixed with Run1. Apply the same verified failure policy to any
separately approved future condition; do not select policies by observed quality.

## Narrow sequential recovery

Reuse the existing Run2 checkpoint walker, ownership/claims and cumulative ledger. A new
`run2-financial-sequential-state-v1` lineage anchors both immutable historical receipts: p0's fixed
BLK-022 prefix and p1's pinned BLK-014 stop. Validate each ancestor against its own archived source,
preflight, sealed inventory and journal, not today's launcher. Future engineering continuations must
advance a verified original BLK-013 fallback; unknown charges and other material failures stop.

The V3 reviewed support migration permits only eight named files (the existing five observed support
files, adapter, runner and new fallback verifier), with explicit Git commit, current-source preflight,
unchanged scientific pins, credential proof and real-runner cloud gate. No schema, prompt, scoring,
generation, action, retrieval or embedding-refresh change is permitted. Old V1/V2 records remain valid.
Only the newest cumulative failure journal is inherited, avoiding repeated ancestor-failure copies.

## One paid authorization

Parent `run2-full-conv-44-r0-p1`; fresh child `run2-full-conv-44-r0-p2`. Restore exactly566 ordered
notes, counter564 and stale566×384 float32 index; preserve both failures and unknown454. NextD24:13;
109 turns and158 original questions,534 logical calls/1,602 physical attempts maximum. Additional
conservative cap **USD2.629990**, original cellUSD5, Run2USD42 usable/50 overall, protectedUSD8.
Existing exposureUSD2.370010 includes unknownUSD0.324404 in full. A consumed approval is never reused.

Before any transmission require full offline suite, exact reference/candidate archive replay,
independent Standards/Spec reviews, merged source/launcher pins, runtime preflight, immutable
checkpoint/ledger verification and conservative affordability/service-capacity checks. New unknown,
provider contract outside the verified narrow fallback, auth/ingestion, provenance or spending fault
stops. No second actual paid phase, later cell, semantic retry or contingency use is authorized.
The one-shot launcher creates no approval and contains no continuation loop.

## Evidence

Local evidence is preserved separately under `artifacts/run2-fallback-recovery/`. The source-bound
cloud fixture remains under `artifacts/run2/observed-recovery/gate-b/<source-fingerprint>/` and must
include explicit malformed-fallback verification. Immutable p0/p1 directories and the original
Run2 ledger remain authoritative. Failed test/preparation attempts remain in the evidence directory.
Release test/review/cloud evidence and the one approved execution outcome will be appended after
verification; this engineering record does not claim a successful paid continuation.

Current source fingerprint: `fc5fc67e0a0276948b1c8ac38ec4bbd0fab2fa09b44badc4c2a517cee3503fa7`;
reviewed source commit `7921b15cccb7b6517e2b2e77a35576cdb04285eb`. Both independent code reviews
and gate audits are clear. The source-bound gate verifies75 evidence hashes, including130 observations
from the actual new Run2 phase/permit/fallback executor:24 turns/one question, two rejected decisions,
counter22 and50 settled mock attempts. Both saved-result Experiments verify two items/28 scores.
Its actual manifest hash matches run, binding and cloud metadata. The separate18-turn helper's
manifest label is an explicit synthetic placeholder; it supplies engineering replay/tracing/length
coverage, not a primary manifest-identity claim. Its131 success/18 length observations and eight
Experiment items/112 scores also verify. All model transmissions use MockTransport, zero LLM network.

Complete original/full-candidate archive replays match1,544 requests,568 notes,204 questions and all
state/index/retrieval/prediction/scoring comparisons, differing only in the implementation label.
Runtime preflight is ready with network disabled. Cost-only sensitivity prices every remaining call
at its empirical stageP95 (Run2 construction, labelled Run1 QA proxy), adds10% retry cost and one
peak-request reservation headroom:USD2.604027 fitsUSD2.629990 byUSD0.025963. This is a conservative
scenario, not a completion guarantee; hard limits dominate. Included Core capacity is bounded at
82,701 units for this one phase, without a new service allocation. See `cost-preflight.json`.

Final release: **784 tests/92 subtests pass**,17 expected warnings,1164.19s. Independent Standards
and Spec reviews and75-file cloud audits are clear. The first full run's sole failure was an
outdated negative-test message expectation (783 tests/92 subtests passed); the implementation had
correctly rejected stale source at preflight. The corrected four rejection cases and complete rerun
pass without production changes. Preserve both logs, including the earlier preparation failures.


## Consumed continuation outcome

PR#31 merged `66d3ffa`; the single p2 approval is consumed. Exact566-note recovery collects all675
turns/158 QA with zero new malformed outputs,534 requests/USD1.796479 and totalUSD4.166489 exposure.
All1,771 runtime observations verify; final Experiment import exceeds64MiB local batch size and
readback fails. The sealed phase stays Incomplete on BLK-024, despite locally complete scientific collection with inherited degradation. Offline16-span batching is a prospective reporting-only remedy, not live verified
or authorized re-import. BLK-009 reopens for measured affordability. No further paid phase/import or
frontier release is authorized. Read [verified outcome and evidence](run2-conv44-collected-export-blocked-20261103.md).
