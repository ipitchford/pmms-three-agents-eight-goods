#!/usr/bin/env python3
"""Put the ten eight-good certificates, downloaded separately from the Zenodo record, into the package layout.

The core archive holds everything except the ten eight-good proofs, which are separate files in the record
(https://doi.org/10.5281/zenodo.23284137).  A proof of at most 600 MB is one file, eight_goods_<case>.proof.lrat.gz;
a larger one is split into consecutive 400 MiB parts eight_goods_<case>.proof.lrat.gz.part00, .part01, ...
This script joins the parts, checks the result against the SHA-256 digest that MANIFEST.json records for
eight_goods/<case>/proof.lrat.gz, and puts it there.  A whole file can be linked instead of copied with --link.
Nothing is placed unless its digest matches.

Usage: python3 -I place_proofs.py DOWNLOAD_DIR [--link]
"""
import hashlib, json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = ['case115'] + [f'case{c}_sub{s}' for c in ('124', '133', '223') for s in range(3)]


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    args = [a for a in sys.argv[1:] if a != '--link']
    if len(args) != 1:
        sys.exit(__doc__)
    src, link = args[0], '--link' in sys.argv[1:]
    man = json.load(open(os.path.join(HERE, 'MANIFEST.json')))['files']
    bad = 0
    for c in CASES:
        rel = f'eight_goods/{c}/proof.lrat.gz'
        want = man[rel]['sha256']
        dst = os.path.join(HERE, rel)
        if os.path.exists(dst) and sha(dst) == want:
            print(f'present  {rel}')
            continue
        if os.path.lexists(dst):
            os.remove(dst)
        p = os.path.join(src, f'eight_goods_{c}.proof.lrat.gz')
        parts = sorted(n for n in os.listdir(src) if n.startswith(f'eight_goods_{c}.proof.lrat.gz.part'))
        if os.path.exists(p):
            if os.path.getsize(p) != man[rel]['bytes'] or sha(p) != want:
                print(f'MISMATCH {p}'); bad += 1; continue
            if link:
                os.symlink(os.path.abspath(p), dst)
            else:
                shutil.copyfile(p, dst)
        elif parts:
            expect = [f'eight_goods_{c}.proof.lrat.gz.part{k:02d}' for k in range(len(parts))]
            if parts != expect:
                print(f'PARTS NOT CONSECUTIVE for {c}'); bad += 1; continue
            tmp = dst + '.joining'
            with open(tmp, 'wb') as out:
                for n in parts:
                    with open(os.path.join(src, n), 'rb') as f:
                        shutil.copyfileobj(f, out, 1 << 24)
            if os.path.getsize(tmp) != man[rel]['bytes'] or sha(tmp) != want:
                os.remove(tmp); print(f'MISMATCH after joining {len(parts)} parts of {c}'); bad += 1; continue
            os.replace(tmp, dst)
        else:
            print(f'MISSING  {p}'); bad += 1; continue
        print(f'placed   {rel}')
    if bad:
        sys.exit(f'{bad} certificate(s) missing or not matching MANIFEST.json')
    print('ALL_TEN_PROOFS_PLACED')


if __name__ == '__main__':
    main()
