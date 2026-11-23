#!/usr/bin/env python3
"""Table 7 from the released result files (data/btc_all.csv, data/eth_all.csv).

Uses the 'tail' rows (the 5,000 heaviest keys per chain, exact counts and active days).
The tail is complete for every threshold in Table 7: its smallest count is 2^13.84 (Bitcoin,
single-key types) and 2^14.89 (Ethereum), and even a one-year key at that count projects
to at most 2^19.8 over 30 years, below the smallest threshold 2^20.0.

Rules (--rule):
  exact      (recommended) compare log2 counts with the thresholds as listed (one decimal) in both columns;
             keys active < 365 days keep their current count in the 30-year column.
  floor      round thresholds down to a power of two in both columns; same projection.
  published  reproduces an earlier draft of the paper: 'now' columns floor-rounded, 30-year columns exact,
             and keys active < 365 days left out of the 30-year columns.

Usage: python3 table7.py --data path/to/data [--rule exact] [--years 30]
"""
import argparse, math, os
import numpy as np
import pandas as pd

SINGLE_KEY = ['pubkeyhash', 'witness_v0_keyhash', 'witness_v1_taproot', 'pubkey', 'eoa']

# name, nominal log2 q, t128 log2, t112 log2 (one decimal, as in Table 7 and Section 7),
# copied from search/results/thresholds.csv (search/src/thresholds.py). All rows except
# K&N at 2^20, S6 and S7 are also recomputed by costmodel/reproduce.py.
SETS = [
    ('SLH-DSA-128s',                             64, 64.7, 66.5),
    ('SHRINCS stateless',                        40, 40.9, 45.2),
    ('K&N W+C P+FP',                             40, 41.3, 43.4),
    ('FIPS-only, 2x signing cap (33, 3, 15, 9)', 30, 31.1, 34.7),
    ('K&N W+C P+FP',                             30, 31.3, 34.1),
    ('BPORS-C+BFP, 2x signing cap (S7)',         30, 30.1, 34.5),
    ('SP 800-230 128-24',                        24, 24.1, 27.2),
    ('FIPS-only (26, 2, 15, 9)',                 24, 24.1, 27.7),
    ('FIPS-only, 2x signing cap (22, 2, 15, 9)', 20, 20.1, 23.7),
    ('K&N W+C P+FP',                             20, 21.0, 25.1),
    ('BPORS+FP, 2x signing cap (S6)',            20, 20.0, 24.8),
    ('BPORS-C+BFP, 2x signing cap (S7)',         20, 20.0, 24.0),
]


def load_tail(path):
    d = pd.read_csv(path)
    t = d[(d['kind'] == 'tail') & d['type'].isin(SINGLE_KEY)]
    return t['n_sigs'].to_numpy(float), t['bucket'].to_numpy(float), t['addr'].to_numpy()


def project(n, days, years, keep_short):
    p = n * 365.0 / np.maximum(days, 1) * years          # lifetime from the first signature
    short = n if keep_short else np.zeros_like(n)
    return np.where(days >= 365, np.maximum(p, n), short)


def count(v, t):
    return int((np.log2(np.maximum(v, 1)) >= t).sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', default='data')
    ap.add_argument('--rule', choices=['exact', 'floor', 'published'], default='exact')
    ap.add_argument('--years', type=float, default=30)
    a = ap.parse_args()

    f_now = (lambda x: x) if a.rule == 'exact' else math.floor
    f_proj = math.floor if a.rule == 'floor' else (lambda x: x)
    keep_short = a.rule != 'published'

    chains = {}
    for c, fn in (('BTC', 'btc_all.csv'), ('ETH', 'eth_all.csv')):
        n, d, addr = load_tail(os.path.join(a.data, fn))
        chains[c] = (n, d, addr, project(n, d, a.years, keep_short))

    y = f'{a.years:g}'
    print(f'Rule: {a.rule}\n')
    print(f'| Parameter set | Nominal q | t128 | t112 | BTC now | BTC {y} years | ETH now | ETH {y} years |')
    print('| --- | --- | --- | --- | --- | --- | --- | --- |')
    for name, q, t128, t112 in SETS:
        cells = []
        for c in ('BTC', 'ETH'):
            n, _, _, p = chains[c]
            now = (count(n, f_now(t128)), count(n, f_now(t112)))
            pro = (count(p, f_proj(t128)), count(p, f_proj(t112)))
            if keep_short:
                assert pro[0] >= now[0] and pro[1] >= now[1]
            cells += [f'{now[0]:,} / {now[1]:,}', f'{pro[0]:,} / {pro[1]:,}']
        print(f'| {name} | 2^{q} | 2^{t128} | 2^{t112} | ' + ' | '.join(cells) + ' |')

    print('\nHeaviest projected keys (for the margins quoted in Sections 6.4, 7.2 and 7.3):')
    for c, (n, d, addr, p) in chains.items():
        for i in np.argsort(-p)[:3]:
            print(f'  {c} {addr[i]}  now 2^{math.log2(n[i]):.2f}  active {int(d[i])} d  '
                  f'rate 2^{math.log2(n[i] * 365 / max(d[i], 1)):.2f}/yr  {y} y 2^{math.log2(p[i]):.2f}')


if __name__ == '__main__':
    main()
