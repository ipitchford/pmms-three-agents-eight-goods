"""Numerical scout: simulated annealing over integer 3 x m valuation matrices,
looking for a profile with NO PMMS allocation (3 agents).  Exact integer arithmetic.
Objective (minimise): (#PMMS allocations, total slack of PMMS allocations).
Usage: python scout_sa.py --goods 8 --seed 1 --iters 2000000 --maxval 200 --out scout_seed1.json
"""
import argparse, json, time, sys
import numpy as np
from numba import njit

@njit(cache=True)
def subset_sums(v, m):
    n = 1 << m
    s = np.zeros(n, dtype=np.int64)
    for mask in range(1, n):
        low = mask & (-mask)
        g = 0
        while (1 << g) != low:
            g += 1
        s[mask] = s[mask ^ low] + v[g]
    return s

@njit(cache=True)
def mu2(s, m):
    """mu[S] = max over T subset S of min(s[T], s[S\\T])."""
    n = 1 << m
    mu = np.zeros(n, dtype=np.int64)
    for S in range(1, n):
        best = 0
        T = S
        while True:
            a = s[T]; b = s[S ^ T]
            c = a if a < b else b
            if c > best:
                best = c
            if T == 0:
                break
            T = (T - 1) & S
        mu[S] = best
    return mu

@njit(cache=True)
def evaluate(V, m, allocs):
    """Return (#PMMS allocations, slack sum, worst-case ratio info)."""
    n = 1 << m
    S = np.zeros((3, n), dtype=np.int64)
    MU = np.zeros((3, n), dtype=np.int64)
    for i in range(3):
        S[i] = subset_sums(V[i], m)
        MU[i] = mu2(S[i], m)
    count = 0
    slack = 0
    for k in range(allocs.shape[0]):
        A0 = allocs[k, 0]; A1 = allocs[k, 1]; A2 = allocs[k, 2]
        ok = True
        minslack = 1 << 60
        # agent 0
        for (i, D, E) in ((0, A0, A1), (0, A0, A2), (1, A1, A0), (1, A1, A2), (2, A2, A0), (2, A2, A1)):
            own = S[i, D]
            mu = MU[i, D | E]
            if own < mu:
                ok = False
                break
            d = own - mu
            if d < minslack:
                minslack = d
        if ok:
            count += 1
            slack += minslack
    return count, slack

def all_allocations(m):
    """All complete allocations with nonempty bundles, as bitmask triples."""
    out = []
    full = (1 << m) - 1
    for A0 in range(1, 1 << m):
        rest = full ^ A0
        sub = rest
        while sub:
            A1 = sub
            A2 = rest ^ A1
            if A2:
                out.append((A0, A1, A2))
            sub = (sub - 1) & rest
    return np.array(out, dtype=np.int64)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--goods', type=int, default=8)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--iters', type=int, default=2_000_000)
    ap.add_argument('--maxval', type=int, default=200)
    ap.add_argument('--restarts', type=int, default=1000)
    ap.add_argument('--out', required=True)
    ap.add_argument('--init', default=None, help='JSON file with 3xm start matrix')
    args = ap.parse_args()
    m = args.goods
    rng = np.random.default_rng(args.seed)
    allocs = all_allocations(m)
    best_global = None
    log = []
    t0 = time.time()
    for restart in range(args.restarts):
        if args.init and restart == 0:
            V = np.array(json.load(open(args.init)), dtype=np.int64)
        else:
            V = rng.integers(1, args.maxval + 1, size=(3, m)).astype(np.int64)
        cur = evaluate(V, m, allocs)
        best = cur; bestV = V.copy()
        T = 2.0
        for it in range(args.iters):
            W = V.copy()
            r = rng.random()
            if r < 0.7:
                i = rng.integers(3); g = rng.integers(m)
                W[i, g] = max(1, min(args.maxval, W[i, g] + rng.integers(-5, 6)))
            elif r < 0.9:
                i = rng.integers(3); g = rng.integers(m)
                W[i, g] = rng.integers(1, args.maxval + 1)
            else:
                i = rng.integers(3); g = rng.integers(m); h = rng.integers(m)
                W[i, g], W[i, h] = W[i, h], W[i, g]
            new = evaluate(W, m, allocs)
            # lexicographic objective: count, then slack
            delta = (new[0] - cur[0]) * 1000.0 + (new[1] - cur[1]) * 0.05
            if delta <= 0 or rng.random() < np.exp(-delta / T):
                V = W; cur = new
                if cur < best:
                    best = cur; bestV = V.copy()
                    if best[0] == 0:
                        break
            T = max(0.05, T * 0.999995)
        entry = {'restart': restart, 'best_count': int(best[0]), 'best_slack': int(best[1]),
                 'matrix': bestV.tolist(), 'elapsed': time.time() - t0}
        log.append(entry)
        if best_global is None or best < best_global[0]:
            best_global = (best, bestV.copy())
        with open(args.out, 'w') as f:
            json.dump({'goods': m, 'seed': args.seed, 'best_count': int(best_global[0][0]),
                       'best_slack': int(best_global[0][1]), 'best_matrix': best_global[1].tolist(),
                       'restarts_done': restart + 1, 'log_tail': log[-50:]}, f, indent=1)
        print(f"restart {restart} best {best} global {best_global[0]} t={time.time()-t0:.0f}s", flush=True)
        if best_global[0][0] == 0:
            print("COUNTEREXAMPLE CANDIDATE FOUND", best_global[1].tolist(), flush=True)
            break

if __name__ == '__main__':
    main()
