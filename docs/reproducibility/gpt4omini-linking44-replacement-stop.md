# Local Linking Only / conv-44 replacement outcome

**Incomplete.** The replacement group started one attempt, `gpt4omini-linking_only-conv44-replacement-r1`. It committed the first 566 of 675 original turns and answered zero of 158 questions. At the next turn the provider returned an unsupported completion status. The restart policy requires a classified transient transport failure, so both remaining ordinals stayed unused. The eleven previously accepted QA cells remain the scientific population.

## Execution and stopping decision

On 7 November 2026 the group opened on PR #50's ledger. Independent Standards and Spec reviews cleared commit `91d651b876acf33c0a3ce3d2eb098677308a84b0` for local execution. The focused offline gate passed 159 tests. The native executor completed an ordered 1,666-call fixture for 675 turns and 158 questions using synthetic opening SQL. Separate checks on copies of PR #50's ledger verified stage admission and unsafe stops. Adverse cases covered cross-attempt isolation, aggregate admission, terminal success, the third-claim limit and rejection of unknown or financially unsafe restarts. The group's USD 10 ceiling includes model reservations and service usage across all ordinals.

The first attempt began at 21:45 Hong Kong time on 7 November in an empty memory store and independent cache namespace. The pinned OpenAI route, native schemas, shared decisions, temperatures, construction neighbours, retrieval and original scoring policies were inherited from the reviewed executor. The repetition was 1. The recorded build ended with counter 566, 557 strengthening actions and zero neighbour updates.

At `D24:13`, the 567th metadata call succeeded. The following shared decision, physical attempt **19482**, returned an HTTP 200 response from OpenAI for `openai/gpt-4o-mini-2024-07-18`. Its JSON envelope reported `finish_reason="error"`, `native_finish_reason=null`, 1,534 prompt tokens and 336 completion tokens under the 4,096-token limit. Its generated content ended inside a JSON string. The provider supplied no more specific reason. The adapter rejected the completion status and sealed the run before inserting that turn. The ledger's generic `BudgetStop` records the admission halt. Spending headroom remained.

This failure falls outside the approved transport restart and the original normally finished malformed-output and output-exhaustion recovery paths. The failed decision was transmitted once. The group retained its raw response, journal, partial memory and terminal SQL receipt. Its output contributes no QA predictions, scores or Experiment items. The PR #50 terminal lineage remains separate, including its full 675-note build and 87 saved answers.

## Finance and observability

| Replacement group | USD |
|---|---:|
| Provider-reported charges on 1,134 generation responses | 0.26973825 |
| Conservative model exposure on the same requests | 0.270704 |
| Metered Langfuse service at the full marginal rate, 2,830 units | 0.226400 |
| Additional model and metered service exposure | **0.497104** |
| Admission exposure including the full first-attempt service earmark | **1.350704** |

The USD 1.08 service earmark covers the actual units above. The failed decision reported a user charge of zero, an upstream inference cost of USD 0.00043170 and a conservative ledger charge of USD 0.000432. All five historical unknown reservations remain held at USD 0.099644 in total. The replacement added zero unknown reservations.

At 16:01:13 UTC on 7 November the authenticated Langfuse account showed 149,523 rolling units, 144,596 billing-period units, USD 3.57 draft usage, USD 29 subscription and zero paid usage on that snapshot. Including the previous eight-unit allowance gives a campaign service upper bound of USD 4.868240. The stopped attempt recorded 2,261 runtime observations across 569 traces. It reached the memory-construction stage only.

The GET-only close verified all 1,134 new generation IDs, including route, native usage and reported cost. Wallet usage and key usage each moved by USD 0.26973825. The residual on both was zero. The closing OpenRouter wallet held **USD 45.68074605**, with **USD 45.69239705** remaining on the key. The ledger now holds 19,477 settled requests and the five historical reservations. Campaign conservative model exposure is USD 4.417062. Together with the service upper bound, **campaign exposure is USD 9.285302**, leaving **USD 32.714698** of the planned USD 42 and the protected USD 8 contingency. Keeping the full service earmark on the admission ledger gives a more conservative USD 10.138902 campaign commitment and USD 31.861098 of planned headroom.

## Scientific handover

| Accepted population | Neither | Evolution Only | Linking Only | Full |
|---|---:|---:|---:|---:|
| 400 matched questions, corrected F1 / BLEU-1 (%) | 37.38 / 33.69 | 34.55 / 31.28 | 36.80 / 33.32 | 35.89 / 32.14 |
| 558 matched questions, corrected F1 / BLEU-1 (%) | 39.00 / 35.01 | 35.86 / 32.29 | Incomplete | 36.91 / 32.81 |
| Adversarial correct on the 400-question population | 61/86 | 57/86 | 58/86 | 53/86 |
| Adversarial correct on the 558-question population | 86/121 | 79/121 | Incomplete | 71/121 |

