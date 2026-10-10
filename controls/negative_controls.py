#!/usr/bin/env python3
"""Negative controls: the clause verifier and both LRAT checkers must REJECT corrupted inputs.

Uses the six-good certificate (small enough to run in seconds) and works on temporary copies only.
  1. a clause deleted from the formula     -> verifier reports a rebuilt clause missing from the formula
     (all copies are removed: the comparison is between clause sets)
  2. a non-derivable clause added          -> verifier reports a formula clause it cannot derive
  3. one hint of one proof step changed     -> lrat-check and the Python checker both reject
  4. the final (empty-clause) step removed  -> neither checker reports VERIFIED
Prints NEGATIVE_CONTROLS_PASS when every corruption is rejected.  Usage: python3 -I controls/negative_controls.py
"""
import gzip, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIX = os.path.join(HERE, 'six_goods')


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=HERE)


def main():
    T = tempfile.mkdtemp(prefix='pmms_negctl_')
    ok_all = True

    def report(name, rejected, detail=''):
        nonlocal ok_all
        ok_all &= rejected
        print(('PASS ' if rejected else 'FAIL ') + name + ('' if rejected else ' ' + detail), flush=True)

    lines = open(os.path.join(SIX, 'base.cnf')).read().splitlines()
    header = lines[0].split(); clauses = [l for l in lines[1:] if l and not l.startswith('c')]
    nv, nc = int(header[2]), int(header[3])

    def formula_case(name, new_clauses):
        d = os.path.join(T, name); os.makedirs(d)
        with open(os.path.join(d, 'base.cnf'), 'w') as f:
            f.write(f'p cnf {nv} {len(new_clauses)}\n' + '\n'.join(new_clauses) + '\n')
        shutil.copy2(os.path.join(SIX, 'dictionary.json'), d)
        r = run([sys.executable, '-I', 'verify_case.py', d, '--goods', '6', '--case', 'plain',
                 '--tmp', os.path.join(T, 'v_' + name), '--result', os.path.join(T, name + '.json')])
        return r.stdout + r.stderr

    # the comparison is between clause sets, so remove every copy of one clause (some clauses are written twice)
    key = lambda c: tuple(sorted(int(x) for x in c.split()[:-1]))
    target = key(clauses[len(clauses) // 2])
    out = formula_case('deleted', [c for c in clauses if key(c) != target])
    report('verifier rejects a formula with one clause deleted', '"expected_not_in_cnf": 0' not in out, out[-300:])
    var = 1
    out = formula_case('added', clauses + [f'{var} 0'])
    report('verifier rejects a formula with a non-derivable unit clause added',
           'ALL_CNF_CLAUSES_INDEPENDENTLY_DERIVED' not in out, out[-300:])

    proof = gzip.open(os.path.join(SIX, 'proof.lrat.gz'), 'rt').read().splitlines()
    adds = [i for i, l in enumerate(proof) if l.split()[1:2] != ['d']]
    lc = os.path.join(T, 'lrat-check')
    if run(['cc', '-O2', '-o', lc, os.path.join(HERE, 'tools', 'lrat-check.c')]).returncode:
        sys.exit('cannot build lrat-check')

    def checkers(name, plines):
        p = os.path.join(T, name + '.lrat.gz')
        with gzip.open(p, 'wt') as f:
            f.write('\n'.join(plines) + '\n')
        raw = os.path.join(T, name + '.lrat')
        with open(raw, 'w') as f:
            f.write('\n'.join(plines) + '\n')
        a = run([lc, os.path.join(SIX, 'base.cnf'), raw]).stdout
        b = run([sys.executable, '-I', 'check_lrat_rup.py', os.path.join(SIX, 'base.cnf'), p])
        return ('c VERIFIED' in a), ('"status": "VERIFIED"' in b.stdout)

    # change one hint of a middle step to a different, earlier clause id
    k = adds[len(adds) // 2]; toks = proof[k].split(); z = toks.index('0', 1)
    hints = toks[z + 1:-1]
    if not hints:
        sys.exit('chosen step has no hints')
    hints[0] = '1' if hints[0] != '1' else '2'
    corrupted = proof[:k] + [' '.join(toks[:z + 1] + hints + ['0'])] + proof[k + 1:]
    a, b = checkers('hint', corrupted)
    report('lrat-check rejects a proof with one hint changed', not a)
    report('Python checker rejects a proof with one hint changed', not b)

    a, b = checkers('noempty', proof[:adds[-1]] + proof[adds[-1] + 1:])
    report('lrat-check does not verify a proof without its empty clause', not a)
    report('Python checker does not verify a proof without its empty clause', not b)

    shutil.rmtree(T, ignore_errors=True)
    print('NEGATIVE_CONTROLS_PASS' if ok_all else 'NEGATIVE_CONTROLS_FAIL')
    sys.exit(0 if ok_all else 1)


if __name__ == '__main__':
    main()
