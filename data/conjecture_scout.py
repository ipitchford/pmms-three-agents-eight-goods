"""Adversarial tests of two candidate statements (eight goods, three agents, exact integers).

Candidate A: if at least one agent's row is balanced (top-2 sum <= bottom-3 sum), then a (2,3,3)
  cut-and-choose PMMS allocation exists: some agent u receives a 2-set P, another agent c1 cuts
  the remaining six goods into a 3/3 split that maximises her smaller part among 3/3 splits,
  the third agent c2 takes her preferred part, and the allocation is PMMS.
  Variant A_top2: as A, but P must be u's own top two goods.
Candidate B: if some agent u has a good g with 2 v_u(g) >= v_u(M - g), then some agent w whose best
  good h is worth at least a third of her total can hold {h} alone while the other two agents
  divide the remaining seven goods by cut-and-choose (cutter maximises her smaller part over all
  bipartitions with nonempty parts, chooser takes her preferred part), and the allocation is PMMS.
Each test: simulated annealing restricted to instances satisfying the hypothesis, minimising the
number of successful constructions; a run reaching zero is a counterexample (re-verified in pure
Python before it is reported).
"""
import json, sys, time
import numpy as np
from numba import njit
from scout_sa import subset_sums, mu2

M = 8
FULL = (1 << M) - 1


def popc(x):
    return bin(x).count('1')


# precompute 2-sets and the 3/3 splits of each complement
TWO = np.array([P for P in range(FULL + 1) if popc(P) == 2], dtype=np.int64)
SPL = np.zeros((len(TWO), 10, 2), dtype=np.int64)
for k, P in enumerate(TWO):
    R = FULL ^ int(P); out = []
    for X in range(FULL + 1):
        if X & ~R == 0 and popc(X) == 3 and X < (R ^ X):
            out.append((X, R ^ X))
    assert len(out) == 10
    SPL[k] = np.array(out)
SINGLE_SPL = {}
for g in range(M):
    R = FULL ^ (1 << g); out = []
    for X in range(1, FULL + 1):
        if X & ~R == 0 and X != R and X < (R ^ X):
            out.append((X, R ^ X))
    SINGLE_SPL[g] = np.array(out, dtype=np.int64)
SSPL = np.stack([SINGLE_SPL[g] for g in range(M)])  # shape (8, 63, 2)


@njit(cache=True)
def tables(V):
    n = 1 << M
    S = np.zeros((3, n), dtype=np.int64); MU = np.zeros((3, n), dtype=np.int64)
    for i in range(3):
        S[i] = subset_sums(V[i], M); MU[i] = mu2(S[i], M)
    return S, MU


@njit(cache=True)
def is_pmms(S, MU, A0, A1, A2):
    for (i, D, E) in ((0, A0, A1), (0, A0, A2), (1, A1, A0), (1, A1, A2), (2, A2, A0), (2, A2, A1)):
        if S[i, D] < MU[i, D | E]:
            return False
    return True


@njit(cache=True)
def count_A(V, TWO, SPL, top2_only):
    S, MU = tables(V)
    cnt = 0
    for u in range(3):
        # u's top-two mask
        order = np.argsort(-V[u])
        t2 = (1 << order[0]) | (1 << order[1])
        for k in range(TWO.shape[0]):
            P = TWO[k]
            if top2_only and P != t2:
                continue
            for oi in range(2):
                c1 = (u + 1 + oi) % 3
                c2 = 3 - u - c1
                best = -1
                for s in range(10):
                    X = SPL[k, s, 0]; Y = SPL[k, s, 1]
                    mn = min(S[c1, X], S[c1, Y])
                    if mn > best:
                        best = mn
                for s in range(10):
                    X = SPL[k, s, 0]; Y = SPL[k, s, 1]
                    if min(S[c1, X], S[c1, Y]) != best:
                        continue
                    for pick in range(2):
                        Bc2 = X if pick == 0 else Y
                        Bc1 = Y if pick == 0 else X
                        if S[c2, Bc2] < S[c2, Bc1]:
                            continue
                        A = np.zeros(3, dtype=np.int64)
                        A[u] = P; A[c1] = Bc1; A[c2] = Bc2
                        if is_pmms(S, MU, A[0], A[1], A[2]):
                            cnt += 1
    return cnt


