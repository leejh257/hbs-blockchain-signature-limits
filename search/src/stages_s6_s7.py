"""Stages S6 (WOTS+C + BPORS+FP) and S7 (WOTS+C + BPORS-C+BFP) of the
decomposition search, in the same SHA-256 compression cost model as S1-S5.

usage: python3 stages_s6_s7.py <V1|V2> <cap> [q ...]

PORS+FP* is the single-bucket special case (K = 1, b = 0) used as a check.
Writes results/s6_s7_<policy>_<cap>.json.
"""
import sys, json, time, math, os
import numpy as np
import paths  # noqa: F401
import engine as E
import bpors as P
M = E.M
STD = E.STD
N = M.N
C_MSG = M.C_HMSG + M.C_PRFMSG


def lcomb(n, k):
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


# ---------- fast security evaluation ----------
_W = {}
def binom_matrix(B, qmax):
    key = (B, qmax)
    if key not in _W:
        p = 1.0 / B
        W = np.zeros((qmax + 1, qmax + 1))
        for q0 in range(qmax + 1):
            for r in range(q0 + 1):
                if p == 1.0:
                    W[q0, r] = 1.0 if r == q0 else 0.0
                else:
                    W[q0, r] = math.exp(lcomb(q0, r) + r * math.log(p) + (q0 - r) * math.log1p(-p))
        _W[key] = W
    return _W[key]

_POIS = {}
def pois(delta):
    if delta not in _POIS:
        lam = 2.0 ** delta
        hi = int(lam + 30 * math.sqrt(lam + 1) + 60)
        v = np.array([math.exp(-lam + q0 * math.log(lam) - math.lgamma(q0 + 1)) if q0 > 0 else 0.0
                      for q0 in range(hi)])
        _POIS[delta] = v
    return _POIS[delta]

_NUM = {}
def chain_nums(k, c, E_, rmax):
    """log of [x^k z^E] P^r for r = 1..rmax (None if 0)."""
    key = (k, c, E_)
    if key in _NUM and len(_NUM[key]) > rmax:
        return _NUM[key]
    Pp = P._chainP(k, c, E_)
    out = [None]
    Pr = Pp
    for r in range(1, rmax + 1):
        if r > 1:
            Pr = P._mul(Pr, Pp, k, E_)
        v = Pr[k][E_]
        out.append(math.log(v) if v > 0 else None)
    _NUM[key] = out
    return out


def alpha_vec(k, t, c, E_, rmax):
    a = np.ones(rmax + 1)
    a[0] = 0.0
    lt = lcomb(t, k)
    for r in range(1, rmax + 1):
        m = min(r * k, t)
        sub = 0.0 if m < k else math.exp(lcomb(m, k) - lt)
        a[r] = min(1.0, sub)
    if c > 0:
        Nn = P.n_const_sum(k, c, E_)
        nums = chain_nums(k, c, E_, min(rmax, 60))
        lN = math.log(Nn)
        for r in range(1, min(rmax, 60) + 1):
            if nums[r] is None:
                g = 0.0
            else:
                g = math.exp(min(0.0, nums[r] - lt - (r + 1) * lN))
            a[r] = min(a[r], g)
    return a


def sec(delta, K, b, k, t, c=0, E_=0):
    pv = pois(delta)
    qmax = len(pv) - 1
    W = binom_matrix(2 ** b, qmax)
    a = alpha_vec(k, t, c, E_, qmax)
    beta = np.minimum(1.0, W @ a)
    with np.errstate(divide='ignore'):
        s = float(np.sum(pv * np.power(beta, K)))
    return 999.0 if s <= 0 else -math.log2(s)


def min_t(delta, K, b, k, c=0, E_=0, target=128.0, tmax=2 ** 18):
    lo, hi = k + 1, tmax
    if sec(delta, K, b, k, hi, c, E_) < target:
        return None
    while lo < hi:
        mid = (lo + hi) // 2
        if sec(delta, K, b, k, mid, c, E_) >= target:
            hi = mid
        else:
            lo = mid + 1
    return lo


