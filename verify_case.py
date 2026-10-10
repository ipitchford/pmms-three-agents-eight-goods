#!/usr/bin/env python3
"""Independent semantic verifier for a case CNF of the eight-good (or seven-good) PMMS proof.

Input: a run directory containing base.cnf (the formula refuted by the LRAT proof) and
dictionary.json (the generator's variable names).  The verifier trusts NOTHING in the
generator's code: it re-derives, from the mathematical definitions and the variable meanings,
the set EXPECTED of clauses that are valid for every positive generic counterexample normalised
into this case, and checks that every clause of base.cnf belongs to EXPECTED.  It also checks
that the dictionary is a consistent naming, that the case list covers every size profile, and
that the long "some allocation is PMMS / EFX" clauses are complete.

Only the Python standard library is used.  Clause membership is checked through sorted text
files to keep memory small (use --tmp for the work directory).

Validity sources (what makes a clause valid):
  sign rules       : linear arithmetic over a positive generic valuation
  definitions      : witness, failure, lemma-selector, EFX-selector and least-selector variables
                     are defined by their meanings
  allocation fails : the instance is a counterexample
  restriction lemma: every sub-instance with 4..7 goods has a PMMS allocation (theorem for <= 7 goods)
  EFX lemma        : every three-agent additive instance has an EFX allocation (Chaudhury-Garg-Mehlhorn)
  cardinality      : Theorem 6.1 of the impasse memorandum (two rows must be top-heavy)
  case clauses     : the normalisation procedure (fixed PMMS allocation B of M minus the last good,
                     own-value maximality for the agent whose least good was dropped, Pareto
                     maximality, tie-breaks and block orders)
"""
import argparse, itertools, json, os, subprocess, sys, hashlib, time
from collections import Counter

BIG = 1 << 40
TRUE, FALSE = BIG, -BIG


def fail(msg):
    print('VERIFICATION FAILED:', msg)
    sys.exit(1)