The four-condition interaction on conv-49 and conv-50 was +1.91 F1 / +1.23 BLEU-1 percentage points across 400 matched questions. The interaction across 558 questions remains unavailable. The 558-question Evolution Only minus Neither comparison was −3.15 / −2.72 points. The reduced-scope coursework report can use these descriptive, single-build results. Category contrasts, historical scores, action and retrieval comparisons and the 22 accepted Experiment links are in the [eleven-cell report](gpt4omini-linking44-transport-stop.md) and [accepted analysis](gpt4omini-eleven-cell-analysis.json).

## Independent verification

Standards and Spec separately reconstructed all 566 committed turns, their actions, five consolidations and the stale retrieval corpus. CPU recomputation matched all 566 × 384 embedding values. The failed turn generated metadata and a shared-decision response, with zero committed changes for that turn. Standards verified the complete remote observation set. Both ordinals 2 and 3 remained unclaimed when the controller exited. The preservation audit rechecked 154,085 historical scientific, billing and observability files, the prior 18,348 SQL attempts, all eleven accepted cells and 1,534 DeepSeek files.

A separate post-stop environment check found the temporary Python installation missing the standard-library file `py_compile.py`. All 2,023 present regular files checked, including the interpreter, matched the retained distribution. This was observed after the recorded provider failure. The stopped-state verification completed, and the local installation was left as observed.

## Reproducibility evidence

The local release and receipts live under `artifacts/gpt4omini/cells/linking_only-conv-44/replacement/`. Original private responses and credentials are excluded from the public report. The first visibility read returned 2,256 of 2,261 observations. A subsequent read verified the complete runtime population. The original visibility failure is retained.

| Evidence | SHA-256 |
|---|---|
| Frozen group release | `fc0e075f9851e14fb1bb56d402413677781215c00e726e340ea3ef00da40d897` |
| Fixed-commit offline tests | `f9332cdd9f3b6b46d5309d212cedf988cbad9141e037cc1a2971db36ac29ff84` |
| Implementation Standards review | `78e8fe2f9281090f453658285614619c4d3b4c04d9ac696fd33df485ab390555` |
| Implementation Spec review | `3650e99995662e2ba56baf34c8b6bfceef58dbfe6c1635b3d9146a57a00a0f18` |
| Phase file | `0532f333e34e8379572a3e19ec22674a5793b26b6433e47377cf9f78c437cd42` |
| Canonical terminal SQL seal | `92ba657e697a9964009a2f84d081bb006fbfe3117acff1643b96f40986adde53` |
| Partial memory | `f1db1add924bc4b40b640b0fc7a435d6bcd0669d0cccfc3555923828e72225ca` |
| Raw provider response 19482 | `8d7b71f183190671333a15aee45a701b40438aa5051cce4185ad35ac38900209` |
| Journal | `87bbade97f5a0918d8cf6abaf02a2b70c66d29d0be4a2581c628b34baf9a2ea6` |
| Runtime readback | `54b5158e505ae4b54ad54d5802fb5d3a6de2e23eaf33c23b8526cb0a2d6b96ad` |
| Closing Langfuse capacity | `aa7f6bcee0f3dd3b13f09b95e65b1decd87f6eb3734a3c631633b67bea760f1b` |
| Generation and account reconciliation | `1a2ce0e93f16210d75d3971de2f6f4150e779b66ac92cd163cab362e090196a5` |
| Independent Spec stopped-state verification | `db4cd651a23b61e23aded483639a5f6c3393713054138893930a66eb64c0c492` |
| Independent Standards stopped-state verification | `a89977b01b6a820ac984252c3c5470ac1841491e9255a4d30d0dd369fd022519` |
| Exact embedding recomputation | `fc22fe9ce9bf7494022c7b793d2530e5cc35f8cad7c4017c1cfeb5888e7d814e` |
| Independent Standards remote readback | `481858d6010ac9e854e065de4ba74a492dac61f4745eff0a976fdff6449df89b` |
| Independent Spec finance verification | `d815d4ffa6cbd600a8b1626d92265a63b9998431e7a6ee44d574dae2049fffce` |
| Independent Standards finance verification | `b39fd46a2963e6ef85fe9a7acfc24af1c6039179f619d5f0c32945b160463253` |
| Independent campaign finance close | `f7b4dc89b1003a96b1f5a4e143eec81ec3e5294879f8a58e7db023b0fbe2ab29` |
| Closing historical preservation | `99685cb9e11360f410b64cd7bbad1d723d4c862bc7ad5fff3256bf41c699fa13` |
