## Fatal issues

1. **Location:** Section 4.2; Sections 5–6.  
   **Failure scenario:** The eight-good run data, CNFs, hashes, proof sizes, and checker results are literally absent: “TO BE FILLED FROM RUN RECORDS.” No eight-good UNSAT certificate is supplied in the material presented. Thus the asserted Boolean refutations cannot be checked, and the theorem does not currently follow from the draft.  
   **Severity:** **Fatal to the current paper/evidence claim.**

2. **Location:** `cases.py`, `build_case(..., efx=True, ...)`; Sections 3.4 and 5.  
   **Failure scenario:** Every case built with the shown defaults includes `enc.add_efx_lemma()`. The paper says the primary certificate does not use EFX, but the supplied normalisation encoder does use it by default. Running `build_case(m, case)` therefore produces the optional EFX-dependent formula, not the claimed primary formula. The replay instructions do not show generation flags or otherwise establish that archived `base.cnf` files were generated with `efx=False`.  
   **Severity:** **Fatal to the claimed dependency audit unless the actual CNFs and generation commands show `efx=False`; otherwise needs repair if the paper is changed to admit the EFX dependency.**

## Clause-family and encoding issues

3. **Location:** Section 3.3 versus `failure_lit`.  
   **Failure scenario:** For a partition
   \[
   X=S_1\cup T_1,\qquad Y=S_2\cup T_2,
   \]
   the correct tests are
   \[
   v(S_1)>v(T_2),\qquad v(S_2)>v(T_1).
   \]
   The code instead uses `a = sign(S1,T1)` and `b = sign(S2,T2)`. The existential disjunction is still equivalent because the code ranges over every split of \(D\), and replacing \(T_1\) by its complement swaps the labels. But an individual `wit(agent,S1,T1,S2,T2)` does **not** have the mathematical meaning stated in the prose. A verifier that claims to rederive each witness according to the displayed partition would reject the code or silently reproduce the same naming error.  
   **Concrete pattern:** \(D=\{d_1,d_2\}\) with values \(100,1\), and \(E=\{e_1,e_2\}\) with values \(101,2\). The genuine witness \(X=\{e_1,d_2\}\), \(Y=\{e_2,d_1\}\) satisfies \(101>100\) and \(2>1\), while the code tests \(101>1\) and \(2>100\) for that same named split.  
   **Severity:** **Needs repair in the specification/verifier semantics; not by itself fatal to the existential \(F\)-encoding.**

4. **Location:** Section 3.3, sentence “more precisely \(v_i(S_1)>v_i(T_2\setminus\ldots)\).”  
   **Failure scenario:** The expression is malformed and never defines the exact two atoms used by the CNF. Since the proof depends on exact clause rederivation, an ellipsis in the central equivalence is not acceptable.  
   **Severity:** **Needs repair.**

5. **Location:** Section 3.4 EFX lemma; `add_efx_lemma`.  
   **Failure scenario:** The selector ranges only over allocations with three nonempty bundles, while a generic EFX existence theorem is usually stated over complete allocations without that extra restriction. For the present positive eight-good setting, an EFX allocation cannot have an empty bundle: an empty agent would require every opponent bundle to have at most one good, impossible with eight goods. That argument is absent. Without strict positivity, the restriction would be invalid.  
   **Severity:** **Needs repair if EFX is used.**

6. **Location:** `add_efx_lemma` documentation.  
   **Failure scenario:** It cites “Chaudhury, Garg, Mehlhorn 2020,” while the paper cites the 2024 JACM result. This makes it unclear which exact theorem, including completeness and valuation assumptions, is injected.  
   **Severity:** **Cosmetic bibliographically, but needs repair in the dependency specification.**

## Normalisation gaps

7. **Location:** Section 3.5 step 2; `cases.py` module comment.  
   **Failure scenario:** The paper chooses \(B\) by first maximizing \(v_a(B_a)\), then choosing a Pareto-maximal allocation among the maximizers. The code comment instead says only “choose one that is Pareto maximal” and even mentions “maximise sum of own values.” Those are not the same selection rule. The clauses actually include both global Pareto maximality and conditional own-value maximality, so the mathematical argument can work, but the stated executable normalisation is inconsistent across the paper and code.  
   **Severity:** **Needs repair.**

