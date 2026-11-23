"""Stages S1-S5 of the decomposition search (Section 5 of the paper).

S1 FIPS 205 with w = 16, S2 adds the choice of w, S3 adds WOTS+C,
S4 adds FORS+C, S5 replaces FORS+C by PORS+FP. For each budget q the
search returns the smallest signature whose signing cost is at most
cap times the SLH-DSA-128s baseline and whose verification meets the
policy: V1 = no more compressions than the baseline, V2 = at most
2.6 compressions per signature byte.

usage: python3 stages_s1_s5.py <V1|V2> <cap> [q ...]
Writes results/s1_s5_<policy>_<cap>.json.
"""
import sys, json, time, os
import paths  # noqa: F401
import engine as E

M = E.M
STD = E.STD

STAGES = [('S1 FIPS 205 (w=16)', 'SPX', [16]),
          ('S2 +choice of w (4,16,256)', 'SPX', [4, 16, 256]),
          ('S3 +WOTS+C', 'W+C', [16, 256]),
          ('S4 +FORS+C', 'W+C_F+C', [16, 256]),
          ('S5 +PORS+FP', 'W+C_P+FP', [16, 256])]


def best(q, scheme, ws, vpol, sg_cap):
    res = None
    for h in range(max(4, q - 10), q + 9):
        for d in range(1, h + 1):
            if h % d or h // d > 22:
                continue
            amax = 20 if scheme == 'W+C_P+FP' else 24
            for a in range(4, amax + 1):
                fam = 'pors' if scheme == 'W+C_P+FP' else 'fors'
                k = E.mink(fam, h, a, q)
                if k is None:
                    continue
                if scheme == 'W+C_P+FP' and k * 2 ** a > 2 ** 20:
                    continue
                for w in ws:
                    try:
                        m = (M.spx_metrics(h, d, k, a, w) if scheme == 'SPX'
                             else M.scheme_metrics(scheme, h, d, k, a, w, E.SWN.get(w, 0)))
                    except Exception:
                        continue
                    if m['sg'] > sg_cap:
                        continue
                    if vpol == 'V1' and m['sv'] > STD['sv']:
                        continue
                    if vpol == 'V2' and m['cpb'] > 2.6:
                        continue
                    if res is None or m['size'] < res['size']:
                        res = dict(m, h=h, d=d, a=a, k=k, w=w, sg_rel=m['sg'] / STD['sg'])
    return res


if __name__ == '__main__':
    vpol = sys.argv[1]
    cap = float(sys.argv[2])
    qs = [int(x) for x in sys.argv[3:]] or [64, 40, 30, 20]
    res = {}
    for q in qs:
        for name, sch, ws in STAGES:
            t0 = time.time()
            r = best(q, sch, ws, vpol, cap * STD['sg'])
            res[f'{q}|{name}'] = r
            print(vpol, cap, q, name, r and (r['size'], r['h'], r['d'], r['a'], r['k'], r['w'],
                                             round(r['sg_rel'], 2), r['sv']),
                  f'{time.time() - t0:.0f}s', flush=True)
    out = os.path.join(paths.HERE, '..', 'results', f's1_s5_{vpol}_{cap:g}.json')
    json.dump(res, open(out, 'w'), indent=1)
