"""Stage-wise exhaustive parameter search (paper, Section 5.1).

Stages are cumulative: each stage may use every option of the stages before it.
  S1  FIPS 205 re-optimized at the budget (WOTS-TW + FORS, w = 16)
  S2  w in {4, 16, 256}
  S3  + WOTS+C
  S4  + FORS+C
  S5  + PORS+FP (pruning budget: the smallest mmax that keeps signing within the cap)
S6 (BPORS+FP) and S7 (BPORS-C+BFP) need the coverage bounds of [5] and [6] and are not
included here.

Constraints: signing <= c * baseline; policy V1: verification <= baseline (2,193);
policy V2: verification <= 2.6 compressions per signature byte; security >= 128 bits
at the nominal budget q.

Grid: h from q-12 to q+14; d from 1 to 25 with h/d <= 22; a from 3 to 24; for each
(h, a) the smallest k that meets the security target (for PORS+FP also the next three).

Usage: python3 search.py LOG2_Q C POLICY STAGES     e.g.  python3 search.py 30 2 V1 1,4,5
"""
import sys
from functools import lru_cache

import model
from octopus_pmf import cost_table

B = model.BASELINE
H_SPAN = (-12, 14)
D_MAX = 25
HP_MAX = 22
A_RANGE = range(3, 25)
K_MAX = 64
V2_CPB = 2.6


@lru_cache(maxsize=None)
def kmin(q, h, a, scheme):
    for k in range(2, K_MAX + 1):
        if scheme == 'PORS' and k * 2 ** a > 2 ** 31:
            return None
        if model.security(q, h, k, a, scheme) >= 128:
            return k
    return None


def feasible(m, c, policy):
    if m is None or m['sg'] > c * B['sg']:
        return False
    if policy == 'V1':
        return m['sv'] <= B['sv']
    return m['sv'] <= V2_CPB * m['size']


def hd_pairs(q):
    for h in range(max(2, q + H_SPAN[0]), q + H_SPAN[1] + 1):
        for d in range(1, min(D_MAX, h) + 1):
            if h % d == 0 and h // d <= HP_MAX:
                yield h, d


def best(q, c, policy, stage):
    """Smallest feasible signature: (metrics, (scheme, h, d, a, k, w[, mmax])) or None."""
    ws = [16] if stage == 1 else [4, 16, 256]
    found = None

    def take(m, tag):
        nonlocal found
        if feasible(m, c, policy) and (
                found is None or (m['size'], m['sg']) < (found[0]['size'], found[0]['sg'])):
            found = (m, tag)

    for h, d in hd_pairs(q):
        for a in A_RANGE:
            k = kmin(q, h, a, 'FORS')
            if k is not None and k * 2 ** a * 3 <= c * B['sg']:
                for w in ws:
                    take(model.spx(h, d, k, a, w), ('SLH-DSA', h, d, a, k, w))
                    if stage >= 3:
                        take(model.wc_fors(h, d, k, a, w), ('WOTS+C/FORS', h, d, a, k, w))
                    if stage >= 4:
                        take(model.wc_forsc(h, d, k, a, w), ('WOTS+C/FORS+C', h, d, a, k, w))
            if stage < 5:
                continue
            kp = kmin(q, h, a, 'PORS')
            if kp is None:
                continue
            for k in range(kp, kp + 4):
                t = k * 2 ** a
                if 3 * t > c * B['sg'] or t > 2 ** 26:
                    break
                for w in ws:
                    loosest = model.wc_porsfp(h, d, k, a, w, 10 ** 6)
                    if loosest is None or loosest['sg'] > c * B['sg']:
                        continue
                    for mmax in sorted(cost_table(t, k)):
                        m = model.wc_porsfp(h, d, k, a, w, mmax)
                        if m and m['sg'] <= c * B['sg']:
                            take(m, ('WOTS+C/PORS+FP', h, d, a, k, w, mmax))
                            break
    return found


def describe(q, c, policy, stage, r):
    if r is None:
        return f'q=2^{q} c={c:g} {policy} S{stage}: none'
    m, tag = r
    return (f"q=2^{q} c={c:g} {policy} S{stage}: {m['size']:,} B  {tag}  "
            f"sign {m['sg']:,} ({m['sg'] / B['sg']:.2f}x)  "
            f"verify {m['sv']:,} ({m['sv'] / m['size']:.2f} C/B)")


if __name__ == '__main__':
    q, c, policy = int(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
    for s in (int(x) for x in sys.argv[4].split(',')):
        print(describe(q, c, policy, s, best(q, c, policy, s)), flush=True)
