## Referee report

I find **no mathematical error in Lemma 3, Lemma 4, Proposition 7, or in the deduction of Theorem 6 from Proposition 7**. The six ordered PMMS comparisons in Proposition 7 are all covered, including ties and zero values. There are, however, several presentation overclaims, one incorrect statement about PMMS and EFX under nonnegative valuations, and a number of computational-observation claims that need qualification.

### 1. Proposition 7 and its proof

#### No gap in the six comparisons

The proof correctly covers all six ordered pairs:

- \(b\) against \(a,c\): two applications of Lemma 4;
- \(a\) against \(c\): the maximin cut of \(R\);
- \(a\) against \(b\): non-envy;
- \(c\) against \(a\): chooser non-envy;
- \(c\) against \(b\): the summation argument.

The potentially delicate step in (ii) is valid. Every unequal split of the \(2q\)-element set \(R\) has a side of size at most \(q-1\), hence that side is worth at most the top-\((q-1)\) sum. Every \(q\)-set is worth at least the bottom-\(q\) sum. Balance therefore shows that an optimal two-way maximin partition can be chosen among the \(q/q\) partitions. Since \(a\) maximizes the smaller side among those partitions, either side left to \(a\) has value at least \(\mu_a(R)\).

The last argument also remains correct with ties and zeros:
\[
v_c(B_c)+v_c(P)>2v_c(B_c)
\quad\Longrightarrow\quad
v_c(P)>v_c(B_c),
\]
contradicting
\[
v_c(B_c)\ge \tfrac12v_c(R)\ge v_c(P).
\]

#### The implication to Theorem 6 is valid

The sentence

> “If \(c\) is also \(q\)-balanced, the hypothesis holds automatically…”

is correct. Since \(P\) has \(q-1\) goods,
\[
v_c(P)\le \text{top-}(q-1)\text{ sum}
 \le \text{bottom-}q\text{ sum}.
\]
The complement \(R\) has \(2q\) goods and can be divided into two \(q\)-sets, each worth at least the bottom-\(q\) sum, so
\[
v_c(R)\ge 2\,\text{bottom-}q\text{ sum}\ge 2v_c(P).
\]
Thus Theorem 6 follows by taking the two balanced agents as \(a\) and \(c\).

#### Misleading description of the proposition

The abstract says:

> “a sufficient condition … that needs only one agent's valuation to be balanced”

and the introduction says:

> “requires only one agent's valuation to be balanced”

These are liable to be read as saying that one balanced agent alone suffices. Proposition 7 also requires the substantial cross-agent inequality
\[
v_c(P)\le \tfrac12v_c(M\setminus P).
\]

**Suggested fix:**

> “a sufficient condition involving one balanced agent together with an additional non-envy inequality for a second agent”

Likewise, the discussion says:

> “Proposition 7 handles every instance with one balanced agent and a non-envious third agent”

This is not the proposition as stated. The hypothesis is the specific pre-cut inequality above, not merely an informally described “non-envious third agent.”

**Suggested fix:**

> “Proposition 7 handles every instance with one balanced agent for which, under a suitable labelling, the second-agent inequality \(v_c(P)\le \frac12v_c(M\setminus P)\) holds.”

#### “Strictly extending” is not demonstrated

The introduction calls Proposition 7

> “strictly extending an earlier two-agent condition.”

It certainly extends Theorem 6, because the two-balanced-agent hypothesis implies Proposition 7’s inequality. Strictness, however, requires an example satisfying Proposition 7 while fewer than two agents are balanced. None is identified as such.

**Suggested fix:** either provide such an example or replace “strictly extending” by “extending.”

#### The explanation after the displayed instance is not a proof

The text says:

> “The other two agents both value the first good above everything else, so each envies the other's top two goods.”

This is imprecise: the agents’ top-two sets overlap in the first good and therefore cannot literally be assigned simultaneously as two disjoint bundles. It also does not establish the exhaustive claim immediately before it.

**Suggested fix:**

> “The two other agents have the same uniquely dominant favourite good, which helps explain why the top-two/cut-and-choose template fails. Exhaustive enumeration verifies the stated claim.”

---

### 2. Lemma 3 and Lemma 4

#### Lemma 3: correct, with a minor hypothesis clarification

The failure-witness characterization is correct. If both sides of a bipartition exceed \(v_i(D)\), neither side can be contained in \(D\), because nonnegativity gives \(v_i(Z)\le v_i(D)\) for every \(Z\subseteq D\). If \(|E|\le1\), one side of any bipartition avoids \(E\), so failure is impossible.

