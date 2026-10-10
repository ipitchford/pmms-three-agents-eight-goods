# Replay receipt

Producer-side replay of every check with `verify_bundle.py`, run on the finished package from
2026-10-10T17:44:43Z to 2026-10-10T18:21:20Z (UTC) on the producer's machine (see `ENVIRONMENT.txt`). The machine-readable
receipt is [`receipts/replay_receipt.json`](receipts/replay_receipt.json). Status: **PASS_ALL_BUNDLE_CHECKS**.

It checked the SHA-256 digest of every file in the manifest at that time, the nine-good counterexamples, the clause
derivation of all fourteen formulas, and `lrat-check` on all fourteen certificates (the certificate files are the
ones distributed). Each certificate was also accepted by the standard-library Python checker; those receipts are the
`python_check.json` files in the certificate directories. The negative controls are run separately
(`controls/negative_controls.py`).

This is internal replay by the producer, not an independent reproduction.

| Check | Result |
|---|---|
| `manifest_digests` | PASS |
| `nine_good_counterexamples` | PASS |
| `build_lrat_check` | PASS |
| `six_goods_clauses_derived` | PASS |
| `six_goods_lrat_check` | PASS |
| `seven_goods_case114_clauses_derived` | PASS |
| `seven_goods_case114_lrat_check` | PASS |
| `seven_goods_case123_clauses_derived` | PASS |
| `seven_goods_case123_lrat_check` | PASS |
| `seven_goods_case222_clauses_derived` | PASS |
| `seven_goods_case222_lrat_check` | PASS |
| `eight_goods_case115_clauses_derived` | PASS |
| `eight_goods_case124_sub0_clauses_derived` | PASS |
| `eight_goods_case115_lrat_check` | PASS |
| `eight_goods_case124_sub1_clauses_derived` | PASS |
| `eight_goods_case124_sub0_lrat_check` | PASS |
| `eight_goods_case124_sub1_lrat_check` | PASS |
| `eight_goods_case124_sub2_clauses_derived` | PASS |
| `eight_goods_case133_sub0_clauses_derived` | PASS |
| `eight_goods_case124_sub2_lrat_check` | PASS |
| `eight_goods_case133_sub1_clauses_derived` | PASS |
| `eight_goods_case133_sub0_lrat_check` | PASS |
| `eight_goods_case133_sub1_lrat_check` | PASS |
| `eight_goods_case133_sub2_clauses_derived` | PASS |
| `eight_goods_case223_sub0_clauses_derived` | PASS |
| `eight_goods_case133_sub2_lrat_check` | PASS |
| `eight_goods_case223_sub1_clauses_derived` | PASS |
| `eight_goods_case223_sub0_lrat_check` | PASS |
| `eight_goods_case223_sub2_clauses_derived` | PASS |
| `eight_goods_case223_sub1_lrat_check` | PASS |
| `eight_goods_case223_sub2_lrat_check` | PASS |
| `eight_goods_all_profiles_covered` | PASS |
