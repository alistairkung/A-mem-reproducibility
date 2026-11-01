# BLK-007: offline parser investigation and proposed compatibility policy

Date: 1 November 2026, Hong Kong time. **Status: proposal for review; no compatibility fix implemented.**
BLK-007 remains Investigating. No paid request, fixture retry or pilot was executed during this work.
The [frozen protocol](experimental-protocol.md), original prompts/schemas and author files are unchanged.

## Finding and recommendation

The released parser already converts numeric connection strings into integer indices. For the exact
saved response, passing the raw argument string to the original parser produces the same memory state
and embedding documents as a control differing only in integer connection values.

Recommend an **explicit, field-scoped compatibility policy** in the isolated adapter: validate a
temporary copy with canonical decimal index strings converted to integers, then return the **original
argument bytes** to A-MEM. Keep global validation and every other schema field strict. This avoids a
second conversion implementation on the algorithm's input path: the existing `as_index` still decides
how links are interpreted and filtered.

This changes the adapter's acceptance policy, not the wire schema. Raw output is still schema-invalid;
it must never be described as strict-provider compliance. **D3's acceptance contract needs explicit
approval before implementation.** Neither an implementation nor a live recovery is authorized by this
report. A newly approved run must use a new policy fingerprint/cache identity and a fresh build;
the archived incomplete run must not be resumed or relabelled.

## Exact author path

Sources: [as_index/valid_link](../../memory_layer.py), `AgenticMemorySystem._evolve`, `process_memory`
and `add_note` in that same frozen file, and [output contracts](../../amem_repro/contracts.py).
The author file is checked against `f9a173d` before characterization.

1. `_evolve` parses the argument string using `json.loads`. It checks the top-level object and
   action-dependent outer lists; it does not enforce all JSON-schema item types itself.
2. For `strengthen`, it builds `shown = {int(i) for i in indices}` from the retrieved global memory
   indices, then iterates `map(as_index, suggested_connections)`.
3. `as_index` rejects booleans first. It converts integers, integral floats, and strings satisfying
   `i.strip().isdigit()` using `int`. Other values return `None`; a digit that `int` cannot parse raises.
4. Only converted indices in `shown` are retained. Others increment `FAILURES['invalid_link']`.
   This does **not** reinterpret positions in the neighbor list as global memory indices.
5. `note.links.extend(...)` preserves order and duplicates. Nonempty new-note tags are applied.
   Neighbor context/tag updates retain their existing order and guards. Refresh remains disabled.
6. A successful boolean positive result increments the evolution counter in `add_note`, including a
   decision with no actions; consolidation occurs at each 100. A caught processing exception returns
   the original failure result and does not increment.

| Input to `as_index` | Observed result | Consequence |
| --- | --- | --- |
| `2`, `2.0`, `"2"` | integer `2` | Same shown-neighbor filtering |
| `" 2 "`, `"02"` | integer `2` | Author tolerances; broader than the proposed whitelist |
| `"٢"` (Arabic-Indic decimal) | integer `2` | Author tolerance; not proposed for provider acceptance |
| `True`, `False`, `1.5`, `"2.0"`, `"2e0"`, `"+2"`, `"-1"`, empty string, `None` | `None` | Not retained as a shown link |
| integer `-1` | integer `-1` | Not in valid shown indices; discarded/counted |
| `"²"` | raises `ValueError` | `isdigit()` alone is insufficient for safe conversion |

`valid_link` protects retrieval of stored links; the strengthening path uses `as_index` plus `shown`
membership. Do not move or duplicate those semantic checks into the provider policy.

## Exact saved-response characterization

The investigation reconstructed the state immediately before the fifth evolution decision from the
partial snapshot: four existing notes plus the fifth note's already-generated metadata. The resulting
original prompt matched the archived request **exactly**. Shown global neighbor indices were
`[3, 2, 0, 1]`; the returned connection strings were `["2", "3"]`.

| Offline path | Counter after insertion | New links | Outcome |
| --- | --- | --- | --- |
| Original parser receives exact raw arguments | 4 | `[2, 3]` | Successful evolution |
| Original parser receives integer-only control | 4 | `[2, 3]` | Same full note/index snapshot and embedding documents |
| Current adapter's strict-rejection control | 3 | `[]` | Original evolution fallback; `FAILURES['evolve']=1` |

The raw path and integer control also preserve new-note tags and all neighbor updates. Thus bounded
normalization or bounded admission preserves the released parser's effective behavior **for this
representation difference**. It does not preserve the earlier adapter's rejection/fallback behavior;
that distinction matters for the counter, consolidation schedule and experimental provenance.

Evidence: safe local `artifacts/blk007-offline-investigation/saved-response-characterization.json`.
Embedding computation was mocked: existing rows, row order, submitted documents and state were compared;
this is not a live embedding experiment or the complete T6 baseline replay. Actual provider reliability
and future stochastic outputs remain unverified.

