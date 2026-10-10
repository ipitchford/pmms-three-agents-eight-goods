# Introduction

An allocation of indivisible goods is *pairwise maximin share fair* when, for every two agents, each values her own bundle at least as much as the best worst-part she could guarantee by splitting the two bundles’ union into two parts herself . For positive additive valuations PMMS implies envy-freeness up to any good, and for some time its existence for additive valuations was open. In September 2026 three preprints settled the general question negatively: Aziz gave a four-agent instance, and Gölz and Bei, Lin, Liu, Luan and Tao gave three-agent instances with nine goods. Gölz remarks that, having found no counterexample with three agents and at most eight goods, he believes nine to be minimal or almost minimal.

Write $`m^\star`$ for the least number of goods admitting a three-agent counterexample. Existence for $`m\le n+2`$, here five goods, follows from Theorem 18 and Corollary 19 of Amanatidis, Markakis and Ntokos (Theorem 5.1 of the expanded version), since their groupwise maximin share allocations are in particular PMMS, and a certified computation extended it to seven goods , so $`m^\star\in\{8,9\}`$. This paper proves:

<div id="thm:main" class="theorem">

**Theorem 1**. *Every instance with three agents, nonnegative additive valuations and at most eight goods admits a complete PMMS allocation.*

</div>

<div class="corollary">

**Corollary 2**. *$`m^\star = 9`$.*

</div>

The corollary follows from Theorem <a href="#thm:main" data-reference-type="ref" data-reference="thm:main">1</a> and either nine-good counterexample, both re-verified here by exhaustive enumeration of all $`3^9`$ complete allocations.

The proof of Theorem <a href="#thm:main" data-reference-type="ref" data-reference="thm:main">1</a> is computer-assisted. A hypothetical counterexample is translated into propositional formulas in conjunctive normal form (CNF); a satisfiability (SAT) solver shows that none of them can be satisfied and emits a certificate in the LRAT format, a proof format with explicit hints that a short program can check . The design aims at a small trusted base: the reduction from fair division to propositional logic is argued in full in Section <a href="#sec:reduction" data-reference-type="ref" data-reference="sec:reduction">4</a>, the formulas are rebuilt from their mathematical definitions by a verifier that shares no code with the generator, and the propositional refutations are certificates in the LRAT format, which a short unit-propagation checker validates. Section <a href="#sec:certificates" data-reference-type="ref" data-reference="sec:certificates">5</a> records each certificate, its checks and its dependencies; Appendix <a href="#app:clauses" data-reference-type="ref" data-reference="app:clauses">8</a> lists every clause schema, and Appendix <a href="#app:registry" data-reference-type="ref" data-reference="app:registry">9</a> every certificate.

The closest methodological precedent is the work of Akrami, Mayorov, Mehlhorn, Srinivas and Weidenbach , who use SAT solving to show that EFX allocations exist for three agents and seven goods under monotone valuations, and to find counterexamples for more goods. Their encoding records an order on subsets, which suits monotone valuations; the encoding here records signs of $`\{-1,0,1\}`$-combinations of an additive valuation, which lets additivity enter as the addition and halving rules of Section <a href="#sec:reduction" data-reference-type="ref" data-reference="sec:reduction">4</a>. They formalise the mathematical reduction in Lean, while their generator code is unverified, and check DRAT proofs with drat-trim. Here the reduction is argued in the text and not formalised, but the generated files themselves are re-derived clause by clause by an independent verifier, and the proofs are LRAT certificates checked twice. The two approaches are complementary. What is specific to this paper is the PMMS threshold, the use of the smaller existence theorems and of Theorem <a href="#thm:card" data-reference-type="ref" data-reference="thm:card">6</a> as injected clauses, and the normal form of Section <a href="#sec:reduction" data-reference-type="ref" data-reference="sec:reduction">4</a>.

Two smaller contributions are of independent interest. Section <a href="#sec:sufficient" data-reference-type="ref" data-reference="sec:sufficient">3</a> proves a sufficient condition for PMMS with $`3q-1`$ goods (Proposition <a href="#prop:onerow" data-reference-type="ref" data-reference="prop:onerow">7</a>) that involves one balanced agent and a non-envy inequality for a second agent, strictly extending an earlier condition that needed two balanced agents. Section <a href="#sec:structure" data-reference-type="ref" data-reference="sec:structure">6</a> reports what the hardest eight-good instances look like, and records explicit instances refuting three natural statements that would have given a human-readable proof. They show that the constructions tested do not suffice on their own; they say nothing about how hard a structural proof would be.

# Preliminaries

Let $`N=\{1,2,3\}`$ be the agents and $`M`$ a finite set of $`m`$ goods. Agent $`i`$ has an additive valuation $`v_i`$ with $`v_i(g)\ge 0`$ for each good $`g`$. A *complete allocation* $`A=(A_1,A_2,A_3)`$ is an ordered partition of $`M`$; bundles may be empty. For $`U\subseteq M`$ let
``` math
\mu_i(U)=\max_{T\subseteq U}\ \min\{v_i(T),\,v_i(U\setminus T)\}.
```
The allocation is PMMS if $`v_i(A_i)\ge \mu_i(A_i\cup A_j)`$ for all ordered pairs $`i\ne j`$. We say agent $`i`$ *satisfies PMMS against* bundle $`E`$ when holding $`D`$ if $`v_i(D)\ge\mu_i(D\cup E)`$.

<div id="lem:witness" class="lemma">

**Lemma 3** (failure witnesses). *For disjoint bundles $`D`$ and $`E`$, agent $`i`$ holding $`D`$ fails PMMS against $`E`$ if and only if $`D\cup E`$ has a bipartition $`X\mid Y`$ with $`v_i(X)>v_i(D)`$ and $`v_i(Y)>v_i(D)`$. In any such bipartition both $`X`$ and $`Y`$ meet $`E`$. In particular an agent never fails against an empty or one-good bundle.*

