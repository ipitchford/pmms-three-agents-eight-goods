"""Sign-abstraction SAT encoding of the three-agent PMMS counterexample question.

A counterexample on m goods (if one exists) can be taken positive and generic (all distinct
subset sums differ, Lemma 3 of the seven-good note).  For each agent i and each nonzero
vector r in {-1,0,1}^m the Boolean variable p[i,r] means  r . v_i > 0.  Necessary rules:
  * opposite signs      p[i,-r] = not p[i,r]            (generic: no ties)
  * constants           r >= 0 nonzero  -> true ;  r <= 0 -> false   (positivity)
  * addition            p[i,r] & p[i,s] -> p[i,r+s]      when r+s in the cube
  * halving             p[i,r] & p[i,s] -> p[i,t]        when r+s = 2t
  * extra exact conflicts  (sum lambda_l r_l = 0, lambda_l > 0)  ->  not all p[i,r_l]   (CEGAR)
Allocation failure: for every complete allocation with nonempty bundles, some agent's PMMS
comparison fails, i.e. some bipartition of the pooled bundle has BOTH sides strictly better.
Lemma injection: every proper sub-instance (drop goods) has a PMMS allocation (true for <= 7
goods by the seven-good theorem).  Optional case structure fixes a canonical PMMS allocation of
M minus {g} with Pareto maximality and symmetry-breaking tie-breaks.
"""
import itertools, json, hashlib
import numpy as np

BIG = 1 << 40
TRUE, FALSE = BIG, -BIG


def popcount(x):
    return bin(x).count('1')