@njit(cache=True)
def count_B(V, SSPL):
    S, MU = tables(V)
    cnt = 0
    for w in range(3):
        h = np.argmax(V[w])
        if 3 * V[w, h] < V[w].sum():
            continue
        for oi in range(2):
            c1 = (w + 1 + oi) % 3
            c2 = 3 - w - c1
            best = -1
            for s in range(SSPL.shape[1]):
                X = SSPL[h, s, 0]; Y = SSPL[h, s, 1]
                mn = min(S[c1, X], S[c1, Y])
                if mn > best:
                    best = mn
            for s in range(SSPL.shape[1]):
                X = SSPL[h, s, 0]; Y = SSPL[h, s, 1]
                if min(S[c1, X], S[c1, Y]) != best:
                    continue
                for pick in range(2):
                    Bc2 = X if pick == 0 else Y
                    Bc1 = Y if pick == 0 else X
                    if S[c2, Bc2] < S[c2, Bc1]:
                        continue
                    A = np.zeros(3, dtype=np.int64)
                    A[w] = 1 << h; A[c1] = Bc1; A[c2] = Bc2
                    if is_pmms(S, MU, A[0], A[1], A[2]):
                        cnt += 1
    return cnt


def hyp_A(V):
    for row in V:
        r = sorted(row)
        if r[-1] + r[-2] <= r[0] + r[1] + r[2]:
            return True
    return False


def hyp_B(V):
    for row in V:
        if 2 * max(row) >= sum(row) - max(row):
            return True
    return False


def sample(rng, hyp, maxval):
    while True:
        V = rng.integers(1, maxval + 1, size=(3, M)).astype(np.int64)
        if hyp == 'A':
            i = rng.integers(3); V[i] = rng.integers(60, 90, size=M)
        else:
            i = rng.integers(3); V[i, rng.integers(M)] = rng.integers(3 * maxval, 6 * maxval)
        if (hyp_A if hyp == 'A' else hyp_B)(V.tolist()):
            return V


def search(name, counter, hyp, budget, rng, maxval=200):
    t0 = time.time(); best = None; runs = 0
    while time.time() - t0 < budget:
        V = sample(rng, hyp, maxval); cur = counter(V); bV = V.copy(); bc = cur; T = 3.0; runs += 1
        for _ in range(20000):
            W = V.copy(); i = rng.integers(3); g = rng.integers(M)
            if rng.random() < 0.8:
                W[i, g] = max(1, W[i, g] + rng.integers(-6, 7))
            else:
                W[i, g] = rng.integers(1, 6 * maxval)
            if not (hyp_A if hyp == 'A' else hyp_B)(W.tolist()):
                continue
            new = counter(W)
            if new <= cur or rng.random() < np.exp(-(new - cur) / T):
                V = W; cur = new
                if cur < bc:
                    bc = cur; bV = V.copy()
                    if bc == 0:
                        break
            T = max(0.05, T * 0.9997)
        if best is None or bc < best[0]:
            best = (bc, bV.tolist())
        if bc == 0:
            break
    print(f'{name}: runs={runs} time={time.time()-t0:.0f}s fewest successful constructions={best[0]} instance={best[1]}', flush=True)
    return best


def main():
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 300
    rng = np.random.default_rng(42)
    res = {}
    res['A'] = search('Candidate A (any P)', lambda V: count_A(V, TWO, SPL, False), 'A', budget, rng)
    res['A_top2'] = search('Candidate A_top2 (P = u top two)', lambda V: count_A(V, TWO, SPL, True), 'A', budget, rng)
    res['B'] = search('Candidate B (singleton)', lambda V: count_B(V, SSPL), 'B', budget, rng)
    json.dump(res, open('conjecture_scout.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
