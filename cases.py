"""Case-split encodings.  A hypothetical positive generic counterexample on m goods is
normalised as follows (all steps are relabellings or valid selections):
  1. choose an agent a and let g be a's least valuable good;
  2. the restriction to M minus {g} has a PMMS allocation (theorem for <= 7 goods); among those
     allocations choose B maximising v_a(B_a), and among the allocations attaining that maximum one
     that is Pareto maximal (e.g. maximising the sum of own values within that tie class);
  3. relabel agents by nondecreasing |B_i|; break ties between agents with equal-size bundles by
     a third agent's strict comparison of the two bundles (generic => strict);
  4. relabel goods so that g is the last good and the bundles are consecutive blocks; inside each
     block order goods by agent 0's values.
Case = size profile.  The formula asserts: all sign rules, every complete allocation fails,
B is PMMS on M minus {g}, Pareto maximality of B (valid by the genericity argument in the paper),
tie-breaks, block orders, selectors c_i (at least one true) with: g least for agent i and B_i the
most valuable bundle of agent i among PMMS allocations of the restriction; all restriction lemmas;
the cardinality theorem; and optionally (efx=True) the EFX existence theorem of Chaudhury, Garg and
Mehlhorn (JACM 71(1), 2024).  Flags are recorded in build_info.json by build_case_cnf.py.
"""
import json, sys, time
from signsat import SignEncoder, TRUE, FALSE, popcount

CASES = {
    7: {'114': [[0], [1], [2, 3, 4, 5]], '123': [[0], [1, 2], [3, 4, 5]], '222': [[0, 1], [2, 3], [4, 5]]},
    8: {'115': [[0], [1], [2, 3, 4, 5, 6]], '124': [[0], [1, 2], [3, 4, 5, 6]],
        '133': [[0], [1, 2, 3], [4, 5, 6]], '223': [[0, 1], [2, 3], [4, 5, 6]]},
}


def mask(goods):
    return sum(1 << g for g in goods)


def build_case(m, case, lemmas=True, cardinality=True, pareto=True, least=True, tiebreak=True, efx=True, amax=True, fix_least=None):
    blocks = CASES[m][case]
    g = m - 1
    enc = SignEncoder(m)
    enc.add_sign_rules()
    info = {'m': m, 'case': case, 'blocks': blocks}
    info['alloc_clauses'] = enc.add_all_allocations_fail()
    if lemmas:
        info['lemma_y'] = enc.add_all_restriction_lemmas(min_size=4)
    if cardinality:
        info['cardinality_clauses'] = enc.add_cardinality_theorem()
    if efx:
        info['efx_x'] = enc.add_efx_lemma()
    B = tuple(mask(b) for b in blocks)
    W = (1 << m) - 1 - (1 << g)
    assert sum(B) == W
    # B is PMMS on W: all six failure literals false
    for f in enc.fails_lits(B):
        if f == TRUE:
            raise RuntimeError('case impossible')
        if f != FALSE:
            enc.add([-f])
    # Pareto maximality
    n_pareto = 0
    if pareto:
        for C in enc.allocations_of(W):
            if C == B:
                continue
            lits = [f for f in enc.fails_lits(C)]
            for i in range(3):
                if C[i] != B[i]:
                    lits.append(enc.sign_lit(i, B[i] & ~C[i], C[i] & ~B[i]))
            enc.add(lits); n_pareto += 1
    info['pareto_clauses'] = n_pareto
    # tie-breaks between equal-size bundles
    sizes = [popcount(b) for b in B]
    if tiebreak:
        for i, j in ((0, 1), (1, 2)):
            if sizes[i] == sizes[j]:
                k = 3 - i - j
                enc.add([enc.sign_lit(k, B[j], B[i])])   # v_k(B_i) < v_k(B_j)
                info[f'tiebreak_{i}{j}'] = f'agent {k}: v(B{i}) < v(B{j})'
    # within-block order by agent 0
    for b in blocks:
        enc.add_agent_order(0, b)
    # dropped good g is the least good of some agent
    if least:
        cs = []
        n_amax = 0
        for i in range(3):
            c = enc.new_var(('least', i))
            cs.append(c)
            for h in range(g):
                enc.add([-c, enc.sign_lit(i, 1 << h, 1 << g)])
            if amax:
                # B maximises agent i's own value among PMMS allocations of W
                for C in enc.allocations_of(W):
                    if C[i] == B[i]:
                        continue
                    lits = [-c] + enc.fails_lits(C) + [enc.sign_lit(i, B[i] & ~C[i], C[i] & ~B[i])]
                    enc.add(lits); n_amax += 1
        enc.add(cs)
        if fix_least is not None:
            # sub-case: the distinguished agent is agent fix_least (the three sub-cases cover the case)
            enc.add([cs[fix_least]])
            info['fixed_least_agent'] = fix_least
        info['amax_clauses'] = n_amax
    info.update(enc.describe())
    return enc, info


if __name__ == '__main__':
    m = int(sys.argv[1]); case = sys.argv[2]
    t = time.time()
    enc, info = build_case(m, case)
    info['build_seconds'] = time.time() - t
    print(json.dumps(info, indent=1))