</div>

<div class="proof">

*Proof.* The maximum defining $`\mu_i`$ exceeds $`v_i(D)`$ exactly when one of its candidate minima does, which happens exactly when both parts of that bipartition exceed $`v_i(D)`$. A part contained in $`D`$ is worth at most $`v_i(D)`$. If $`|E|\le 1`$, some part avoids $`E`$ and lies in $`D`$. ◻

</div>

<div id="lem:topk" class="lemma">

**Lemma 4** (top-$`k`$ protection). *If $`P`$ is a set of $`k`$ goods of maximum value to agent $`i`$ among all $`k`$-sets, and $`|P\cup B|\le 2k+1`$ for a disjoint bundle $`B`$, then $`i`$ holding $`P`$ satisfies PMMS against $`B`$.*

</div>

<div class="proof">

*Proof.* Every bipartition of $`P\cup B`$ has a part with at most $`k`$ goods, worth to $`i`$ at most $`v_i(P)`$. ◻

</div>

<div id="lem:generic" class="lemma">

**Lemma 5** (genericity). *If some instance on $`m`$ goods has no complete PMMS allocation, then so does an instance on the same goods in which every value is positive and, for each agent, distinct subsets have distinct values.*

</div>

<div class="proof">

*Proof.* Choose one witness from Lemma <a href="#lem:witness" data-reference-type="ref" data-reference="lem:witness">3</a> for each of the finitely many complete allocations. The chosen strict inequalities persist on an open neighbourhood of the valuation matrix. That neighbourhood contains positive matrices avoiding the finitely many hyperplanes $`r\cdot v_i=0`$, $`r\in\{-1,0,1\}^m\setminus\{0\}`$. ◻

</div>

Adding goods worth zero to every agent, or deleting them, changes no own value and no two-way maximin share. Hence existence for exactly $`m`$ goods implies existence for fewer goods.

# Sufficient conditions with a human proof

For an integer $`q\ge2`$, call agent $`i`$’s valuation *$`q`$-balanced* if her $`q-1`$ most valuable goods together are worth at most her $`q`$ least valuable goods together. For eight goods ($`q=3`$) this says that her top two goods are worth at most her bottom three.

<div id="thm:card" class="theorem">

**Theorem 6**. *Let three agents divide $`3q-1`$ goods, $`q\ge 2`$. If two agents have $`q`$-balanced valuations, a complete PMMS allocation exists for every valuation of the third.*

</div>

Theorem <a href="#thm:card" data-reference-type="ref" data-reference="thm:card">6</a> is due to earlier unpublished work . It is the case $`v_c`$ balanced of the following stronger statement, which needs only one balanced agent.

<div id="prop:onerow" class="proposition">

**Proposition 7**. *Let three agents divide $`3q-1`$ goods, $`q\ge2`$, and let agent $`a`$ have a $`q`$-balanced valuation. Suppose that for some labelling $`\{b,c\}`$ of the other two agents, with $`P`$ the set of $`b`$’s $`q-1`$ most valuable goods,
``` math
v_c(P)\ \le\ \tfrac12\, v_c(M\setminus P).
```
Then a PMMS allocation exists. One is obtained by giving $`P`$ to $`b`$, letting $`a`$ cut $`R=M\setminus P`$ into two parts of $`q`$ goods each so as to maximise her smaller part, and letting $`c`$ take the part she prefers.*

</div>

<div class="proof">

*Proof.* Let $`B_c`$ be $`c`$’s chosen part and $`B_a`$ the other. We check the six comparisons.

1.  *$`b`$ against $`a`$ and $`c`$.* Each union $`P\cup B`$ has $`2q-1`$ goods, so Lemma <a href="#lem:topk" data-reference-type="ref" data-reference="lem:topk">4</a> applies with $`k=q-1`$.

2.  *$`a`$ against $`c`$.* A bipartition of $`R`$ into parts of unequal size has a part of at most $`q-1`$ goods, worth to $`a`$ at most her top-$`(q-1)`$ sum. Both parts of a $`q/q`$ bipartition are worth at least her bottom-$`q`$ sum, which is at least as large by balance. So $`a`$’s best $`q/q`$ split attains $`\mu_a(R)`$, and $`v_a(B_a)\ge\mu_a(B_a\cup B_c)`$.

3.  *$`a`$ against $`b`$.* $`v_a(B_a)`$ is at least $`a`$’s bottom-$`q`$ sum, hence at least her top-$`(q-1)`$ sum, hence at least $`v_a(P)`$. An agent who does not envy a bundle satisfies PMMS against it.

4.  *$`c`$ against $`a`$.* $`c`$ chose first, so she does not envy $`B_a`$.

5.  *$`c`$ against $`b`$.* If $`B_c\cup P`$ had a bipartition with both parts worth more than $`v_c(B_c)`$ to $`c`$, adding the two inequalities would give $`v_c(P)>v_c(B_c)`$. But $`v_c(B_c)\ge \tfrac12 v_c(R)\ge v_c(P)`$.

 ◻

</div>

