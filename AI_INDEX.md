# Agent-readable research index

## Claim, version and limits

Version 0.1.0-candidate, Anonymous, unrefereed, DOI 10.5281/zenodo.23284137. The [paper](paper/pmms8.pdf)
([LaTeX](paper/pmms8.tex), [Markdown](paper/pmms8.md)) proves Theorem 1: every instance with three agents,
nonnegative additive valuations and at most eight indivisible goods has a complete PMMS allocation; with the
published nine-good counterexamples this gives m* = 9. [Assurance](ASSURANCE.md) states the trusted base and the
dimensions not established (formalisation, independent reproduction, specialist and editorial review). The
[claim ledger](paper/CLAIMS.json) lists every claim with its evidence and dependencies; [status](STATUS.md) and
[provenance](PROVENANCE.md) give version and production history.

## Proof structure

1. Written reduction: paper Sections 2–4, clause schemas (C1)–(C10) and the soundness proposition in Appendix A. A
   counterexample on eight goods yields a positive generic one (genericity lemma), which satisfies one of ten
   normal-form formulas: profiles (1,1,5), and (1,2,4), (1,3,3), (2,2,3) with three least-agent sub-cases each.
2. Smaller cases, injected as restriction clauses: [six goods](six_goods/) and the seven-good normal forms
   [(1,1,4)](seven_goods/case114/), [(1,2,3)](seven_goods/case123/), [(2,2,2)](seven_goods/case222/).
3. Ten eight-good refutations: [case115](eight_goods/case115/), [case124_sub0](eight_goods/case124_sub0/),
   [case124_sub1](eight_goods/case124_sub1/), [case124_sub2](eight_goods/case124_sub2/),
   [case133_sub0](eight_goods/case133_sub0/), [case133_sub1](eight_goods/case133_sub1/),
   [case133_sub2](eight_goods/case133_sub2/), [case223_sub0](eight_goods/case223_sub0/),
   [case223_sub1](eight_goods/case223_sub1/), [case223_sub2](eight_goods/case223_sub2/). `sub` is zero-based
   (`sub2` is the paper's s₃). The ten `proof.lrat.gz` files are separate assets in the Zenodo record (proofs above 600 MB split into 400 MiB
   parts); run [place_proofs.py](place_proofs.py) to join them and put them in place after checking their digests
   against [MANIFEST.json](MANIFEST.json).

## Checking

* [Clause verifier](verify_case.py): standard library only, imports nothing from the [generator](build_case_cnf.py)
  ([signsat.py](signsat.py), [cases.py](cases.py)); rebuilds every clause from the variable dictionary.
* LRAT checkers: [lrat-check](tools/lrat-check.c) (third-party, drat-trim) and [check_lrat_rup.py](check_lrat_rup.py)
  (standard library; rejects RAT steps).
* [Nine-good check](verify_nine_good.py) with [result](nine_good_check.json): all 3^9 allocations of each published
  instance.
* [One-command replay](verify_bundle.py): manifest digests, nine-good check, clause derivation and lrat-check for all
  fourteen certificates; prints `PASS_ALL_BUNDLE_CHECKS`. Receipts are in [receipts/](receipts/); the per-certificate
  `lrat_check.out` and `python_check.json` record both checkers.
* Generator controls: [semantic control](controls/semantic_control.py) and
  [normal-form control](controls/normalisation_control8.py).
* [Negative controls](controls/negative_controls.py): a deleted or added clause is caught by the verifier, and a
  changed hint or a missing empty clause is rejected by both checkers (prints `NEGATIVE_CONTROLS_PASS`).

Expected counts: all eight-good formulas have 252,930 variables; trimmed proof steps per certificate are in each
`trim_summary.json` and in Appendix B of the paper.

## Non-proof material

[Section 6 data](data/) (hard instances, refuted strengthenings, annealing scout) is computational observation, not
part of any proof. [Reviews and responses](review/) record the adversarial model reviews and the response to an
external review. [Prior-art record](paper/novelty_report.md) and [research gates](RESEARCH_GATES.json) bound the
priority claim; [citation audit](CITATION_AUDIT.md) maps each reference to its use.

## Licensing and further work

See the [component licence map](LICENSES.md). Open directions: a human-readable proof, a construction covering the
instance of Observation 3(a), formalising the reduction, independent replay, and four agents.
