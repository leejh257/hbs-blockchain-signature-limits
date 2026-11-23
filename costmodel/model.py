"""Size, cost and security of SLH-DSA and its variants (paper, Sections 3.2, 3.3 and 5.1).

Costs are SHA-256 compression calls with the PK.seed midstate cached, as in the public
model of BlockstreamResearch/SPHINCS-Parameters [9] at commit 3172178 (2026-11-16),
the version before the "top layer saving" change of 2026-11-17. Set TOP_SAVE = True
to follow the later version; the baseline signing cost then drops from 2,218,486 to
2,218,200 compressions.

Schemes:
  spx        SLH-DSA (WOTS-TW + FORS), any w
  wc_fors    WOTS+C + FORS
  wc_forsc   WOTS+C + FORS+C
  wc_porsfp  WOTS+C + PORS+FP with an explicit pruning budget mmax

Security follows equation (2) of the paper for FORS and FORS+C (k trees of 2^a
leaves; FORS+C keeps the k of the underlying FORS), and the subset-forgery bound
C(min(r*k, t), k) / C(t, k) of [9] for PORS+FP (one tree of t = k * 2^a leaves).
"""
from fractions import Fraction
from functools import lru_cache
from math import ceil, floor, log2, comb, log, log1p

import numpy as np
from scipy.special import gammaln, logsumexp

from octopus_pmf import cost_table

N = 16            # hash output bytes (NIST category 1)
C_SIZE = 4        # WOTS+C counter per layer, bytes
R_SIZE = 16       # randomizer, bytes
C_HMSG = 4        # H_msg compressions
C_PRFMSG = 3      # PRF_msg compressions
TOP_SAVE = False  # see the module docstring
SWN = {16: 240, 32: 403, 64: 693, 128: 1206, 256: 2040}   # WOTS+C target digit sums


def th(m):
    """Compressions of a tweakable hash over m n-byte values."""
    return ceil((22 * 8 + 128 * m + 65) / 512)


def len1(w):
    return ceil(8 * N / log2(w))


def len_tw(w):
    """WOTS-TW chains: len1 message chains plus len2 checksum chains."""
    l1 = len1(w)
    return l1 + floor(log2(l1 * (w - 1)) / log2(w)) + 1


def swn(w):
    return SWN.get(w, ceil(len1(w) * (w - 1) / 2))


def _digit_sum(x, w):
    s = 0
    while x:
        s += x % w
        x //= w
    return s