No problem arises from empty parts, zero-valued goods, or ties: the witness inequalities are strict.

For complete precision, the lemma should explicitly say that \(D\) and \(E\) are disjoint, rather than relying on the allocation context.

**Suggested fix:**

> “For disjoint bundles \(D,E\), agent \(i\) holding \(D\) fails…”

#### Lemma 4: correct

The proof is sound. If \(|P\cup B|\le 2k+1\), every bipartition has a side containing at most \(k\) goods. Since \(P\) is a maximum-value \(k\)-set, every set of at most \(k\) goods has value at most \(v_i(P)\). This remains true with ties and zero values.

For clarity, “\(k\) most valuable goods” should be understood as any maximum-value \(k\)-subset when ties occur.

---

### 3. Section 6: observations and computational support

These statements are not part of the proof, but several are currently stronger or less precise than the described computations justify.

#### “Obtained as in Proposition 7” conflicts with “every valuation is unbalanced”

Observation 1 says:

> “In all fifteen, every agent's valuation is unbalanced…”

and then:

> “Each nevertheless has a PMMS allocation … obtained as in Proposition 7.”

Literally, no allocation in such an instance can be obtained *under the hypotheses* of Proposition 7, because that proposition requires a balanced cutter.

Presumably the intended claim is only that the same allocation template works: give one agent her top two goods, let another cut the remaining six into two triples, and let the third choose.

**Suggested fix:**

> “Each nevertheless has a PMMS allocation produced by the same top-two/cut-and-choose template as Proposition 7, although Proposition 7’s balance hypothesis is not satisfied.”

#### The 47% claim needs a denominator and a definition

Observation 2 says:

> “Among instances where three goods dominate every valuation, 47% have no PMMS allocation of sizes \((2,3,3)\).”

“Dominate” is not defined, and “47%” sounds like a population-level statement rather than a statistic about a finite experimental sample. The five family sizes and random distributions are also not given.

**Suggested fix:**

> “Among the \(x\) sampled instances in our explicitly defined ‘three dominant goods’ family, \(y\) (\(47\%\)) had no PMMS allocation of size profile \((2,3,3)\).”

The sampling distribution or generation rule should be stated or referenced.

#### “Either construction above” is undefined

Observation 3(a) says:

> “which has 36 PMMS allocations but none from either construction above.”

There is no formal definition of the second construction, and even the Proposition 7 “construction” can mean either the exact proposition with hypotheses or merely its allocation template.

**Suggested fix:** formally define two named templates before the observations, e.g. “top-two cut-and-choose” and “singleton cut-and-choose,” and use those names consistently.

#### “Worth a third” is numerically inaccurate

Observation 3(c) says:

> “An agent whose best good is worth a third of her total…”

In the displayed instance, the relevant third agent has total value
\[
2727
\]
and best-good value
\[
1045>2727/3=909.
\]
Thus the good is worth **more than** one third, not exactly one third.

**Suggested fix:**

> “An agent whose best good is worth at least one third of her total…”

#### “Independent enumeration” needs the same qualification as the certificate checks

The section says:

> “Every instance quoted is available in machine-readable form and was re-verified by independent enumeration.”

It should say whether this means an implementation independent of the search code, independent authorship, or simply a second run. Elsewhere the paper carefully distinguishes implementation independence from authorship independence.

**Suggested fix:**

> “Every quoted instance was re-enumerated by a separate implementation sharing no code with the search program.”

if that is what happened.

#### The restriction conclusion is too broad

The text says:

> “So the restriction clauses of Section 4 prune; they do not construct.”

The computation shows only that, for three selected instances, an eight-good PMMS allocation cannot be obtained by taking a seven-good PMMS allocation arising as the restriction described. It does not support a general claim that restriction arguments cannot be constructive.

**Suggested fix:**

> “Thus, for these three instances, the particular restriction clauses used in Section 4 act only as pruning constraints and do not directly yield an eight-good allocation.”

The quantifier in

> “after removing some agent's least valuable good”

should also be made explicit: does the claim mean for every agent, or that no agent can be chosen successfully?

#### The nine-good interpretation is unsupported

The text says:

> “three dominant goods among nine leave no agent free to hold one alone.”

The number nine by itself does not prevent an allocation of profile \((1,4,4)\), so this is not a combinatorial consequence. Even as informal interpretation, it requires a specific property of the two counterexamples that has not been stated or measured.

