"""Control for the case normalisation: canonicalise random positive generic matrices exactly as
the proof prescribes and check that every clause of the case formula EXCEPT the complete
allocation failure clauses is satisfied by the canonical matrix."""
import sys, json, itertools
import numpy as np
from signsat import TRUE, FALSE, popcount
from cases import build_case, CASES, mask

def is_pmms(V, alloc, goods):
    for i in range(3):
        for j in range(3):
            if i == j: continue
            own = sum(V[i][g] for g in alloc[i]); pool = alloc[i] | alloc[j]
            pl = sorted(pool)
            best = 0
            for r in range(len(pl) + 1):
                for T in itertools.combinations(pl, r):
                    a = sum(V[i][g] for g in T); b = sum(V[i][g] for g in pl if g not in T)
                    best = max(best, min(a, b))
            if own < best: return False
    return True

def allocations(goods):
    goods = list(goods)
    for labels in itertools.product(range(3), repeat=len(goods)):
        A = [set(), set(), set()]
        for g, l in zip(goods, labels): A[l].add(g)
        if all(A): yield tuple(frozenset(x) for x in A)

def canonicalise(V, m, a):
    g = min(range(m), key=lambda h: V[a][h])
    W = [h for h in range(m) if h != g]
    pm = [A for A in allocations(W) if is_pmms(V, A, W)]
    assert pm
    best = max(sum(V[a][h] for h in A[a]) for A in pm)
    cand = [A for A in pm if sum(V[a][h] for h in A[a]) == best]
    # Pareto maximal among cand
    def dominates(C, B):
        ge = all(sum(V[i][h] for h in C[i]) >= sum(V[i][h] for h in B[i]) for i in range(3))
        gt = any(sum(V[i][h] for h in C[i]) > sum(V[i][h] for h in B[i]) for i in range(3))
        return ge and gt
    B = max(cand, key=lambda A: sum(sum(V[i][h] for h in A[i]) for i in range(3)))
    assert not any(dominates(C, B) for C in cand)
    # agent relabelling by size with tie-breaks
    agents = [0, 1, 2]
    agents.sort(key=lambda i: len(B[i]))
    # fix ties: for equal sizes, need third agent k: v_k(B_first) < v_k(B_second)
    def ok(order):
        for p, q in ((0, 1), (1, 2)):
            i, j = order[p], order[q]
            if len(B[i]) == len(B[j]):
                k = order[3 - p - q]
                if not (sum(V[k][h] for h in B[i]) < sum(V[k][h] for h in B[j])): return False
        return True
    found = None
    for perm in itertools.permutations(range(3)):
        if [len(B[i]) for i in perm] == sorted(len(B[i]) for i in range(3)) and ok(perm):
            found = perm; break
    assert found is not None, 'no valid agent relabelling'
    order = list(found)
    case = ''.join(str(len(B[i])) for i in order)
    # goods relabelling: blocks consecutive, within block by new agent 0's values, g last
    new_goods = []
    a0 = order[0]
    for i in order:
        blk = sorted(B[i], key=lambda h: V[a0][h])
        new_goods += blk
    new_goods.append(g)
    Vn = [[V[i][h] for h in new_goods] for i in order]
    return case, Vn, order.index(a)

def check_case(m, case, Vn, a_can):
    enc, info = build_case(m, case)
    val = {}
    for (ag, code), var in enc.sign_var_of.items():
        vec = enc.vec_of_code(code)
        val[var] = sum(x * Vn[ag][h] for h, x in enumerate(vec)) > 0
    def lv(l):
        return True if l == TRUE else False if l == FALSE else (val[abs(l)] if l > 0 else not val[abs(l)])
    for var, name in enc.var_names.items():
        if name[0] == 'wit':
            _, ag, S1, T1, S2, T2 = name
            val[var] = lv(enc.sign_lit(ag, S1, T1)) and lv(enc.sign_lit(ag, S2, T2))
    for var, name in enc.var_names.items():
        if name[0] == 'F':
            val[var] = any(lv(z) for z in enc.witness_lits[name[1:]])
    for var, name in enc.var_names.items():
        if name[0] == 'y':
            val[var] = not any(lv(f) for f in enc.fails_lits(name[2]))
        elif name[0] == 'efx':
            alloc = name[1]; ok = True
            for i in range(3):
                for j in range(3):
                    if i == j: continue
                    sub = alloc[j]
                    while sub:
                        gg = sub & (-sub); sub ^= gg
                        if lv(enc.sign_lit(i, alloc[j] ^ gg, alloc[i])): ok = False
            val[var] = ok
        elif name[0] == 'least':
            i = name[1]
            val[var] = (i == a_can)
            if i == a_can:
                assert all(Vn[i][h] > Vn[i][m - 1] for h in range(m - 1))
    full = (1 << m) - 1
    alloc_clauses = set()
    for alloc in enc.allocations_of(full):
        c = enc.simplify(enc.fails_lits(alloc))
        if c is not None: alloc_clauses.add(tuple(c))
    bad = [c for c in enc.clauses if not any(lv(l) for l in c) and tuple(c) not in alloc_clauses]
    return bad, enc

if __name__ == '__main__':
    m = int(sys.argv[1]); trials = int(sys.argv[2])
    rng = np.random.default_rng(int(sys.argv[3]) if len(sys.argv) > 3 else 11)
    seen = {}
    for t in range(trials):
        while True:
            V = rng.integers(1, 2000, size=(3, m)).tolist()
            ok = True
            for ag in range(3):
                sums = set()
                for mk in range(1 << m):
                    s_ = sum(V[ag][h] for h in range(m) if mk >> h & 1)
                    if s_ in sums: ok = False; break
                    sums.add(s_)
                if not ok: break
            if ok: break
        a = int(rng.integers(3))
        case, Vn, a_can = canonicalise(V, m, a)
        bad, enc = check_case(m, case, Vn, a_can)
        seen[case] = seen.get(case, 0) + 1
        status = 'OK' if not bad else f'VIOLATED {len(bad)}: ' + str([[enc.var_names.get(abs(l), ('sign',)) for l in c] for c in bad[:3]])
        print(f'trial {t}: case {case} {status}', flush=True)
    print('cases seen', seen)
