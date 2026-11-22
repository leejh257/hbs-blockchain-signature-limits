# Size distribution of the Octopus authentication set, for the PORS+FP grinding work.
#
# Transcribed from https://github.com/MehdiAbri/PORS-FP (MIT License), as vendored in
# https://github.com/BlockstreamResearch/SPHINCS-Parameters/blob/main/third_party/octopus_pmf.py.
# The recursion is unchanged; only the output helper differs (cost_table returns a dict).
# SPDX-License-Identifier: MIT
import math
from collections import defaultdict
from functools import lru_cache


def comb(n, k):
    if n < 0 or k < 0 or k > n:
        return 0
    return math.comb(n, k)


def P(x, j, s):
    if x % 2 != 0 or j < 0 or s < 0 or j > x or 2 * s > j:
        return 0.0
    num = comb(x // 2, j - s) * comb(j - s, s) * (2 ** (j - 2 * s))
    den = comb(x, j)
    if den == 0:
        return 0.0
    return num / den


@lru_cache(maxsize=None)
def M(ell, L, R, kL, kR, c=0):
    if ell == 0:
        return {0: 1.0}
    if not (0 <= kL <= L and 0 <= kR <= R):
        return {}
    out = defaultdict(float)
    if L % 2 == 0:
        if c == 0:
            for rL in range(0, kL // 2 + 1):
                wL = P(L, kL, rL)
                if wL == 0.0:
                    continue
                for rR in range(0, kR // 2 + 1):
                    wR = P(R, kR, rR)
                    if wR == 0.0:
                        continue
                    singles = (kL + kR) - 2 * (rL + rR)
                    nxt = M(ell - 1, L // 2, R // 2, kL - rL, kR - rR, 0)
                    w = wL * wR
                    for m, p in nxt.items():
                        out[singles + m] += w * p
        elif c == +1:
            if R < 1 or kR < 1:
                return {}
            if R == 1:
                for rL in range(0, kL // 2 + 1):
                    wL = P(L, kL, rL)
                    if wL == 0.0:
                        continue
                    singles = (kL + kR) - 2 * rL
                    nxt = M(ell - 1, L // 2, 0, kL - rL, kR, +1)
                    for m, p in nxt.items():
                        out[singles + m] += wL * p
            else:
                denom = comb(R - 1, kR - 1)
                if denom == 0:
                    return {}
                wY1 = comb(R - 2, kR - 2) / denom
                wY0 = comb(R - 2, kR - 1) / denom
                for rL in range(0, kL // 2 + 1):
                    wL = P(L, kL, rL)
                    if wL == 0.0:
                        continue
                    for y, wy in ((1, wY1), (0, wY0)):
                        if wy == 0.0:
                            continue
                        for rRp in range(0, (kR - 1 - y) // 2 + 1):
                            wRp = P(R - 2, kR - 1 - y, rRp)
                            if wRp == 0.0:
                                continue
                            rR = y + rRp
                            singles = (kL + kR) - 2 * (rL + rR)
                            nxt = M(ell - 1, L // 2, R // 2, kL - rL, kR - rR, +1)
                            w = wL * wy * wRp
                            for m, p in nxt.items():
                                out[singles + m] += w * p
        else:
            if R == 0 or R == 1:
                if kR != 0:
                    return {}
                for rL in range(0, kL // 2 + 1):
                    wL = P(L, kL, rL)
                    if wL == 0.0:
                        continue
                    singles = (kL + kR) - 2 * rL
                    nxt = M(ell - 1, L // 2, 0, kL - rL, kR, -1)
                    for m, p in nxt.items():
                        out[singles + m] += wL * p
            else:
                denom = comb(R - 1, kR)
                if denom == 0:
                    return {}
                wZ0 = comb(R - 2, kR) / denom
                wZ1 = comb(R - 2, kR - 1) / denom
                for rL in range(0, kL // 2 + 1):
                    wL = P(L, kL, rL)
                    if wL == 0.0:
                        continue
                    for z, wz in ((0, wZ0), (1, wZ1)):
                        if wz == 0.0:
                            continue
                        for rRp in range(0, (kR - z) // 2 + 1):
                            wRp = P(R - 2, kR - z, rRp)
                            if wRp == 0.0:
                                continue
                            singles = (kL + kR) - 2 * (rL + rRp)
                            cn = +1 if z == 1 else -1
                            nxt = M(ell - 1, L // 2, R // 2, kL - rL, kR - rRp, cn)
                            w = wL * wz * wRp
                            for m, p in nxt.items():
                                out[singles + m] += w * p
    else:
        denomL = comb(L, kL)
        if denomL == 0:
            return {}
        if c == 0:
            denomR = comb(R, kR)
            if denomR == 0:
                return {}
            for xL in (0, 1):
                w_xL = comb(L - 1, kL - xL) / denomL if 0 <= kL - xL <= L - 1 else 0.0
                if w_xL == 0.0:
                    continue
                for xR in (0, 1):
                    w_xR = comb(R - 1, kR - xR) / denomR if 0 <= kR - xR <= R - 1 else 0.0
                    if w_xR == 0.0:
                        continue
                    kL_in, kR_in = kL - xL, kR - xR
                    for rL in range(0, kL_in // 2 + 1):
                        wL = P(L - 1, kL_in, rL)
                        if wL == 0.0:
                            continue
                        for rR in range(0, kR_in // 2 + 1):
                            wR = P(R - 1, kR_in, rR)
                            if wR == 0.0:
                                continue
                            bm = xL * xR
                            singles = (kL + kR) - 2 * (rL + rR + bm)
                            nxt = M(ell - 1, (L - 1) // 2, (R - 1) // 2 + 1,
                                    kL - xL - rL, kR - xR - rR + (xL + xR - bm),
                                    +1 if (xL + xR) >= 1 else -1)
                            w = w_xL * w_xR * wL * wR
                            for m, p in nxt.items():
                                out[singles + m] += w * p
        elif c == +1:
            if R < 1 or kR < 1:
                return {}
            for xL in (0, 1):
                w_xL = comb(L - 1, kL - xL) / denomL if 0 <= kL - xL <= L - 1 else 0.0
                if w_xL == 0.0:
                    continue
                kL_in, kR_in = kL - xL, kR - 1
                for rL in range(0, kL_in // 2 + 1):
                    wL = P(L - 1, kL_in, rL)
                    if wL == 0.0:
                        continue
                    for rR in range(0, kR_in // 2 + 1):
                        wR = P(R - 1, kR_in, rR)
                        if wR == 0.0:
                            continue
                        singles = (kL + kR) - 2 * (rL + rR + xL)
                        nxt = M(ell - 1, (L - 1) // 2, (R - 1) // 2 + 1,
                                kL - xL - rL, kR - rR, +1)
                        w = w_xL * wL * wR
                        for m, p in nxt.items():
                            out[singles + m] += w * p
        else:
            if R < 1:
                return {}
            for xL in (0, 1):
                w_xL = comb(L - 1, kL - xL) / denomL if 0 <= kL - xL <= L - 1 else 0.0
                if w_xL == 0.0:
                    continue
                kL_in, kR_in = kL - xL, kR
                for rL in range(0, kL_in // 2 + 1):
                    wL = P(L - 1, kL_in, rL)
                    if wL == 0.0:
                        continue
                    for rR in range(0, kR_in // 2 + 1):
                        wR = P(R - 1, kR_in, rR)
                        if wR == 0.0:
                            continue
                        singles = (kL + kR) - 2 * (rL + rR)
                        nxt = M(ell - 1, (L - 1) // 2, (R - 1) // 2 + 1,
                                kL - xL - rL, kR - rR + xL, +1 if xL == 1 else -1)
                        w = w_xL * wL * wR
                        for m, p in nxt.items():
                            out[singles + m] += w * p
    return dict(out)


def pmf_leftfilled(t, k):
    if not (1 <= k <= t):
        return {}
    h = (t - 1).bit_length()
    p = 1 << (h - 1) if h > 0 else 1
    L = t - p
    x = 2 * L
    pmf = defaultdict(float)
    denom = comb(t, k)
    for j in range(0, min(k, x) + 1):
        wj = comb(x, j) * comb(t - x, k - j) / denom
        if wj == 0.0:
            continue
        for s in range(0, j // 2 + 1):
            ws = P(x, j, s)
            if ws == 0.0:
                continue
            upper = M(max(h - 1, 0), L if h > 0 else 0, (p - L) if h > 0 else 0,
                      j - s, k - j, 0)
            for m, pu in upper.items():
                pmf[j - 2 * s + m] += wj * ws * pu
    return dict(pmf)


@lru_cache(maxsize=None)
def cost_table(t, k):
    """{mmax: log2 E[attempts]} = -log2 P(|auth set| <= mmax)."""
    pmf = pmf_leftfilled(t, k)
    out, run = {}, 0.0
    for m in range(max(pmf) + 1):
        run += pmf.get(m, 0.0)
        if run > 0:
            out[m] = -math.log2(run)
    return out