class SignEncoder:
    def __init__(self, m, agents=3):
        self.m = m
        self.agents = agents
        self.nvec = 3 ** m
        self.base = (3 ** m - 1) // 2          # code of the zero vector
        self.pow3 = [3 ** g for g in range(m)]
        self.w = [sum(self.pow3[g] for g in range(m) if mask >> g & 1) for mask in range(1 << m)]
        self.nvars = 0
        self.clauses = []          # list of lists (base clauses)
        self.var_names = {}        # var -> description
        # sign literal tables
        self.lit = np.zeros((agents, self.nvec), dtype=np.int64)
        self.sign_var_of = {}      # (agent, code) -> var, canonical codes only
        self._build_sign_vars()
        self.F = {}                # (agent, D, E) -> literal (TRUE/FALSE or var)
        self.witness_lits = {}     # (agent, D, E) -> list of witness literals
        self.y = {}                # (W, alloc) -> var
        self.allocs_cache = {}

    # ---------- vector helpers ----------
    def vec_of_code(self, code):
        v = []
        for g in range(self.m):
            v.append(code % 3 - 1)
            code //= 3
        return tuple(v)

    def code_of_vec(self, vec):
        return sum((x + 1) * p for x, p in zip(vec, self.pow3))

    def atom_code(self, S, T):
        """code of 1_S - 1_T for disjoint masks."""
        assert S & T == 0
        return self.base + self.w[S] - self.w[T]

    def new_var(self, name=None):
        self.nvars += 1
        if name is not None:
            self.var_names[self.nvars] = name
        return self.nvars

    def _build_sign_vars(self):
        m = self.m
        for code in range(self.nvec):
            vec = self.vec_of_code(code)
            if all(x == 0 for x in vec):
                for a in range(self.agents):
                    self.lit[a, code] = FALSE
                continue
            if all(x >= 0 for x in vec):
                for a in range(self.agents):
                    self.lit[a, code] = TRUE
                continue
            if all(x <= 0 for x in vec):
                for a in range(self.agents):
                    self.lit[a, code] = FALSE
                continue
            first = next(x for x in vec if x != 0)
            neg_code = (self.nvec - 1) - code
            if first == 1:
                for a in range(self.agents):
                    v = self.new_var(('sign', a, code))
                    self.sign_var_of[(a, code)] = v
                    self.lit[a, code] = v
                    self.lit[a, neg_code] = -v
        self.n_sign_vars = self.nvars

    def sign_lit(self, agent, S, T):
        return int(self.lit[agent, self.atom_code(S, T)])

    # ---------- clause helpers ----------
    @staticmethod
    def simplify(lits):
        out = []
        seen = set()
        for l in lits:
            if l == TRUE:
                return None
            if l == FALSE:
                continue
            if -l in seen:
                return None
            if l not in seen:
                seen.add(l)
                out.append(l)
        return out

    def add(self, lits):
        c = self.simplify(lits)
        if c is None:
            return
        if not c:
            raise RuntimeError('empty clause generated')
        self.clauses.append(c)

    # ---------- sign rules ----------
    def add_sign_rules(self):
        m = self.m
        n_add = n_half = 0
        # addition rule: pairs (r,s), r+s in cube; coordinate options
        opts = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, -1), (-1, 1)]
        self._rule_pairs(opts, kind='add')
        opts2 = [(0, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        self._rule_pairs(opts2, kind='half')

    def _rule_pairs(self, opts, kind):
        m = self.m
        k = len(opts)
        N = k ** m
        idx = np.arange(N, dtype=np.int64)
        r_code = np.zeros(N, dtype=np.int64)
        s_code = np.zeros(N, dtype=np.int64)
        rd = np.array([o[0] for o in opts]); sd = np.array([o[1] for o in opts])
        for g in range(m):
            d = (idx // (k ** g)) % k
            r_code += (rd[d] + 1) * self.pow3[g]
            s_code += (sd[d] + 1) * self.pow3[g]
        if kind == 'add':
            t_code = r_code + s_code - self.base
        else:
            t_code = (r_code + s_code) // 2
        zero = self.base
        keep = (r_code != zero) & (s_code != zero) & (t_code != zero) & (r_code < s_code)
        if kind == 'half':
            keep &= (r_code + s_code != 2 * zero)
        r_code, s_code, t_code = r_code[keep], s_code[keep], t_code[keep]
        count = 0
        for a in range(self.agents):
            L = self.lit[a]
            lr, ls, lt = -L[r_code], -L[s_code], L[t_code]
            # clause (lr | ls | lt); drop if any TRUE; remove FALSE
            drop = (lr == TRUE) | (ls == TRUE) | (lt == TRUE)
            lr, ls, lt = lr[~drop], ls[~drop], lt[~drop]
            for cl in zip(lr.tolist(), ls.tolist(), lt.tolist()):
                c = [x for x in cl if x != FALSE]
                # tautology check
                if len(c) == 3 and (c[0] == -c[1] or c[0] == -c[2] or c[1] == -c[2]):
                    continue
                if len(c) == 2 and c[0] == -c[1]:
                    continue
                if not c:
                    raise RuntimeError('empty rule clause')
                self.clauses.append(c)
                count += 1
        return count

    # ---------- PMMS failure structure ----------
    def failure_lit(self, agent, D, E):
        """Literal F[agent,D,E] <-> agent holding D fails PMMS against bundle E."""
        key = (agent, D, E)
        if key in self.F:
            return self.F[key]
        assert D and E and D & E == 0
        if popcount(E) <= 1:
            self.F[key] = FALSE
            return FALSE
        lowE = E & (-E)
        wl = []
        # S1 subset of E containing lowE, S1 != E ; T1 subset of D
        sub = E
        subsets_E = []
        while True:
            if sub & lowE and sub != E:
                subsets_E.append(sub)
            if sub == 0:
                break
            sub = (sub - 1) & E
        subsets_D = []
        sub = D
        while True:
            subsets_D.append(sub)
            if sub == 0:
                break
            sub = (sub - 1) & D
        for S1 in subsets_E:
            S2 = E ^ S1
            for T1 in subsets_D:
                T2 = D ^ T1
                a = self.sign_lit(agent, S1, T1)
                b = self.sign_lit(agent, S2, T2)
                if a == FALSE or b == FALSE:
                    continue
                if a == TRUE:
                    wl.append(b)
                elif b == TRUE:
                    wl.append(a)
                else:
                    z = self.new_var(('wit', agent, S1, T1, S2, T2))
                    self.add([-z, a]); self.add([-z, b]); self.add([z, -a, -b])
                    wl.append(z)
        wl = [x for x in dict.fromkeys(wl)]
        if not wl:
            self.F[key] = FALSE
            return FALSE
        f = self.new_var(('F', agent, D, E))
        self.add([-f] + wl)
        for z in wl:
            self.add([f, -z])
        self.F[key] = f
        self.witness_lits[key] = wl
        return f

    def allocations_of(self, W):
        """All ordered allocations (A0,A1,A2) of mask W with nonempty bundles."""
        if W in self.allocs_cache:
            return self.allocs_cache[W]
        out = []
        sub = W
        while sub:
            A0 = sub
            rest = W ^ A0
            s2 = rest
            while s2:
                A1 = s2
                A2 = rest ^ A1
                if A2:
                    out.append((A0, A1, A2))
                s2 = (s2 - 1) & rest
            sub = (sub - 1) & W
        self.allocs_cache[W] = out
        return out

    def fails_lits(self, alloc):
        A0, A1, A2 = alloc
        return [self.failure_lit(0, A0, A1), self.failure_lit(0, A0, A2),
                self.failure_lit(1, A1, A0), self.failure_lit(1, A1, A2),
                self.failure_lit(2, A2, A0), self.failure_lit(2, A2, A1)]

    def add_all_allocations_fail(self):
        full = (1 << self.m) - 1
        n = 0
        for alloc in self.allocations_of(full):
            self.add(self.fails_lits(alloc))
            n += 1
        return n

    def add_restriction_lemma(self, W):
        """Some allocation of goods W (nonempty bundles) is PMMS (valid when |W| <= 7)."""
        ys = []
        for alloc in self.allocations_of(W):
            fl = self.fails_lits(alloc)
            if any(f == TRUE for f in fl):
                continue
            fl = [f for f in fl if f != FALSE]
            if not fl:
                # always PMMS: lemma trivially true
                return 0
            y = self.new_var(('y', W, alloc))
            self.y[(W, alloc)] = y
            for f in fl:
                self.add([-y, -f])
            ys.append(y)
        self.add(ys)
        return len(ys)

    def add_all_restriction_lemmas(self, min_size=4, max_size=None):
        m = self.m
        if max_size is None:
            max_size = min(7, m - 1)
        n = 0
        for W in range(1, 1 << m):
            k = popcount(W)
            if min_size <= k <= max_size:
                n += self.add_restriction_lemma(W)
        return n

    def add_cardinality_theorem(self):
        """Theorem 6.1 for 3q-1 goods: at most one agent has top-(q-1) sum <= bottom-q sum.
        Encoded as: for each pair of agents, one of them has some (q-1)-set P and disjoint q-set T
        with v(P) > v(T)."""
        m = self.m
        if (m + 1) % 3 != 0:
            return 0
        q = (m + 1) // 3
        if q < 2:
            return 0
        goods = range(m)
        pairs = []
        for P in itertools.combinations(goods, q - 1):
            Pm = sum(1 << g for g in P)
            rest = [g for g in goods if g not in P]
            for T in itertools.combinations(rest, q):
                pairs.append((Pm, sum(1 << g for g in T)))
        n = 0
        for i, j in itertools.combinations(range(self.agents), 2):
            lits = [self.sign_lit(i, P, T) for P, T in pairs] + [self.sign_lit(j, P, T) for P, T in pairs]
            self.add(lits); n += 1
        return n


    def add_efx_lemma(self):
        """Some complete allocation (nonempty bundles) is EFX: for all i != j and all g in A_j,
        v_i(A_i) >= v_i(A_j - g)  (Chaudhury, Garg, Mehlhorn, JACM 71(1) 2024, Theorem 1.1; EC 2020).
        Positive instance with >= 4 goods: an EFX allocation has three nonempty bundles.
        Under genericity the weak inequality is the negation of a strict sign atom."""
        full = (1 << self.m) - 1
        xs = []
        for alloc in self.allocations_of(full):
            x = self.new_var(('efx', alloc))
            dead = False
            for i in range(3):
                for j in range(3):
                    if i == j:
                        continue
                    Aj = alloc[j]
                    sub = Aj
                    while sub:
                        g = sub & (-sub)
                        sub ^= g
                        l = self.sign_lit(i, Aj ^ g, alloc[i])   # v_i(A_j - g) > v_i(A_i) must be false
                        if l == TRUE:
                            dead = True
                        elif l != FALSE:
                            self.add([-x, -l])
            if dead:
                self.add([-x])
            else:
                xs.append(x)
        self.add(xs)
        return len(xs)

    def add_agent_order(self, agent, order):
        """v_agent(order[0]) < v_agent(order[1]) < ... (unit clauses)."""
        for g, h in zip(order, order[1:]):
            self.add([self.sign_lit(agent, 1 << h, 1 << g)])

    # ---------- output ----------
    def write_cnf(self, path, extra=()):
        clauses = self.clauses + list(extra)
        with open(path, 'w') as f:
            f.write(f'p cnf {self.nvars} {len(clauses)}\n')
            for c in clauses:
                f.write(' '.join(map(str, c)) + ' 0\n')
        h = hashlib.sha256(open(path, 'rb').read()).hexdigest()
        return len(clauses), h

    def describe(self):
        return {'m': self.m, 'agents': self.agents, 'vars': self.nvars,
                'sign_vars': self.n_sign_vars, 'clauses': len(self.clauses),
                'F_lits': sum(1 for v in self.F.values() if v not in (TRUE, FALSE)),
                'y_vars': len(self.y)}


def build(m, lemmas=True, cardinality=True, order_agent0=True, min_lemma_size=4):
    enc = SignEncoder(m)
    enc.add_sign_rules()
    n_alloc = enc.add_all_allocations_fail()
    info = {'alloc_clauses': n_alloc}
    if lemmas:
        info['lemma_y'] = enc.add_all_restriction_lemmas(min_size=min_lemma_size)
    if cardinality:
        info['cardinality_clauses'] = enc.add_cardinality_theorem()
    if order_agent0:
        enc.add_agent_order(0, list(range(m)))
    info.update(enc.describe())
    return enc, info


if __name__ == '__main__':
    import sys, time
    m = int(sys.argv[1])
    t = time.time()
    enc, info = build(m)
    info['build_seconds'] = time.time() - t
    print(json.dumps(info, indent=1))
    if len(sys.argv) > 2:
        n, h = enc.write_cnf(sys.argv[2])
        print('wrote', n, 'clauses sha256', h)
