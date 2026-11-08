# Experimental wrapper architecture

The Section 4.2 asset follows the supplied Mermaid screenshot's nested composition. The outer **Experimental wrapper** contains one controls box and an inner **Original A-MEM algorithm**. Two prominent side-by-side gates follow the shared evolution decision. A single **Experimental evidence** box appears below the wrapper. The screenshot supplies layout guidance; source-verified behaviour determines the labels and connections.

- [Primary SVG](amem_wrapper_architecture.svg)
- [300-DPI PNG](amem_wrapper_architecture.png)
- [Editable layout and reproduction source](generate_diagram.py)

## Suggested caption

**Figure X. Experimental wrapper around the frozen A-MEM implementation.** The wrapper supplies frozen configuration, provider and execution controls, isolated cell stores, observability and financial accounting. The original workflow creates a memory note, retrieves neighbours and generates a shared evolution decision in every configuration. The bound gates permit the selected memory mutations only when enabled. Note insertion follows decision processing, and QA uses the completed memory store. Local memory states, predictions and scores, together with trace and cost evidence, support experimental verification.

## Source fidelity and intentional simplification

The author files remain frozen. The gates are Boolean additions to the original action conditions in a per-instance copy of the evolution method. Both the author's decision and the configuration gate must permit an action. Strengthening bundles new-note links and tags; neighbour updates bundle existing-note contexts and tags. Neither disables both, Linking Only enables strengthening, Evolution Only enables neighbour updates and Full enables both.

The two branches represent independent mutation scopes, not mandatory actions, mutually exclusive routes or parallel threads. If neither action applies, the note is still inserted. The author retains its decision/action order, counter, consolidation and original stale-index behaviour. Those bookkeeping details are omitted from the graphic for readability.

Memory metadata is generated before retrieving up to five existing neighbours. The shared LLM decision is generated even when both gates are disabled. QA is a later phase over the completed per-cell memory and index; the vertical diagram does not imply asking all benchmark questions after each insertion. The compact QA box covers original question-keyword generation, initial top-ten retrieval, author link expansion (including possible duplicates) and answering.

All four LLM stages pass through the controlled adapter under frozen settings. Langfuse capture and Experiments, provider controls, local exposure reservations and provider-charge reconciliation belong to the surrounding wrapper. They do not select memory mutations. The evidence box collects locally authoritative scientific records and separate service/accounting evidence. Scores evaluate saved predictions under the historical and alternative-reference policies, with binary adversarial correctness where applicable. The single arrow to evidence summarizes record capture throughout execution.

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

From the repository root, run in the existing publication-assets Matplotlib environment:

```sh
python reports/publication_assets/architecture/generate_diagram.py
```

The Python source is the editable layout. Matplotlib 3.11.2 and DejaVu Sans were used. The SVG has a white 16 cm by 19 cm canvas and outlined lettering for consistent rendering in LaTeX and PowerPoint. Text and positions remain editable in the source. PNG is 1889 × 2244 pixels at 300 DPI. Body text is 9 pt at 16 cm width, approximately 8.44 pt at 15 cm. Insert at 15–16 cm width to retain report-scale readability.

The final PNG and an independent CairoSVG 2.9.1 rendering of the SVG were inspected at report scale for overlaps, clipping and crossing or ambiguous arrows. Repeated generation produces byte-identical exports. The revision is confined to this architecture directory and does not regenerate existing scientific figures or change accepted experiments or results.
