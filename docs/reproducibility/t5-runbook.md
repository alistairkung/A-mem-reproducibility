# T5: bounded compatibility and cost pilot

Status: `compatibility-d9a-20261101` completed the 18-turn/four-question fixture under reviewed D9a
settings. Its degraded status is solely seven audited D3a completions/19 string indices: 44 physical
requests, no retries, USD0.053118 conservative phase charge. BLK-007 is Mitigated; BLK-013 is Resolved
for this fixture. The two earlier failed runs remain unchanged. See the [current readiness record](baseline-readiness.md).

D9a permits 4,000 shared-decision output tokens and 1,000 elsewhere under output policy
`d9a-shared-decision-4000-v1`, uniformly across arms with original prompts/schemas/parsers/temperatures.
All three phase authorizations are consumed. The user authorized PR #13's reviewed changes for merge;
no merge commit is claimed here. A verified **unapproved** conv-50 pilot plan is prepared, but pilot/main
execution and another recovery phase require separate approval. See [D9a authority](decisions.md#d9a--approved-shared-decision-output-allowance-and-one-fresh-verification-phase).
Issue: [T5 / #5](https://github.com/alistairkung/A-mem-reproducibility/issues/5).
The [frozen protocol](experimental-protocol.md), D1–D13 and approved D3a/D9a amendments remain the research authority.

## Local preparation

Install the existing lock, including the author runtime. No original requirements change is needed:

```sh
uv sync --frozen --python 3.11 --extra author --extra test --extra provider --extra reporting
.venv/bin/python -m pytest -q
```

`config/assets.json` v2 pins individual HF files by repository revision, size and SHA256 or Git blob
ID; it also pins the NLTK data commit and four archive SHA256 values. Download those public files into
the ignored `artifacts/assets` directory, without downloading any DeepSeek model weights:

```python
import json
import os
from pathlib import Path
from urllib.request import urlopen
from huggingface_hub import hf_hub_download

os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"
root = Path("artifacts/assets").resolve()
config = json.loads(Path("config/assets.json").read_text())
for asset in config["assets"]:
    for file in asset["files"]:
        hf_hub_download(asset["repository"], filename=file["path"],
                        revision=asset["revision"], token=False,
                        cache_dir=root / "huggingface/hub")
for archive in config["nltk"]["archives"]:
    target = root / "nltk_archives" / archive["filename"]
    target.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(archive["url"], timeout=120) as response:
        target.write_bytes(response.read())
```

Allow about 1.6 GB for download, plus extracted resources and installed packages. Asset preparation
verifies every source file before extracting NLTK or setting local cache aliases. The authors' literal
model names remain unchanged: MiniLM for retrieval/SBERT, and BERTScore's English `roberta-large` default.
No model library runs in the offline unit tests. Public asset downloads are separate from model API calls.

Run the actual local runtime check in a fresh process:

```sh
.venv/bin/python -m amem_repro.phases preflight \
  --assets artifacts/assets --output <fresh-d9a-preflight.json>
```

It checks active Python/platform dependency versions against `uv.lock`, verifies frozen author bytes,
disables sockets, loads the original retriever and scorer, and exercises embeddings, search and all author
metrics. It also loads the pinned local DeepSeek tokenizer. The receipt fingerprints source/configuration
and verified local bytes; any subsequent code/configuration change requires a new receipt. Existing
receipts/plans/run outputs are never overwritten.

The local runtime smoke passed on macOS arm64, Python 3.11.17: 2×384 embeddings, no metric failures,
F1/BLEU-1=1 and BERTScore/SBERT≈1 for identical text. This is a dependency smoke, not a benchmark result.
Initial import/model/metric checking took about 20 seconds on this machine. The locked Transformers
loader reports unused RoBERTa language-head weights and newly initialized pooler weights; the author's
BERTScore call uses hidden states. No metric, model choice or scoring expression was changed.

HF/Transformers offline flags and the documented `LITELLM_LOCAL_MODEL_COST_MAP=True` setting prevent
irrelevant import-time downloads. LiteLLM's provider is unused by the isolated DeepSeek controller.
`LITELLM_MODE=PRODUCTION` and `PYTHON_DOTENV_DISABLED=1` prevent dependency-driven dotenv loading.
The pinned HF tokenizer differs in some special tokens from DeepSeek's official downloadable archive;
its text-context counts are explicitly estimates (`exact=False`). API usage supplies final prompt and
billing counts. Hosted parity and strict beta acceptance require live evidence.

## Review a concrete phase plan

The compatibility commands below document the already consumed D9a workflow; they do not authorize
another fixture. For the prepared conv-50 pilot plan and future command, use the dedicated section below.

```sh
.venv/bin/python -m amem_repro.phases plan --phase compatibility \
  --run-id <fresh-d9a-run-id> \
  --provider-contract-policy canonical-index-strings-v1 \
  --assets artifacts/assets --preflight <fresh-d9a-preflight.json> \
  --output <fresh-d9a-plan.json>
```

Plans contain `approved:false`. After the D9a offline/review/preflight gates pass, the orchestrator may
record the user's existing explicit one-phase D9a authorization in the exact provenance-bound plan.
Verify its policy/stage map, fixture and limits before setting approval identity/time and `approved:true`.
Pilot approval is separate; credentials, issue state or an unapproved plan do not authorize spending.

The default provider policy is `strict-original-v1`. A future reviewed plan may explicitly select
`--provider-contract-policy canonical-index-strings-v1` (D3a); execution takes the policy from the
approved binding and offers no runtime override. After this source change, refresh preflight and use
a unique new run ID and plan filename. Never overwrite/reuse the original fixture plan or approval.
Changing policy invalidates cache identity and pilot-compatibility provenance. The wire integer schema
and raw parser input remain unchanged; admitted violations are recorded and completed runs degraded.
The approval binding must also carry `d9a-shared-decision-4000-v1` and the complete stage-cap map.
Recompute source/configuration/cache identities; legacy 1,000-token receipts cannot authorize D9a runs.

| Phase | Frozen workload | Logical ceiling | Physical ceiling | USD hard cap |
| --- | --- | --- | --- | --- |
| Compatibility | conv-26 session 1, 18 turns, original QA 0/1/2/4 | 44 | 132 | 2 |
| Pilot | all conv-50, 568 turns and 204 QA | 1,544 | 4,632 | 10 |

The 44-call fixture exercises all four schemas; no separate schema-probe calls are added. Caps include
SDK retries (max3 attempts per logical call), serial non-streaming execution and the unchanged 120-second
timeout. There are no semantic retries. A pilot plan additionally requires `--compatibility <phase.json>`
from an archived successful compatibility run with matching configuration/source/preflight provenance.
The paid pilot still requires its own approval.

After the relevant separate approval and private environment configuration:

```sh
.venv/bin/python -m amem_repro.phases execute \
  --assets artifacts/assets --preflight <fresh-d9a-preflight.json> \
  --approval <fresh-d9a-approved.json>
```

Credentials come only from the process environment; the CLI never reads `.env` and never records request
headers or exception text. Model, route, original prompts/schemas/parsers and approved D9a stage settings
are fixed. Required schema-semantic changes stop the study for review. Provider model/fingerprint
changes and exhausted transport/contract failures prevent subsequent requests. A pilot detects a change
from the archived compatibility model/fingerprint before continuing.

## Spending and artifacts

One SQLite ledger, `artifacts/study-budget.sqlite`, governs the whole study. Every physical attempt is
durably reserved **before transmission**, including SDK retries. Reservations use peak uncached prices
verified on 1 November 2026: [USD0.30 input / USD1.20 output per million tokens](https://api-docs.deepseek.com/quick_start/pricing/).
Input is conservatively bounded at 1,048,576 tokens. D9a pricing validation allows at most 4,000 output
tokens; reserve USD0.319373 for a shared-decision attempt and USD0.315773 for a 1,000-token other-stage
attempt. The request validator enforces each bound from the approved stage map. Valid reported
usage releases the unused reservation. Unknown or interrupted charges retain it; invalid usage halts.
This accounting is a conservative peak-price estimate, not an invoice or a claim of actual cache discounts.

Atomic transactions enforce the phase cap and USD42 cumulative usable allowance, preserving USD8 of the
USD50 total. Insufficient remaining capacity stops before sending, even when the final bill might have
fit. Keep the ledger with the study artifacts; never delete it, replace it, or use a new ledger to reset
allowance. Reused approval/run identities fail on restart. Any recovery/rerun needs new explicit approval,
and earlier charges stay in the shared ledger.

Each run saves approval/preflight receipts, fsynced request/response events, returned model/fingerprint,
physical attempts, original predictions/prompts/context, canonical complete or partial memory/index state,
and corrected/historical scoring from identical predictions. A hash inventory verifies the archived phase
files before reuse. Complete/degraded/incomplete classifications remain visible; no output is repaired.
Local action timing, retrieval expansion, tokenizer estimates, API usage and metric failures retain the
existing foundation behavior. No Langfuse upload is automatic.

## Review and offline evidence

Final integration validation: **131 tests and 71 subtests passed** with sockets denied; `uv lock --check
--offline` passes (137 packages). The final real local preflight also passes; its detailed receipt and
unapproved fixture plan are kept in ignored `artifacts/` rather than adding generated inventories to review.

The Standards review found two issues, both fixed: reject unexpected loadable snapshot files and check
the locked HTTPX/HTTPcore transport versions. The Spec review found two issues, both fixed: include
rescoring failures in completion status with the correct question/policy, and retain received response
payloads when usage validation forces a stop. Regressions also cover echoed credential redaction,
pre-transmission retry rejection, missing credentials before one-shot approval claim, active lock markers
and disabled dotenv loading. Original author bytes and the dependency lock remain unchanged.

## Scope decision and unfinished acceptance criteria

After the separately approved pilot:

```sh
.venv/bin/python -m amem_repro.phases forecast \
  --pilot artifacts/runs/<pilot-run-id>/phase.json --output artifacts/cost-forecast.json
```

For D3a study planning, also pass `--provider-contract-policy canonical-index-strings-v1` to the
forecast command. Policy must match to credit a pilot build; it is otherwise counted as overhead.

The forecast reads generation usage and the shared ledger, not comparative quality. It requires all
1,544 logical generations/204 QA and known physical-attempt usage. It includes already incurred costs,
remaining calls for all four arms and USD8 contingency. An exact-provenance pilot receives one full-mode
conv-50 credit; otherwise it is overhead. Recommend full scope if incurred costs, the remaining forecast
and USD8 contingency together fit USD50; otherwise only the predefined conv-49/conv-50/conv-44 fallback. Both point
totals and a 2× remaining-cost sensitivity diagnostic are shown. The latter is an assumption, not a
measured bound or an extra scope-selection rule. If neither population's planning total fits, stop.
Main execution requires a separate explicit decision/approval regardless
of the recommendation. No automatic population reduction, additional repetitions or baseline run exists
in this command.

| T5 criterion | Current evidence / remaining gate |
| --- | --- |
| Offline compatibility first; separate paid approvals | D9a tests/reviews and live fixture pass; all fixture approvals consumed; pilot approval pending |
| Archive four live schema outcomes and untouched full mode | 18 metadata/18 decisions/4 query/4 answer calls, raw arguments and complete fixture state verified; benchmark baseline pending |
| Measure cost, latency, retries and context expansion | Complete functional fixture measurements archived; representative pilot evidence still pending |
| Cost-only full/fallback choice within USD50 | Forecast tested; actual pilot and explicit main decision still pending |
| Fresh builds, one repetition, no truncation/tuning | Original full mode only; no repetition/recovery automation |
| Reuse valid pilot, preserve failures, avoid duplicate charges | Provenance receipts and forecast credit implemented; main baseline orchestration awaits scope decision |

T5 must remain open until the approved live phases and selected original baseline are archived. T6/T7
action refactoring remains blocked. The single D9a phase has succeeded and its authorization is
consumed. Pilot/main execution, another recovery phase and additional repetitions require separate
approval. The fixture was accepted under the documented D3a audit and D9a settings; its four scores
are functional evidence, not a benchmark quality estimate.

## Prepared conv-50 pilot — separate authorization required

`artifacts/pilot-conv50-d9a-plan.json` is `approved:false`: 568 turns, 204 original QA, 1,544 logical
calls, at most 4,632 physical attempts and a USD10 hard cap. Its source/configuration/preflight,
D3a policy, stage caps and verified compatibility receipt match the completed fixture. No pilot cache,
run directory or execution exists. A 4,000-token cap and a tiny fixture's cost do not guarantee full
pilot feasibility or the later four-condition budget.

After separate explicit pilot approval, create `artifacts/pilot-conv50-d9a-approved.json` from the exact
reviewed plan with approval identity/time. That approved file does not exist at this checkpoint.
Configure `DEEPSEEK_API_KEY` privately in the process environment; the CLI never loads `.env`.
The future command is **not executed**:

```sh
.venv/bin/python -m amem_repro.phases execute \
  --assets artifacts/assets \
  --preflight artifacts/compatibility-d9a-preflight.json \
  --compatibility artifacts/runs/compatibility-d9a-20261101/phase.json \
  --approval artifacts/pilot-conv50-d9a-approved.json
```

## BLK-012 correction and final review

Commit `d0e0bf9` makes failed usage settlements terminal before they can reach SDK retry handling.
The original maximum reservation and received payload survive. A separate transaction persists the
halt; if SQLite remains unwritable, a local irreversible latch and the already-durable one-shot claim
prevent continuation/restart. `halt_persisted:false` identifies that fallback rather than claiming a
successful halt write. Genuine 429/503/transport retries retain the existing SDK policy.

Full offline suite: **247 tests and 71 subtests passed**. Repeat Standards review: no actionable defect,
independent 26-test focused run passed. Repeat Spec review: no unmet safety requirement, independent
111-test/39-subtest focused run passed. Existing schemas/raw return, later-deviation persistence, asset
integrity and manifest hashes were checked. BLK-012 is Resolved. D9a's later live verification mitigates
BLK-007 as recorded above; pilot authorization remains separate. Safe local evidence: `artifacts/blk012-fix/`.