If $`c`$ is also $`q`$-balanced, the hypothesis holds automatically: $`v_c(P)`$ is at most $`c`$’s top-$`(q-1)`$ sum, which is at most her bottom-$`q`$ sum, and $`R`$ contains two disjoint $`q`$-sets, so $`v_c(R)`$ is at least twice that sum. This gives Theorem <a href="#thm:card" data-reference-type="ref" data-reference="thm:card">6</a>. The hypothesis of Proposition <a href="#prop:onerow" data-reference-type="ref" data-reference="prop:onerow">7</a> is equivalent to $`3v_c(P)\le v_c(M)`$. For $`q=2`$ (five goods) existence is already known , and for $`q=3`$ (eight goods) Theorem <a href="#thm:main" data-reference-type="ref" data-reference="thm:main">1</a> gives it in general, so the proposition then adds an explicit construction; as an existence statement it is new for $`q\ge4`$, that is, for $`11, 14, 17,\dots`$ goods. The extension of Theorem <a href="#thm:card" data-reference-type="ref" data-reference="thm:card">6</a> is strict: in the instance
``` math
\begin{pmatrix}789&591&645&327&110&577&427&403\\731&986&303&679&240&91&658&847\\673&844&887&893&892&629&595&641\end{pmatrix}
```
only the third agent is $`3`$-balanced, so Theorem <a href="#thm:card" data-reference-type="ref" data-reference="thm:card">6</a> does not apply, while Proposition <a href="#prop:onerow" data-reference-type="ref" data-reference="prop:onerow">7</a> applies with $`a`$ the third agent, $`b`$ the first and $`c`$ the second: $`P`$ consists of the first and third goods, $`v_c(P)=1034`$ and $`v_c(M\setminus P)=3501`$.

<div class="remark">

*Remark 8*. For eight goods, a counterexample must therefore have at least two agents whose valuation is not $`3`$-balanced. That is, each of them has two goods worth more than some three disjoint goods. This consequence is used in the encoding of Section <a href="#sec:reduction" data-reference-type="ref" data-reference="sec:reduction">4</a>.

</div>

The non-envy condition in Proposition <a href="#prop:onerow" data-reference-type="ref" data-reference="prop:onerow">7</a> cannot simply be dropped for this construction. The instance
``` math
\begin{pmatrix}
72&80&72&76&75&65&57&80\\
1123&70&99&7&136&32&144&80\\
946&92&26&54&42&170&28&21
\end{pmatrix}
```
(rows are agents) has a $`3`$-balanced first agent, yet exhaustive enumeration shows that no allocation built as in the proposition is PMMS, for any choice of roles. The two other agents have the same, strongly preferred, favourite good, which is the situation the inequality excludes. The instance still has 30 PMMS allocations, as Theorem <a href="#thm:main" data-reference-type="ref" data-reference="thm:main">1</a> requires.

# Reduction to propositional logic

By Lemma <a href="#lem:generic" data-reference-type="ref" data-reference="lem:generic">5</a> it suffices to refute positive generic counterexamples on eight goods.

## Sign variables

For each agent $`i`$ and nonzero $`r\in\{-1,0,1\}^M`$ let $`p_{i,r}`$ be the truth value of $`r\cdot v_i>0`$; the comparison $`v_i(S)>v_i(T)`$ for disjoint $`S,T`$ is $`p_{i,\mathbf 1_S-\mathbf 1_T}`$. The following rules are necessary consequences of positivity, genericity and additivity:

- $`p_{i,-r}=\lnot p_{i,r}`$, implemented by representing $`r`$ and $`-r`$ by opposite literals of one variable;

- $`p_{i,r}`$ is true if $`r\ge0`$ and false if $`r\le0`$;

- $`p_{i,r}\wedge p_{i,s}\to p_{i,r+s}`$ whenever $`r`$, $`s`$ and $`r+s`$ are nonzero vectors in $`\{-1,0,1\}^M`$, and $`p_{i,r}\wedge p_{i,s}\to p_{i,t}`$ whenever $`r+s=2t`$ with $`r`$, $`s`$, $`t`$ nonzero.

These rules do not characterise additive valuations: a Boolean assignment satisfying them need not be realised by real numbers. That is harmless for a refutation, which only uses the fact that every real counterexample yields a Boolean model.

## Failure and allocation clauses

For agent $`i`$, own bundle $`D`$ and opposing bundle $`E`$, a bipartition $`X\mid Y`$ of $`D\cup E`$ corresponds to the quadruple $`S_1=X\cap E`$, $`T_1=D\setminus X`$, $`S_2=Y\cap E`$, $`T_2=D\setminus Y`$, and it witnesses failure exactly when $`v_i(S_1)>v_i(T_1)`$ and $`v_i(S_2)>v_i(T_2)`$. Each witness is a conjunction of two sign atoms, and a failure variable $`F_{i,D,E}`$ is defined as the disjunction of its witnesses; it is the constant false when $`|E|\le1`$. Every complete allocation with three nonempty bundles contributes the clause stating that one of its six failure variables is true. Allocations with an empty bundle need no clause: with positive values, the agent holding nothing faces an opponent holding at least two goods and fails against it.

## Injected theorems

Three families of clauses encode theorems that a counterexample cannot escape.

- *Restriction.* For every $`W\subset M`$ with $`4\le|W|\le7`$, the sub-instance on $`W`$ has a PMMS allocation with three nonempty bundles. This is the existence theorem for at most seven goods, re-proved below. Deleting zero-valued dummy goods cannot empty a bundle here, because an agent with nothing would face a bundle of at least two positive goods. The clauses use one selector per candidate allocation of $`W`$.

- *Cardinality.* By Theorem <a href="#thm:card" data-reference-type="ref" data-reference="thm:card">6</a>, for each pair of agents one of them has two goods worth more than some three disjoint goods. This gives three clauses.

- *EFX (replications only).* Chaudhury, Garg and Mehlhorn prove that an EFX allocation exists for three additive agents; for positive values and at least four goods its bundles are nonempty. Clauses encoding this were used in replication certificates but in none of the certificates that prove Theorem <a href="#thm:main" data-reference-type="ref" data-reference="thm:main">1</a>.

## Normal form