8. **Location:** Section 3.5, claim that the selected \(B\) is globally Pareto maximal.  
   **Failure scenario:** The selection only explicitly gives Pareto maximality among allocations attaining the maximum \(v_a(B_a)\), whereas the formula excludes domination by every PMMS allocation. This implication needs proof: if \(C\) weakly dominates \(B\), maximality of \(B_a\) forces \(v_a(C_a)=v_a(B_a)\); genericity then forces \(C_a=B_a\), so \(C\) belongs to the tie class and contradicts the second selection. The draft does not state this argument.  
   **Severity:** **Needs repair.**

9. **Location:** Section 3.5 step 3, especially the reproduced seven-good \((2,2,2)\) case.  
   **Failure scenario:** With three equal-sized bundles there is no single ordinary sorting key: the comparison between two bundles is made using the third agent, which changes with the permutation. The code imposes
   \[
   v_2(B_0)<v_2(B_1),\qquad v_0(B_1)<v_0(B_2).
   \]
   The draft merely says to “order them” and gives no combinatorial argument that some permutation satisfies both context-dependent inequalities. Such an argument appears possible, but it is missing; a conventional sort does not establish it.  
   **Severity:** **Needs repair**, principally for the claimed independent seven-good reproving chain.

10. **Location:** Section 3.5 step 3.  
    **Failure scenario:** “Swapping the two agents together with their bundles is a symmetry of everything chosen so far” is asserted without tracking the distinguished agent \(a\). If \(a\) is one of the swapped agents, the least-good and own-maximality properties must move with its label. The selector \(c_i\) does allow this, but the prose must explicitly say that the distinguished-agent designation is relabelled as well.  
    **Severity:** **Needs repair.**

11. **Location:** Section 3.5 and the random canonicalisation control.  
    **Failure scenario:** Sixteen random trials do not prove that every generic counterexample can be canonicalised or that every canonical clause is valid. Rare tie-profile/orientation failures would not be excluded by random testing.  
    **Severity:** **Needs repair in presentation; the tests are not proof evidence for normalisation.**

12. **Location:** `cases.py` module description versus actual formula.  
    **Failure scenario:** The comment says \(B\) is selected as Pareto maximal by “maximise sum of own values,” but the code does not encode sum maximisation. It encodes nondomination plus, under a least-agent selector, maximisation of one agent’s bundle. A reviewer cannot infer the intended normalisation from the executable description.  
    **Severity:** **Needs repair.**

## Injected theorem issues

13. **Location:** Appendix A, proof of Theorem A.1.  
    **Failure scenario:** The proof shows that a balanced \(q\)-versus-\(q\) partition attains \(c_1\)’s true maximin value, but then says \(c_1\) “chooses a bipartition maximising her minimum.” An unbalanced partition may tie for the maximum. The later assertion that both controlled agents receive exactly \(q\) goods then need not follow.  
    **Concrete scenario:** Equality in  
    \[
    \text{top-}(q-1)=\text{bottom-}q
    \]
    can allow both balanced and unbalanced optimum partitions. Choosing an unbalanced optimum can leave one controlled agent fewer than \(q\) goods, invalidating the bottom-\(q\) argument. The construction must explicitly choose a balanced maximizing partition.  
    **Severity:** **Needs repair; the theorem appears repairable.**

14. **Location:** Section 3.4 and Appendix A, use of the cardinality theorem.  
    **Failure scenario:** The CNF encodes, for each pair of agents, that at least one has some disjoint \((q-1)\)-set \(P\) and \(q\)-set \(T\) with \(v(P)>v(T)\). This is the contrapositive only after proving
    \[
    \text{top-}(q-1)\le\text{bottom-}q
    \iff
    v(P)<v(T)\ \text{for every disjoint }P,T
    \]
    in the positive generic setting. The appendix sketches this for \(q=3,m=8\), but the clause verifier must use precisely that restricted equivalence, not a broader unstated theorem.  
    **Severity:** **Needs repair/documentation; no concrete false clause found for \(m=8\).**

