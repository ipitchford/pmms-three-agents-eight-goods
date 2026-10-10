# Novelty gate report: three-agent PMMS existence at eight goods

Search date: 7 October 2026. Corpus boundary: arXiv listings and full texts reachable on that
date, the OpenAlex/Semantic Scholar neighbourhood of the papers below, and the research
bundle supplied by the user (`PMMS_Impasse_Research_Bundle_20261007.zip`, which records its
own source review of 7 October 2026).

## 0. Frozen claim

Narrowest claim that counts as success: *for three agents with nonnegative additive valuations
over eight indivisible goods, a complete pairwise maximin share (PMMS) allocation always exists;
consequently the least number of goods admitting a three-agent counterexample is exactly nine.*

Contribution units:

1. Statement (m* = 9). Not previously stated as a theorem anywhere found.
2. Proof (computer-assisted, independently checkable certificates). New.
3. Identification/bridge: the sign-abstraction and lemma-injection method is an instance of
   standard SAT-based combinatorial proof with cut-and-choose style existence lemmas; no
   claim of methodological novelty is made.
4. Verification artefacts (CNF generators, independent clause verifier, LRAT certificates). New.

Exclusions: no claim about n >= 4 agents, chores, approximate PMMS, or non-additive valuations.

## 1. Definitions and normalisation

PMMS as in Caragiannis, Kurokawa, Moulin, Procaccia, Shah and Wang (2019): allocation
(A_1,...,A_n) of all goods; for all i != j, v_i(A_i) >= max over T subset of A_i cup A_j of
min(v_i(T), v_i((A_i cup A_j) minus T)). Valuations additive and nonnegative; empty bundles
allowed. This agrees with Goelz (2026) and with the user's seven-good note.

## 2. Primary literature inspected (ring 1-3)

| Source | Load-bearing content | Relation to the claim |
|---|---|---|
| Goelz, arXiv:2609.08954 (8 Sep 2026) | 3 agents, 9 goods, no PMMS allocation; 78/79 approximation bound; states "Not having found any counterexample instances with n=3 and m<=8, I believe that m=9 is minimal or almost minimal" | Upper bound m* <= 9; leaves m = 8 open |
| Bei, Lin, Liu, Luan, Tao, arXiv:2609.10493 (9 Sep 2026) | chores-to-goods reduction (n agents, m items -> nm goods); 3-agent 9-good goods instance with PMMS factor 226/227 (Table 2) | Second independent 9-good obstruction; no 8-good statement |
| Aziz, arXiv:2609.06282 (5 Sep 2026) | 4 agents, 52 goods, strictly positive valuations, no complete PMMS allocation; explicitly says the three-agent additive case remains open | Earlier counterexample with more agents; does not touch m* for 3 agents |
| Amanatidis, Markakis, Ntokos, AAAI 2020 | GMMS (hence PMMS) allocations exist for m <= n+2 | Gives existence for 3 agents and <= 5 goods |
| User's note *Pairwise maximin fairness for three agents and seven goods* (6 Oct 2026) | certified existence for m <= 7 via sign-abstraction SAT; Corollary m* in {8,9}; notes Goelz leaves 6,7,8 open | Lower bound m* >= 8; the direct predecessor of this work |
| User's bundle memorandum (7 Oct 2026) | adaptive-completion theorems, cardinality theorem (3q-1 goods), master/subproblem search that stalled | Methods and lemmas reused; records the impasse |
| Chaudhury, Garg, Mehlhorn, EC 2020 / JACM 71(1) 2024 | EFX allocations exist for three additive agents | Used only in the optional (fast) certificate variant as an injected lemma |
| Feige, Sapir, Tauber, arXiv:2104.04977 | 3-agent 9-good MMS obstruction; MMS exists for 3 agents and <= 8 goods | Different notion; not used |
| Feldman, Fiat, Nissan, Ponitka, arXiv:2606.18921 | epistemic PMMS for three agents | Different guarantee; not used |

## 3. Fingerprint and alias searches

The object is a finite decision problem rather than a sequence or kernel, so the fingerprints
are (a) the exact statement, (b) the known small instances (Goelz's two 9-good matrices and Bei
et al.'s Table 2 matrix, all three re-verified here by exact enumeration: zero PMMS allocations;
every one-good deletion leaves at least five PMMS allocations), and (c) the term aliases
"pairwise maximin share", "PMMS", "EFX via PMMS", "minimum number of goods",
"smallest counterexample", "n=3, m=8". Searches on 7 October 2026 for these aliases combined
with "eight goods" / "m <= 8" / "minimal" returned only the sources above.

## 4. Adjudication

- Statement unit: **CLEAR TO PROVE** within the recorded boundary. Goelz's remark is an
  expectation, not a theorem; no source states existence at m = 8.
- Proof unit: **CLEAR**; no earlier proof exists to collide with.
- Bridge unit: **not claimed**.
- Artefact unit: **CLEAR**; the sign-abstraction encoding follows the user's seven-good note and
  Marshall's comparative-probability cone framework, which are cited.

Permitted language: "to our knowledge the first determination of m*", "not found in the
bounded search described here". Forbidden: "proved novel", "first ever" without the boundary.

## 5. Next enquiry

If the result is released, an author enquiry to P. Goelz and to Bei et al. would close the
priority boundary; this is out of scope for the present session (external engagement is
excluded by standing instruction).
