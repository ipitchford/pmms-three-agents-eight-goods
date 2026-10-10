#!/usr/bin/env python3
"""Build the final trimmed evidence bundle.

For each certificate of the proof (six goods, three seven-good normal forms, ten eight-good formulas):
decompress the solver's LRAT proof, trim it with lrat-trim (ASCII output), check the trimmed proof with
lrat-check, compress it with gzip -9 into the bundle, and check it again with the standard-library Python checker
(two workers in parallel). Formulas, dictionaries and receipts are copied unchanged. Writes a progress log.

Usage: python3 make_trimmed_bundle.py OUT_DIR TMP_DIR
"""
import concurrent.futures as cf, json, os, shutil, subprocess, sys, time

SRC = os.path.dirname(os.path.abspath(__file__))
TRIM = os.path.join(SRC, 'tools', 'lrat-trim', 'lrat-trim')
LCHECK = os.path.join(SRC, 'tools', 'drat-trim', 'lrat-check')
PY = '/opt/homebrew/bin/python3'

CERTS = [('six_goods', 'run6_nolemmas', 'final.cnf', 'proof.lrat')]
CERTS += [(f'seven_goods/case{c}', f'rebuild7_lean/case{c}', 'base.cnf', 'proof.lrat.gz') for c in ('114', '123', '222')]
CERTS += [('eight_goods/case115', 'run8lean_case115', 'base.cnf', 'proof.lrat.gz')]
CERTS += [(f'eight_goods/case{c}_sub{s}', f'run8sub_case{c}_s{s}', 'base.cnf', 'proof.lrat.gz')
          for c in ('124', '133', '223') for s in range(3)]
KEEP = ['dictionary.json', 'build_info.json', 'cadical.out', 'verify_case_result.json', 'verify.out']


def log(msg):
    line = time.strftime('%H:%M:%S ') + msg
    print(line, flush=True)
    with open(os.path.join(OUT, 'BUILD_LOG.txt'), 'a') as f:
        f.write(line + '\n')


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def python_check(dst, cnf):
    t = time.time()
    r = run([PY, '-I', os.path.join(SRC, 'check_lrat_rup.py'), os.path.join(dst, cnf), os.path.join(dst, 'proof.lrat.gz')])
    open(os.path.join(dst, 'python_check.json'), 'w').write(r.stdout + r.stderr)
    ok = '"status": "VERIFIED"' in r.stdout
    log(f'python check {dst}: {"VERIFIED" if ok else "FAILED"} ({time.time()-t:.0f}s)')
    return dst, ok


def main():
    global OUT
    OUT, TMP = sys.argv[1], sys.argv[2]
    os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
    pool = cf.ThreadPoolExecutor(max_workers=2); futures = []
    summary = []
    for rel, srcrel, cnf, proof in CERTS:
        src = os.path.join(SRC, srcrel); dst = os.path.join(OUT, rel)
        if os.path.exists(os.path.join(dst, 'trim_summary.json')):
            log(f'skip {rel} (already done)'); summary.append(json.load(open(os.path.join(dst, 'trim_summary.json'))))
            futures.append(pool.submit(python_check, dst, cnf)) if not os.path.exists(os.path.join(dst, 'python_check.json')) else None
            continue
        os.makedirs(dst, exist_ok=True)
        shutil.copy2(os.path.join(src, cnf), os.path.join(dst, cnf))
        for f in KEEP:
            p = os.path.join(src, f)
            if os.path.exists(p):
                shutil.copy2(p, os.path.join(dst, 'solver_log.txt' if f == 'cadical.out' else f))
        t0 = time.time()
        raw = os.path.join(TMP, 'in.lrat'); out = os.path.join(TMP, 'out.lrat')
        psrc = os.path.realpath(os.path.join(src, proof))
        if psrc.endswith('.gz'):
            with open(raw, 'wb') as f:
                subprocess.run(['gunzip', '-c', psrc], stdout=f, check=True)
        else:
            shutil.copy2(psrc, raw)
        r = run([TRIM, '-a', os.path.join(dst, cnf), raw, out])
        open(os.path.join(dst, 'trim_log.txt'), 'w').write(r.stdout + r.stderr)
        os.remove(raw)
        if r.returncode not in (0, 20) or 's VERIFIED' not in (r.stdout + r.stderr):
            log(f'TRIM FAILED {rel}: rc={r.returncode}'); sys.exit(1)
        r = run([LCHECK, os.path.join(dst, cnf), out])
        open(os.path.join(dst, 'lrat_check.out'), 'w').write(r.stdout)
        if 'c VERIFIED' not in r.stdout:
            log(f'LRAT-CHECK FAILED {rel}'); sys.exit(1)
        with open(os.path.join(dst, 'proof.lrat.gz'), 'wb') as f:
            subprocess.run(['gzip', '-9', '-c', out], stdout=f, check=True)
        os.remove(out)
        import re
        added = re.search(r'Added clauses = (\d+)', open(os.path.join(dst, 'lrat_check.out')).read())
        nclauses = int(open(os.path.join(dst, cnf)).readline().split()[3])
        s = {'certificate': rel, 'source': srcrel, 'trimmed_steps': int(added.group(1)) - nclauses, 'clauses': nclauses,
             'proof_bytes': os.path.getsize(os.path.join(dst, 'proof.lrat.gz')), 'seconds': round(time.time() - t0)}
        json.dump(s, open(os.path.join(dst, 'trim_summary.json'), 'w'), indent=1)
        summary.append(s)
        log(f'trimmed {rel}: {s["trimmed_steps"]:,} steps, {s["proof_bytes"]/1e9:.2f} GB, lrat-check VERIFIED, {s["seconds"]}s')
        futures.append(pool.submit(python_check, dst, cnf))
    results = [f.result() for f in futures if f is not None]
    pool.shutdown()
    bad = [d for d, ok in results if not ok]
    json.dump(summary, open(os.path.join(OUT, 'TRIM_SUMMARY.json'), 'w'), indent=1)
    log('ALL CERTIFICATES TRIMMED AND CHECKED' if not bad else f'PYTHON CHECK FAILURES: {bad}')


if __name__ == '__main__':
    main()
