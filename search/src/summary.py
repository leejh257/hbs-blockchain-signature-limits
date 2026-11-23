"""Assemble Tables 3 and 4 of the paper from the search results.

usage: python3 summary.py     (after the stage searches have run)
"""
import json
import os
import paths

R = os.path.join(paths.HERE, '..', 'results')
BASE = 7856  # SLH-DSA-SHA2-128s, bytes


def load(policy, cap):
    a = json.load(open(os.path.join(R, f's1_s5_{policy}_{cap:g}.json')))
    b = json.load(open(os.path.join(R, f's6_s7_{policy}_{cap:g}.json')))
    return a, b


def row(a, b, q):
    fips = min(a[f'{q}|S1 FIPS 205 (w=16)']['size'], a[f'{q}|S2 +choice of w (4,16,256)']['size'])
    s4 = a[f'{q}|S4 +FORS+C']['size']
    s6 = b[f'{q}|BPORS+FP']['size']
    s7 = b[f'{q}|BPORS-C+BFP']['size']
    budget = BASE - fips
    variants = fips - s7
    return dict(q=q, fips=fips, s4=s4, s6=s6, s7=s7, budget=budget, variants=variants,
                share=budget / (budget + variants))


if __name__ == '__main__':
    a, b = load('V1', 2)
    print('## Table 3 (policy V1, signing cap 2)\n')
    print('| q | SLH-DSA-128s | S1 FIPS 205 re-optimized | S4 WOTS+C, FORS+C | S6 BPORS+FP | S7 BPORS-C+BFP '
          '| Saved by budget | Saved by variants | Budget share |')
    print('|---|---|---|---|---|---|---|---|---|')
    for q in (64, 40, 30, 20):
        r = row(a, b, q)
        print(f"| 2^{q} | {BASE:,} | {r['fips']:,} | {r['s4']:,} | {r['s6']:,} | {r['s7']:,} "
              f"| {r['budget']:,} | {r['variants']:,} | {r['share']:.0%} |")
    print('\n## Table 4 (policy V1)\n')
    print('| Cap | Budget share (2^40 / 2^30 / 2^20) | Saved by variants (2^40 / 2^30 / 2^20) | S7 at 2^30 |')
    print('|---|---|---|---|')
    for cap in (1, 2, 4):
        a, b = load('V1', cap)
        rs = [row(a, b, q) for q in (40, 30, 20)]
        print(f"| {cap} | " + ' / '.join(f"{r['share']:.0%}" for r in rs) + ' | '
              + ' / '.join(f"{r['variants']:,}" for r in rs) + f" | {rs[1]['s7']:,} |")
    print('\n## Policy V2, signing cap 2 (cross-check)\n')
    print('This search uses a narrower grid than Section 5.1 for S5 (PORS+FP). The S5 sizes and the')
    print('policy V2 figures of Section 5.2 come from costmodel/search.py, which reports a largest')
    print('further saving of 396 B and verification costs of 6,272 to 12,492 compressions.\n')
    a = json.load(open(os.path.join(R, 's1_s5_V1_2.json')))
    v = json.load(open(os.path.join(R, 's1_s5_V2_2.json')))
    gains = [(a[k]['size'] - v[k]['size'], k, v[k]['sv']) for k in a if a[k] and v[k]]
    g = max(gains)
    svs = [v[k]['sv'] for k in v if v[k] and v[k]['w'] == 256]
    print(f'- Largest further saving from w = 256: {g[0]} B ({g[1]})')
    print(f'- Verification cost of the w = 256 sets: {min(svs):,} to {max(svs):,} compressions')

