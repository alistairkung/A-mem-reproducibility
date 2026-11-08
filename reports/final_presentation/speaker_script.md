# Reproducing A-MEM

## Recording script

1,751 spoken words · 14:00 target including pauses. At 130 words per minute the spoken text takes 13:28. Bracketed cues are silent.

## Slide 1 — Reproducing A-MEM

Target 0:35  ·  72 spoken words  ·  finish by 0:35

*[Leave a beat between the two questions.]*

I set out to reproduce the A-MEM paper’s comparison of three ways to build a memory. One combination was missing. Does updating an older memory help when the system cannot link new notes to it? And when the system does more work, is the gain in answer quality worth the cost? As I worked through the evaluation, I found that the second question also depended on what counted as a good answer.

*Coursework report §§1, 3.1, 7*

## Slide 2 — How A-MEM works

Target 1:05  ·  137 spoken words  ·  finish by 1:40

*[Follow the new note across the diagram, then point to the older neighbour.]*

Imagine telling an assistant that you’ve just started a new job. A-MEM keeps your words in a note. A language model adds keywords, a short description of the context, and tags. The system uses similarity to find up to five existing notes that might be related. A single model decision then proposes what, if anything, should change.

Strengthening acts on the new note. It can add outgoing links to earlier notes and change the new note’s tags. Neighbour evolution acts on an older note. It can revise that note’s context and tags as later information arrives. In both cases, the words originally recorded stay intact.

The system then inserts the new note. Later, when I ask a question, it starts with the ten most similar notes. Following their links can bring additional entries into the answer prompt.

*Coursework report §2.1*

## Slide 3 — The missing ablation

Target 1:00  ·  124 spoken words  ·  finish by 2:40

*[Point to Evolution Only, then compare it with Neither in the same row.]*

An ablation switches off part of a system to see what changes. Here the rows tell us whether a new note can acquire links and updated tags. The columns tell us whether an older neighbour’s context and tags can change.

The paper gives us Neither, Linking Only and Full. Comparing Full with Linking Only tells me what happens when I enable evolution in a system that already creates links. It leaves a different question open. If older notes acquire context as events unfold, could that alone help the system answer questions about when something happened?

I added the highlighted cell, Evolution Only. I can now compare it directly with Neither and then ask whether the effect of evolution changes when linking is also available.

*Coursework report §4.1*

## Slide 4 — Experimental wrapper and fidelity

Target 1:10  ·  146 spoken words  ·  finish by 3:50

*[Trace the shared decision to the two gates. Pause before the replay counts.]*

I kept the authors’ source frozen and put the experiment around it. In the inner box, every configuration still asks the model for the shared decision. Each gate permits a change only if the model selected that action and the configuration enables it. The new note still goes into memory when both gates are off.

Outside that box, each build has its own store, retrieval index and cache. I fixed the model route and prompts, traced execution with Langfuse, and recorded model usage and charges separately.

For a separate fidelity check, I gave the frozen implementation and my Full configuration the same recorded DeepSeek responses from conversation fifty. The replay matched five hundred and sixty-eight insertion states, fifteen hundred and forty-four recorded requests, and two hundred and four answers. That establishes implementation fidelity on this replay. Independent live runs can still produce different memories and answers.

*Coursework report §§2.2, 4.2–4.3*

## Slide 5 — Experimental population and metrics

Target 0:55  ·  128 spoken words  ·  finish by 4:45

*[Read across the three conversation rows, then the total.]*

For the primary experiment I used GPT four o mini throughout. I chose three LoCoMo conversations by length before seeing their scores. Together they give each configuration seventeen hundred and fifty-two turns and five hundred and fifty-eight questions. Four configurations across three conversations meant twelve separate memory builds. The questions match across conditions, but the memories used to answer them were generated independently.

I used the authors’ word-overlap measures. F1 balances how many of the answer’s distinct words appear in the reference with how many reference words the answer captures. BLEU one measures individual word overlap and penalises answers that are too short. I averaged question scores with equal weight. For questions about missing information, I also counted how often the system chose to say it didn’t know.

*Coursework report §§1.1, 3.2–3.4*

## Slide 6 — Historical and complementary adversarial evaluation

Target 1:10  ·  143 spoken words  ·  finish by 5:55

*[Use the salary example. Indicate each reference before describing its score.]*

Suppose Alice says she has started a job and never gives her salary. I ask, “What is Alice’s salary?” One option says a hundred and fifty thousand dollars. The other says, “Not mentioned in the conversation.” The second choice fits Alice’s account.

In the released historical evaluation, the reference for this kind of question is the supplied distractor. An answer containing the salary can therefore earn word overlap with that reference. I retained this procedure so I could compare my results with the paper. I also asked how well the same answers matched the no-information response. The figures call this complementary measure “alternative-reference.”

I scored each saved prediction twice. Only the reference for these adversarial questions changes. F1 and BLEU one are calculated exactly as before. Counting whether the system selected the no-information option gives me a more direct measure of appropriate abstention.

*Coursework report §3.4*

## Slide 7 — Did we reproduce the paper’s conclusion?

Target 1:20  ·  165 spoken words  ·  finish by 7:15

*[Follow the solid bars first. Pause, then switch to the hatched bars.]*

Look first at the solid bars for the three configurations in the paper. Historical F1 rises from thirty point zero three percent for Neither to thirty point two one for Linking Only and thirty-two point six nine for Full. I recovered that aggregate ordering on my subset. The exact Table Three scores and the category rankings differed.

Now look at the hatched bars. Neither comes first at thirty-nine percent. Linking Only follows at thirty-seven point three four, then Full at thirty-six point nine one. Evolution Only is last at thirty-five point eight six. Every bar pair uses the same saved answers from that configuration.