# ---------- candidate few-time components per delta = q - h ----------
_CANDS = {}
def candidates(delta, family):
    key = (delta, family)
    if key in _CANDS:
        return _CANDS[key]
    out = []
    if family == 'BPORS+FP':
        grid = [(K, b, k, 0, 0) for K in range(1, 9) for b in range(0, 17) for k in range(2, 13)]
    else:
        grid = []
        for K in range(1, 9):
            for b in range(0, 17):
                for k in range(3, 9):
                    for c in (2, 4, 8, 16):
                        for E_ in sorted({max(1, c // 2), c, 2 * c, 3 * c}):
                            if E_ <= k * c:
                                grid.append((K, b, k, c, E_))
    for (K, b, k, c, E_) in grid:
        t = min_t(delta, K, b, k, c, E_)
        if t is None:
            continue
        out.append((K, b, k, t, c, E_))
    _CANDS[key] = out
    return out


def fts_costs(family, K, b, k, t, c, E_):
    th1, th2 = M.C_TH1, M.C_TH2
    child = t * M.C_PRF + (c + 1) * t * th1 + (t - 1) * th2
    gen = K * 2 ** b * child + K * (2 ** b - 1) * th2 + M.compute_th(K)
    return gen


def best(q, family, cap, vpol, ws=(16,)):
    best_r = None
    for h in range(max(4, q - 4), q + 9):
        delta = q - h
        if family == 'PORS+FP*':
            cands = [x for x in candidates(delta, 'BPORS+FP') if x[0] == 1 and x[1] == 0]
        else:
            cands = candidates(delta, family)
        if not cands:
            continue
        for d in range(1, h + 1):
            if h % d:
                continue
            hp = h // d
            if hp > 22:
                continue
            for w in ws:
                l = M.wots_len(w, wc=True)
                thl = M.compute_th(l)
                swn = E.SWN.get(w, 0)
                nu = M._nu(l, swn, w)
                d_search = d * (-(-(w ** l) // nu))
                c_merkle = 2 ** hp * (l * M.C_PRF + l * (w - 1) * M.C_TH1 + thl) + (2 ** hp - 1) * M.C_TH2
                c_hyper = d * c_merkle + d_search * M.C_TH1C
                room = cap * STD['sg'] - c_hyper
                if room <= 0:
                    continue
                c_wots = ((w - 1) * l - swn) * M.C_TH1 + M.C_TH1C + thl
                sv_fixed = M.C_HMSG + d * c_wots + h * M.C_TH2
                base_size = d * (hp * N + l * N + M.C_SIZE) + M.R_SIZE
                for (K, b, k, t, c, E_) in cands:
                    gen = fts_costs(family, K, b, k, t, c, E_)
                    left = room - gen
                    if left < C_MSG:
                        continue
                    tau_req = C_MSG / left
                    # smallest child budget L with acceptance >= tau_req
                    cdf = P.octo_conv(t, k, K)
                    L = next((i for i, v in enumerate(cdf) if v >= tau_req), None)
                    if L is None:
                        continue
                    tau = cdf[L]
                    attempts = math.ceil(1.0 / tau)
                    sg = c_hyper + gen + attempts * C_MSG
                    if family in ('BPORS+FP', 'PORS+FP*'):
                        fts_size = (K * k + L + K * b) * N
                        c_fts = K * k * M.C_TH1 + (K * (k - 1) + L + K * b) * M.C_TH2 + M.compute_th(K)
                    else:
                        fts_size = (K * k + K * b + L) * N
                        c_fts = K * (k + E_) * M.C_TH1 + (K * (k - 1) + L + K * b) * M.C_TH2 + M.compute_th(K)
                    sv = sv_fixed + c_fts
                    size = base_size + fts_size
                    if vpol == 'V1' and sv > STD['sv']:
                        continue
                    if vpol == 'V2' and sv / size > 2.6:
                        continue
                    if best_r is None or size < best_r['size']:
                        best_r = dict(size=size, sg=sg, sv=sv, kg=c_merkle, h=h, d=d, w=w,
                                      K=K, b=b, k=k, t=t, c=c, E=E_, L=L, tau=tau,
                                      sg_rel=sg / STD['sg'])
    return best_r


if __name__ == '__main__':
    vpol = sys.argv[1]
    cap = float(sys.argv[2])
    qs = [int(x) for x in sys.argv[3:]] or [64, 40, 30, 20]
    res = {}
    for q in qs:
        for fam in ('PORS+FP*', 'BPORS+FP', 'BPORS-C+BFP'):
            t0 = time.time()
            r = best(q, fam, cap, vpol)
            res[f'{q}|{fam}'] = r
            print(vpol, cap, q, fam, r, f'{time.time() - t0:.0f}s', flush=True)
    out = os.path.join(paths.HERE, '..', 'results', f's6_s7_{vpol}_{cap:g}.json')
    json.dump(res, open(out, 'w'), indent=1)