15. **Location:** Restriction lemmas, Appendix B.  
    **Failure scenario:** The dummy-good argument establishes a nonempty allocation only because all original goods are strictly positive for every agent and \(|W|\ge4\). If the restriction clauses were reused before perturbation, or for merely nonnegative rows, deletion of dummy goods could leave an empty bundle without the stated contradiction. The proof order must be: perturb first, then invoke these nonempty restriction selectors.  
    **Severity:** **Needs repair in dependency ordering; valid under the stated positive-generic normalisation.**

16. **Location:** Sections 4.1 and 5, dependency on the seven-good theorem.  
    **Failure scenario:** The eight-good restriction clauses are sound only if the reproduced seven-good proof is itself complete. That reproduced proof uses the same normalisation code, including the unresolved equal-size \((2,2,2)\) orientation argument, and—under the shown defaults—the EFX lemma. Thus the claimed dependency chain “six, seven, cardinality only” is not established by the supplied code.  
    **Severity:** **Fatal to the claimed dependency chain unless the archived seven-good CNFs and missing normalisation proof resolve it.**

## Boolean abstraction and verification risks

17. **Location:** Section 5.2, “checks that every clause belongs to the re-derived set.”  
    **Failure scenario:** A second program that reproduces the same incorrect mathematical translation is not independent validation. This is particularly material for the swapped \(T_1/T_2\) witness naming and the normalisation selectors. Clause-set equality proves consistency between two implementations, not semantic validity.  
    **Severity:** **Needs repair in the verification claim.**

18. **Location:** Section 5.2.  
    **Failure scenario:** Checking that each CNF clause belongs to an allowed set does not by itself verify that variable dictionary entries have unique, consistent meanings, that all literals use the intended polarity, or that selector/auxiliary variables are fresh and not aliased. The draft says meanings are recomputed but supplies no verifier code here, so these properties cannot be assessed.  
    **Severity:** **Residual fatal verification risk until the evidence bundle is available.**

19. **Location:** Section 3.2 sign abstraction.  
    **Failure scenario:** The abstraction is sound for refutation only if every real normalized counterexample extends to values of all auxiliary variables satisfying the defining clauses. This requires exact correctness of every `F`, witness, restriction, EFX, Pareto, and maximum-selector clause. The fact that the sign rules are merely necessary is harmless, but it does not protect against one overstrong injected or normalisation clause.  
    **Severity:** **Conceptual warning; no defect in using a necessary-only sign abstraction itself.**

20. **Location:** Section 5.3.  
    **Failure scenario:** LRAT checking proves only that the archived CNF is inconsistent. It does not establish that the CNF corresponds to the formula described in the paper. Given the default-EFX mismatch and missing eight-good artifacts, the certificate layer cannot currently close that gap.  
    **Severity:** **Fatal to the current evidence claim.**

## Points that appear valid but need clearer justification

- Omitting empty-bundle complete allocations is valid after perturbation to strictly positive values: an empty agent must face an opponent with at least two goods and therefore has positive two-way maximin share.
- The failure encoding’s swapped \(D\)-part labels preserve the existential failure predicate, but only after an explicit complement-renaming argument.
- Maximizing the distinguished agent’s bundle and then taking a Pareto-maximal tie winner can imply the global Pareto clauses, but the missing genericity argument must be written.
- The cardinality CNF is the correct contrapositive for positive generic eight-good rows, assuming Appendix A is repaired to choose a balanced optimum.

**Conclusion:** The draft does not presently constitute a sound completed proof. The strongest problems are the absent eight-good certificates/run records, the fact that the shown case generator injects EFX despite the claimed primary dependency set, and the unresolved dependency of the seven-good reproving chain on the same code and normalisation details. No independently checkable basis is supplied here for asserting that the four advertised primary formulas were actually generated and refuted.