Fix a positive generic counterexample on eight goods and an agent $`a`$. Let $`g`$ be $`a`$’s least valuable good and $`W=M\setminus\{g\}`$. Among the PMMS allocations of $`W`$ with nonempty bundles (which exist by the seven-good theorem), choose $`B`$ maximising $`v_a(B_a)`$, and among those a Pareto-maximal one with respect to the three own values. Relabel agents by nondecreasing $`|B_i|`$, carrying the designation of $`a`$ with its label. When two bundles have equal size, order their holders so that the third agent prefers the second holder’s bundle. Then relabel goods so that $`g`$ is last and the bundles form consecutive blocks ordered within each block by the first agent’s values.

The size profiles of $`B`$ are $`(1,1,5)`$, $`(1,2,4)`$, $`(1,3,3)`$ and $`(2,2,3)`$. Each case formula adds to the clauses above: the six comparisons of $`B`$ hold; for every other allocation $`C`$ of $`W`$, either $`C`$ fails or some agent $`i`$ with $`C_i\ne B_i`$ strictly prefers $`B_i`$ (Lemma <a href="#lem:pareto" data-reference-type="ref" data-reference="lem:pareto">9</a>); the tie-break and block-order units; and selector variables $`s_1,s_2,s_3`$, at least one true, where $`s_i`$ asserts that $`g`$ is $`i`$’s least valuable good and that $`B_i`$ is $`i`$’s best bundle among PMMS allocations of $`W`$.

<div id="lem:pareto" class="lemma">

**Lemma 9**. *If $`C\ne B`$ is a PMMS allocation of $`W`$ with nonempty bundles, some agent $`i`$ with $`C_i\ne B_i`$ has $`v_i(B_i)>v_i(C_i)`$.*

</div>

<div class="proof">

*Proof.* Otherwise, by genericity, every agent with a changed bundle strictly prefers $`C`$, and some bundle changed. Then $`v_a(C_a)\ge v_a(B_a)`$. Maximality forces equality, and genericity forces $`C_a=B_a`$. So $`C`$ belongs to the set from which $`B`$ was chosen as Pareto-maximal, and strictly dominates it, a contradiction. ◻

</div>

<div id="lem:tiebreak" class="lemma">

**Lemma 10**. *If all three bundles have equal size, the agents can be labelled so that agent 3 prefers agent 2’s bundle to agent 1’s and agent 1 prefers agent 3’s bundle to agent 2’s.*

</div>

<div class="proof">

*Proof.* Let $`\mathrm{pref}(x)`$ be the other agent whose bundle $`x`$ prefers. Take any $`x`$, $`y=\mathrm{pref}(x)`$, $`z=\mathrm{pref}(y)`$. If $`z\ne x`$, label $`x,y,z`$ as $`1,3,2`$. Otherwise $`x`$ and $`y`$ prefer each other; label the third agent $`w`$ as 1, $`\mathrm{pref}(w)`$ as 3 and the remaining agent as 2. ◻

</div>

Lemma <a href="#lem:tiebreak" data-reference-type="ref" data-reference="lem:tiebreak">10</a> is needed only for the seven-good profile $`(2,2,2)`$. For the three profiles other than $`(1,1,5)`$ each case formula $`F`$ was refuted as three formulas $`F\wedge s_i`$. Several selectors may hold at once, which is harmless: refuting each $`F\wedge s_i`$ refutes $`F\wedge(s_1\vee s_2\vee s_3)`$.

# Certificates

## Verification layers

<figure data-latex-placement="H">

<figcaption>Each layer is checked independently of the code that produced the next.</figcaption>
</figure>

The generator writes each formula together with a dictionary naming every variable. The verifier reads only the formula and the dictionary. It recomputes each variable’s meaning, rebuilds from the definitions of Section <a href="#sec:reduction" data-reference-type="ref" data-reference="sec:reduction">4</a> the set of clauses valid for the case, and checks that every clause of the formula is in that set. For the six-good formula and every eight-good formula the two sets are equal; for the seven-good formulas the rebuilt set also contains clauses of one family that those formulas do not use. The verifier imports only the Python standard library and no code from the generator; it was written by the same author, so its independence lies in implementation, not authorship.

The refutations were produced by CaDiCaL 3.0.1 in the LRAT format . Each proof was then trimmed to the steps the refutation needs: with `lrat-trim` , which also checks every step it keeps, except for $`(2,2,3)`$, $`s_3`$, whose untrimmed proof (73 GB of text) exceeded the memory available to `lrat-trim` and was trimmed by a short external-memory program distributed with the evidence (`tools/lowmem_trim.c`). Trimming is not trusted: the trimmed certificates are the ones checked below and distributed with the paper. Each was accepted by `lrat-check`, the checker distributed with drat-trim (commit `2e3b2dc`) and written independently of this work, and by a separate standard-library Python checker. The Python checker performs plain unit propagation, rejects RAT steps, and skips a hint clause already satisfied under the current assignment; such a hint yields neither a unit nor a conflict, so skipping it preserves soundness. Two controls guard the implementation. For random positive generic matrices, and for an eight-good restriction of Gölz’s counterexample, every non-allocation clause of the base formula holds and the number of violated allocation clauses equals the number of PMMS allocations computed directly. For random matrices put into normal form by the procedure of Section <a href="#sec:reduction" data-reference-type="ref" data-reference="sec:reduction">4</a>, every clause of the corresponding case formula other than the allocation clauses holds; the trials covered all four eight-good profiles. The controls test the code; the validity of each clause family rests on the arguments in the text.

## Six and seven goods

The same framework re-proves the earlier results. A single six-good formula with no injected theorem (141,035 clauses) is refuted in one second. The seven-good theorem follows from three normal-form formulas of about 1.14 million clauses each. They use the restriction clauses for four to six goods and no other injected theorem, and are refuted in 33, 284 and 182 seconds. No auxiliary arithmetic clauses are needed. The earlier certificate for seven goods required thousands of separately certified integer-conflict clauses .

