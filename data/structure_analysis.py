"""Structural analysis for the conceptual account of why eight goods suffice.

For each 3 x 8 integer instance, records:
  n_pmms            number of complete PMMS allocations (nonempty bundles)
  card              Theorem A.1 applies: at least two rows with top-2 sum <= bottom-3 sum
  safe_single       (S1) some agent i and good g with v_i(M - {g,h}) <= v_i(g) for all h != g
  ef                an envy-free complete allocation exists
  ext[a]            for agent a with least good g: some PMMS allocation of M restricts to a PMMS
                    allocation of M - {g} (with nonempty bundles)
  sizes             bundle-size profiles of the PMMS allocations
  dominant          number of goods each agent values above 1/6 of their total
Families: random uniform, deletions of the three published nine-good counterexamples,
dominant-goods (three large + five small), balanced (all values within a factor 1.5),
and simulated-annealing near-misses (instances minimising the number of PMMS allocations).
Output: structure_analysis.json and a printed summary.  Exact integer arithmetic.
"""
import json, itertools, sys, time
import numpy as np
from numba import njit
from scout_sa import subset_sums, mu2, all_allocations, evaluate

M = 8
FULL = (1 << M) - 1


@njit(cache=True)
def pmms_flags(S, MU, allocs):
    n = allocs.shape[0]
    out = np.zeros(n, dtype=np.bool_)
    for k in range(n):
        A0 = allocs[k, 0]; A1 = allocs[k, 1]; A2 = allocs[k, 2]
        ok = True
        for (i, D, E) in ((0, A0, A1), (0, A0, A2), (1, A1, A0), (1, A1, A2), (2, A2, A0), (2, A2, A1)):
            if S[i, D] < MU[i, D | E]:
                ok = False
                break
        out[k] = ok
    return out


def tables(V, m):
    S = np.zeros((3, 1 << m), dtype=np.int64); MU = np.zeros((3, 1 << m), dtype=np.int64)
    for i in range(3):
        S[i] = subset_sums(V[i], m); MU[i] = mu2(S[i], m)
    return S, MU


def is_pmms_alloc(S, MU, A):
    for i in range(3):
        for j in range(3):
            if i != j and S[i, A[i]] < MU[i, A[i] | A[j]]:
                return False
    return True


ALLOCS = all_allocations(M)


def analyse(V):
    V = np.array(V, dtype=np.int64)
    S, MU = tables(V, M)
    flags = pmms_flags(S, MU, ALLOCS)
    pm = ALLOCS[flags]
    res = {'n_pmms': int(flags.sum())}
    # cardinality theorem
    bal = []
    for i in range(3):
        r = sorted(V[i]); bal.append(bool(r[-1] + r[-2] <= r[0] + r[1] + r[2]))
    res['balanced_rows'] = int(sum(bal)); res['card'] = res['balanced_rows'] >= 2
    # safe singleton
    ss = False
    for i in range(3):
        tot = int(V[i].sum())
        for g in range(M):
            rest = tot - int(V[i][g])
            if all(rest - int(V[i][h]) <= int(V[i][g]) for h in range(M) if h != g):
                ss = True
    res['safe_single'] = ss
    # envy-free existence
    ef = False
    for A in ALLOCS:
        if all(S[i, A[i]] >= S[i, A[j]] for i in range(3) for j in range(3) if i != j):
            ef = True; break
    res['ef'] = ef
    # extension property
    ext = []
    for a in range(3):
        g = int(np.argmin(V[a])); bit = 1 << g
        ok = False
        for A in pm:
            B = [int(x) & ~bit for x in A]
            if all(B) and is_pmms_alloc(S, MU, B):
                ok = True; break
        ext.append(ok)
    res['ext'] = ext
    res['sizes'] = sorted({tuple(sorted(bin(int(x)).count('1') for x in A)) for A in pm})
    res['dominant'] = [int((V[i] * 6 > V[i].sum()).sum()) for i in range(3)]
    return res