Nine existing evidence files, including the raw reproducer, all incomplete-run files and the cost
ledger, were inventoried before investigation and remain byte-identical. The original failure remains
an incomplete ten-request run, with conservative ledger cost USD0.005851 and zero completed QA.

## Four-schema audit

Every schema requires its fields and forbids extra properties. Missing fields, nulls, malformed JSON,
wrong tool names, incomplete completions and unrelated type mismatches remain rejection cases.

| Schema | Required types and relevant parser behavior | Compatibility risk / proposed treatment |
| --- | --- | --- |
| Metadata | `keywords: list[str]`, `context: str`, `tags: list[str]`. Analysis fills missing keys; note construction joins list contexts. A scalar keyword/tag string can instead be iterated character by character in embedding documents. | Existing tolerance is not a general conversion contract. String-to-list or list-to-string repairs can change embeddings/metadata. Retain strict validation for every metadata field. |
| Shared decision | `should_evolve: bool`; actions/tags/context lists; nested neighbor-tag lists; integer connection list. Only connection indices pass through `as_index`. | Permit only the proposed connection-string exception. `"false"` is truthy in the author action path but is not equal to boolean `True` at counter increment; casting can change both actions and consolidation. Flattening/wrapping tag/context arrays changes assignments. Reject those mismatches. |
| Query keywords | `keywords: str`. The parser returns the decoded field without checking its type; parse failure falls back to the raw response text. | Lists/numbers/nulls can reach retrieval in a different form. Joining or stringifying them changes the query sent to embeddings. Retain strict string validation. |
| Answer | `answer: str`. The runner extracts the field, and author scoring checks falsiness **before** converting nonempty values to strings. | Numeric `0` scores as an empty prediction, whereas `"0"` can score correctly against `"0"`. Numeric/boolean/list stringification can change evaluation. Retain strict string validation. |

JSON-schema integer semantics already allow integral JSON numbers such as `2.0`; the current validator
and `as_index` agree on those. Booleans remain invalid integer values. Empty arrays and unknown action
strings already allowed by the original schema must not acquire new constraints in this change.
No other live type violation was observed in the stopped fixture; the remaining risks above follow
from source inspection and explicit offline counterexamples, not claims of additional provider failures.

## Resolution options

| Option | Effect on algorithm/evaluation | Trade-off and recommendation |
| --- | --- | --- |
| Keep strict rejection | Preserves the present D3 validation gate. Rejecting this response invokes failure behavior instead of the original successful index handling. | Valid conservative choice, but compatibility remains blocked. It does not solve the observed failure. |
| Bounded normalization of returned arguments | Converting only these indices to integers produces equivalent original memory behavior in the tested cases. | Changes parser-input bytes and needs both raw/transformed artifacts. Larger deviation from D3's unchanged-argument requirement than necessary. |
| **Bounded admission with a validation copy** | Strictly validate a canonical copy, return raw arguments unchanged, and let `as_index` perform the actual conversion. | **Recommended minimum.** One stage/path exception, explicit policy and deviation record; all other validation stays unchanged. Still requires D3 approval and a new live compatibility test. |
| Retry the unchanged request after schema failure | Keeps prompts/settings, but samples another completion and pays again. Discarding invalid outputs changes the effective sampling/failure process. | Not a transport retry and not currently authorized. A bounded diagnostic could investigate reliability if separately approved; no default semantic retry loop is recommended. |

## Proposed code change — not applied

Keep `validate_arguments` unchanged. In `DeepSeekController.get_completion`, replace only the direct
validation call with a private stage/policy-aware validator. Strict rejection remains the default.
The proposed opt-in policy ID is `canonical-index-strings-v1`.

```python
# Review sketch only; not installed in the adapter.
try:
    validate_arguments(value, schema)
except ContractError as raw_error:
    require(policy == "canonical-index-strings-v1")
    require(stage == "shared_decision")
    require(type(value) is dict)
    require(type(value.get("suggested_connections")) is list)
    shadow = deepcopy(value)
    changes = []
    for i, item in enumerate(shadow["suggested_connections"]):
        if type(item) is str:
            require(fullmatch(r"0|[1-9][0-9]*", item, flags=ASCII))
            # Conversion errors still reject. No signs, padding, whitespace,
            # exponents, non-ASCII digits, floats or booleans are coerced.
            shadow["suggested_connections"][i] = int(item)
            changes.append((i, item, shadow["suggested_connections"][i]))
    require(changes)
    validate_arguments(shadow, schema)  # catches every remaining violation
    record_deviation(raw_error, changes, validation_view_only=True)
return arguments  # original string, never json.dumps(shadow)
```