## Eight goods

Table <a href="#tab:cert" data-reference-type="ref" data-reference="tab:cert">1</a> lists the ten refutations that make up the proof of Theorem <a href="#thm:main" data-reference-type="ref" data-reference="thm:main">1</a>: one for the profile $`(1,1,5)`$ and three sub-cases for each of $`(1,2,4)`$, $`(1,3,3)`$ and $`(2,2,3)`$.

<div id="tab:cert">

| Formula | Clauses | Solver CPU | Proof (gz) | Proof steps | SHA-256 prefix |
|:---|---:|---:|---:|---:|---:|
| $`(1,1,5)`$ | 8 441 557 | 0.8 h | 0.54 GB | 1 810 478 | `d12fc3bf2fa4` |
| $`(1,2,4)`$, $`s_1`$ | 8 441 959 | 4.2 h | 2.64 GB | 6 522 144 | `e6d9052fed8f` |
| $`(1,2,4)`$, $`s_2`$ | 8 441 959 | 2.1 h | 1.10 GB | 3 324 990 | `61dab634c504` |
| $`(1,2,4)`$, $`s_3`$ | 8 441 959 | 2.5 h | 1.37 GB | 4 035 802 | `0dd1d635e15f` |
| $`(1,3,3)`$, $`s_1`$ | 8 442 088 | 9.6 h | 3.86 GB | 9 278 536 | `437417eda7af` |
| $`(1,3,3)`$, $`s_2`$ | 8 442 088 | 5.9 h | 2.37 GB | 6 167 188 | `c00dc1e7ccbe` |
| $`(1,3,3)`$, $`s_3`$ | 8 442 088 | 7.5 h | 2.83 GB | 7 055 726 | `29adb1cf23df` |
| $`(2,2,3)`$, $`s_1`$ | 8 442 154 | 16.2 h | 5.24 GB | 15 582 346 | `0c30c93cf24b` |
| $`(2,2,3)`$, $`s_2`$ | 8 442 154 | 19.2 h | 6.78 GB | 18 262 676 | `e60c953abe8c` |
| $`(2,2,3)`$, $`s_3`$ | 8 442 154 | 22.5 h | 6.69 GB | 20 476 217 | `c83cc82b1ae4` |

The ten refutations proving Theorem <a href="#thm:main" data-reference-type="ref" data-reference="thm:main">1</a>. All formulas have 252 930 variables. Proof sizes and steps refer to the trimmed certificates distributed with the paper; solver times refer to the original runs. SHA-256 prefixes identify the uncompressed formula file `base.cnf`; the evidence manifest gives full digests of every file. Solver times are measurements on a shared Apple M2 and play no role in the proof.

</div>

#### Dependencies.

Every certificate in Table <a href="#tab:cert" data-reference-type="ref" data-reference="tab:cert">1</a> depends only on the lemmas of Sections <a href="#sec:prelim" data-reference-type="ref" data-reference="sec:prelim">2</a>–<a href="#sec:reduction" data-reference-type="ref" data-reference="sec:reduction">4</a> and on the six- and seven-good theorems re-proved above. The EFX existence theorem of is not used: earlier runs whose formulas included EFX clauses, for $`(1,1,5)`$ and $`(1,2,4)`$, were replications, play no role in the proof and are not part of the evidence package.

# Where the hard instances lie

The certificates say nothing about which allocation works. This section records computational observations that do, separately from the proof. Each instance below was evaluated exhaustively over all 5 796 allocations with nonempty bundles. The instances come from five families: 300 random instances (values uniform in $`1,\dots,999`$); the 27 instances obtained by removing one good from a published nine-good counterexample; 300 instances with three dominant goods (values uniform in $`300,\dots,999`$ for three goods and in $`1,\dots,59`$ for five, columns shuffled); 300 balanced instances (values uniform in $`60,\dots,89`$); and 15 near-misses, found by simulated annealing that minimises the number of PMMS allocations. Further annealing runs searched specifically for counterexamples to each statement in Observation 3. The 27 deletion instances are the single-good deletions of Gölz’s two matrices and of Bei et al.’s matrix. Annealing looks for extreme instances, so the near-miss family says nothing about how common such instances are. Every instance, the generating scripts with their seeds and stopping rules, and the per-instance results are in the evidence bundle. Every instance quoted below was re-enumerated by a separate pure-Python implementation that shares no code with the search programs.

Two allocation templates are used. In the *pair template*, one agent receives two goods, a second agent splits the remaining six goods into two sets of three so as to maximise her smaller part, and the third agent takes the part she prefers; Proposition <a href="#prop:onerow" data-reference-type="ref" data-reference="prop:onerow">7</a> uses this template with the pair equal to the first agent’s top two goods. In the *singleton template*, one agent receives a single good worth at least a third of her total, a second agent splits the remaining seven goods into two nonempty parts so as to maximise her smaller part, and the third agent chooses.

<div class="observation">

*Observation 1*. The near-misses have between one and four PMMS allocations each. In all fifteen, no agent’s valuation is $`3`$-balanced, so Theorem <a href="#thm:card" data-reference-type="ref" data-reference="thm:card">6</a> and Proposition <a href="#prop:onerow" data-reference-type="ref" data-reference="prop:onerow">7</a> do not apply. Each nevertheless has a PMMS allocation produced by the pair template, and in thirteen of them every PMMS allocation has bundle sizes $`(2,3,3)`$.

</div>

<div class="observation">