**Suggested fix:** delete this sentence, or replace it by a precise empirical statement about the published counterexamples.

---

### 4. Abstract and introduction

#### The EFX dependency is hidden

The abstract says:

> “The encoding uses only necessary consequences of additivity, together with existence theorems for smaller instances, which are re-proved within the same framework.”

This is false as written. The \((1,2,4)\) certificate additionally uses the external three-agent EFX existence theorem, which is neither a smaller-instance theorem nor re-proved in the paper.

This is especially important because the dependencies paragraph still contains:

> “A certificate for \((1,2,4)\) without the EFX clauses … \textsc{[status to be inserted]}.”

The placeholder must not remain in a submitted version.

**Suggested abstract fix:**

> “The encoding uses necessary consequences of additivity, internally re-certified existence results for six and seven goods, and, in one normal form, the known theorem that EFX allocations exist for three additive agents.”

The introduction should disclose this dependency when first describing the trusted base, not only in Section 5.

#### “Every clause of every formula” is stronger than the body documents

The abstract says:

> “Every clause of every formula is re-derived by a separate verifier…”

The body specifically states:

> “For every eight-good formula the two sets are equal.”

It is therefore unclear whether the same full re-derivation/equality check was performed for the six- and seven-good formulas.

**Suggested fix:** either document that all six-, seven-, and eight-good formulas were checked, or restrict the abstract to “every clause of every eight-good formula.”

#### “Two independent checkers” should be qualified

The paper itself says that the Python checker was written by the same author. Thus the checkers are implementation-independent, not independently authored.

**Suggested fix:**

> “checked by two implementation-independent checkers”

This is still a meaningful and accurate claim.

#### The displayed hashes are not full SHA-256 digests

The table column is headed:

> “CNF SHA-256”

but entries such as `d12fc3bf2fa4` contain only 12 hexadecimal characters. These are SHA-256 prefixes, not SHA-256 digests.

**Suggested fix:** label the column “SHA-256 prefix” or print the full 64-character digests.

#### “Published” is questionable for arXiv preprints

The abstract says:

> “two independent nine-good counterexamples were published in September 2026”

while the bibliography lists arXiv manuscripts. Unless these appeared in formal venues, “posted” or “circulated as preprints” is more accurate.

Likewise:

> “In September 2026 three papers settled…”

would be safer as “three preprints established…”

---

### 5. Misleading or incorrect literature statements

#### PMMS does not imply EFX for general nonnegative valuations

The introduction says:

> “PMMS implies envy-freeness up to any good…”

Under the paper’s allowance of zero-valued goods, this is false for the usual EFX definition.

For example, let an agent’s own bundle have value \(10\), and let the other bundle consist of goods worth \(11\) and \(0\). The two-way MMS of the union is \(10\): partition it as the \(11\)-valued good versus the own bundle plus the zero-valued good. Hence the agent satisfies PMMS. But after removing the zero-valued good from the other bundle, she still sees value \(11>10\), so EFX fails.

The implication is valid under strictly positive item values, which is enough after the genericity reduction, but not for the full nonnegative model stated in the theorem.

**Suggested fix:**

> “For strictly positive additive valuations, PMMS implies EFX.”

Alternatively, specify the weaker EFX convention being used if zero-valued removals are excluded.

#### The AMN citation should identify the exact result

The sentence

> “Existence for \(m\le n+2\), here five goods, follows from Amanatidis, Markakis and Ntokos…”

should cite a theorem or corollary number and briefly explain the implication to PMMS. The cited paper’s title concerns approximation guarantees for EFX and GMMS, so the exact route to the claimed PMMS result is not transparent.

I do not assert that the claim is false, but in its present form it is bibliographically under-supported.

#### Unpublished prior work

The sentence

> “Theorem 6 appeared in unpublished work preceding this paper.”

is not independently checkable without a citation, date-stamped manuscript, or archived source. Either provide one or soften/delete the priority statement.

---

## Bottom line

- **No mathematical error found in Lemma 3, Lemma 4, Proposition 7, or Proposition 7’s implication of Theorem 6.**
- The most important substantive correction is the false unqualified statement that **PMMS implies EFX under nonnegative valuations**.
- The abstract must disclose that the \((1,2,4)\) case relies on the external three-agent EFX theorem.
- Section 6 needs clearer definitions, sample counts, and narrower wording.
- The unresolved status placeholder and the truncated “SHA-256” labels must be fixed before publication.