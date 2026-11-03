# Run 2 Gate A — DeepSeek output allowance

Checked3 November2026 against current official documentation, actual adapter/SDK code and immutable
Run1 artifacts. No hosted generation probe or Run2 benchmark request was made. Run1 remains an
exploratory engineering campaign, preserved with its original labels, USD8.530133 ledger and results.

## Provider and actual request path

The current `deepseek-flash` alias maps to **DeepSeek-V4.1-Flash-1017**, with1M context and384K maximum
output. Peak conservative rates remain USD0.30/M input and USD1.20/M output tokens. Billing follows
actual token usage; no cap-dependent rate surcharge is documented. Discounts are excluded from the
study's conservative bound. [Model/pricing table](https://api-docs.deepseek.com/quick_start/pricing/).

The Chat Completions API accepts `max_tokens`1–393,216, subject to combined input/output context.
The documented hard range is shared across modes; defaults differ:8K non-thinking,64K thinking,
128K with maximum thinking effort. Named forced function calls require thinking disabled. Our exact
route remains `https://api.deepseek.com/beta/chat/completions`; there is no separate4,000 function
limit documented. [API reference](https://api-docs.deepseek.com/api/create-chat-completion/).

Beta strict functions support both modes and require the beta URL, strict flag and supported schema
types. This does not remove output-length or observed provider-contract failures.
[Strict functions](https://api-docs.deepseek.com/guides/tool_calls/).
Explicit disabled thinking preserves the existing temperature semantics; thinking mode ignores
temperature. [Mode parameters](https://api-docs.deepseek.com/guides/thinking_mode/).
JSON-object mode is a different interface and its own guide warns about output truncation. No mode,
prompt or parser switch is needed. [JSON output](https://api-docs.deepseek.com/guides/json_mode/).

`amem_repro/adapter.py` uses direct OpenAI SDK2.54.0/HTTPX, not LangChain. The4,000 restriction is
the frozen local `config.py:stage_output_limits`/approval/budget policy. Three socket-disabled real
SDK MockTransport cases forward8,192,16,384 and393,216 unchanged, with the original schema, strict
flag and disabled thinking. That verifies local serialization, not hosted acceptance or reliability
above4,000. Official documented support is the provider evidence; no unapproved paid probe is used.

## Observed Run 1 output sizes

Count each actual generation once across seven parent/child archives, excluding inherited copies.
All1,713 shared decisions are accounted for:1,708 adapter-accepted responses and five rejected
outputs (conv-50's BLK-014 malformed response, conv-49's one length failure and three conv-44 length
failures). Statistics below use API completion-token usage and linear NumPy quantiles. They are
conditional on success below the old cap, not uncensored estimates of required output length.

| Conversation | Accepted decisions | Median | p95 | p99 | Maximum |
| --- | ---: | ---: | ---: | ---: | ---: |
| conv-49 |508 |1,746 |3,073.4 |3,710.27 |3,982 |
| conv-50 |567 |1,441 |2,292.6 |2,836.62 |3,851 |
| conv-44, incomplete |633 |1,788 |3,104.2 |3,664.36 |3,987 |
| Combined |1,708 |1,642.5 |2,956.5 |3,570.04 |3,987 |

Combined p99.9 is3,956.55;20 successful outputs exceed3,500 and three exceed3,900.
Conv-44 failures at `D18:21`, `D26:18` and `D26:44` each returned HTTP200/`length` and4,000 output
tokens, with3,633 /5,566 /5,638 input tokens. Raw response hashes, exact requests and unchanged
fallbacks are preserved in the [first](t8-conv44-incomplete-20261103.md),
[second](t8-conv44-recovery-incomplete-20261103.md) and
[third](t8-conv44-second-recovery-incomplete-20261103.md) failure reports. These are right-censored
outputs; completing them by editing JSON or extrapolating exact missing tokens would fabricate evidence.

Neighbour contexts plus neighbourhood tags comprise95.7% of compact serialized field characters
over accepted decisions (7,678,281 context /4,243,991 tag characters). The largest success includes
five updated contexts and291 neighbourhood tags.1,705 accepted decisions request both actions and
have neighbour payloads; the three no-evolution outputs average151 tokens. This is an observed size
association in Full mode, not a causal comparison between ablation conditions. Repeated enrichment
plausibly drives growth, but the exact counterfactual completed lengths and future maxima are unknown.
Character shares are not provider-token attribution or proof of local tokenizer parity.

## Recommended generation policy and financial implications

Use **8,192 shared-decision tokens**,1,000 for metadata/query/answer, with policy ID
`run2-shared-decision-8192-v1`. This is the documented non-thinking default and the smallest
power-of-two allowance above twice both the observed3,987 maximum and4,000 censoring threshold.
It supplies a clear safety margin without approaching the provider maximum. No observed data
demonstrate that16K or384K is necessary.8K may still fail; exact-state continuation, original fallback
retention and Degraded classification address residual length failures without repairing responses.

Keep model/endpoint, thinking disabled, original prompts/schemas/parsers, temperatures, D3a, five
construction neighbours, k=10, stale-index policy and scoring unchanged. Apply the same stage map
to all12 fresh Run2 cells and bind it to approvals/configuration/cache/trace identities. Preserve the
Run1 default/replay at4,000. Final Run2 configuration freezes only after GateB and independent review.
The larger cap is a controlled generation deviation; never pool Run1/Run2 primary results or claim
absolute comparability with the paper's GPT-4o-mini scores.

At8,192, maximum shared output charge is USD0.0098304 per attempt, USD0.0050304 above4,000 if all
extra tokens are generated. The existing full-context conservative reservation becomes324,404
microUSD, versus319,373; other-stage reservations remain315,773. A cap is not an up-front charge.

Measured selected-conversation stage means project **USD38.764609** for all12 fresh cells, plusUSD8
reserve =USD46.764609. The new campaign has a separate USD42 execution ledger; Run1's USD8.530133
is excluded from its allowance and remains unchanged. Execution headroom is onlyUSD3.235391;
10% cost growth projects USD42.641070 execution, aboveUSD42. Thus this is a point forecast, not a
guarantee. Reconcile/reforecast each bounded cell, retain all retries/failures, preserve shared
cell limits across continuations and stop before exceeding allocation. No contingency top-up is
authorized. Nothing here justifies reducing the fixed population or tuning on observed quality.

## Reproducible evidence and gate status

Safe local evidence under `artifacts/run2/gate-a/`: `run1-preservation.json` hashes557 prior artifact
files, with a read-only ledger backup; `analysis.json` and `shared-decision-records.json` contain
deduplicated response-size/structure observations; provider SDK proof is stored separately.
All prior hashes/ledger bytes verify unchanged. No model/network request was used for local analysis.

GateA supports the8,192 recommendation from official limits and offline request serialization.
Hosted long-output reliability is untested and must not be claimed. GateB real-runner Langfuse
visibility, saved-result experiment import, deterministic equivalence, two successive simulated
recoveries, independent reviews and affordable frozen preflight remain required before paid cells.
