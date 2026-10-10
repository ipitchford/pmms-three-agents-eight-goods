# Response to the external review of 10 October 2026

The review assessed the PDF only and recommended major revisions. The reviewer's identity is not recorded and the review itself is not redistributed; this file records each point and the action taken.

The review found no error in the written mathematics and reproduced every printed example. Each point was checked
before acting; the reviewer's computations for Observations 3(a) and 3(c), the extra allocation for 3(a) and the
Akrami et al. comparison were independently confirmed.

| Point | Action |
|---|---|
| 4.1 Proof objects not inspectable | The evidence bundle accompanies the paper: all fourteen formulas, dictionaries, trimmed LRAT certificates, generator, verifier, both checkers, receipts and a replay script, with a SHA-256 manifest. Deposited at https://doi.org/10.5281/zenodo.23284137 (the paper's Data and code paragraph). |
| 4.2 Encoding interface too compressed | New Appendix A: complete clause schemas (C1)–(C10), matched to the generator, and a soundness proposition (every positive generic counterexample satisfies some listed formula). |
| 4.3 Smaller-case dependencies | New Appendix B: registry of all 14 refutations (6, 7 and 8 goods) with variables, clauses, trimmed proof steps, sizes, both checking times and formula hashes; dependency induction stated in the soundness proof. |
| 4.4 Akrami et al. (2026) precedent | New paragraph comparing encodings (subset order vs additive sign rules), verification responsibilities (Lean reduction vs re-derivation of generated files; DRAT vs LRAT checked twice) and what is specific here. |
| 4.5 Section 6 reproducibility | Deletion family identified; annealing caveat added; all instances, scripts, seeds and per-instance results in the bundle (`data/`). |
| Minor 1 AMN pinpoint | Theorem 18 and Corollary 19 of the AAAI version (Theorem 5.1 of the expanded version). |
| Minor 2 zero sign vector | Rules stated for nonzero vectors (as implemented). |
| Minor 3 singleton | Holder's own comparisons stated as remaining obligations. |
| Minor 4 proof difficulty | Inference narrowed. |
| Minor 5 open question | Restated: explain the pair template's failure on 3(a) and find a covering construction. |
| Minor 6 terminology | SAT, CNF, LRAT defined at first use; q stated to be an integer. |
| Minor 7 hashes and versions | Hash prefixes identified as uncompressed `base.cnf`; lrat-check commit pinned; lrat-trim cited. |
| Minor 8 wording | "Two preprints of September 2026 gave nine-good counterexamples." |
| Should: positioning of Proposition 7 | Equivalent form 3 v_c(P) <= v_c(M); new as an existence statement only for q >= 4. |
| Should: sharper Observations 3(a), 3(c) | 3(a): 28 of 36 PMMS allocations have sizes (2,3,3), example given; singleton template inapplicable. 3(c): none of 58 PMMS allocations contains a one-good bundle. |
| Should: verification resources | Checking times for both checkers per certificate in Appendix B, separate from solver times in Table 1. |