@lru_cache(maxsize=None)
def _checksum_digit_sum_total(l1, w):
    top = l1 * (w - 1)
    bl = [comb(l1, j) for j in range(l1 + 1)]

    def count(s):
        return sum((-1) ** j * bl[j] * comb(s - j * w + l1 - 1, l1 - 1)
                   for j in range(min(l1, s // w) + 1))
    total = 0
    for s in range(top // 2 + 1):
        c = count(s)
        total += c * _digit_sum(s, w)
        if top - s != s:
            total += c * _digit_sum(top - s, w)
    return total


def tw_mean_steps(w, count=1):
    """Mean chain steps to verify `count` WOTS-TW signatures, rounded once."""
    l1 = len1(w)
    l2 = len_tw(w) - l1
    mean = (Fraction(l1 * (w - 1), 2) + l2 * (w - 1)
            - Fraction(_checksum_digit_sum_total(l1, w), w ** l1))
    return floor(count * mean + Fraction(1, 2))


@lru_cache(maxsize=None)
def _nu(l, s, w):
    """Number of l-digit base-w strings whose digits sum to s."""
    v = 0
    for j in range(l + 1):
        nv = (s + l) - j * w - 1
        v += (-1) ** j * comb(l, j) * (comb(nv, l - 1) if nv >= l - 1 else 0)
    return max(v, 1)


def _tree(hp, l, w):
    """One XMSS tree: 2^h' WOTS public keys and 2^h' - 1 nodes."""
    return 2 ** hp * (l + l * (w - 1) + th(l)) + (2 ** hp - 1)


# ---------- costs ----------

def spx(h, d, k, a, w=16):
    hp = h // d
    l = len_tw(w)
    tree = _tree(hp, l, w)
    fors = k * 2 ** a * 2 + k * (2 ** a - 1) + th(k)
    top = (tw_mean_steps(w, 1) + th(l) + hp) if TOP_SAVE else 0
    return dict(
        size=N * (1 + k * (a + 1) + h + d * l),
        kg=tree,
        sg=fors + C_HMSG + C_PRFMSG + d * tree - top,
        sv=C_HMSG + k + k * a + th(k) + tw_mean_steps(w, d) + d * th(l) + h)


def _wc_hypertree(h, d, w):
    hp = h // d
    l = len1(w)
    s = swn(w)
    search = d * (-(-(w ** l) // _nu(l, s, w)))
    tree = _tree(hp, l, w)
    v_layer = ((w - 1) * l - s) + 1 + th(l)
    sg = d * tree + search - ((v_layer + hp) if TOP_SAVE else 0)
    size = d * (hp * N + l * N + C_SIZE) + R_SIZE
    return sg, size, d * v_layer + h, tree


def wc_fors(h, d, k, a, w):
    sg, size, sv, tree = _wc_hypertree(h, d, w)
    fors = k * 2 ** a * 2 + k * (2 ** a - 1) + th(k)
    return dict(size=size + k * (a + 1) * N, kg=tree,
                sg=sg + fors + C_HMSG + C_PRFMSG,
                sv=C_HMSG + k + k * a + th(k) + sv)


def wc_forsc(h, d, k, a, w):
    sg, size, sv, tree = _wc_hypertree(h, d, w)
    k1 = k - 1
    fors = k1 * 2 ** a * 2 + k1 * (2 ** a - 1) + th(k1)
    return dict(size=size + k1 * (a + 1) * N, kg=tree,
                sg=sg + fors + 2 ** a * (C_HMSG + C_PRFMSG),
                sv=C_HMSG + k1 + k1 * a + th(k1) + sv)


def wc_porsfp(h, d, k, a, w, mmax):
    """None if mmax is below the smallest authentication-set size."""
    sg, size, sv, tree = _wc_hypertree(h, d, w)
    t = k * 2 ** a
    sub = floor(log2(t))
    pors = 2 * t + (2 ** sub - 1) + (t - 2 ** sub)
    tab = cost_table(t, k)
    lows = [m for m in tab if m <= mmax]
    if not lows:
        return None
    attempts = ceil(2.0 ** tab[max(lows)])
    return dict(size=size + (k + mmax) * N, kg=tree,
                sg=sg + pors + attempts * (C_HMSG + C_PRFMSG),
                sv=C_HMSG + k + mmax + sv, mmax=mmax)


def wc_porsfp_kn(h, d, k, a, w):
    """PORS+FP with the pruning rule of Kudinov and Nick [2] and [9]: from
    (k-1)*a - ceil(350/n) up, the first mmax whose signing costs less than
    1.11 times signing with FORS+C (at most 19 steps)."""
    fc = wc_forsc(h, d, k, a, w)['sg']
    m0 = (k - 1) * a - ceil(350 / N)
    for i in range(20):
        m = wc_porsfp(h, d, k, a, w, m0 + i)
        if m and (m['sg'] / fc < 1.11 or i == 19):
            return m
    return None


# ---------- security ----------

@lru_cache(maxsize=None)
def security(qlog2, h, k, a, scheme='FORS'):
    """Security in bits, at most 8n = 128, after 2^qlog2 signatures.

    scheme 'FORS': k trees of 2^a leaves (also FORS+C); 'PORS': one tree of k*2^a leaves.
    Sums the binomial number r of signatures on the attacked instance over
    lambda +- (30*sqrt(lambda) + 30), lambda = 2^(qlog2 - h), in the log domain.
    """
    q = 2.0 ** qlog2
    lam = 2.0 ** (qlog2 - h)
    p = 2.0 ** (-h)
    span = 30 * lam ** 0.5 + 30
    r0, r1 = max(1, int(lam - span)), int(lam + span) + 2
    r = np.arange(r0, r1 + 1, dtype=np.float64)
    i = np.arange(0, r1 + 1, dtype=np.float64)
    cum = np.concatenate([[0.0], np.cumsum(np.log1p(-i / q))])
    log_binom = r * log(q) + cum[r.astype(int)] - gammaln(r + 1)
    log_weight = log_binom + r * log(p) + (q - r) * log1p(-p)
    if scheme == 'FORS':
        log_forge = k * np.log(-np.expm1(r * log1p(-1.0 / 2 ** a)))
    else:
        t = k * 2 ** a
        m = np.minimum(r * k, t)
        log_forge = ((gammaln(m + 1) - gammaln(m - k + 1))
                     - (gammaln(t + 1) - gammaln(t - k + 1)))
    log2_p = logsumexp(log_weight + log_forge) / log(2)
    return min(128.0, -log2_p)


def threshold(h, k, a, bits, scheme='FORS'):
    """log2 of the signature count at which security falls below `bits`."""
    lo, hi = 0.0, 80.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if security(round(mid, 4), h, k, a, scheme) >= bits:
            lo = mid
        else:
            hi = mid
    return lo


BASELINE = spx(63, 7, 14, 12, 16)   # SLH-DSA-SHA2-128s
