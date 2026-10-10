"""Positive control: evaluate the encoding on a concrete positive generic matrix.
Every clause except allocation-failure clauses must hold; the number of violated allocation
clauses must equal the number of PMMS allocations of the matrix."""
import sys, json, numpy as np
from signsat import build, TRUE, FALSE, popcount
from scout_sa import evaluate, all_allocations

def check(m, V, lemmas=True, cardinality=True, order=False):
    enc, info = build(m, lemmas=lemmas, cardinality=cardinality, order_agent0=order)
    full = (1 << m) - 1
    # assign sign vars
    val = {}
    for (a, code), var in enc.sign_var_of.items():
        vec = enc.vec_of_code(code)
        val[var] = sum(x * V[a][g] for g, x in enumerate(vec)) > 0
    # witnesses: z <-> a & b ; F <-> or z ; y <-> allocation PMMS on W
    for var, name in enc.var_names.items():
        if name[0] == 'wit':
            _, a, S1, T1, S2, T2 = name
            la = enc.sign_lit(a, S1, T1); lb = enc.sign_lit(a, S2, T2)
            def lv(l):
                return True if l == TRUE else False if l == FALSE else (val[abs(l)] if l > 0 else not val[abs(l)])
            val[var] = lv(la) and lv(lb)
    def lv(l):
        return True if l == TRUE else False if l == FALSE else (val[abs(l)] if l > 0 else not val[abs(l)])
    for var, name in enc.var_names.items():
        if name[0] == 'F':
            val[var] = any(lv(z) for z in enc.witness_lits[name[1:]])
    for var, name in enc.var_names.items():
        if name[0] == 'y':
            _, W, alloc = name
            val[var] = not any(lv(f) for f in enc.fails_lits(alloc))
    # evaluate clauses; identify allocation clauses as the ones we re-generate
    alloc_clauses = set()
    for alloc in enc.allocations_of(full):
        c = enc.simplify(enc.fails_lits(alloc))
        if c is not None:
            alloc_clauses.add(tuple(c))
    bad_other = 0; bad_alloc = 0
    for c in enc.clauses:
        ok = any(lv(l) for l in c)
        if not ok:
            if tuple(c) in alloc_clauses:
                bad_alloc += 1
            else:
                bad_other += 1
    cnt, _ = evaluate(np.array(V, dtype=np.int64), m, all_allocations(m))
    return bad_other, bad_alloc, cnt, info

if __name__ == '__main__':
    m = int(sys.argv[1])
    rng = np.random.default_rng(7)
    for trial in range(3):
        while True:
            V = rng.integers(1, 1000, size=(3, m)).tolist()
            # generic: all subset sums distinct per agent
            ok = True
            for a in range(3):
                sums = set()
                for mask in range(1 << m):
                    s = sum(V[a][g] for g in range(m) if mask >> g & 1)
                    if s in sums: ok = False; break
                    sums.add(s)
                if not ok: break
            if ok: break
        bo, ba, cnt, info = check(m, V)
        print(f'm={m} trial {trial}: other-clause violations {bo}, allocation-clause violations {ba}, PMMS allocations {cnt}', 'OK' if bo == 0 and ba == cnt else 'MISMATCH')
    if m == 8:
        V = [[143,133,137,22,20,21,29,38],[159,140,133,15,8,1,1,35],[135,133,134,13,11,20,28,40]]
        bo, ba, cnt, info = check(m, V)
        print('Golz-drop-d:', bo, ba, cnt, 'OK' if bo == 0 and ba == cnt else 'MISMATCH')
