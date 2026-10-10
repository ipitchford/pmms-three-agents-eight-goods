#!/usr/bin/env python3
"""Replay every check of this evidence bundle. Reads the bundle; writes nothing inside it.

Checks, in order:
  1. every file's size and SHA-256 against MANIFEST.json;
  2. the published nine-good counterexamples have no PMMS allocation (exhaustive enumeration);
  3. for each of the fourteen certificates (six goods; seven-good normal forms; eight-good formulas):
     a. verify_case.py re-derives every clause of base.cnf from the definitions (exact equality required
        for the six- and eight-good formulas; the seven-good formulas use a subset of the derived set);
     b. lrat-check (compiled from tools/lrat-check.c) accepts proof.lrat.gz;
     c. with --python-lrat, the standard-library checker check_lrat_rup.py accepts it as well (slow);
  4. the eight-good certificates cover all four normal-form profiles.
Requires Python 3, a C compiler and gzip.  Usage: python3 -I verify_bundle.py --out RECEIPT.json [--python-lrat]
"""
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile, threading, time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
SIX = ['six_goods']
SEVEN = [('114', 'seven_goods/case114'), ('123', 'seven_goods/case123'), ('222', 'seven_goods/case222')]
EIGHT = [('115', None, 'eight_goods/case115')] + [(c, s, f'eight_goods/case{c}_sub{s}') for c in ('124', '133', '223') for s in range(3)]


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--python-lrat', action='store_true')
    ap.add_argument('--jobs', type=int, default=2, help='certificates checked in parallel')
    args = ap.parse_args()
    if os.path.exists(args.out):
        sys.exit('refusing to overwrite ' + args.out)
    T = tempfile.mkdtemp(prefix='pmms_replay_')
    res = {'started_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'checks': []}

    lock = threading.Lock()

    def record(name, ok, detail=''):
        with lock:
            res['checks'].append({'name': name, 'passed': bool(ok), 'detail': detail})
            print(('PASS ' if ok else 'FAIL ') + name, '' if ok else detail, flush=True)

    def run(cmd):
        return subprocess.run(cmd, capture_output=True, text=True, cwd=HERE)

    man = json.load(open(os.path.join(HERE, 'MANIFEST.json')))['files']
    bad = [r for r, v in man.items() if not os.path.exists(os.path.join(HERE, r))
           or os.path.getsize(os.path.join(HERE, r)) != v['bytes'] or sha(os.path.join(HERE, r)) != v['sha256']]
    record('manifest_digests', not bad, {'files': len(man), 'mismatch': bad[:10]})

    r = run([sys.executable, '-I', 'verify_nine_good.py', os.path.join(T, 'nine.json')])
    record('nine_good_counterexamples', 'UPPER_BOUND_NINE_VERIFIED' in r.stdout, r.stdout[-300:])

    lc = os.path.join(T, 'lrat-check')
    r = run(['cc', '-O2', '-o', lc, os.path.join(HERE, 'tools', 'lrat-check.c')])
    record('build_lrat_check', r.returncode == 0, r.stderr[-300:])

    def derive(label, d, goods, case, sub=None, exact=True):
        cmd = [sys.executable, '-I', 'verify_case.py', '--tmp', os.path.join(T, 'v_' + label), '--result', os.path.join(T, label + '.json'),
               d, '--goods', str(goods), '--case', case]
        if sub is not None:
            cmd += ['--sub', str(sub)]
        r = run(cmd)
        ok = 'ALL_CNF_CLAUSES_INDEPENDENTLY_DERIVED' in r.stdout and (not exact or '"expected_not_in_cnf": 0' in r.stdout)
        record(f'{label}_clauses_derived', ok, (r.stdout + r.stderr)[-300:])

    def check(label, d):
        cnf = os.path.join(HERE, d, 'base.cnf'); proof = os.path.join(HERE, d, 'proof.lrat.gz')
        r = subprocess.run(['bash', '-c', f'"{lc}" "{cnf}" <(gunzip -c "{proof}")'], capture_output=True, text=True)
        record(f'{label}_lrat_check', 'c VERIFIED' in r.stdout, r.stdout[-300:])
        if args.python_lrat:
            r = run([sys.executable, '-I', 'check_lrat_rup.py', cnf, proof])
            record(f'{label}_python_lrat', '"status": "VERIFIED"' in r.stdout, (r.stdout + r.stderr)[-300:])

    tasks = [('six_goods', 'six_goods', 6, 'plain', None, True)] + \
            [(f'seven_goods_case{c}', d, 7, c, None, False) for c, d in SEVEN] + \
            [(f'eight_goods_case{c}' + ('' if s is None else f'_sub{s}'), d, 8, c, s, True) for c, s, d in EIGHT]

    def one(t):
        label, d, goods, case, sub, exact = t
        derive(label, d, goods, case, sub, exact); check(label, d)

    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as ex:
        list(ex.map(one, tasks))
    covered = set()
    for c, s, d in EIGHT:
        label = f'eight_goods_case{c}' + ('' if s is None else f'_sub{s}')
        mine = [x for x in res['checks'] if x['name'] in (label + '_clauses_derived', label + '_lrat_check', label + '_python_lrat')]
        if len(mine) >= 2 and all(x['passed'] for x in mine):
            covered.add((c, s))
    profiles = {'115': [None], '124': [0, 1, 2], '133': [0, 1, 2], '223': [0, 1, 2]}
    record('eight_goods_all_profiles_covered', all((c, s) in covered for c, ss in profiles.items() for s in ss), sorted(map(str, covered)))
    shutil.rmtree(T, ignore_errors=True)
    res['status'] = 'PASS_ALL_BUNDLE_CHECKS' if all(x['passed'] for x in res['checks']) else 'FAIL'
    res['finished_utc'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    json.dump(res, open(args.out, 'w'), indent=1)
    print(res['status'])


if __name__ == '__main__':
    main()
