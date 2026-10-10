# PMMS allocations for three agents exist up to eight goods

Version 0.1.0-candidate, 10 October 2026. Anonymous. Unrefereed candidate published by Evidence Press.
DOI [10.5281/zenodo.23284137](https://doi.org/10.5281/zenodo.23284137).

The paper is [`paper/pmms8.pdf`](paper/pmms8.pdf) (source [`paper/pmms8.tex`](paper/pmms8.tex), accessible text
[`paper/pmms8.md`](paper/pmms8.md)). It proves that every three-agent instance with at most eight goods and
nonnegative additive valuations has a complete pairwise maximin share (PMMS) allocation. Since nine-good instances
without one are known, nine is the least number of goods in a three-agent counterexample. The proof is
computer-assisted: a hypothetical eight-good counterexample is reduced to ten propositional formulas, each refuted by
an LRAT certificate. See [`STATUS.md`](STATUS.md) and [`ASSURANCE.md`](ASSURANCE.md) for what has and has not been
checked, and [`AI_INDEX.md`](AI_INDEX.md) for an index of the evidence.

## Where the files are

| Location | Contents |
|---|---|
| Zenodo record, core archive `pmms-three-agents-eight-goods-v0.1.0-candidate-core.zip` | Everything in this README's layout except the ten eight-good proofs |
| Zenodo record, `eight_goods_<case>.proof.lrat.gz` and `....part00`, `.part01`, ... | The ten eight-good certificates (about 33 GB in total). Proofs larger than 600 MB are split into consecutive 400 MiB parts so that each upload and download is manageable |
| Zenodo record, `pmms8.pdf`, `SHA256SUMS` | The paper, and digests of every asset in the record |
| GitHub `ipitchford/pmms-three-agents-eight-goods` | Code, paper and records; the GitHub release carries the core archive, the PDF and `SHA256SUMS`. Large formulas and proofs are not in Git history |

To assemble the complete package: unpack the core archive, download the proof files and parts into one directory and run

```sh
python3 -I place_proofs.py DOWNLOAD_DIR          # add --link to symlink instead of copying
```

which joins the parts and checks each proof against the digest in `MANIFEST.json` before putting it in place.

## Contents

| Path | What it is |
|---|---|
| `paper/` | The paper, its LaTeX source, an accessible Markdown version, the claim ledger and the prior-art record |
| `six_goods/` | Six-good base formula and its refutation |
| `seven_goods/case114,123,222/` | The three seven-good normal forms |
| `eight_goods/case115/` | Eight-good profile (1,1,5) |
| `eight_goods/case124_sub0..2/`, `case133_sub0..2/`, `case223_sub0..2/` | Profiles (1,2,4), (1,3,3), (2,2,3), three sub-cases each |
| `signsat.py`, `cases.py`, `build_case_cnf.py` | Formula generator (needs NumPy) |
| `verify_case.py` | Independent clause verifier (standard library only; imports nothing from the generator) |
| `check_lrat_rup.py`, `tools/lrat-check.c` | The two LRAT checkers (the second is third-party, see `LICENSES.md`) |
| `verify_nine_good.py`, `nine_good_check.json` | Exhaustive check of the published nine-good counterexamples |
| `controls/` | Semantic and normal-form controls of the generator, and negative controls showing that corrupted formulas and proofs are rejected |
| `data/` | Instances, measurements and scripts behind Section 6 of the paper, including the annealing scout |
| `review/` | Adversarial review reports received during preparation and the responses |
| `verify_bundle.py`, `place_proofs.py`, `MANIFEST.json`, `MANIFEST.sha256`, `receipts/` | Replay, proof placement, SHA-256 digests of every file, and replay receipts |

Each certificate directory holds:

| File | Content |
|---|---|
| `base.cnf` | The propositional formula |
| `dictionary.json` | The meaning of every variable |
| `build_info.json` | Generation flags and SHA-256 of the formula (absent for six goods) |
| `proof.lrat.gz` | The refutation in ASCII LRAT, trimmed with lrat-trim (with `tools/lowmem_trim.c` for `case223_sub2`) |
| `lrat_check.out`, `python_check.json` | Acceptance by the two checkers |
| `trim_log.txt`, `trim_summary.json` | The trimming run (lrat-trim also re-checks every kept step) |
| `solver_log.txt` | The original CaDiCaL run that produced the untrimmed proof |
| `verify_case_result.json` | The clause verifier's result for this formula |

## Replay

Requires Python 3, a C compiler and gzip; no SAT solver.

```sh
python3 -I verify_bundle.py --out /tmp/replay_receipt.json
```

The last line is `PASS_ALL_BUNDLE_CHECKS` when every digest matches, the nine-good counterexamples are confirmed,
every formula is re-derived clause by clause, and `lrat-check` accepts every refutation. It checks two certificates
at a time (`--jobs N` to change) and takes roughly an hour on a laptop. Add `--python-lrat` to run the
standard-library checker as well (several more hours). Single checks:

```sh
python3 -I verify_case.py eight_goods/case223_sub2 --goods 8 --case 223 --sub 2 --result /tmp/r.json --tmp /tmp/v
cc -O2 -o /tmp/lrat-check tools/lrat-check.c
/tmp/lrat-check eight_goods/case223_sub2/base.cnf <(gunzip -c eight_goods/case223_sub2/proof.lrat.gz)
python3 -I check_lrat_rup.py eight_goods/case223_sub2/base.cnf eight_goods/case223_sub2/proof.lrat.gz
```

Formulas are deterministic: `python3 build_case_cnf.py 8 223 DIR noefx sub2` regenerates the formula above with the
same SHA-256 digest. The `sub` index is zero-based (`sub2` is the paper's $s_3$).

## Scope and licence

The proof is computer-assisted and not formalised in a proof assistant. No independent reproduction, specialist
review or editorial peer review has taken place. Author: Anonymous. Text, data and certificates CC0-1.0; original
code MIT; third-party components keep their own terms (see `LICENSES.md`).