The separate choice count helps explain the change. Neither recognised missing information on eighty-six of the one hundred and twenty-one adversarial questions. Full did so on seventy-one. Which reference I use determines how those answers contribute to the overall score. The historical result answers the reproduction question. The complementary result tells me what happens when the evaluation rewards acknowledging missing information.

*Coursework report §§5.1, 7.1–7.2*

## Slide 8 — Which mechanisms helped?

Target 1:10  ·  128 spoken words  ·  finish by 8:25

*[Use the multi-hop row first, then move down to temporal.]*

The heatmap breaks the complementary F1 score down by question type. Start with the multi-hop row. These questions require putting together facts from different turns, so there’s a reason links might help. Linking Only improved on Neither by three point four zero percentage points. Full scored lower than Linking Only on that same row.

My hypothesis about neighbour evolution was different. I thought updating an older note might make it easier to recover a sequence of events. On the pooled temporal questions, Evolution Only scored two point four four points below Neither. Across all questions, the difference was minus three point one five points. I found no overall support for that independent benefit.

Full led on single-hop and open-domain questions, although the open-domain row contains just twenty-seven questions.

*Coursework report §5.2*

## Slide 9 — Factorial interaction

Target 0:55  ·  114 spoken words  ·  finish by 9:20

*[Read the vertical gaps at linking OFF and ON. The narrowing gap is the interaction.]*

Read this graph vertically at each end. On the left, with linking off, switching evolution on lowers complementary F1 by three point one five points. On the right, with linking on, the same switch lowers F1 by only zero point four three points.

The difference between those two changes is positive two point seven two. That is the four-term interaction. It’s positive because the loss is smaller on the right. Neither still has the highest pooled score.

The interaction was positive in conversations forty-four and fifty and negative in forty-nine. With one stochastic build in each cell, I can describe how the observed contrasts differ. I can’t estimate run-to-run variation or claim statistical significance.

*Coursework report §§5.2, 7.3*

## Slide 10 — Is additional complexity worth its cost?

Target 1:20  ·  166 spoken words  ·  finish by 10:40

*[Identify the filled markers in each panel. Both panels use identical costs.]*

Professor Nguyen’s discussion of Pareto trade-offs prompted me to ask what extra inference actually bought. A filled point lies on the frontier. To beat it, a competitor would have to be cheaper for at least the same F1, or score higher for at most the same cost.

On the left, using historical F1, Neither, Linking Only and Full each have a place on the frontier. On the right, exactly the same costs are plotted against complementary F1. Neither is now both the cheapest and the highest scoring, so it is the only frontier point.

The retrieval records show where some of the extra work went. From Neither to Linking Only, average retrieval rose from ten entries per question to just over twenty. Total native input tokens for answering went from about three quarters of a million to just over one and a half million.

Both panels use identified model charges for the twelve accepted builds. The frontier depends on the sample, model, prices and scoring policy.

*Coursework report §5.3*

## Slide 11 — The unplanned DeepSeek detour

Target 1:15  ·  154 spoken words  ·  finish by 11:55

*[Let the exploratory qualification register before comparing the two F1 scores.]*

Before running that experiment, I tried DeepSeek Flash for a practical reason. I already had credit. Its interface was compatible with OpenAI’s, and I assumed that meant the model could fill the same role. I soon had responses with the wrong field types, malformed output, and decisions that hit the output limit. I spent much of my time validating responses and working out which failures I could recover from.

Three Full lineages eventually completed with Degraded status. On the same questions their pooled complementary F1 was fifty point three seven percent, compared with thirty-six point nine one for GPT four o mini Full. These are exploratory observations. The provider, output limits, compatibility rules and recovery history also differed, so I couldn’t attribute the gap to the model.

I returned to GPT-four-o-mini for the factorial study because the question I wanted to answer was about memory operations. Porting the system had become a different project.

*Coursework report §6.1*

## Slide 12 — Operational reliability versus research focus

Target 1:00  ·  137 spoken words  ·  finish by 12:55

*[Distinguish the three cost scopes. Read the clean-run line last.]*

I learned to trace answers to memories and charges to requests. I’d set bounded retry rules in advance and check new charges incrementally. Rechecking the whole history took time away from the hypothesis.

The accounting illustrates the distinction. The twelve accepted builds cost about four dollars and six cents in identified model charges. Across the GPT four o mini campaign, including earlier attempts and compatibility checks, that rose to about four dollars seventy. With unresolved reservations and a conservative allowance for Langfuse service, exposure reached about ten dollars forty-six. The final invoice could differ from that upper bound.

The final fresh Linking Only build on conversation forty-four produced six hundred and seventy-five memories and answered all one hundred and fifty-eight questions. All sixteen hundred and sixty-six model requests succeeded on their first transmission. It needed zero retries.

*Coursework report §§4.3, 6.2*

## Slide 13 — Conclusions

Target 1:05  ·  137 spoken words  ·  finish by 14:00

*[Pause before the final sentence.]*

What can I claim to have reproduced? Under the same recorded responses, Full followed the frozen implementation through memory construction and answering. Under the historical scoring policy, I also recovered the paper’s aggregate ordering of its three configurations.

I didn’t reproduce the exact published scores or a consistent ranking across question types. The complementary reference changed the overall ordering. Evolution Only gave me a direct test of my temporal hypothesis. I found no independent aggregate gain.

I used three preselected conversations, started retrieval with ten notes, and had one stochastic build per cell. The exact questions and retrieval depths behind the paper’s Table Three are incompletely specified. Repeating each build would tell me how much these contrasts move when the memory is generated again.

Reproducing an algorithm is not the same as reproducing every conclusion about it.

*Coursework report §§7.1–7.3*
