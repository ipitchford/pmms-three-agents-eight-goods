# Assurance and trusted boundary

Unrefereed candidate, version 0.1.0-candidate. Scholarly creator: Anonymous.

## Claim

Theorem 1 of the paper: every instance with three agents, nonnegative additive real valuations and at most eight
indivisible goods admits a complete PMMS allocation (bundles may be empty). With the published nine-good
counterexamples, re-checked here by enumerating all 3^9 allocations, this gives m* = 9. The paper also proves
Proposition 7 (a sufficient condition for PMMS with 3q−1 goods) by hand, and reports computational observations
(Section 6) that are not part of any proof.

It is not a claim about four or more agents, chores, approximate PMMS or non-additive valuations.

## How the claim is supported

| Layer | Evidence | Trusted |
|---|---|---|
| Reduction from fair division to propositional logic | Written argument, Sections 2–4 and Appendix A (clause schemas C1–C10, soundness proposition) | Yes: the text |
| Each formula is what the text says | `verify_case.py` rebuilds every clause from the variable dictionary and the definitions; for the six- and eight-good formulas the rebuilt set equals the formula exactly | Yes: the verifier and Python |
| Each formula is unsatisfiable | LRAT certificate per formula, trimmed (lrat-trim; `tools/lowmem_trim.c` for one certificate), accepted by `lrat-check` (drat-trim commit 2e3b2dc) and by the standard-library checker `check_lrat_rup.py` | Yes: either checker and the C/Python toolchains |
| Smaller cases | Six- and seven-good existence re-proved in the same framework and injected as restriction clauses; no external existence theorem is used | As above |
| Generator behaviour | `controls/`: semantic control (violated allocation clauses = exact PMMS count on random and Gölz-derived matrices) and normal-form control (all four eight-good profiles) | Tests the code only |

The SAT solver (CaDiCaL 3.0.1), the formula generator and the trimming tools are untrusted producers: their outputs
are checked, not assumed.

## Assurance dimensions

| Dimension | State |
|---|---|
| Availability | Zenodo DOI 10.5281/zenodo.23284137; GitHub release; SHA-256 manifest |
| Internal replay | Producer-side replay of every check from the package (`receipts/`), including from a fresh extraction of the published assets |
| Independent rerun | Not established |
| Independent reimplementation | Not established. The clause verifier and the Python LRAT checker were written separately from the generator but by the same producer; `lrat-check` is third-party |
| Formal verification | Not established; the reduction is argued in the text, not formalised |
| Specialist review | Not established |
| Editorial peer review | Not established |
| Environment reproducibility | Standard-library Python and C only for replay; tool versions in `ENVIRONMENT.txt`; no container |

Three adversarial reviews by an OpenAI model (`review/sol_review*.md`) and one external review of the PDF of
unrecorded authorship were received during preparation; all points are dispositioned in `review/`. Neither is
specialist or editorial peer review.

## Priority

Historical priority is claimed only within the recorded literature search of 7–9 October 2026
(`paper/novelty_report.md`, `RESEARCH_GATES.json`), which found no earlier statement of Theorem 1 or Proposition 7.
