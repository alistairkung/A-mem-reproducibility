# BLK-014 — offline compatibility and checkpoint investigation

Investigated 1 November 2026. **Proposal only; no production change or recovery execution.**
BLK-014 remains Open. The [original pilot report](t5-pilot-conv50-d9a-20261101.md) and its immutable
incomplete receipt remain authoritative. No paid call was made and the study ledger is unchanged.

## Failure location

The preserved transport response is valid outer JSON, containing an invalid JSON *string* in
`choices[0].message.tool_calls[0].function.arguments`. That string is identical in the transport's
decoded response, SDK response and adapter output event: 4,076 characters, SHA256
`e4343dbdcc385261cff04faac6b4f8e101ffe2b8b64fbb2c072c4befb95f2ece`.
At offset4075 the final `}` appears while `new_tags_neighborhood`'s outer array remains open.
The terminal suffix is `"festival performance"]}`; the missing delimiter is an outer `]`.

The exact request contains the frozen schema with `strict:true`, beta endpoint, disabled thinking,
temperature0.7 and max_tokens4000. Response: HTTP200, `finish_reason=tool_calls`, 970 output tokens.
The schema still requires integer connection indices and nested string arrays for neighbour tags.
There is no evidence of SDK serialization or compatibility-layer shortening. The malformed arguments
are already present at the earliest preserved transport boundary, before SDK validation. Original
HTTP response bytes/headers were not retained; attribution to a particular internal provider component
is unavailable. Why the service returned malformed arguments remains unknown.

