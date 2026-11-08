# Reproducing A-MEM: A Cost-Aware Study of Memory Linking and Evolution

**FTEC5660 individual reproducibility assignment · Alistair Kung**

Xu et al. (2025) introduced A-MEM, a memory system that converts conversation turns into structured notes and retrieves them to answer later questions. In this student reproduction, I tested whether updating older notes helps independently of linking, and whether the extra retrieval and inference cost improves answer quality. [Original paper, Table 3](https://arxiv.org/html/2502.12110v11#S4.T3) · [Upstream implementation](https://github.com/WujiangXu/A-mem/tree/f9a173dec325d84fcc97e7828775c7b241c33466)

[Final coursework report (PDF)](reports/final_coursework/AMEM_FTEC5660_Report.pdf) · [Results tables and figures](reports/publication_assets/README.md)

## Experiment and findings

I added **Evolution Only** to the paper’s Neither, Linking Only and Full conditions. These four configurations form a 2 × 2 design. Strengthening can change the **new** note’s links and tags. Neighbour evolution can change **older** notes’ contexts and tags. Every condition still asks the model to choose which actions to apply. Independent gates control which proposed changes are applied.

The primary study used GPT-4o-mini on three preselected LoCoMo conversations (conv-44, conv-49 and conv-50). Each condition processed 1,752 turns and answered the same 558 questions from its own memory. Twelve builds were accepted, one per condition and conversation. F1 measures word overlap with a reference answer. Both evaluations score the same predictions and change only the reference for adversarial questions.

| Configuration | Historical F1 | Alternative-reference F1 | Identified model charges for three accepted builds |
|---|---:|---:|---:|
| Neither | 30.03% | 39.00% | $0.95044785 |
| Linking Only | 30.21% | 37.34% | $1.07939100 |
| Evolution Only | 29.29% | 35.86% | $0.95332785 |
| Full A-MEM | 32.69% | 36.91% | $1.08083640 |

With the historical distractor reference, pooled F1 follows the paper’s three-condition direction. With the alternative “no information” reference, Neither ranks first. Evolution Only scored 3.15 percentage points below Neither overall and 2.44 points below it on temporal questions. Linking Only gained 3.40 points on multi-hop questions, while mean retrieval rose from 10.00 to 20.15 entries per question.

Neither, Linking Only and Full each offer a cost–quality trade-off under historical F1. Under alternative-reference F1, Neither has both the lowest cost and the highest score. These comparisons cover identified model charges on the accepted builds. The subset, fixed initial retrieval depth of ten and single stochastic build per cell limit generalisation. The reproduction recovered a direction of change. Exact Table 3 scores and run-to-run variability remain unresolved. The earlier DeepSeek runs are exploratory. [Accepted twelve-cell evidence](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/docs/reproducibility/gpt4omini-twelve-cell-results.md) · [Verified results and cost tables](reports/publication_assets/tables/07_dual_scoring_cost_performance.csv)

## Install

Use a full Git clone and [uv](https://docs.astral.sh/uv/getting-started/installation/). The project declares Python 3.11–3.12. The commands below use POSIX shell syntax and were checked on macOS arm64 with Python 3.11.17. After cloning, run the remaining commands from the repository root.

```sh
git clone https://github.com/alistairkung/A-mem-reproducibility.git
cd A-mem-reproducibility
```

If you are reviewing the submission before it reaches `main`, run `git switch codex/coursework-readme` in the clone to get this guide and the report. Then install and check the study environment:

```sh
uv sync --frozen --python 3.11 --extra test --extra provider
.venv/bin/python -m pytest -q tests/test_config.py tests/test_manifests.py
```

`uv sync` creates `.venv` and installs the locked packages for these checks. The offline workflows need no API keys, Langfuse account or model-weight download. The `author` extra adds the original model and metric libraries. The `reporting` extra adds the Langfuse SDK used for campaign tracing. The publication generator uses its own requirements file. [Project dependencies](pyproject.toml) · [Dependency lock](uv.lock)

## Run

### 1. Verify the mechanism offline

```sh
.venv/bin/python -m pytest -q tests/test_replay.py tests/test_actions.py
```

These tests exercise recorded opening responses, deterministic test embeddings and synthetic edge cases across all four gate settings. A passing run checks note changes, suppressed actions, cache isolation and replay behaviour. The test harness denies socket connections. The full research replay also matched 568 insertion states, 1,544 recorded requests and 204 answers using the separately archived responses and model assets. [Replay fixtures and full archive requirements](docs/reproducibility/t6-replay.md)

### 2. Reproduce the published metrics and tables

The public repository provides matched **question-level scores** under both reference policies. The generator reads them at scientific commit `8485673`, recalculates pooled, category and conversation means and factorial contrasts, and checks 864 aggregate values. It writes into its own `reports/publication_assets/` directory. To regenerate the tables and figures in a separate checkout of the merged report revision:

```sh
git worktree add --detach ../amem-reporting e736a007e243442ef65b156f184bb70b78c578a2
(
  cd ../amem-reporting &&
  uv run --no-project --python 3.11.17 --with-requirements reports/publication_assets/requirements.txt python reports/publication_assets/generate_assets.py &&
  cat reports/publication_assets/tables/02_overall_results.csv
)
```

The last command prints the four score rows, including BLEU-1 and binary adversarial correctness. The generator also writes CSV, LaTeX, Word and chart outputs. A full clone includes the scientific commit through the branch that received PR #52. [Per-question score file](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/docs/reproducibility/gpt4omini-558q-four-condition-scores.jsonl) · [Reporting inputs and output catalogue](reports/publication_assets/README.md)

Rescoring the original **answer text** requires the private accepted run journals and pinned local scoring assets. The pipeline passes saved question records to `rescore_records` with the frozen `AuthorScorer`, then exports both policies with `write_tables`. The accepted study contains 2,232 saved primary answers across the four conditions. [Scorer](amem_repro/scoring.py) · [Table exporter](amem_repro/reporting.py) · [Accepted run and verification receipts](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/docs/reproducibility/gpt4omini-twelve-cell-results.md#verification-receipts)

<details>
<summary>Rescore one archived cell locally (requires the private research archive)</summary>

From the research checkout with the accepted final cell and prepared `artifacts/assets/`, this example reads the 158 saved Linking Only / conv-44 answers, scores them twice and writes fresh tables to a temporary directory. The `author` extra supplies the model and metric libraries for local scoring.

```sh
uv sync --frozen --python 3.11 --extra author --extra provider
.venv/bin/python - <<'PY'
import json
import os
import tempfile
from pathlib import Path

from amem_repro.preflight import asset_environment
from amem_repro.reporting import write_tables
from amem_repro.scoring import AuthorScorer, rescore_records

root = Path.cwd()
os.environ.update(asset_environment(root / "artifacts/assets"))
attempt = root / "artifacts/gpt4omini/cells/linking_only-conv-44/final-eight-hour/attempt-1"
run = attempt / "runs/gpt4omini-linking_only-conv44-final-r1"
with (run / "events.jsonl").open() as journal:
    records = [e["result"] for e in map(json.loads, journal) if e["type"] == "question_result"]
assert [r["question_id"] for r in records] == [f"conv-44:qa:{i}" for i in range(158)]
output = Path(tempfile.mkdtemp(prefix="amem-rescore-"))
write_tables(rescore_records(records, AuthorScorer(root)), output)
print(output)
PY
```

</details>

### 3. Inspect the live experiment entry point

```sh
.venv/bin/python scripts/gpt4omini-baseline.py --help
```

Help displays the supported conversations and conditions without transmitting a request. The collection driver uses `--execute`, `--cell` and `--condition`. **Live execution incurs model charges and generates stochastic results.** The recorded campaign is closed. A public clone lacks its private preflight evidence, verified local assets, prior acceptances and financial ledger. A new campaign needs its own reviewed, unused approval and budget. The historical Full / conv-44 command form is `.venv/bin/python scripts/gpt4omini-baseline.py --execute --cell conv-44 --condition full`.

The scientific configuration pins `openai/gpt-4o-mini-2024-07-18` through OpenRouter with OpenAI as the sole upstream. For authorised collection the driver loads `OPENROUTER_API_KEY`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` and `LANGFUSE_BASE_URL` (or `LANGFUSE_HOST`, set to `https://cloud.langfuse.com`) from an untracked root `.env`. Langfuse observation was required for this campaign. Keep credentials private. A cell writes its own memory/cache, event journal, predictions, two scoring views and phase receipt under `artifacts/gpt4omini/`. The final clean conv-44 replacement used a separately reviewed driver. [Configuration](config/gpt4omini.json) · [Campaign entry point](scripts/gpt4omini-baseline.py) · [Accepted replacement driver](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/scripts/gpt4omini_final_fresh.py)

## Repository map

```text
memory_layer.py, test_advanced.py          Frozen author memory system and QA evaluation
load_dataset.py, utils.py                 Frozen dataset parser and scoring functions
data/locomo10.json                        Released LoCoMo sample
manifests/                                Frozen conversation and question selections
config/                                   Study, provider and local asset settings
amem_repro/actions.py, runner.py           Action gates and independent build execution
amem_repro/adapter.py, openrouter.py       DeepSeek and native OpenRouter adapters
amem_repro/scoring.py, reporting.py        Dual rescoring and exports
tests/                                    Offline regression tests and replay fixtures
docs/reproducibility/                     Protocol, decisions, blockers and technical reports
reports/publication_assets/               Verified tables, figures and reporting code
reports/final_coursework/                 Submission manuscript and PDF
```

## Development history

The fork retains the authors’ history through `f9a173d`. The table traces coursework changes after that boundary. Hashes link to individual commits and numbered PR links open the corresponding reviews. [Frozen protocol](docs/reproducibility/experimental-protocol.md) · [Troubleshooting record](docs/reproducibility/blockers.md)

| Phase | What changed | Representative commits or PRs, earliest first |
|---|---|---|
| 1. Protocol, dataset and measurement | Froze the LoCoMo selection and Python environment, added per-build caches and journals, then implemented paired scoring and passive measurements. | [`5aaa5f6` · Freeze inputs](https://github.com/alistairkung/A-mem-reproducibility/commit/5aaa5f693b7315bf2e668d7540cebbe7523f96b7) · [`70646d7` · Record builds](https://github.com/alistairkung/A-mem-reproducibility/commit/70646d76fe303d6f5a75692bd1e47ffa37e79950) · [`60e109e` · Add scoring](https://github.com/alistairkung/A-mem-reproducibility/commit/60e109ef4de25db97f3f0fea6bd65fffc276515c) |
| 2. DeepSeek compatibility | Added bounded spending and structured-output checks, investigated truncated decisions, then built checkpoint recovery for a malformed response. | [PR #11 · Provider contracts](https://github.com/alistairkung/A-mem-reproducibility/pull/11) · [PR #13 · Output limits](https://github.com/alistairkung/A-mem-reproducibility/pull/13) · [PR #14 · Checkpoint recovery](https://github.com/alistairkung/A-mem-reproducibility/pull/14) |
| 3. Replay and independent gates | Replayed the recorded Full baseline and tested the two action gates against the frozen author implementation. | [PR #15 · Full replay](https://github.com/alistairkung/A-mem-reproducibility/pull/15) · [PR #16 · Action gates](https://github.com/alistairkung/A-mem-reproducibility/pull/16) |
| 4. Exploratory collection and reporting | A stopped conv-44 build exposed recovery limits, and the second DeepSeek campaign added tracing and recovered its oversized reporting export. | [PR #19 · Incomplete baseline](https://github.com/alistairkung/A-mem-reproducibility/pull/19) · [PR #26 · Observed Run 2](https://github.com/alistairkung/A-mem-reproducibility/pull/26) · [PR #34 · Reporting completion](https://github.com/alistairkung/A-mem-reproducibility/pull/34) |
| 5. GPT-4o-mini via OpenRouter | Switched to native schemas with OpenAI as the sole upstream, verified routing and billing, and collected three Full baselines. | [PR #35 · Provider transition](https://github.com/alistairkung/A-mem-reproducibility/pull/35) · [PR #36 · First Full release](https://github.com/alistairkung/A-mem-reproducibility/pull/36) · [PR #41 · Three Full results](https://github.com/alistairkung/A-mem-reproducibility/pull/41) |
| 6. Four-condition experiment | Compared all four conditions on conv-49, expanded to the other conversations, and recorded the final transport stop with eleven cells accepted. | [PR #43 · First factorial results](https://github.com/alistairkung/A-mem-reproducibility/pull/43) · [PR #44 · Expand the ablation](https://github.com/alistairkung/A-mem-reproducibility/pull/44) · [PR #47 · Eleven-cell stop](https://github.com/alistairkung/A-mem-reproducibility/pull/47) |
| 7. Final cell recovery | Preserved the stopped answer prefix and failed replacement, then accepted a fresh Linking Only / conv-44 build and reconciled the twelve cells. | [PR #50 · Answer-stage stop](https://github.com/alistairkung/A-mem-reproducibility/pull/50) · [PR #51 · Replacement stop](https://github.com/alistairkung/A-mem-reproducibility/pull/51) · [PR #52 · Twelve-cell result](https://github.com/alistairkung/A-mem-reproducibility/pull/52) |
| 8. Analysis and figures | Built tables from matched scores, compared the two cost frontiers and documented the exploratory DeepSeek comparison. | [PR #53 · Publication tables](https://github.com/alistairkung/A-mem-reproducibility/pull/53) · [PR #54 · Cost frontiers](https://github.com/alistairkung/A-mem-reproducibility/pull/54) · [PR #56 · DeepSeek comparison](https://github.com/alistairkung/A-mem-reproducibility/pull/56) |
| 9. Coursework report | Typeset the manuscript, reviewed its numerical fidelity and clarified the distinction between accepted-build and campaign costs. | [`3b9297c` · Typeset report](https://github.com/alistairkung/A-mem-reproducibility/commit/3b9297c3b2bf5f08230cae58c356b4544a31bc76) · [`c7c2b0e` · Clarify costs](https://github.com/alistairkung/A-mem-reproducibility/commit/c7c2b0e4bd0fe16f382d17f2c5390e50daf24619) · [PR #58 · Final report](https://github.com/alistairkung/A-mem-reproducibility/pull/58) |

PR #52 merged into the replacement-group branch after PR #51 merged into `main`. Publication code pins `8485673` directly, so that result can be inspected even on a branch without the final experimental files in its working tree.

## Attribution and licence

Wujiang Xu, Zujie Liang, Kai Mei, Hang Gao, Juntao Tan and Yongfeng Zhang authored **A-Mem: Agentic Memory for LLM Agents** (NeurIPS 2025). Their memory implementation, evaluation scripts, parser and scoring code are inherited from the frozen upstream release. The wrapper, four-condition experiment, execution controls, analysis and coursework materials are this reproduction’s contributions. [Paper](https://arxiv.org/abs/2502.12110v11) · [Original authors’ README and BibTeX citations](UPSTREAM_README.md) · [MIT licence and original copyright notice](LICENSE)

The preserved README is byte-identical to upstream `f9a173d:README.md`. Its SHA-256 is `e0825d6e3ae360150d1996505d4084ebebdd497482f1acd8bbf7af99b8f29efd`.