*Observation 2*. Of the 300 instances with three dominant goods, 140 have no PMMS allocation with bundle sizes $`(2,3,3)`$. Each of those 140 has a PMMS allocation in which some agent holds exactly her single most valuable good. By Lemma <a href="#lem:witness" data-reference-type="ref" data-reference="lem:witness">3</a>, neither other agent can fail against that one-good bundle; the holder’s own two comparisons still have to hold, and in these allocations they do.

</div>

<div class="observation">

*Observation 3*. Three natural statements that would turn these observations into a proof are false.

1.  “If one agent is $`3`$-balanced, the pair template produces a PMMS allocation” fails for the instance displayed after Proposition <a href="#prop:onerow" data-reference-type="ref" data-reference="prop:onerow">7</a>, and also for
    ``` math
    \begin{pmatrix}355&683&1114&181&1190&302&1070&1102\\900&935&1025&1019&576&978&751&931\\65&1&149&23&111&61&121&100\end{pmatrix},
    ```
    which has 36 PMMS allocations, none produced by either template. It is the procedure, not the size profile, that fails: 28 of the 36 have sizes $`(2,3,3)`$, for instance $`\{2,5\},\{1,4,6,7\},\{3,8\}`$ with goods numbered by column. No agent there has a good worth a third of her total, so the singleton template does not apply.

2.  “Some PMMS allocation has bundle sizes $`(2,3,3)`$” fails for
    ``` math
    \begin{pmatrix}41&16&141&144&175&73&135&91\\74&10&176&159&191&35&158&106\\118&25&132&146&200&73&168&156\end{pmatrix},
    ```
    all of whose ten PMMS allocations have sizes $`(2,2,4)`$.

3.  “If some agent’s best good is worth at least a third of her total, the singleton template produces a PMMS allocation” fails for the following instance, in which the third agent has two such goods; in fact none of its 58 PMMS allocations contains a one-good bundle:
    ``` math
    \begin{pmatrix}73&137&105&44&139&9&150&193\\11&929&71&432&995&11&128&477\\107&93&1045&1036&127&70&129&189\end{pmatrix}.
    ```

</div>

Two further intuitions also fail. In each of the three near-misses with a single PMMS allocation, and for each of the three agents, no PMMS allocation of the eight goods restricts to a PMMS allocation of the seven goods left after removing that agent’s least valuable good. For these instances, then, the restriction clauses of Section <a href="#sec:reduction" data-reference-type="ref" data-reference="sec:reduction">4</a> only prune; they do not supply an allocation. And envy-free allocations, which exist for every random instance tested, exist for only two of the fifteen near-misses.

A reading of these observations, offered as interpretation rather than as a theorem: in most instances examined, a PMMS allocation either gives one agent fewer goods than the others, so that counting arguments of the kind in Proposition <a href="#prop:onerow" data-reference-type="ref" data-reference="prop:onerow">7</a> apply, or isolates a single dominant good, which reduces the problem to two agents. The instance in Observation 3(a) shows that this reading is incomplete.

# Discussion

Theorem <a href="#thm:main" data-reference-type="ref" data-reference="thm:main">1</a> settles the minimum size of a three-agent PMMS counterexample. The proof is a certificate, not an explanation, and Section <a href="#sec:structure" data-reference-type="ref" data-reference="sec:structure">6</a> indicates why an explanation is not close: the natural constructions each fail somewhere, and some hard instances are rescued by allocations that neither construction produces.

Three questions remain open. The first is a human-readable proof of Theorem <a href="#thm:main" data-reference-type="ref" data-reference="thm:main">1</a>. Proposition <a href="#prop:onerow" data-reference-type="ref" data-reference="prop:onerow">7</a> handles every instance with a $`3`$-balanced agent for which, under a suitable labelling, $`v_c(P)\le\tfrac12 v_c(M\setminus P)`$; the hardest instances found have no balanced agent at all. The second is to explain why the pair template fails on the instance of Observation 3(a), although 28 of its PMMS allocations have the template’s bundle sizes, and to find a construction that covers such instances. The third is the analogue for four agents, where the smallest known counterexample, Aziz’s, has 52 goods.

#### Limitations.

The proof is computer-assisted and has not been formalised in a proof assistant. The trusted base consists of the arguments of Sections <a href="#sec:prelim" data-reference-type="ref" data-reference="sec:prelim">2</a>–<a href="#sec:reduction" data-reference-type="ref" data-reference="sec:reduction">4</a>, the clause verifier and the two LRAT checkers. The ten certificates of Table <a href="#tab:cert" data-reference-type="ref" data-reference="tab:cert">1</a> total about 33 GB compressed; checking all of them with `lrat-check` takes about an hour. Historical priority is asserted only within a recorded literature search of 7–9 October 2026, which found no earlier statement of Theorem <a href="#thm:main" data-reference-type="ref" data-reference="thm:main">1</a> or Proposition <a href="#prop:onerow" data-reference-type="ref" data-reference="prop:onerow">7</a>.

#### Data and code.

The evidence is deposited at <https://doi.org/10.5281/zenodo.23284137>: the generators, the verifier, both checkers, every formula and certificate with SHA-256 digests, the instances quoted above, and a single replay script (`verify_bundle.py`) that re-runs every check using Python’s standard library and a C compiler. The ten eight-good certificates are separate files in that record; the remaining material is in its core archive and at <https://github.com/ipitchford/pmms-three-agents-eight-goods>.

#### Method statement.

This work was produced with AI assistance (Anthropic’s Claude models, with adversarial review by an OpenAI model); the author line is therefore Anonymous. All mathematical claims are either proved in the text, certified by the checked computations described, or explicitly labelled as observations.

# Clause schemas and soundness

