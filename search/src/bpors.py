"""BPORS+FP [RZY26] and BPORS-C+BFP [WLCHY26] security, acceptance and cost.

Security follows RZY26 Theorem 1 and WLCHY26 Theorem 1 (generic
generating-function bound, eq. 16 and 18). The SPHINCS+ average over the
bottom-key use count q0 ~ Bin(Q, 2^-h) is computed with a Poisson
approximation, as in engine.py.
"""
import math
from functools import lru_cache
import paths  # noqa: F401  (sets up sys.path)
from octopus_pmf import pmf_leftfilled  # Abri and Katz, PORS-FP, MIT license

LOG2 = math.log(2)


def _lcomb(n, k):
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


@lru_cache(None)
def octo_pmf(t, k):
    """PMF of the Octopus authentication-set size for a uniform k-subset of t leaves."""
    d = pmf_leftfilled(t, k)
    m = max(d)
    return tuple(d.get(i, 0.0) for i in range(m + 1))


@lru_cache(None)
def octo_conv(t, k, K):
    p = octo_pmf(t, k)
    out = [1.0]
    for _ in range(K):
        new = [0.0] * (len(out) + len(p) - 1)
        for i, a in enumerate(out):
            if a == 0.0:
                continue
            for j, b in enumerate(p):
                if b:
                    new[i + j] += a * b
        out = new
    cdf, s = [], 0.0
    for v in out:
        s += v
        cdf.append(s)
    return tuple(cdf)


def accept_prob(t, k, K, budget):
    """Probability that the K child Octopus sizes sum to at most budget."""
    if budget < 0:
        return 0.0
    cdf = octo_conv(t, k, K)
    return cdf[min(budget, len(cdf) - 1)]


# ---------- coverage, child level ----------

def alpha_pors(r, k, t):
    m = min(r * k, t)
    if m < k:
        return 0.0
    return math.exp(_lcomb(m, k) - _lcomb(t, k))


@lru_cache(None)
def _chainP(k, c, E):
    """P(x, z) = sum over constant-sum depth tuples e of prod (1 + x G_{e_l}(z)),
    as integer coefficients P[i][j] of x^i z^j, truncated to i <= k, j <= E."""
    # state: dict sum_e -> 2D list poly[x][z]
    zero = lambda: [[0] * (E + 1) for _ in range(k + 1)]
    states = {0: zero()}
    states[0][0][0] = 1
    for _ in range(k):
        nxt = {}
        for s, poly in states.items():
            for d in range(0, c + 1):
                if s + d > E:
                    break
                tgt = nxt.setdefault(s + d, zero())
                # multiply poly by (1 + x * (1 + z + ... + z^d))
                for i in range(k + 1):
                    row = poly[i]
                    for j in range(E + 1):
                        v = row[j]
                        if not v:
                            continue
                        tgt[i][j] += v
                        if i + 1 <= k:
                            r2 = tgt[i + 1]
                            for dz in range(0, d + 1):
                                if j + dz > E:
                                    break
                                r2[j + dz] += v
        states = nxt
    return states.get(E, zero())


def _mul(A, B, k, E):
    C = [[0] * (E + 1) for _ in range(k + 1)]
    for i in range(k + 1):
        for j in range(E + 1):
            a = A[i][j]
            if not a:
                continue
            for i2 in range(k + 1 - i):
                Bi = B[i2]
                Ci = C[i + i2]
                for j2 in range(E + 1 - j):
                    b = Bi[j2]
                    if b:
                        Ci[j + j2] += a * b
    return C


@lru_cache(None)
def n_const_sum(k, c, E):
    poly = [1]
    for _ in range(k):
        new = [0] * (len(poly) + c)
        for i, v in enumerate(poly):
            for d in range(c + 1):
                new[i + d] += v
        poly = new
    return poly[E] if E < len(poly) else 0


@lru_cache(None)
def alpha_chain_table(k, c, E, t, rmax=400):
    """alpha_C(r) for r = 0..rmax (WLCHY26 eq. 16); stops at 1."""
    if c == 0 and E == 0:
        return tuple(alpha_pors(r, k, t) for r in range(rmax + 1))
    N = n_const_sum(k, c, E)
    P = _chainP(k, c, E)
    lden0 = _lcomb(t, k) + math.log(N)
    out = [0.0]
    Pr = P
    for r in range(1, rmax + 1):
        if r > 1:
            Pr = _mul(Pr, P, k, E)
        num = Pr[k][E]
        val = 1.0
        if num > 0:
            lv = math.log(num) - lden0 - r * math.log(N)
            val = min(1.0, math.exp(lv))
        # the generic bound is never worse than the subset bound
        val = min(val, alpha_pors(r, k, t))
        out.append(val)
        if val >= 1.0:
            break
    return tuple(out)


def beta(q0, B, alpha_tab):
    """E_{R ~ Bin(q0, 1/B)} alpha(R); B = number of buckets."""
    p = 1.0 / B
    s = 0.0
    lp, lq = math.log(p), (math.log1p(-p) if p < 1 else -math.inf)
    for r in range(0, q0 + 1):
        a = alpha_tab[r] if r < len(alpha_tab) else 1.0
        if a == 0.0:
            continue
        if p == 1.0:
            w = 1.0 if r == q0 else 0.0
        else:
            w = math.exp(_lcomb(q0, r) + r * lp + (q0 - r) * lq)
        s += w * a
    return min(1.0, s)


def sec_bits(h, q_log2, K, B, alpha_tab, lam_bits=128.0):
    """-log2 of E_{q0 ~ Pois(2^(q-h))} beta(q0)^K, capped at lam_bits."""
    lam = 2.0 ** (q_log2 - h)
    s = 0.0
    lo = max(1, int(lam - 30 * math.sqrt(lam + 1) - 30))
    hi = int(lam + 30 * math.sqrt(lam + 1) + 60)
    for q0 in range(lo, hi):
        lp = -lam + q0 * math.log(lam) - math.lgamma(q0 + 1)
        b = beta(q0, B, alpha_tab)
        if b <= 0:
            continue
        s += math.exp(lp + K * math.log(b))
    if s <= 0:
        return lam_bits
    return min(lam_bits, -math.log2(s))
