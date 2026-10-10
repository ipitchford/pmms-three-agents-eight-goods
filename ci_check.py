#!/usr/bin/env python3
"""Continuous-integration checks that fit on a hosted runner (the full replay needs the 33 GB of certificates):
regenerate all ten eight-good formulas and compare their SHA-256 with build_info.json and MANIFEST.json, and
re-derive the clauses of one of them with the independent verifier.  Usage: python3 ci_check.py WORKDIR"""
import hashlib, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = [('115', None)] + [(c, s) for c in ('124', '133', '223') for s in range(3)]


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    work = sys.argv[1]
    man = json.load(open(os.path.join(HERE, 'MANIFEST.json')))['files']
    bad = 0
    for c, s in CASES:
        d = f'eight_goods/case{c}' + ('' if s is None else f'_sub{s}')
        out = os.path.join(work, d.replace('/', '_'))
        cmd = [sys.executable, os.path.join(HERE, 'build_case_cnf.py'), '8', c, out, 'noefx'] + ([] if s is None else [f'sub{s}'])
        subprocess.run(cmd, check=True, capture_output=True)
        got = sha(os.path.join(out, 'base.cnf'))
        info = json.load(open(os.path.join(HERE, d, 'build_info.json')))['base_sha256']
        ok = got == info == man[f'{d}/base.cnf']['sha256']
        print(('PASS ' if ok else 'FAIL ') + f'{d} formula regenerated, sha256 {got[:12]}', flush=True)
        bad += not ok
        if (c, s) == ('115', None):
            r = subprocess.run([sys.executable, '-I', os.path.join(HERE, 'verify_case.py'), out, '--goods', '8', '--case', c,
                                '--tmp', os.path.join(work, 'v'), '--result', os.path.join(work, 'v.json')],
                               capture_output=True, text=True, cwd=HERE)
            ok = 'ALL_CNF_CLAUSES_INDEPENDENTLY_DERIVED' in r.stdout and '"expected_not_in_cnf": 0' in r.stdout
            print(('PASS ' if ok else 'FAIL ') + f'{d} clauses re-derived', flush=True)
            bad += not ok
        os.remove(os.path.join(out, 'base.cnf'))
    if bad:
        sys.exit(f'{bad} check(s) failed')
    print('CI_FORMULA_CHECKS_PASS')


if __name__ == '__main__':
    main()