Throughout, $`p_{i,r}`$ denotes the sign literal of Section 4.1, with one Boolean variable per agent $`i`$ and per vector $`r\in\{-1,0,1\}^M`$ having both signs and first nonzero coordinate $`+1`$; the literal for $`-r`$ is the negation of that variable. A vector $`r\ne0`$ with $`r\ge0`$ gives the constant true, a vector with $`r\le0`$ (including $`r=0`$) the constant false. Every clause below is simplified by these constants: a clause containing a true literal is dropped, false literals are deleted, and tautologies are dropped. For disjoint $`S,T`$ write $`[S>_iT]`$ for $`p_{i,\mathbf1_S-\mathbf1_T}`$.

1.  *Addition.* $`\lnot p_{i,r}\vee\lnot p_{i,s}\vee p_{i,r+s}`$ for nonzero $`r\ne s`$ with $`r+s`$ nonzero in the cube.

2.  *Halving.* $`\lnot p_{i,r}\vee\lnot p_{i,s}\vee p_{i,t}`$ for nonzero $`r\ne s`$ with $`r+s=2t`$, $`t\ne0`$.

3.  *Witnesses.* For agent $`i`$, own bundle $`D`$, opposing bundle $`E`$ and a bipartition with $`S_1,T_1,S_2,T_2`$ as in Section 4.2, put $`a=[S_1>_iT_1]`$ and $`b=[S_2>_iT_2]`$. If both are non-constant, a variable $`z`$ with $`(\lnot z\vee a)`$, $`(\lnot z\vee b)`$, $`(z\vee\lnot a\vee\lnot b)`$; if one is the constant true, the witness literal is the other; if one is false, there is no witness.

4.  *Failure.* If $`(D,E)`$ has witness literals $`z_1,\dots,z_k`$ with $`k\ge1`$, a variable $`F_{i,D,E}`$ with $`(\lnot F\vee z_1\vee\dots\vee z_k)`$ and $`(F\vee\lnot z_j)`$ for each $`j`$; otherwise $`F_{i,D,E}`$ is the constant false.

5.  *Allocations.* For every complete allocation $`A`$ with nonempty bundles, the clause $`\bigvee_{i\ne j}F_{i,A_i,A_j}`$.

6.  *Restriction.* For every $`W\subset M`$ with $`4\le|W|\le m-1`$ and $`|W|\le7`$: one variable $`y_C`$ per allocation $`C`$ of $`W`$ with nonempty bundles whose six failure literals are not all false and none is true, the clauses $`(\lnot y_C\vee\lnot F)`$ for each of its non-constant failure literals $`F`$, and $`\bigvee_C y_C`$. (If some allocation of $`W`$ has six constant-false failure literals, nothing is added for $`W`$.)

7.  *Cardinality* ($`m=8`$ only). For each pair of agents $`\{i,j\}`$, the disjunction of $`[P>_iT]`$ and $`[P>_jT]`$ over all disjoint $`P,T`$ with $`|P|=2`$, $`|T|=3`$.

8.  *Normal form* (seven and eight goods). With $`g`$ the last good, $`W=M\setminus\{g\}`$ and $`B`$ the case allocation: the units $`\lnot F`$ for the six comparisons of $`B`$; for every other allocation $`C`$ of $`W`$ with nonempty bundles, $`\bigvee F(C)\vee\bigvee_{i:C_i\ne B_i}[B_i\setminus C_i>_iC_i\setminus B_i]`$; the tie-break units of Section 4.4; within each block of $`B`$ the units $`[\{x+1\}>_1\{x\}]`$; selector variables $`s_1,s_2,s_3`$ with $`(s_1\vee s_2\vee s_3)`$, $`(\lnot s_i\vee[\{h\}>_i\{g\}])`$ for every $`h\ne g`$, and, at eight goods, $`(\lnot s_i\vee\bigvee F(C)\vee[B_i\setminus C_i>_iC_i\setminus B_i])`$ for every allocation $`C`$ of $`W`$ with $`C_i\ne B_i`$.

9.  *Sub-case.* For the sub-case formulas, the unit $`s_i`$.

10. *Six goods.* The base formula consists of (C1)–(C5) and the units $`[\{x+1\}>_1\{x\}]`$ for consecutive goods.

<div id="prop:sound" class="proposition">

**Proposition 11** (soundness). *If some instance with three agents and $`m\in\{6,7,8\}`$ goods has no complete PMMS allocation, then, after relabelling agents and goods, some formula of Table <a href="#tab:registry" data-reference-type="ref" data-reference="tab:registry">2</a> for $`m`$ goods is satisfiable. Hence the refutations of all formulas in Table <a href="#tab:registry" data-reference-type="ref" data-reference="tab:registry">2</a> prove Theorem <a href="#thm:main" data-reference-type="ref" data-reference="thm:main">1</a>.*

</div>

<div class="proof">

*Proof.* By Lemma <a href="#lem:generic" data-reference-type="ref" data-reference="lem:generic">5</a> take the counterexample positive and generic. For $`m=6`$ relabel goods so that agent 1’s values increase; for $`m=7,8`$ apply the normal form of Section 4.4, using existence for $`m-1`$ goods, which holds by induction on $`m`$ through the six- and seven-good formulas. Assign every sign variable its truth value, every witness, failure and restriction selector its defining value, and $`s_i`$ true exactly when agent $`i`$ satisfies the selector conditions; $`s_a`$ is true. Then (C1)–(C2) hold by additivity, (C3)–(C4) by definition and Lemma <a href="#lem:witness" data-reference-type="ref" data-reference="lem:witness">3</a>, (C5) because no allocation is PMMS, (C6) by existence for fewer goods with the dummy-good argument of Section 4.3, (C7) by Theorem <a href="#thm:card" data-reference-type="ref" data-reference="thm:card">6</a>, and (C8) by the choice of $`B`$, Lemmas <a href="#lem:pareto" data-reference-type="ref" data-reference="lem:pareto">9</a> and <a href="#lem:tiebreak" data-reference-type="ref" data-reference="lem:tiebreak">10</a> and the relabelling. For the profiles refuted by sub-cases, the unit $`s_a`$ of (C9) holds. So the assignment satisfies the formula of its case, or of one of its sub-cases. ◻

