import sys, json, time, os
from cases import build_case
m = int(sys.argv[1]); case = sys.argv[2]; out = sys.argv[3]
flags = set(sys.argv[4:])
kw = dict(efx='noefx' not in flags, cardinality='nocard' not in flags, amax='noamax' not in flags)
sub = [f for f in flags if f.startswith('sub')]
if sub:
    kw['fix_least'] = int(sub[0][3:])
os.makedirs(out, exist_ok=True)
t = time.time()
enc, info = build_case(m, case, **kw)
info['flags'] = sorted(flags)
info['build_seconds'] = time.time() - t
n, h = enc.write_cnf(os.path.join(out, 'base.cnf'))
info['base_clauses'] = n; info['base_sha256'] = h
json.dump(info, open(os.path.join(out, 'build_info.json'), 'w'), indent=1)
print(json.dumps(info))
# export the variable dictionary (names assigned by the generator) for the independent verifier
json.dump({str(v): list(name) for v, name in enc.var_names.items()}, open(os.path.join(out, 'dictionary.json'), 'w'))
print('dictionary entries', len(enc.var_names))
