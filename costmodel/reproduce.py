#!/usr/bin/env python3
"""Checks the cost model and parameter search against the numbers in the paper.

  python3 costmodel/reproduce.py            all checks (about 10 minutes)
  python3 costmodel/reproduce.py --quick    without the PORS+FP searches (under a minute)

Each line prints the computed value, the value in the paper (or, for the S5 rows that
v0.09 of the paper does not print, the value this code is expected to give), and OK or DIFF.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model    # noqa: E402
import search   # noqa: E402

B = model.BASELINE
results = []


def check(label, got, want, ref='paper'):
    ok = got == want
    results.append(ok)
    print(f"  {'OK  ' if ok else 'DIFF'} {label}: {got}  ({ref}: {want})")


def section(title):
    print(f'\n{title}')


def main(quick):
    section('Baseline SLH-DSA-SHA2-128s (Section 5.1)')
    check('size (B)', B['size'], 7856)
    check('signing (C)', B['sg'], 2218486)
    check('verification (C)', B['sv'], 2193)
    check('key generation (C)', B['kg'], 292351)

    section('Table 3: S1 and S4, policy V1, c = 2')
    t3 = {64: (7296, 6668), 40: (5344, 4864), 30: (4528, 4140), 20: (3792, 3448)}
    for q, (s1, s4) in t3.items():
        check(f'q=2^{q} S1', search.best(q, 2, 'V1', 1)[0]['size'], s1)
        check(f'q=2^{q} S4', search.best(q, 2, 'V1', 4)[0]['size'], s4)

    section('Section 5.2: savings of WOTS+C and FORS+C at q = 2^30')
    s1, s3, s4 = (search.best(30, 2, 'V1', s)[0]['size'] for s in (1, 3, 4))
    check('WOTS+C (B)', s1 - s3, 132)
    check('FORS+C (B)', s3 - s4, 256)

    section('Table 4: budget share from S1 at c = 1 and 4 (variant savings taken from the table)')
    variants = {1: {40: 1472, 30: 1476, 20: 1336}, 4: {40: 1444, 30: 1220, 20: 1176}}
    shares = {1: {40: 59, 30: 67, 20: 74}, 4: {40: 65, 30: 74, 20: 78}}
    s7 = {1: 3388, 4: 3212}
    for c in (1, 4):
        for q in (40, 30, 20):
            s1 = search.best(q, c, 'V1', 1)[0]['size']
            budget = B['size'] - s1
            check(f'c={c} q=2^{q} budget share (%)',
                  round(100 * budget / (budget + variants[c][q])), shares[c][q])
        check(f'c={c} q=2^30 smallest set S7 (B)',
              search.best(30, c, 'V1', 1)[0]['size'] - variants[c][30], s7[c])

    section('Section 5.1: SHRINCS stateless set found by the search (q = 2^40, c = 1)')
    m, tag = search.best(40, 1, 'V1', 1)
    check('size (B)', m['size'], 5776)
    check('(h, d)', tag[1:3], (45, 5))

    section('Section 5.4: SP 800-230 128-bit set and the FIPS 205 set of the same size')
    sp = model.spx(22, 1, 6, 24, 4)
    fi = model.spx(26, 2, 9, 15, 16)
    check('SP 800-230 size (B)', sp['size'], 3856)
    check('SP 800-230 verification (C)', sp['sv'], 298)
    check('SP 800-230 signing / baseline', round(sp['sg'] / B['sg']), 686)
    check('SP 800-230 key generation / baseline', round(sp['kg'] / B['kg']), 4175)
    check('FIPS 205 (26, 2, 15, 9) size (B)', fi['size'], 3856)
    check('FIPS 205 verification (C)', fi['sv'], 731)
    check('signing speed-up', round(sp['sg'] / fi['sg']), 149)
    check('key generation speed-up', round(sp['kg'] / fi['kg']), 261)

    section('Table 7: overuse thresholds t128 / t112 (log2, one decimal)')
    t7 = [('SLH-DSA-128s', (63, 14, 12, 'FORS'), (64.7, 66.5)),
          ('SHRINCS stateless', (45, 10, 13, 'FORS'), (40.9, 45.2)),
          ('K&N W+C P+FP, 2^40', (40, 11, 14, 'PORS'), (41.3, 43.4)),
          ('FIPS-only (33, 3, 15, 9)', (33, 9, 15, 'FORS'), (31.1, 34.7)),
          ('K&N W+C P+FP, 2^30', (32, 10, 14, 'PORS'), (31.3, 34.1)),
          ('SP 800-230 128-24', (22, 6, 24, 'FORS'), (24.1, 27.2)),
          ('FIPS-only (26, 2, 15, 9)', (26, 9, 15, 'FORS'), (24.1, 27.7)),
          ('FIPS-only (22, 2, 15, 9)', (22, 9, 15, 'FORS'), (20.1, 23.7))]
    for name, (h, k, a, s), want in t7:
        got = tuple(round(model.threshold(h, k, a, b, s), 1) for b in (128, 112))
        check(name, got, want)

    section('Published sets of Kudinov and Nick, with their pruning rule')
    for q, (h, d, a, k, w), size, ref in [(40, (40, 5, 14, 11, 256), 4036, 'paper'),
                                          (30, (32, 4, 14, 10, 256), 3440, 'K&N [1]')]:
        m = model.wc_porsfp_kn(h, d, k, a, w)
        check(f'q=2^{q} {(h, d, a, k, w)} size (B), mmax {m["mmax"]}', m['size'], size, ref)
        check(f'q=2^{q} security (bits)', model.security(q, h, k, a, 'PORS'), 128.0)

    if quick:
        return

    section('S5 (PORS+FP), policy V1, c = 2: not printed in v0.09 of the paper')
    for q, want in ((64, 6428), (40, 4576), (30, 3900), (20, 3176)):
        r = search.best(q, 2, 'V1', 5)
        print('  ' + search.describe(q, 2, 'V1', 5, r))
        check(f'q=2^{q} S5', r[0]['size'], want, 'expected')

    section('S5 under policy V2, c = 4, q = 2^40 (the rule of Section 5.1, not that of K&N)')
    r = search.best(40, 4, 'V2', 5)
    print('  ' + search.describe(40, 4, 'V2', 5, r))
    check('size (B)', r[0]['size'], 4004, 'expected')


if __name__ == '__main__':
    main('--quick' in sys.argv)
    print(f'\n{sum(results)} of {len(results)} checks match.')
    sys.exit(0 if all(results) else 1)
