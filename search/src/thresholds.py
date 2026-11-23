"""Overuse thresholds t128 and t112 of Table 7.

t_x is the log2 of the number of signatures under one key at which the
security of the few-time layer falls below x bits. FORS and PORS+FP sets
use engine.py; the S6 (BPORS+FP) and S7 (BPORS-C+BFP) sets use the
coverage bounds in bpors.py.
Values are rounded to one decimal.

usage: python3 thresholds.py
Writes results/thresholds.csv.
"""
import os
import paths  # noqa: F401
import engine as E
import bpors as P

# name, nominal log2 q, family, parameters
SETS = [
    ('SLH-DSA-128s', 64, 'fors', dict(h=63, a=12, k=14)),
    ('SHRINCS stateless', 40, 'fors', dict(h=45, a=13, k=10)),
    ('K&N W+C P+FP 2^40', 40, 'pors', dict(h=40, a=14, k=11)),
    ('FIPS-only 2x cap (33,3,15,9)', 30, 'fors', dict(h=33, a=15, k=9)),
    ('K&N W+C P+FP 2^30', 30, 'pors', dict(h=32, a=14, k=10)),
    ('S7 BPORS-C+BFP 2x cap 2^30', 30, 'new', dict(h=33, K=3, b=8, k=6, t=58, c=16, E=32)),
    ('SP 800-230 128-24', 24, 'fors', dict(h=22, a=24, k=6)),
    ('FIPS-only (26,2,15,9)', 24, 'fors', dict(h=26, a=15, k=9)),
    ('FIPS-only 2x cap (22,2,15,9)', 20, 'fors', dict(h=22, a=15, k=9)),
    ('K&N W+C P+FP 2^20', 20, 'pors', dict(h=24, a=16, k=8)),
    ('S6 BPORS+FP 2x cap 2^20', 20, 'new', dict(h=22, K=3, b=8, k=5, t=328, c=0, E=0)),
    ('S7 BPORS-C+BFP 2x cap 2^20', 20, 'new', dict(h=22, K=3, b=8, k=6, t=64, c=16, E=32)),
]


def security(fam, p, lq):
    if fam == 'fors':
        return E.sec_fors(p['h'], p['a'], p['k'], lq)
    if fam == 'pors':
        return E.sec_pors(p['h'], p['a'], p['k'], lq)
    tab = P.alpha_chain_table(p['k'], p['c'], p['E'], p['t'])
    return P.sec_bits(p['h'], lq, p['K'], 2 ** p['b'], tab, lam_bits=200.0)


def threshold(fam, p, target, nom):
    lo, hi = nom - 4.0, nom + 12.0
    for _ in range(30):
        mid = round((lo + hi) / 2, 4)
        if security(fam, p, mid) >= target:
            lo = mid
        else:
            hi = mid
    return lo


if __name__ == '__main__':
    rows = ['set,nominal,t128,t112']
    for name, nom, fam, p in SETS:
        t128 = threshold(fam, p, 127.999, nom)
        t112 = threshold(fam, p, 112.0, nom)
        rows.append(f'{name},2^{nom},2^{t128:.1f},2^{t112:.1f}')
        print(rows[-1], flush=True)
    out = os.path.join(paths.HERE, '..', 'results', 'thresholds.csv')
    open(out, 'w').write('\n'.join(rows) + '\n')
