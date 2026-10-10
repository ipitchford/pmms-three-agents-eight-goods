# Citation audit

Each reference in `paper/pmms8.tex`, what the paper uses it for, and how that use was checked (7–10 October 2026).

| Key | Source | Used for | Check |
|---|---|---|---|
| Golz26 | P. Gölz, arXiv:2609.08954 | Nine-good three-agent counterexample; remark that nine is believed minimal or almost minimal | Full text read; both instances re-verified by enumeration (`nine_good_check.json`); remark quoted from the HTML text |
| BLLLT26 | X. Bei, Z. Lin, S. Liu, R. Luan, B. Tao, arXiv:2609.10493 | Second nine-good goods instance | Full text read; Table 2 instance re-verified by enumeration |
| Aziz26 | H. Aziz, arXiv:2609.06282 | Four-agent counterexample with 52 goods | Full text read for instance size and the three-agent remark |
| AMN20 | G. Amanatidis, E. Markakis, A. Ntokos, AAAI 34 (2020) | Existence for m ≤ n+2 | Statement confirmed from search results; theorem pinpoint (Theorem 18, Corollary 19; Theorem 5.1 of the expanded version) supplied by the external review |
| AMMSW26 | H. Akrami, A. Mayorov, K. Mehlhorn, S. Srinivas, C. Weidenbach, arXiv:2604.18216v3 | Closest methodological precedent | v3 full text read for encoding, Lean scope and proof checking |
| CGM24 | B. R. Chaudhury, J. Garg, K. Mehlhorn, J. ACM 71(1) (2024) | Cited only to state that EFX existence is not used | Bibliographic statement confirmed |
| CKMPSW19 | I. Caragiannis et al., ACM TEAC 7(3) (2019) | Definition of PMMS | Standard definition; agrees with Gölz 2026 |
| CHHKS17 | L. Cruz-Filipe et al., CADE-26 (2017) | LRAT format | Format as implemented by `lrat-check` and `check_lrat_rup.py` |
| Cadical | A. Biere et al., CaDiCaL 2.0, CAV 2024 | Solver that produced the proofs (version 3.0.1 used) | Producer only; its output is checked, not trusted |
| LratTrim | A. Biere, lrat-trim | Proof trimming | Producer only; commit in `tools/LRAT_TRIM_VERSION.txt` |
| Anon7 | Anonymous, seven-good note, 6 October 2026 | Prior bound m* ∈ {8, 9} | Unpublished; part of the input package (see `PROVENANCE.md`); its result is re-proved here |
| AnonMemo | Anonymous, impasse memorandum, 7 October 2026 | Cardinality theorem and methods reused | Unpublished; part of the input package; Theorem 6 is re-proved in the paper |

No load-bearing step of the proof depends on a cited result: six- and seven-good existence are re-proved, and the
eight-good certificates use only clauses justified in the paper.
