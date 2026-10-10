"""Eight-good normalisation control with structured random matrices so that every size profile
(1,1,5),(1,2,4),(1,3,3),(2,2,3) is exercised."""
import sys, numpy as np, json
from normalisation_control import canonicalise, check_case
m = 8
rng = np.random.default_rng(int(sys.argv[1]))
trials = int(sys.argv[2])
seen = {}
def generic(V):
    for ag in range(3):
        sums = set()
        for mk in range(1 << m):
            s_ = sum(V[ag][h] for h in range(m) if mk >> h & 1)
            if s_ in sums: return False
            sums.add(s_)
    return True
for t in range(trials):
    while True:
        k = int(rng.integers(0, 4))   # number of dominant goods
        big = rng.integers(400, 1200, size=(3, k)); small = rng.integers(1, 80, size=(3, m - k))
        V = np.concatenate([big, small], axis=1)
        # common-ish structure: shuffle columns, add agent-specific noise
        V = V[:, rng.permutation(m)].tolist()
        if generic(V): break
    a = int(rng.integers(3))
    case, Vn, a_can = canonicalise(V, m, a)
    bad, enc = check_case(m, case, Vn, a_can)
    seen[case] = seen.get(case, 0) + 1
    status = 'OK' if not bad else f'VIOLATED {len(bad)}: ' + str([[enc.var_names.get(abs(l), ('sign',)) for l in c] for c in bad[:3]])
    print(f'trial {t}: dominant {k} case {case} {status}', flush=True)
print('cases seen', seen)
