# BLK-027: two-score representation acceptance

The user's 6 November 2026 decision authorises a representation exception for
Neither / conv-50 only. It changes no author score, prompt, generation, memory,
retrieval setting or primary metric. No result is re-imported and no inference
is repeated. The original Incomplete phase and SQL terminal state remain immutable.

| Policy | Question | Score ID | Item observation | Experiment |
| --- | --- | --- | --- | --- |
| author-corrected-v1 | conv-50:qa:76 | 11db9dd69284d175 | 23208ab4fba94152 | adc0d9055c4d79ec |
| author-legacy-c5-v1 | conv-50:qa:76 | 03f14c429aa18b91 | 79280b22de9c5d26 | fc26ec074fa15cf0 |

Both metrics are `bleu4`. The saved author value is
`4.0194972443398975e-7` (`0x1.af971954baf8dp-22`); the only differing remote
representation admitted is `4.019497244339897e-7` (`0x1.af971954baf8cp-22`).
The full project/run/policy/trace/item/score tuple, original-record hashes and
immutable input evidence are pinned in [the exception binding](../../config/blk027-acceptance.json).
There is no epsilon, rounding rule, relative error or general one-ULP allowance.
Every other score, including another BLEU-4, requires exact equality.

The separate GET-only verifier checks all 204 original questions, 408 Experiment
items, 5,804 numeric scores, original QA trace associations, input/output/reference
and metadata. It first validates both exact tuples and then applies the existing
strict verifier to temporary comparison copies. It preserves all raw reads and
never changes the saved scores or remote records. It restores and checks the
original completed cache in memory and writes new proof files only beneath the
separate outcome namespace. Runtime observation verification also remains exact.

A supplement is accepted as Degraded only with both independent acceptance axes,
complete raw financial reconciliation and immutable evidence. Future approvals pin
its digest. Ledger admission recognises only the original reporting-only terminal
phase under that supplement; the phase remains terminal. Existing halt, unknown
charge, cell cap, predecessor order and no-repeat checks remain active. The normal
verifier for all three remaining cells has no numerical exception.

A fresh source-bound cloud release check uses mock model completions only. Its new
one-shot allocation is 1,118 units, US$0.089440 at the full marginal service rate.
The two old claims remain consumed. The cumulative programme service reserve is
US$6.769440; each new cell still reserves US$1.08 service within its US$5 total cap.
The US$42 planned allocation and US$8 protected contingency are unchanged.

Required before collection: focused adverse tests, complete offline suite, frozen
author/Full archive replay, independent Standards/Spec approval, ordinary merge,
fresh runtime/Experiment readback and separate acceptance supplement, then current
financial and service capacity checks. Resume Neither / conv-44, Linking Only /
conv-50 and Linking Only / conv-44 in that order. Stop on any new mismatch or
unsupported failure; this decision does not authorise a wider numerical policy.

Independent review additionally requires all gate service/fixture dependencies to
match reviewed Git bytes, and requires the exact reviewed head to be the second
parent of the normal merge. These checks apply before any new cloud admission,
supplement acceptance or remaining paid release. All other historical release
paths retain their original rules.