</div>

The clause verifier of Section 5.1 implements exactly this list: from a formula’s variable dictionary it rebuilds (C1)–(C10) for the case and checks that the formula’s clauses are among them.

# Certificate registry

<div id="tab:registry">

| Goods | Formula | Variables | Clauses | Proof steps | Proof (gz) | `lrat-check` | Python | SHA-256 prefix |
|:---|:---|---:|---:|---:|---:|---:|---:|:---|
| 6 | six goods | 4 683 | 141 035 | 20 268 | 2 MB | 0 s | 1 s | `db8756e1486a` |
| 7 | $`(1,1,4)`$ | 40 407 | 1 137 360 | 113 466 | 15 MB | 1 s | 5 s | `8343ec695615` |
| 7 | $`(1,2,3)`$ | 40 407 | 1 137 409 | 674 184 | 113 MB | 7 s | 46 s | `02e50818d156` |
| 7 | $`(2,2,2)`$ | 40 407 | 1 137 425 | 431 477 | 61 MB | 4 s | 24 s | `6c7c4d75b439` |
| 8 | $`(1,1,5)`$ | 252 930 | 8 441 557 | 1 810 478 | 537 MB | 38 s | 4 min | `d12fc3bf2fa4` |
| 8 | $`(1,2,4)`$, $`s_1`$ | 252 930 | 8 441 959 | 6 522 144 | 2640 MB | 230 s | 16 min | `e6d9052fed8f` |
| 8 | $`(1,2,4)`$, $`s_2`$ | 252 930 | 8 441 959 | 3 324 990 | 1100 MB | 73 s | 7 min | `61dab634c504` |
| 8 | $`(1,2,4)`$, $`s_3`$ | 252 930 | 8 441 959 | 4 035 802 | 1367 MB | 124 s | 8 min | `0dd1d635e15f` |
| 8 | $`(1,3,3)`$, $`s_1`$ | 252 930 | 8 442 088 | 9 278 536 | 3861 MB | 227 s | 24 min | `437417eda7af` |
| 8 | $`(1,3,3)`$, $`s_2`$ | 252 930 | 8 442 088 | 6 167 188 | 2367 MB | 198 s | 15 min | `c00dc1e7ccbe` |
| 8 | $`(1,3,3)`$, $`s_3`$ | 252 930 | 8 442 088 | 7 055 726 | 2835 MB | 212 s | 17 min | `29adb1cf23df` |
| 8 | $`(2,2,3)`$, $`s_1`$ | 252 930 | 8 442 154 | 15 582 346 | 5242 MB | 352 s | 31 min | `0c30c93cf24b` |
| 8 | $`(2,2,3)`$, $`s_2`$ | 252 930 | 8 442 154 | 18 262 676 | 6784 MB | 423 s | 46 min | `e60c953abe8c` |
| 8 | $`(2,2,3)`$, $`s_3`$ | 252 930 | 8 442 154 | 20 476 217 | 6686 MB | 455 s | 36 min | `c83cc82b1ae4` |

All fourteen refutations. Proof steps and sizes refer to the trimmed certificates in the evidence bundle; the two right-hand time columns are the checking times of the two checkers on an Apple M2 shared with other work. The seven-good formulas omit the own-value clauses of (C8). Every formula is re-derived by the clause verifier; for the six- and eight-good formulas the rebuilt clause set equals the formula exactly.

</div>

<div class="thebibliography">

99 H. Akrami, A. Mayorov, K. Mehlhorn, S. Srinivas, C. Weidenbach. A counterexample to EFX: $`n\ge3`$ agents, $`m\ge n+5`$ items, submodular valuations via SAT-solving. arXiv:2604.18216v3 (2026). G. Amanatidis, E. Markakis, A. Ntokos. Multiple birds with one stone: beating 1/2 for EFX and GMMS via envy cycle elimination. *AAAI* 34 (2020) 1790–1797. Anonymous. PMMS: impasse audit and adaptive completion certificates. Research memorandum, 7 October 2026. Anonymous. Pairwise maximin fairness for three agents and seven goods: a certified existence theorem. Research note, 6 October 2026. H. Aziz. Pairwise maximin share allocations need not exist. arXiv:2609.06282 (2026). X. Bei, Z. Lin, S. Liu, R. Luan, B. Tao. Non-existence of PMMS allocations and a 4/3-PMMS guarantee for additive chores. arXiv:2609.10493 (2026). A. Biere, T. Faller, K. Fazekas, M. Fleury, N. Froleyks, F. Pollitt. CaDiCaL 2.0. *CAV* 2024, LNCS 14681, 133–152. A. Biere. `lrat-trim`: trimming and checking LRAT proofs. Software, <https://github.com/arminbiere/lrat-trim> (2023–2026). I. Caragiannis, D. Kurokawa, H. Moulin, A. D. Procaccia, N. Shah, J. Wang. The unreasonable fairness of maximum Nash welfare. *ACM Trans. Econ. Comput.* 7(3) (2019) 12. B. R. Chaudhury, J. Garg, K. Mehlhorn. EFX exists for three agents. *J. ACM* 71(1) (2024) 4. L. Cruz-Filipe, M. J. H. Heule, W. A. Hunt, M. Kaufmann, P. Schneider-Kamp. Efficient certified RAT verification. *CADE-26*, LNCS 10395 (2017) 220–236. P. Gölz. PMMS allocations need not exist for 3 agents with additive valuations. arXiv:2609.08954 (2026).

</div>