`require` above means reject through the existing adapter failure path, not a new repair mechanism.
`record_deviation` means attach plain diagnostic data to the existing completion event; it performs
no I/O or extra callback inside validation. Existing observer-error isolation must remain intact.
Do not sort/deduplicate/filter indices, remap neighbor positions, change boolean/metadata/answer fields,
salvage truncated JSON, add defaults or invoke another completion. Canonical ASCII decimal strings are
a deliberately smaller accepted subset than every representation `as_index` happens to tolerate.

The implementation target is the unpushed `codex/t5-pilot` work (`dad8908`), not a change to the
frozen author source. This investigation branch adds documentation and characterization tests only.
The implementation review should cover:

- `adapter.py`: scoped helper, explicit policy selection, unchanged raw return, diagnostic event.
- Fingerprinted run/provider identity and phase approval: closed policy IDs, default strict, identical
  approved policy across all four arms. Do not silently relax `validate_config` or alter study settings.
- Completion classification/reporting: accepted provider-contract deviations remain visible and mark
  the run degraded; D12 prevents automatic exclusion. Existing counter/index/scoring logic is untouched.
- Blocker/decision documentation: record explicit D3 policy approval before implementation and a new
  separately approved compatibility attempt afterward. A mitigation would not retroactively establish
  the provider's strict-enforcement guarantee.

## Offline regression requirements

Completed characterization: [38 tests](../../tests/test_type_compatibility_characterization.py), plus
the exact archived-payload check above. The branch's complete offline suite passed **92 tests and
32 subtests**. These are author-behavior tests, not tests of an implemented compatibility policy.

Before a paid compatibility request, the proposed patch must additionally prove:

1. Global validation still rejects raw connection strings; default adapter policy also rejects them.
2. Only canonical decimal strings at `shared_decision.suggested_connections[*]` are admitted. A second
   wrong field, wrong outer type, null, missing/extra key, bad boolean or malformed/truncated response
   still rejects. Exercise all four schemas with these cases.
3. The raw argument string is returned byte-for-byte, raw artifacts are immutable, and diagnostics
   retain raw invalidity plus the validation copy's success. No request/prompt/schema/settings change.
4. Original string/integer paths match note links, order/duplicates, tags, neighbor updates, submitted
   embeddings/index rows, retrieval context, failures and counter/consolidation behavior, including
   negative decisions, no-action positives, unshown indices and 99→100. Existing characterization
   covers these full-mode cases; four-arm gating/equivalence remains T7 work.
5. Answer/query/metadata types are never coerced; especially answer `0`, boolean strings and nested
   tag-list errors. Existing author score definitions and both rescoring policies remain unchanged.
6. A schema violation adds no model call, semantic retry or fabricated token usage. Transport retries
   and durable budget stops retain the existing contract.
7. Policy identity changes cache/approval fingerprints; mixed-policy reuse is rejected. Accepted
   deviations appear consistently in local manifests, failure classification, tables and Langfuse.

## Experiment records

Proposed run-level fields: `provider_contract_policy`, original schema fingerprints, support-code
fingerprint and `provider_contract_deviation_count`. Bind the policy to phase approval and cache identity.
Never record credentials. Preserve actual model/version/fingerprint, requests, usage and costs as before.
Count affected **completions** at run level and affected array items separately: this observed response
is one completion with two invalid items. Distinguish raw-valid, policy-admitted, rejected and
untransmitted outcomes rather than reporting all admitted responses as schema-valid.

For each accepted deviation, retain the raw response and record:

```json
{
  "provider_contract_policy": "canonical-index-strings-v1",
  "raw_schema_valid": false,
  "validation_view_schema_valid": true,
  "algorithm_input_modified": false,
  "changes": [
    {"path": "$.suggested_connections[0]", "raw": "2", "validation_view": 2},
    {"path": "$.suggested_connections[1]", "raw": "3", "validation_view": 3}
  ],
  "status": "degraded"
}
```

Also record hashes of raw arguments, returned arguments (equal), and the validation view; question or
build identity; original processing outcome; and actual physical attempts. The temporary integer copy
is an audit view, not a replacement for the provider's output. All arms use one fixed policy, so this
controlled provider deviation cannot become an unrecorded treatment difference.
The provider-contract policy is a separate identity dimension from scoring policy: keep the corrected
and historical scorer IDs/reference data unchanged, and include the provider policy in Langfuse metadata.

## Langfuse preparation

See [Langfuse readiness](langfuse-readiness.md) and BLK-011. Project authentication and a synthetic
zero-model-call span were verified with SDK 5.1.0; readback confirmed the expected data. Actual T5
phase/generation wiring is a separate proposed observation-only change for review, not an implemented
compatibility fix. No old benchmark data or failing response was uploaded.
