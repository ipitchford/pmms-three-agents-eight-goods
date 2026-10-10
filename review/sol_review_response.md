# Response to Sol's adversarial review (7 October 2026)

Reviewer: gpt-5.6-sol via /v1/responses, prompted to refute. Each finding was checked against the
code and run records before acting. Verdict tags: CONFIRMED (real defect, repaired), PROSE (the text
was wrong, the artefacts were right), PENDING (depends on results not yet available), REJECTED.

| # | Finding | Verdict | Action |
|---|---|---|---|
| 1 | Eight-good certificates absent from the draft | PENDING | Section 4.2 is filled from run records when the solvers finish; the bundle ships the CNFs, proofs and receipts. |
| 2 | `build_case` injects EFX by default while the paper claims a lean primary certificate | CONFIRMED | `build_case_cnf.py` now records generation flags in `build_info.json`; the lean seven-good formulas were built with `noefx noamax` and are byte-identical to the originally refuted formulas (SHA-256 recorded). The eight-good runs in progress use EFX; the paper will state the dependency set of whichever variant is shipped, and lean eight-good runs are scheduled after the EFX runs. |
| 3 | Witness quadruple naming disagrees with the prose | PROSE | The encoder and the independent verifier both use S_1 = X∩E, T_1 = D∖X, S_2 = Y∩E, T_2 = D∖Y; Section 3.3 was rewritten to state exactly this. |
| 4 | Malformed sentence in 3.3 | CONFIRMED | Rewritten. |
| 5 | EFX selectors restricted to nonempty bundles without argument | CONFIRMED | Argument added (positive instance, ≥ 4 goods). |
| 6 | Citation year of the EFX theorem | CONFIRMED | Docstring and paper now cite JACM 71(1) 2024, Theorem 1.1, with EC 2020 as the conference version. |
| 7, 12 | Selection rule stated inconsistently between paper and code comment | CONFIRMED | `cases.py` docstring rewritten to the two-stage rule. |
| 8 | Global Pareto clause needs the genericity argument | CONFIRMED | Lemma 5 added. |
| 9 | Two simultaneous tie-breaks in the (2,2,2) case lack a proof | CONFIRMED | Lemma 4 added (path of length two in the preference map). The eight-good cases use at most one tie-break. |
| 10 | Designation of agent a under relabelling | CONFIRMED | Step 3 now says the designation is carried along; the selector c_i absorbs it. |
| 11 | Random controls are not proof | CONFIRMED | Stated explicitly. |
| 13 | Appendix A must choose a balanced maximin partition | CONFIRMED | Proof corrected; the memorandum's original proof already used a q-versus-q partition. |
| 14 | Equivalence top-heavy ⇔ ∃(P,T) must be stated | CONFIRMED | Stated in Appendix A for m ≥ 5. |
| 15 | Perturb before using nonempty restriction selectors | CONFIRMED | Stated at the head of Section 3.5. |
| 16 | Seven-good chain depends on EFX and the (2,2,2) argument | CONFIRMED in part | Lean seven-good certificates (no EFX, no own-value clauses) exist and are verified; Lemma 4 closes the (2,2,2) argument. |
| 17 | A second program by the same author is not independent | CONFIRMED | Stated in Section 5; the verifier is in the bundle for inspection. |
| 18 | Dictionary uniqueness and polarity | CONFIRMED | Verifier now rejects duplicate meanings; polarity is recomputed by the verifier from vectors, never read from the generator. |
| 19 | Over-strong injected clause would break soundness | REJECTED as a defect; accepted as a risk statement | This is exactly why Section 3 proves each family valid. |
| 20 | LRAT proves only inconsistency of the archived CNF | CONFIRMED | Hence the clause verifier; stated in Section 5. |


# Response to Sol's second pass (9 October 2026)

Verdict: no fatal mathematical gap; four presentation defects, all CONFIRMED and repaired.

| # | Finding | Action |
|---|---|---|
| 1 | Two-checker claim contradicted by the running Python check on (2,2,3)/agent 3 | Abstract, status line and Section 5 now say the C checker accepted every certificate and the Python checker all but the last-completed one at the time of writing; the table is the source of truth and is updated when the check finishes. |
| 2 | Section 5 called the EFX variant optional | Reworded: the fast variant is part of the proof through profile (1,2,4) until a lean certificate exists. |
| 3 | Abstract understated the dependency set | Abstract now names genericity, the six- and seven-good theorems, the cardinality theorem, and EFX for one profile. |
| 4 | "Fixing the distinguished agent" overstates the selector unit | Reworded: the unit clause asserts that agent i satisfies the selector conditions; refuting F ∧ c_i for each i covers F ∧ (c_1 ∨ c_2 ∨ c_3). |
| residual | Which formulas had exact verifier/CNF set equality | Stated explicitly in Section 5 (all eight-good formulas exact; lean seven-good differ only by unused own-value clauses). |

# Response to the third pass (9 October 2026): new content of the typeset paper

No mathematical error was found in Lemmas 3–4, Proposition 7, or the derivation of Theorem 6. All presentation
points were checked against the data and acted on:

| Finding | Action |
|---|---|
| "PMMS implies EFX" is false with zero-valued goods | Restricted to positive valuations (the reviewer's example is correct). |
| Abstract hid the EFX dependency of one normal form | Abstract and introduction now state it. |
| "Strictly extending" not demonstrated | Explicit instance added: one balanced agent, Proposition 7 applies, Theorem 6 does not. |
| Abstract claimed every formula re-derived; body documented only eight goods | The six-good formula was then put through the verifier (new plain mode): exact equality. Body now states the six-, seven- and eight-good results. |
| Section 6 wording, denominators, undefined constructions, "a third", restriction claim, nine-good interpretation | Families defined with sizes and distributions; two named templates; "at least a third"; restriction claim scoped to the three instances and every agent; nine-good sentence removed. |
| Truncated digests labelled SHA-256 | Column relabelled "SHA-256 prefix"; full digests are in the bundle manifest. |
| "Published" for preprints; AMN citation; unpublished priority | "Posted as preprints"; Theorem 5.1 cited with the GMMS ⇒ PMMS step; memorandum cited. |
| Placeholder for the (1,2,4) status | Replaced by the current state; updated when the lean certificate completes. |
