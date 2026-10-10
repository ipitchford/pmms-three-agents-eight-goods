"""Test the shape hypothesis H233: every 3-agent, 8-good additive instance has a PMMS allocation
whose bundle sizes are {2,3,3}.  Also tests the stronger cut-and-choose form H233cc: some agent u
receives a 2-set P, and the other two agents split the remaining six goods 3/3 so that the
'cutter' c1 regards the split as her best balanced split (maximin over 3/3 splits) and the
chooser c2 takes her preferred part, and the whole allocation is PMMS.
Method: family statistics, then simulated annealing minimising the number of {2,3,3} PMMS
allocations (an adversarial search for a counterexample to H233).
"""
import json, sys, time
import numpy as np
from numba import njit
from scout_sa import subset_sums, mu2, all_allocations, evaluate
from structure_analysis import pmms_flags, tables

M = 8
ALL = all_allocations(M)
pc = np.array([[bin(int(x)).count('1') for x in A] for A in ALL])
SHAPE = np.array([sorted(r) == [2, 3, 3] for r in pc])
A233 = ALL[SHAPE]


@njit(cache=True)
def count_flags(V, allocs, m):
    n = 1 << m
    S = np.zeros((3, n), dtype=np.int64); MU = np.zeros((3, n), dtype=np.int64)
    for i in range(3):
        S[i] = subset_sums(V[i], m); MU[i] = mu2(S[i], m)
    c = 0; slack = 0
    for k in range(allocs.shape[0]):
        A0 = allocs[k, 0]; A1 = allocs[k, 1]; A2 = allocs[k, 2]
        ok = True; ms = 1 << 60
        for (i, D, E) in ((0, A0, A1), (0, A0, A2), (1, A1, A0), (1, A1, A2), (2, A2, A0), (2, A2, A1)):
            d = S[i, D] - MU[i, D | E]
            if d < 0:
                ok = False; break
            if d < ms:
                ms = d
        if ok:
            c += 1; slack += ms
    return c, slack


def cut_choose_exists(V):
    V = np.array(V, dtype=np.int64)
    S, MU = tables(V, M)
    full = (1 << M) - 1
    for u in range(3):
        others = [a for a in range(3) if a != u]
        for P in range(full + 1):
            if bin(P).count('1') != 2:
                continue
            R = full ^ P
            # balanced 3/3 splits of R
            splits = []
            sub = R
            while sub:
                if bin(sub).count('1') == 3 and sub < (R ^ sub):
                    splits.append((sub, R ^ sub))
                sub = (sub - 1) & R
            for c1, c2 in (others, others[::-1]):
                best = max(min(S[c1, X], S[c1, Y]) for X, Y in splits)
                for X, Y in splits:
                    if min(S[c1, X], S[c1, Y]) != best:
                        continue
                    pick, rest = (X, Y) if S[c2, X] >= S[c2, Y] else (Y, X)
                    A = [0, 0, 0]; A[u] = P; A[c2] = pick; A[c1] = rest
                    if all(S[i, A[i]] >= MU[i, A[i] | A[j]] for i in range(3) for j in range(3) if i != j):
                        return True
    return False


def main():
    data = json.load(open('structure_analysis.json'))
    for fam, rows in data.items():
        has233 = 0; hascc = 0
        for r in rows:
            V = np.array(r['matrix'], dtype=np.int64)
            c, _ = count_flags(V, A233, M)
            has233 += c > 0
            hascc += cut_choose_exists(V)
        print(f'{fam:15s} n={len(rows):4d} has233={has233/len(rows):5.2f} has233_cutchoose={hascc/len(rows):5.2f}', flush=True)
    rng = np.random.default_rng(233)
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 900
    t0 = time.time(); best_global = None; found = []
    while time.time() - t0 < budget:
        V = rng.integers(1, 201, size=(3, M)).astype(np.int64)
        cur = count_flags(V, A233, M); best = cur; bestV = V.copy(); T = 2.0
        for _ in range(40000):
            W = V.copy(); i = rng.integers(3); g = rng.integers(M)
            if rng.random() < 0.8:
                W[i, g] = max(1, min(200, W[i, g] + rng.integers(-5, 6)))
            else:
                W[i, g] = rng.integers(1, 201)
            new = count_flags(W, A233, M)
            d = (new[0] - cur[0]) * 1000.0 + (new[1] - cur[1]) * 0.05
            if d <= 0 or rng.random() < np.exp(-d / T):
                V = W; cur = new
                if cur < best:
                    best = cur; bestV = V.copy()
                    if best[0] == 0:
                        break
            T = max(0.05, T * 0.9999)
        if best_global is None or best < best_global[0]:
            best_global = (best, bestV.tolist())
        if best[0] == 0:
            tot = evaluate(bestV, M, ALL)[0]
            found.append({'matrix': bestV.tolist(), 'total_pmms': int(tot)})
            print('H233 COUNTEREXAMPLE', bestV.tolist(), 'total PMMS allocations', tot, flush=True)
            if len(found) >= 3:
                break
    print('best 233-count found', best_global[0], best_global[1])
    json.dump({'best': best_global, 'counterexamples': found}, open('shape233_test.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