The [adapter](../../amem_repro/adapter.py) rejects `json.loads(arguments)` before the D3a temporary-copy
validator can operate. It preserves the response and stops the permit. The original
[`process_memory`](../../memory_layer.py) catches that ordinary adapter exception, records an evolution
failure, and stores the new note unevolved. The following metadata attempt encounters terminal
`BudgetStop` before transmission. Thus 526 physical calls produced 527 generation events, not 527 charges.
The [existing SDK replay](t5-pilot-conv50-d9a-20261101.md#failure-and-offline-investigation) already
verifies the identical wire request, one mock transmission, settlement and blocked continuation.

## Parser equivalence: bracket repair changes the algorithm's outcome

An offline characterization fed the exact raw string directly to the frozen author's `process_memory`,
using a copy of saved notes and the five recorded neighbour indices. It returned `(False, note)`,
recorded one `evolve` failure, changed no existing neighbour, and kept the new note's initial tags and
empty links. This agrees with the saved failure state. Its parser trims wrappers but does not repair
missing delimiters; [as_index](../../memory_layer.py) is never reached for malformed JSON.

A diagnostic copy with **one `]` inserted immediately before the terminal `}`** parses. It still
needs D3a for four string indices. The unchanged author then returns a positive decision, creates
links `[261, 259, 244, 243]`, replaces new-note tags and updates four neighbours. `process_memory`
itself does not increment counters; `add_note` increments only for its positive return, so applying
the repaired decision would also change the saved counter transition from 261→261 to 261→262.
It would eventually shift consolidation timing and the resulting index.

These are controlled parser tests with recorded neighbour selection, not a replay of the full build
or a test of a provider fix. **Returning repaired arguments cannot preserve the original parser's
effective behaviour for this response.** A temporary validation-copy repair followed by returning raw
arguments would retain the author's failure fallback, not apply the repaired positive decision. Such
an acceptance exception would nevertheless amend the current strict boundary/fail-stop policy; D3a
does not authorize it. Syntax repair is not equivalent to integer-string compatibility.

## What the checkpoint can preserve

The snapshot passes structural validation and restores/exports exactly: all 263 note identities,
attributes/order, links, context/tags, outcomes, corpus, document map, float32 embedding values,
counter261 and threshold100. Embedding bytes survive the JSON→float32 round trip. Eight comparisons
of frozen cosine-search code at k=5/10, using four deterministic cached-row query vectors, reproduce
the direct cached-matrix result. These exercise restoration/search, **not live query embedding or a
completed continuation**; runtime assets still need the existing pinned preflight.

Crucially, **227 corpus rows differ from documents reconstructed from current note metadata**. This
is expected with immediate index refresh disabled. Re-embedding the notes would erase intentional
staleness. Preserve the corpus and embedding matrix together; never rebuild them as a recovery shortcut.

The retained prefix is exactly the first 263 frozen turn IDs through `D15:7`; the next turn is
`D15:8` (zero-based offset263). Note263 already exists with its original failure fallback. Do not
regenerate its metadata, rerun its rejected decision, insert it again, or roll back its failure.
The aborted next metadata event has zero attempts and created no additional stored note.
Remaining nominal work is **305 turns × 2 + 204 QA × 2 = 1,018 logical calls**, at most 3,054 attempts
under the existing retry bound, subject to a separately approved dollar cap and conservative reservations.

This is a viable *candidate* checkpoint, not an existing resumable cache. Current constraints:

- `partial-memory.json` is `complete:false`; the cache loader correctly refuses to treat it as complete.
  The runner supports fresh builds or complete-cache QA, not prefix continuation.
- The old phase/permit remains halted and consumed. A child recovery needs its own approval, phase ID
  and directory, linked to parent receipt, snapshot and event hashes; it must use the same study ledger.
- Failure counters/build-failure records are not all contained in the partial state. Import parent
  failure/deviation events explicitly and baseline counters appropriately; preserve 176 D3a audits,
  661 transformed indices, the rejected decision, incurred charges and original outputs without
  double-counting calls or costs. A completed child/composite stays degraded; the parent stays incomplete.
- Restore the exact source/data/config/model/output-policy/repetition/asset identity and check provider
  fingerprint on subsequent responses. A source change for recovery support needs new preflight and an
  explicit reviewed provenance migration/compatibility decision: current receipt validators reject a
  source mismatch. Do not rewrite old bindings, label the prefix freshly built under new code, or use
  a second independent repetition to disguise continuation of the same memory build.
- Current phase completion checks expect 1,544 calls in one phase; the cost forecaster also rejects
  failed generations. A recovery-aware composite receipt/forecast path requires reviewed support;
  concatenating files or promoting the old phase is insufficient. All original question IDs/order,
  scores and full expected coverage must still verify before a representative forecast.

## Options and recommendation

| Option | Fidelity and operational trade-off |
| --- | --- |
| Fresh build under current strict policy | Simplest existing runner/provenance; discards no historical evidence but repeats 526 paid prefix calls, changes the stochastic prefix, and can hit the same class of failure again. A successful fresh run must not hide the failed one. |
| Restore all 263 notes with the failure retained | Preserves the realised author trajectory and saves prefix regeneration; requires reviewed checkpoint/lineage/forecast support and new approval. Full-mode recovered results are one dependent build, not a new trial. Future contract failures still halt under current policy. |
| Repair JSON and apply the positive decision | Changes links, metadata, counter and consolidation; rejected as a behaviour-preserving compatibility fix. Requires a separately defined algorithmic variant if ever pursued. |
| Audited raw shared-decision fallback | An opt-in, separately approved exception could return the original malformed string to the author parser, record failure and allow its existing unevolved-note fallback. It preserves this failure's memory semantics but changes fail-stop orchestration and admits a response without normal schema validation. It must apply uniformly across arms and preserve strict handling of other stages, transport/accounting stops and all valid-JSON field validation. Not implemented or authorized. |

**Recommend checkpoint recovery retaining the failed 263rd note, with the current strict boundary
unchanged initially.** First approve and offline-test only the necessary recovery/lineage support;
then decide on a separately bounded paid continuation. This avoids inventing the provider's intended
decision and avoids unnecessary regeneration. If repeated syntax failures make strict continuation
impractical, consider the explicit raw-fallback policy as a separate scientific/protocol decision.
It is not a provider-contract repair or an automatic extension of D3a. Raising max_tokens has no
support from this normal-finish, below-cap failure.

## Required deterministic regression gates before recovery

1. Exact captured response plus a minimal nested-array missing-bracket fixture: adapter rejects once,
   preserves raw strings/usage, halts durably and transmits nothing further. Valid outer JSON must not
   be mistaken for valid function arguments. Reject unrelated syntax/type errors and truncation.
2. Frozen-author differential: raw output yields the saved unevolved-note fallback; repaired output
   changes links/neighbours and positive counter semantics. No production repair is introduced.
3. Checkpoint round trip: all fields and embedding bytes identical; retrieval k=5/10 and duplicate link
   expansion identical with a deterministic encoder. Assert stale corpus preservation and no encode
   call during restore. Reject missing/mismatched corpus, rows, dtype, IDs and provenance.
4. Synthetic interrupted/uninterrupted construction with identical mocked responses and fixed note
   IDs: equal notes, prompts, outcomes, index and counters after continuation; cover 99→100 and
   299→300 consolidation. Preserve failure note263 once; restart at offset263, not262 or264.
5. New-approval/parent binding and interruption fault injection: old permits stay halted, retained
   unknown charges block forecasts, costs cannot reset, duplicate prefix calls are forbidden and
   settlement errors stay terminal. Completion merges parent failure/deviation evidence once.
6. Composite full workload and QA: expected original 568 turns/204 questions, 526+1,018 nominal
   transmissions, both scoring views from identical saved predictions, no performance-dependent
   retry and no double credit of the prefix. Recovered completion is labelled degraded.

Gates3–6 above include **proposed recovery tests**, not claims of implemented recovery support.
Existing tests and the narrower characterization outcomes are recorded separately below.

## Evidence and limits

Existing offline verification passed **176 tests / 7 subtests** across artifact, author-parser,
adapter, D3a, SDK-budget, phase and forecast modules, with sockets disabled by the test suite.
These tests verify existing controls, not the proposed recovery feature.

New ignored local files: `artifacts/blk014-investigation/{investigate.py,findings.json,tests.txt}`.
The script reproduces the parser difference, eight fixed-vector retrieval comparisons, exact snapshot
round trip and unchanged hashes of every parent phase file and the study ledger. Existing evidence
was read only. Raw HTTP body bytes are unavailable; no internal provider-cause hypothesis is confirmed.
No production code, prompts, schemas, settings or scorer changed; no pilot resumed.
