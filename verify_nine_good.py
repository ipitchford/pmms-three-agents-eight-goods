#!/usr/bin/env python3
"""Exact enumeration check of the published nine-good counterexamples (upper bound m* <= 9).
Pure Python, standard library only.  For each instance, every one of the 3^9 complete allocations
(including those with empty bundles) is checked, and a strict failure witness is recorded for a
sample; the output states the number of PMMS allocations, which must be zero.
Also reports, for each instance and each deleted good, the number of PMMS allocations of the
eight-good restriction (all must be positive, consistent with Theorem 1)."""
import itertools, json, sys

INSTANCES = {
    'Golz_2026_main_Table1': [[143, 133, 137, 22, 20, 21, 29, 38, 2],
                              [159, 140, 133, 15, 8, 1, 1, 35, 2],
                              [135, 133, 134, 13, 11, 20, 28, 40, 2]],
    'Golz_2026_approx_78_79': [[1, 3, 4, 5, 8, 14, 16, 18, 23],
                               [10, 2, 15, 6, 8, 22, 31, 30, 32],
                               [14, 2, 22, 13, 15, 27, 42, 38, 48]],
    'Bei_et_al_2026_Table2': [[80, 63, 73, 77, 81, 66, 72, 60, 83],
                              [86, 60, 74, 76, 78, 75, 73, 66, 80],
                              [85, 60, 63, 75, 80, 72, 62, 61, 81]],
}


def mu_table(v, m):
    n = 1 << m
    s = [0] * n
    for mask in range(1, n):
        low = mask & -mask
        s[mask] = s[mask ^ low] + v[low.bit_length() - 1]
    mu = [0] * n
    for S in range(1, n):
        best = 0
        T = S
        while True:
            c = min(s[T], s[S ^ T])
            if c > best:
                best = c
            if T == 0:
                break
            T = (T - 1) & S
        mu[S] = best
    return s, mu


def count_pmms(V, m):
    tabs = [mu_table(v, m) for v in V]
    count = 0
    sample_fail = None
    for labels in itertools.product(range(3), repeat=m):
        A = [0, 0, 0]
        for g, l in enumerate(labels):
            A[l] |= 1 << g
        ok = True
        for i in range(3):
            s, mu = tabs[i]
            for j in range(3):
                if i != j and s[A[i]] < mu[A[i] | A[j]]:
                    ok = False
                    if sample_fail is None:
                        sample_fail = {'allocation_masks': A, 'agent': i, 'opponent': j,
                                       'own_value': s[A[i]], 'two_way_mms': mu[A[i] | A[j]]}
                    break
            if not ok:
                break
        if ok:
            count += 1
    return count, sample_fail


def main():
    report = {}
    for name, V in INSTANCES.items():
        c9, sample = count_pmms(V, 9)
        restr = []
        for g in range(9):
            W = [[row[h] for h in range(9) if h != g] for row in V]
            restr.append(count_pmms(W, 8)[0])
        report[name] = {'matrix': V, 'pmms_allocations_of_19683': c9,
                        'first_failure_witness': sample,
                        'pmms_allocations_after_deleting_each_good': restr}
        print(name, 'PMMS allocations:', c9, '| after deleting each good:', restr, flush=True)
    status = 'UPPER_BOUND_NINE_VERIFIED' if all(r['pmms_allocations_of_19683'] == 0 for r in report.values()) else 'FAILED'
    report['status'] = status
    json.dump(report, open(sys.argv[1] if len(sys.argv) > 1 else 'nine_good_check.json', 'w'), indent=1)
    print(status)


if __name__ == '__main__':
    main()
