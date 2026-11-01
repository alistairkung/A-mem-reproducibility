# BLK-007: approved compatibility patch, offline review

1 November 2026, Hong Kong time. Implementation and offline tests only, under
[D3a](decisions.md#d3a--blk-007-validation-copy-compatibility-policy).
**BLK-007 remains Investigating. No live recovery, fixture resume or pilot was run.**
Implementation/test commit: `48bc2d1`, branch `codex/blk007-compatibility`, based on local T5 work
plus the tracker and parser-investigation commits. Review the implementation with
`git diff 900b6b7..48bc2d1`; original evidence and historical reports stay unchanged.

## Change and preservation boundary

The [adapter](../../amem_repro/adapter.py) admits only canonical unsigned ASCII decimal strings
(`0|[1-9][0-9]*`, convertible by Python `int`) in `shared_decision.suggested_connections[*]`, when
explicitly selected with `canonical-index-strings-v1`. It validates a temporary deep copy with integer
values against the full original schema, then returns the **original argument string unchanged**.
`strict-original-v1` remains the default. The global validator and all four wire schemas are unchanged.

No string conversion is applied to metadata, actions, booleans, tags, neighbor contexts, query keywords
or answers. Invalid mixed lists, malformed/signed/padded/Unicode/decimal strings, wrong tools and
truncated completions still fail. Unshown indices, order and duplicates reach the original `as_index`
and shown-neighbor filter. No index remapping, repair generation or semantic retry is added.
Original author code, prompts, retrieval, embedding/refresh policy, counter/consolidation and scoring
are unchanged. Four-arm action gating and complete baseline replay remain later tickets.

## Recorded deviation and experiment identity

Each affected generation retains its original response/output and records:

- `provider_contract_policy`, `raw_schema_valid:false`, `validation_copy_schema_valid:true`.
- `compatibility_deviation.affected_field`, raw type violation and each original/copy item/path.
- `original_arguments_sha256` and equal `returned_arguments_sha256`: exact UTF-8 bytes.
- `original_value_sha256` and `validation_copy_sha256`: canonical JSON (sorted keys, compact
  separators, UTF-8, non-ASCII preserved, non-finite values forbidden).
- `validation_copy_only:true` and `algorithm_input_modified:false`.

The runner records a `provider_contract_deviation` failure. Completed affected runs are **degraded**;
aborted/missing-result runs remain **incomplete**. Summaries count affected completions separately
from transformed items; cached-build deviations have separate inherited counts and retain their audit
records. A fresh build is required after changing policy. Policy is bound to approval/request metadata,
run/build/cache identity, saved QA, CSVs and optional Langfuse experiment identity. Pilot provenance
must match; cost forecasting never credits a pilot under another provider policy. Raw-invalid
admitted outputs are never counted as raw schema-valid.

Existing optional Langfuse exports include policy metadata; no upload or live tracing was added here.
[BLK-011](blockers.md#blk-011) remains Open: the earlier verified connection smoke does not wire the
paid runner to Langfuse.

## Offline verification

`.venv/bin/python -m pytest -q --tb=short --show-capture=no`:
**238 tests and 71 subtests passed**, with test-suite sockets disabled.

[Policy regressions](../../tests/test_compatibility_policy.py) cover strict/default isolation,
numeric/malformed/boolean/out-of-range/mixed values, unchanged parser input and all other schemas.
Adapter-to-frozen-parser comparisons cover all four action sets, positive/negative decisions and
counter 99→100, comparing full note/index state, retrieval, duplicates and invalid-index failures.
[Mocked phase tests](../../tests/test_phases.py) exercise the complete 44-call SDK fixture: 17 admitted
completions / 75 transformed items yield degraded status; all 44 requests remain bounded, and
postprocessing aborts retain incomplete status and deviation counts. Cache reuse inherits degradation;
policy mismatches reject reuse, approval and exports. Existing budget, scoring and transport tests pass.

The **exact archived failing response** was replayed through the SDK using HTTPX MockTransport.
Both serialized requests matched the archived request; default strict rejection remained intact and
the approved policy returned the original arguments. Raw argument SHA-256:
`58aa5fe10d2fcc5907c4141b33a7806ea5a6246381fc8c04b60c23ac2a0fd7c8`.
Safe local evidence: `artifacts/blk007-policy-offline/saved-response-validation.json` and `pytest.txt`.
The prior failed run, raw reproducer, plans/approval, preflight receipts, investigation evidence and
cost ledger are protected by `preservation-before.json`; verification is in `preservation-after.json`.
These local artifacts are ignored by Git; portable regression coverage uses deterministic mocks.

## Remaining gate

Offline success establishes only the bounded representation equivalence, not hosted schema enforcement
or future response reliability. Preserve the original failed run unchanged. After code review, refresh
offline preflight and prepare a **new, unapproved** plan binding this policy/source and a unique fresh-run
ID. Obtain separate explicit live compatibility authorization before any request; never reuse the old
approval or resume the incomplete run. A successful live test may mitigate BLK-007, while the observed
strict-provider violation remains part of the research record. The conv-50 pilot needs its own approval.
