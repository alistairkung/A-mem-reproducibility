# T5 compatibility attempt: 1 November 2026

Outcome: **incomplete; compatibility gate failed**. T5 remains open. No pilot, baseline or recovery
request is authorized by this attempt. No prompts, schemas, parser, algorithm or generation settings
were changed in response to the failure.

## Approval and provenance

The user explicitly approved only the 18-turn/four-question fixture with a USD2 ceiling, 44 logical
calls and at most 132 physical attempts. Approval was recorded on 1 November 2026 at 06:31:59 UTC.
The frozen research protocol's separate pilot/main/recovery gates remain in force.

| Identity | Value |
| --- | --- |
| Support commit | `502b376` on `codex/t5-pilot` |
| Author source | `f9a173dec325d84fcc97e7828775c7b241c33466`, unchanged |
| Run | `compatibility-20261101` |
| Fixture | conv-26 session 1; 18 turns; original QA indices 0,1,2,4 |
| Expanded manifest SHA256 | `d4e5652bcc8e7f3c5054c1f6c4547906b130e36bb2e21b7cf50c40a85153ec99` |
| Source/configuration bundle SHA256 | `ba0879d2f6d7ea35ad1c4cf4af187c4666d1e58ba33379317cbf3d5868cf449e` |
| Preflight fingerprint | `88bdff725dc5ae99f44283b6c773f5e31bdf1e8cda5e89d7b10a0fd8e1fd665f` |
| Requested / returned model | `deepseek-flash` / `deepseek-flash` |
| Provider fingerprint | `bc19ba97cbe016479903222bb1578db6` |
| Endpoint | `https://api.deepseek.com/beta/chat/completions` |

The provider returned the alias, not a separately verifiable immutable version. The official model
page maps that alias to DeepSeek-V4.1-Flash-1017; this is documentation, not independent weight-version
verification. [Model documentation](https://api-docs.deepseek.com/quick_start/pricing/)

The private launcher supplied only the project's DeepSeek variable to the process environment. No
credential value or request header was printed, committed or added to artifacts. The experiment CLI's
disabled implicit dotenv behavior remains unchanged.

## Observed failure

Ten physical requests were sent: five metadata calls and five shared evolution decisions. All received
HTTP200, with no transport retries. Nine argument payloads passed their frozen contracts. The fifth
shared decision returned:

```json
{"suggested_connections": ["2", "3"]}
```

This excerpt contains strings; the original contract requires an array of integers. Both our unchanged
validator and an independent `jsonschema.Draft202012Validator` identify exactly those two type violations.
The received response was valid JSON, finished with `tool_calls`, and used 640 output tokens of the
1,000-token allowance. Truncation is not the cause.

The archived serialized SDK request confirms one forced `response` function with `strict:true`, thinking
disabled, temperature0.7, max_tokens1000 and stream=false. Its parameters equal the frozen author schema.
DeepSeek's current strict-mode guide documents beta routing, strict function definitions and integer
support; this observed response contradicts the documented adherence guarantee. The exact server-side
cause remains unresolved. [Strict-mode guide](https://api-docs.deepseek.com/guides/tool_calls/)

The released prompt's example uses a quoted neighbor-ID placeholder (`memory_layer.py:768`), while
the schema requires integers (`_evolve`) and the existing action parser accepts numeric strings through
`as_index`. That prompt/schema tension may influence generation; it does not explain or excuse strict-mode
noncompliance. Forwarding invalid arguments or changing validation would require an explicit D3 decision.

The original evolution caller retained its failure fallback. The permit blocked the next metadata call
before transmission. That blocked event is **not** an eleventh paid request or evidence of a metadata
schema violation. No string-to-integer coercion, semantic retry, prompt edit or alternative pipeline ran.

## Usage and retained artifacts

| Measurement | Value |
| --- | --- |
| Physical requests / retries | 10 / 0 |
| Input / output tokens | 8,997 / 2,622 |
| Input cache hits / misses | 2,560 / 6,437 |
| Sum of completion-call durations | 17.464 seconds |
| Conservative ledger cost | USD0.005851 |
| Unknown or pending charges | 0 |
| Completed QA | 0 of 4 |
| Preserved notes / embedding rows | 5 / 5 |
| Positive-decision counter | 3 |

The ledger uses rounded-up, peak uncached prices, not the provider invoice; the amount includes the
failed response. Usage and cache counters are preserved separately. This fixture supplies no benchmark
accuracy estimate and cannot establish all four schemas' live compatibility: query/answer were not reached.

Ignored local archive: `artifacts/runs/compatibility-20261101/` contains approval/preflight receipts,
serialized request/response events, partial canonical memory/index state and incomplete run/phase summaries.
Its recorded artifact SHA256 inventory was verified offline after execution. The durable study ledger is
`artifacts/study-budget.sqlite`; do not reset it or reuse this stopped approval/run identity.
An offline request/response reproducer is saved separately as
`artifacts/compatibility-20261101-reproducer.json`. The follow-up offline suite passes **132 tests and
71 subtests**, including unchanged integer-contract validation and independent-validator agreement.

## Next gate

Recommend investigating the provider-side strict-mode failure before spending on the pilot. Keep the
frozen contract and original outputs intact. A repeated model call or a new diagnostic generation needs
separate recovery/test authorization; changes to schema semantics, prompts, parsing, model or generation
settings require an explicit protocol decision. Do not infer recovery permission from the unspent cap.