def sa_near_miss(rng, iters=60000, maxval=200):
    V = rng.integers(1, maxval + 1, size=(3, M)).astype(np.int64)
    cur = evaluate(V, M, ALLOCS); best = cur; bestV = V.copy(); T = 2.0
    for _ in range(iters):
        W = V.copy(); i = rng.integers(3); g = rng.integers(M)
        if rng.random() < 0.8:
            W[i, g] = max(1, min(maxval, W[i, g] + rng.integers(-5, 6)))
        else:
            W[i, g] = rng.integers(1, maxval + 1)
        new = evaluate(W, M, ALLOCS)
        d = (new[0] - cur[0]) * 1000.0 + (new[1] - cur[1]) * 0.05
        if d <= 0 or rng.random() < np.exp(-d / T):
            V = W; cur = new
            if cur < best:
                best = cur; bestV = V.copy()
        T = max(0.05, T * 0.9999)
    return bestV.tolist()


def main():
    rng = np.random.default_rng(20261009)
    fam = {}
    fam['random'] = [rng.integers(1, 1000, size=(3, M)).tolist() for _ in range(300)]
    nine = {'Golz': [[143,133,137,22,20,21,29,38,2],[159,140,133,15,8,1,1,35,2],[135,133,134,13,11,20,28,40,2]],
            'Golz78': [[1,3,4,5,8,14,16,18,23],[10,2,15,6,8,22,31,30,32],[14,2,22,13,15,27,42,38,48]],
            'Bei': [[80,63,73,77,81,66,72,60,83],[86,60,74,76,78,75,73,66,80],[85,60,63,75,80,72,62,61,81]]}
    fam['nine_minus_one'] = [[[r[h] for h in range(9) if h != g] for r in V] for V in nine.values() for g in range(9)]
    dom = []
    for _ in range(300):
        big = rng.integers(300, 1000, size=(3, 3)); small = rng.integers(1, 60, size=(3, 5))
        V = np.concatenate([big, small], axis=1); dom.append(V[:, rng.permutation(M)].tolist())
    fam['dominant3'] = dom
    fam['balanced'] = [rng.integers(60, 90, size=(3, M)).tolist() for _ in range(300)]
    scout = []
    for s in (1, 2, 3):
        try:
            scout.append(json.load(open(f'scout/scout_seed{s}.json'))['best_matrix'])
        except Exception:
            pass
    t = time.time()
    for _ in range(int(sys.argv[1]) if len(sys.argv) > 1 else 12):
        scout.append(sa_near_miss(rng))
    fam['near_miss'] = scout
    print(f'near-miss search {time.time()-t:.0f}s', flush=True)
    out = {}
    for name, insts in fam.items():
        rows = [dict(analyse(V), matrix=V) for V in insts]
        out[name] = rows
        n = len(rows)
        mn = min(r['n_pmms'] for r in rows)
        print(f"{name:15s} n={n:4d} minPMMS={mn:4d} medianPMMS={int(np.median([r['n_pmms'] for r in rows])):4d} "
              f"card={sum(r['card'] for r in rows)/n:5.2f} safe1={sum(r['safe_single'] for r in rows)/n:5.2f} "
              f"EF={sum(r['ef'] for r in rows)/n:5.2f} ext_all3={sum(all(r['ext']) for r in rows)/n:5.2f} "
              f"ext_any={sum(any(r['ext']) for r in rows)/n:5.2f} card|safe1={sum(r['card'] or r['safe_single'] for r in rows)/n:5.2f}",
              flush=True)
    json.dump(out, open('structure_analysis.json', 'w'), indent=1)
    print('NEAR-MISS DETAIL')
    for r in sorted(out['near_miss'], key=lambda r: r['n_pmms'])[:8]:
        print(r['n_pmms'], 'sizes', r['sizes'], 'balanced_rows', r['balanced_rows'], 'dominant', r['dominant'],
              'safe1', r['safe_single'], 'EF', r['ef'], 'ext', r['ext'], r['matrix'])


if __name__ == '__main__':
    main()