class Verifier:
    def __init__(self, m, case_blocks, dictionary):
        self.m = m
        self.goods = list(range(m))
        self.blocks = case_blocks
        self.names = {}
        for v, name in dictionary.items():
            self.names[int(v)] = tuple(tuple(x) if isinstance(x, list) else x for x in name)
        self.sign = {}   # (agent, vec) -> var for canonical vec
        self.wit = {}    # (agent, S1, T1, S2, T2) -> var
        self.Fvar = {}   # (agent, D, E) -> var
        self.yvar = {}   # (W, alloc) -> var
        self.efx = {}    # alloc -> var
        self.least = {}  # agent -> var
        self.nvars = max(self.names) if self.names else 0
        if len(set(self.names.values())) != len(self.names):
            fail('two variables share the same meaning in the dictionary')
        self._index_dictionary()

    # --- vectors ---
    def decode(self, code):
        v = []
        for _ in range(self.m):
            v.append(code % 3 - 1); code //= 3
        return tuple(v)

    @staticmethod
    def canonical(vec):
        for x in vec:
            if x != 0:
                return vec if x > 0 else tuple(-y for y in vec)
        return vec

    def lit(self, agent, vec):
        """literal for  vec . v_agent > 0  under positivity and genericity."""
        if all(x == 0 for x in vec):
            return FALSE
        if all(x >= 0 for x in vec):
            return TRUE
        if all(x <= 0 for x in vec):
            return FALSE
        c = self.canonical(vec)
        var = self.sign.get((agent, c))
        if var is None:
            fail(f'missing sign variable for agent {agent} vector {c}')
        return var if c == vec else -var

    def cmp_lit(self, agent, S, T):
        """literal for v_agent(S) > v_agent(T), S and T disjoint sets of goods."""
        if S & T:
            fail('cmp_lit with overlapping sets')
        vec = tuple(1 if g in S else -1 if g in T else 0 for g in self.goods)
        return self.lit(agent, vec)

    def _index_dictionary(self):
        m = self.m
        for var, name in self.names.items():
            kind = name[0]
            if kind == 'sign':
                _, a, code = name
                vec = self.decode(code)
                if vec != self.canonical(vec) or all(x >= 0 for x in vec) or all(x <= 0 for x in vec):
                    fail(f'sign var {var} has non-canonical or constant vector {vec}')
                key = (a, vec)
                if key in self.sign:
                    fail(f'duplicate sign variable for {key}')
                self.sign[key] = var
            elif kind == 'wit':
                _, a, S1, T1, S2, T2 = name
                S1, T1, S2, T2 = (self.setof(x) for x in (S1, T1, S2, T2))
                sets = [S1, T1, S2, T2]
                for i in range(4):
                    for j in range(i + 1, 4):
                        if sets[i] & sets[j]:
                            fail(f'witness {var} has overlapping parts')
                if not S1 or not S2 or not (T1 | T2):
                    fail(f'witness {var} degenerate')
                self.wit[(a, S1, T1, S2, T2)] = var
            elif kind == 'F':
                _, a, D, E = name
                D, E = self.setof(D), self.setof(E)
                if not D or not E or D & E:
                    fail(f'F var {var} degenerate')
                self.Fvar[(a, D, E)] = var
            elif kind == 'y':
                _, W, alloc = name
                W = self.setof(W); alloc = tuple(self.setof(x) for x in alloc)
                self.check_partition(alloc, W, f'y var {var}')
                if not (4 <= len(W) <= 7) or len(W) >= m:
                    fail(f'y var {var}: lemma set W of size {len(W)} not allowed')
                self.yvar[(W, alloc)] = var
            elif kind == 'efx':
                alloc = tuple(self.setof(x) for x in name[1])
                self.check_partition(alloc, frozenset(self.goods), f'efx var {var}')
                self.efx[alloc] = var
            elif kind == 'least':
                if name[1] not in (0, 1, 2) or name[1] in self.least:
                    fail(f'least var {var} bad')
                self.least[name[1]] = var
            else:
                fail(f'unknown variable kind {kind}')

    def setof(self, mask):
        return frozenset(g for g in self.goods if mask >> g & 1)

    @staticmethod
    def check_partition(alloc, W, what):
        if len(alloc) != 3 or any(not A for A in alloc):
            fail(f'{what}: not three nonempty bundles')
        if alloc[0] | alloc[1] | alloc[2] != W or (alloc[0] & alloc[1]) or (alloc[0] & alloc[2]) or (alloc[1] & alloc[2]):
            fail(f'{what}: not a partition of its ground set')

    # --- PMMS failure structure (recomputed independently) ---
    def failure_literal(self, agent, D, E):
        """literal meaning: agent holding D fails the PMMS comparison against bundle E.
        Also returns the complete witness literal list (None if the comparison never fails)."""
        if len(E) <= 1:
            return FALSE, None
        pool = sorted(D | E)
        witnesses = []
        seen_cuts = set()
        for r in range(len(pool) + 1):
            for X in itertools.combinations(pool, r):
                X = frozenset(X); Y = frozenset(pool) - X
                if not (X & E) or not (Y & E):
                    continue            # a side inside D can never beat D
                key = frozenset((X, Y))
                if key in seen_cuts:
                    continue
                seen_cuts.add(key)
                # side X beats D  <=>  v(X - D) > v(D - X);  side Y beats D <=> v(Y - D) > v(D - Y)
                S1, T1 = X & E, D - X
                S2, T2 = Y & E, D - Y
                a = self.cmp_lit(agent, S1, T1)
                b = self.cmp_lit(agent, S2, T2)
                if a == FALSE or b == FALSE:
                    continue
                if a == TRUE:
                    witnesses.append(b)
                elif b == TRUE:
                    witnesses.append(a)
                else:
                    z = self.wit.get((agent, S1, T1, S2, T2))
                    if z is None:
                        z = self.wit.get((agent, S2, T2, S1, T1))
                    if z is None:
                        fail(f'no witness variable for agent {agent} cut {sorted(S1)},{sorted(T1)} | {sorted(S2)},{sorted(T2)}')
                    witnesses.append(z)
        witnesses = sorted(set(witnesses))
        if not witnesses:
            return FALSE, None
        f = self.Fvar.get((agent, D, E))
        if f is None:
            fail(f'no failure variable for agent {agent} D={sorted(D)} E={sorted(E)}')
        return f, witnesses

    def fails(self, alloc):
        A0, A1, A2 = alloc
        return [self.failure_literal(0, A0, A1)[0], self.failure_literal(0, A0, A2)[0],
                self.failure_literal(1, A1, A0)[0], self.failure_literal(1, A1, A2)[0],
                self.failure_literal(2, A2, A0)[0], self.failure_literal(2, A2, A1)[0]]

    def allocations(self, W):
        W = sorted(W)
        for labels in itertools.product(range(3), repeat=len(W)):
            A = [set(), set(), set()]
            for g, l in zip(W, labels):
                A[l].add(g)
            if all(A):
                yield tuple(frozenset(x) for x in A)

    # --- expected clause generation ---
    def emit(self, out, lits):
        """write a simplified clause; drop tautologies and clauses containing TRUE."""
        s = set()
        for l in lits:
            if l == TRUE:
                return
            if l == FALSE:
                continue
            s.add(l)
        for l in s:
            if -l in s:
                return
        if not s:
            fail('empty expected clause')
        out.write(' '.join(map(str, sorted(s))) + '\n')

    def gen_sign_rules(self, out):
        m = self.m
        cube = [-1, 0, 1]
        n = 0
        # addition rule
        pairs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, -1), (-1, 1)]
        for a in range(3):
            for combo in itertools.product(pairs, repeat=m):
                r = tuple(x for x, _ in combo); s = tuple(y for _, y in combo)
                if not any(r) or not any(s):
                    continue
                t = tuple(x + y for x, y in zip(r, s))
                if not any(t):
                    continue
                self.emit(out, [-self.lit(a, r), -self.lit(a, s), self.lit(a, t)]); n += 1
        # halving rule r + s = 2t
        pairs2 = [(0, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        for a in range(3):
            for combo in itertools.product(pairs2, repeat=m):
                r = tuple(x for x, _ in combo); s = tuple(y for _, y in combo)
                if not any(r) or not any(s) or r == s:
                    continue
                t = tuple((x + y) // 2 for x, y in zip(r, s))
                if not any(t):
                    continue
                self.emit(out, [-self.lit(a, r), -self.lit(a, s), self.lit(a, t)]); n += 1
        return n

    def gen_definitions(self, out):
        n = 0
        for (a, S1, T1, S2, T2), z in self.wit.items():
            la = self.cmp_lit(a, S1, T1); lb = self.cmp_lit(a, S2, T2)
            if la in (TRUE, FALSE) or lb in (TRUE, FALSE):
                fail(f'witness {z} on constant atoms')
            self.emit(out, [-z, la]); self.emit(out, [-z, lb]); self.emit(out, [z, -la, -lb]); n += 3
        for (a, D, E), f in self.Fvar.items():
            f2, wl = self.failure_literal(a, D, E)
            if f2 != f:
                fail('failure variable mismatch')
            self.emit(out, [-f] + wl); n += 1
            for z in wl:
                self.emit(out, [f, -z]); n += 1
        return n

    def gen_allocation_failures(self, out):
        n = 0
        for alloc in self.allocations(frozenset(self.goods)):
            self.emit(out, self.fails(alloc)); n += 1
        return n

    def gen_restriction_lemmas(self, out):
        """For each W in the dictionary's lemma sets: all nonempty allocations of W, with the
        selector clauses; the long clause must mention every allocation that can be PMMS."""
        n = 0
        Ws = sorted({W for (W, _) in self.yvar}, key=lambda W: (len(W), sorted(W)))
        for W in Ws:
            ys = []
            for alloc in self.allocations(W):
                fl = self.fails(alloc)
                if any(f == TRUE for f in fl):
                    continue          # always fails PMMS: cannot be the guaranteed allocation
                fl = [f for f in fl if f != FALSE]
                if not fl:
                    fail(f'lemma set {sorted(W)} has an always-PMMS allocation; generator should have skipped')
                y = self.yvar.get((W, alloc))
                if y is None:
                    fail(f'lemma selector missing for W={sorted(W)} alloc={[sorted(x) for x in alloc]}')
                for f in fl:
                    self.emit(out, [-y, -f]); n += 1
                ys.append(y)
            self.emit(out, ys); n += 1
        return n

    def gen_efx_lemma(self, out):
        n = 0
        xs = []
        for alloc in self.allocations(frozenset(self.goods)):
            x = self.efx.get(alloc)
            if x is None:
                fail('EFX selector missing for an allocation')
            for i in range(3):
                for j in range(3):
                    if i == j:
                        continue
                    for g in alloc[j]:
                        l = self.cmp_lit(i, alloc[j] - {g}, alloc[i])
                        if l == TRUE:
                            fail('EFX condition constant true; unexpected')
                        if l != FALSE:
                            self.emit(out, [-x, -l]); n += 1
            xs.append(x)
        self.emit(out, xs); n += 1
        return n

    def gen_cardinality(self, out):
        m = self.m
        if (m + 1) % 3:
            return 0
        q = (m + 1) // 3
        lits_of = {}
        for a in range(3):
            L = []
            for P in itertools.combinations(self.goods, q - 1):
                for T in itertools.combinations([g for g in self.goods if g not in P], q):
                    L.append(self.cmp_lit(a, frozenset(P), frozenset(T)))
            lits_of[a] = L
        n = 0
        for i, j in itertools.combinations(range(3), 2):
            self.emit(out, lits_of[i] + lits_of[j]); n += 1
        return n

    def gen_case_clauses(self, out):
        m = self.m
        g = m - 1
        W = frozenset(self.goods) - {g}
        B = tuple(frozenset(b) for b in self.blocks)
        self.check_partition(B, W, 'case allocation')
        sizes = [len(b) for b in B]
        if sizes != sorted(sizes):
            fail('case blocks not sorted by size')
        n = 0
        # B is PMMS on W
        for f in self.fails(B):
            if f == TRUE:
                fail('case allocation can never be PMMS')
            if f != FALSE:
                self.emit(out, [-f]); n += 1
        # Pareto maximality among PMMS allocations of W
        for C in self.allocations(W):
            if C == B:
                continue
            lits = list(self.fails(C))
            for i in range(3):
                if C[i] != B[i]:
                    lits.append(self.cmp_lit(i, B[i] - C[i], C[i] - B[i]))
            self.emit(out, lits); n += 1
        # tie-breaks
        for i, j in ((0, 1), (1, 2)):
            if sizes[i] == sizes[j]:
                k = 3 - i - j
                self.emit(out, [self.cmp_lit(k, B[j], B[i])]); n += 1
        # within-block order by agent 0
        for b in self.blocks:
            for x, y in zip(b, b[1:]):
                self.emit(out, [self.cmp_lit(0, frozenset([y]), frozenset([x]))]); n += 1
        # least-good selectors and own-value maximality
        cs = []
        if not self.least:
            return n
        for i in range(3):
            c = self.least.get(i)
            if c is None:
                fail('least selector missing')
            cs.append(c)
            for h in range(g):
                self.emit(out, [-c, self.cmp_lit(i, frozenset([h]), frozenset([g]))]); n += 1
            for C in self.allocations(W):
                if C[i] == B[i]:
                    continue
                self.emit(out, [-c] + self.fails(C) + [self.cmp_lit(i, B[i] - C[i], C[i] - B[i])]); n += 1
        self.emit(out, cs); n += 1
        return n


def normalise_cnf(path, out_path):
    nvars = ncl = None
    seen = 0
    with open(path) as f, open(out_path, 'w') as o:
        for line in f:
            if line.startswith('c'):
                continue
            if line.startswith('p'):
                _, _, nv, nc = line.split(); nvars, ncl = int(nv), int(nc); continue
            lits = list(map(int, line.split()))
            if lits[-1] != 0:
                fail('clause line not 0-terminated')
            lits = sorted(set(lits[:-1]))
            if not lits:
                fail('empty clause in CNF')
            o.write(' '.join(map(str, lits)) + '\n'); seen += 1
    if seen != ncl:
        fail('clause count mismatch with header')
    return nvars, ncl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rundir')
    ap.add_argument('--goods', type=int, required=True)
    ap.add_argument('--case', required=True, help="size profile, e.g. 124, or 'plain' for the six-good base formula (no normal form; first agent's goods in increasing order)")
    ap.add_argument('--tmp', default=None)
    ap.add_argument('--result', default=None, help='where to write the JSON result (default: RUNDIR/verify_case_result.json); replay scripts pass a scratch path so the bundle is never modified')
    ap.add_argument('--cnf', default='base.cnf')
    ap.add_argument('--sub', type=int, default=None, help='sub-case: the least-good selector of this agent is a unit clause')
    args = ap.parse_args()
    # Static case table, written out independently of the generator (cases.py) so that this verifier
    # imports nothing from the generator and needs only the standard library.  A separate consistency
    # check against cases.CASES is in test_case_table.py.
    CASES = {
        7: {'114': [[0], [1], [2, 3, 4, 5]], '123': [[0], [1, 2], [3, 4, 5]], '222': [[0, 1], [2, 3], [4, 5]]},
        8: {'115': [[0], [1], [2, 3, 4, 5, 6]], '124': [[0], [1, 2], [3, 4, 5, 6]],
            '133': [[0], [1, 2, 3], [4, 5, 6]], '223': [[0, 1], [2, 3], [4, 5, 6]]},
    }
    plain = args.case == 'plain'
    all_cases = CASES.get(args.goods, {})
    m = args.goods
    # coverage of size profiles (normal-form formulas only)
    if not plain:
        profiles = set()
        for a in range(1, m):
            for b in range(a, m):
                c = (m - 1) - a - b
                if c >= b:
                    profiles.add((a, b, c))
        have = {tuple(len(b) for b in blocks) for blocks in all_cases.values()}
        if have != profiles:
            fail(f'case list {sorted(have)} does not cover size profiles {sorted(profiles)}')

    blocks = None if plain else all_cases[args.case]
    tmp = args.tmp or os.path.join(args.rundir, 'verify_tmp')
    os.makedirs(tmp, exist_ok=True)
    t0 = time.time()
    cnf = os.path.join(args.rundir, args.cnf)
    cnf_sha = hashlib.sha256(open(cnf, 'rb').read()).hexdigest()
    nvars, ncl = normalise_cnf(cnf, os.path.join(tmp, 'cnf_norm.txt'))
    dpath = os.path.join(args.rundir, 'dictionary.json')
    if os.path.exists(dpath):
        dictionary = json.load(open(dpath))
    else:
        import gzip
        dictionary = json.load(gzip.open(dpath + '.gz', 'rt'))
    V = Verifier(m, blocks, dictionary)
    if V.nvars > nvars:
        fail('dictionary names a variable beyond the CNF header')
    counts = {}
    with open(os.path.join(tmp, 'expected.txt'), 'w') as out:
        counts['sign_rules'] = V.gen_sign_rules(out)
        counts['definitions'] = V.gen_definitions(out)
        counts['allocation_failures'] = V.gen_allocation_failures(out)
        counts['restriction_lemmas'] = V.gen_restriction_lemmas(out)
        counts['efx'] = V.gen_efx_lemma(out) if V.efx else 0
        counts['cardinality'] = V.gen_cardinality(out)
        if plain:
            # base formula: the first agent's goods are in strictly increasing order of value
            n = 0
            for x in range(m - 1):
                V.emit(out, [V.cmp_lit(0, frozenset([x + 1]), frozenset([x]))]); n += 1
            counts['order'] = n
        else:
            counts['case'] = V.gen_case_clauses(out)
        if args.sub is not None:
            V.emit(out, [V.least[args.sub]]); counts['subcase_unit'] = 1
    print('expected clauses generated', counts, f'{time.time()-t0:.0f}s', flush=True)
    # every CNF clause must be expected; also every variable used must be named
    env = dict(os.environ, LC_ALL='C')
    subprocess.check_call(['sort', '-u', '-o', os.path.join(tmp, 'cnf_sorted.txt'), os.path.join(tmp, 'cnf_norm.txt')], env=env)
    subprocess.check_call(['sort', '-u', '-o', os.path.join(tmp, 'exp_sorted.txt'), os.path.join(tmp, 'expected.txt')], env=env)
    missing = subprocess.run(['comm', '-23', os.path.join(tmp, 'cnf_sorted.txt'), os.path.join(tmp, 'exp_sorted.txt')],
                             capture_output=True, text=True, env=env).stdout
    if missing.strip():
        lines = missing.strip().split('\n')
        fail(f'{len(lines)} CNF clauses are not derivable; first: {lines[:3]}')
    unused = subprocess.run(['comm', '-13', os.path.join(tmp, 'cnf_sorted.txt'), os.path.join(tmp, 'exp_sorted.txt')],
                            capture_output=True, text=True, env=env).stdout.count('\n')
    # variables appearing in the CNF must all be in the dictionary
    used = set()
    with open(os.path.join(tmp, 'cnf_norm.txt')) as f:
        for line in f:
            for l in line.split():
                used.add(abs(int(l)))
    unnamed = [v for v in used if v not in V.names]
    if unnamed:
        fail(f'{len(unnamed)} CNF variables have no meaning in the dictionary')
    result = {'status': 'ALL_CNF_CLAUSES_INDEPENDENTLY_DERIVED', 'goods': m, 'case': args.case, 'sub': args.sub,
              'cnf': cnf, 'cnf_sha256': cnf_sha, 'cnf_clauses': ncl, 'cnf_vars': nvars,
              'expected_counts': counts, 'expected_not_in_cnf': unused,
              'seconds': round(time.time() - t0, 1)}
    print(json.dumps(result, indent=1))
    json.dump(result, open(args.result or os.path.join(args.rundir, 'verify_case_result.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
