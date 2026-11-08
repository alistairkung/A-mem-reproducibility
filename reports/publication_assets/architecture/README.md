# Experimental wrapper architecture

The diagram is intended for Section 4.2, Wrapper Implementation and Validation. It distinguishes the wrapper controls, the author scientific workflow with its two bound action guards, and the resulting scientific and service evidence.

- [Primary vector diagram](amem_wrapper_architecture.svg)
- [300-DPI PNG](amem_wrapper_architecture.png)
- [Editable layout and reproduction source](generate_diagram.py)

## Suggested caption

**Figure X. Experimental wrapper around the frozen A-MEM implementation.** The wrapper selects the configuration, binds two action gates to a copy of the original evolution method, controls model execution and records experimental evidence. The author workflow generates the shared evolution decision in every configuration and applies only selected, enabled memory mutations. Each condition–conversation cell begins with an independent store and retrieval index. Passive capture exports generations, actions, retrieval and QA to Langfuse. The local request ledger reserves and records model-call exposure, and separate provider readback verifies charges.

## Reading the diagram

Solid arrows indicate scientific data flow, configuration binding or model requests and responses. The double-headed boundary arrow denotes every box marked LLM: metadata, shared evolution, question keywords and answering. Dashed arrows denote observation exports and accounting evidence. The blue-grey outline identifies the wrapper's bound action guards. The original author files are preserved; the gates are Boolean additions to the original action conditions in a per-instance method copy.

The action stage also requires the author's decision to select the action. Strengthening bundles outgoing links and tag changes on the new note. Neighbour evolution bundles context and tag changes on existing notes. Neither disables both, Linking Only enables strengthening, Evolution Only enables neighbour updates and Full enables both. The common model decision runs under all four settings, including Neither.

Metadata is generated while constructing the pending MemoryNote. The author then retrieves up to five neighbours, generates the shared decision, applies any permitted actions, inserts the note, adds its retrieval document and applies the original conditional counter/consolidation logic. The diagram groups insertion and its bookkeeping for readability. The accepted original stale-index semantics are retained.

QA generates query keywords, retrieves an initial top ten memories with the author's subsequent link expansion and generates an answer. Link expansion can include duplicates. Saved predictions are evaluated under the authors' historical and the additional alternative-reference policies, with F1, BLEU-1 and binary adversarial correctness where applicable. The evaluation box represents wrapper reporting after generation.

Memory/index snapshots and saved predictions/scores are authoritative local scientific evidence. Langfuse is the separate observability service. Its traces and Experiments reflect local execution and saved scores. Accounting is a local durable request journal plus independent OpenRouter generation/account readback. The adapter reserves exposure before transmission and records returned usage afterward. Budget and critical-observation checks can halt paid admission; the ledger and service do not choose memory content or actions.

## Verified source references

The architecture was checked against the accepted execution source at commit `8485673183d7b8018c841082d075b21158002700`. Links below pin that commit. The frozen author revision is `f9a173dec325d84fcc97e7828775c7b241c33466`.

| Diagram responsibility | Production source and inspected symbols |
|---|---|
| Bound action copy and fixed gates | [actions.py](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/amem_repro/actions.py), `gated_evolution_tree`, `make_action_agent_factory` |
| Author loading, per-instance agent and controller binding | [author.py](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/amem_repro/author.py), `_load_memory`, `make_agent_factory` |
| Metadata, neighbour decision, mutations, insertion and consolidation | [memory_layer.py](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/memory_layer.py), `MemoryNote`, `add_note`, `process_memory`, `_evolve`, `find_related_memories`, `consolidate_memories` |
| Keywords, initial retrieval, link expansion and answering | [test_advanced.py](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/test_advanced.py), `generate_query_llm`, `answer_question`; `memory_layer.py`, `find_related_memories_raw` |
| Isolated cell execution and saved QA records | [runner.py](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/amem_repro/runner.py), `run_manifest`; [artifacts.py](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/amem_repro/artifacts.py), `CacheStore` |
| Model schema/routing, request journal and reserve-before-POST | [openrouter.py](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/amem_repro/openrouter.py), `OpenRouterController.get_completion` |
| Passive action and retrieval capture | [measurements.py](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/amem_repro/measurements.py), `observe_actions`, `observe_retrieval` |
| Runtime traces and bounded saved-result Experiments | [observability.py](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/amem_repro/observability.py), `LangfuseObserver`; [gpt4omini_reporting.py](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/amem_repro/gpt4omini_reporting.py), `import_results` |
| Historical/alternative views and adversarial metrics | [scoring.py](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/amem_repro/scoring.py), `AuthorScorer`, `rescore_records` |
| Active final-campaign reservations, settlement and readback | [linking44_final_ledger.py](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/amem_repro/linking44_final_ledger.py), `FinalLedger._reserve`, `settle`, `close_attempt`; [linking44_retry.py](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/amem_repro/linking44_retry.py), `FinalController` |
| Generic stop and historical budget infrastructure | [budget.py](https://github.com/alistairkung/A-mem-reproducibility/blob/8485673183d7b8018c841082d075b21158002700/amem_repro/budget.py), `BudgetStop`; active accounting is identified in the preceding row |

The accepted configuration is dated `openai/gpt-4o-mini-2024-07-18` through OpenRouter with OpenAI-only upstream, provider fallbacks disabled, native author schemas and prompts, temperature 0.7 except category-5 answering at 0.5, output limits 1,000 except 4,096 for evolution, construction neighbours five and initial QA retrieval ten. Detailed retries, malformed-output fallbacks and checkpoint recovery are omitted from the diagram for legibility. The accepted final fresh cell used no operational retries.

## Reproduce and inspect

From the repository root, use the Matplotlib environment recorded by the existing publication pipeline:

```sh
python reports/publication_assets/architecture/generate_diagram.py
```

The Python source is the editable diagram layout. Box positions and arrow routes are explicit so that regeneration preserves report-scale typography. Matplotlib 3.11.2 and DejaVu Sans were used. SVG IDs and metadata are stable. The SVG has a white 16 cm by 16.6 cm canvas and outlined lettering for consistent display across document and presentation renderers. Text and layout are editable in the Python source. PNG is exported at 300 DPI. Text is 8 pt at the intended 16 cm report width; insert at that width to preserve it. For PowerPoint, use the SVG or the 300-DPI PNG.

Both output formats were inspected at report scale for sequence, arrow direction, overlaps and clipping. The SVG was independently rasterized with CairoSVG 2.9.1 to check consistency with the PNG; outlining lettering avoids renderer-specific font substitutions. Export regeneration is byte-identical in the recorded Matplotlib environment. Only this architecture directory is added by the PR; existing scientific figures are not regenerated.
