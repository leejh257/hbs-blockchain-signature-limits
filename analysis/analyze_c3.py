#!/usr/bin/env python3
"""Per-key signature counts measured on chain, and overuse risk of hash-based parameter sets.

Input (CSV files exported from BigQuery)
  --all   one result CSV of btc_all.sql or eth_all.sql (hist, rate and tail rows combined)
  --hist  histogram only: columns bucket, n_keys[, type][, n_sigs]
  --tail  optional: columns n_sig, active_days[, type, addr]
  --rate  optional: columns log2_rate_per_year, n_keys[, type]
  --types script types to include (Bitcoin only; default: single-key types)
  --label chain name used in tables and figure
Output: Markdown tables on standard output, CCDF figure (SVG, PNG) with prefix --out

Overuse thresholds are precomputed with the cost and security model of Blockstream's
SPHINCS-Parameters (FORS and PORS+FP forgery probability, Poisson approximation).
"""
import argparse
import math
import pandas as pd

# Per parameter set: log2 of the signature count above which security falls below x bits
THRESHOLDS = {
    #  name                         : (nominal budget, 128, 112, 100, 80)
    'SLH-DSA 128s':                  (64, 64.7, 66.5, 67.6, 69.2),
    'SHRINCS stateless':             (40, 40.9, 45.2, 47.3, 49.8),
    'K&N W+C P+FP 2^40':             (40, 41.3, 43.4, 44.7, 46.7),
    'FIPS 2x q=2^30 (33,3,15,9)':    (30, 31.1, 34.7, 36.5, 39.0),
    'K&N W+C P+FP 2^30':             (30, 31.3, 34.1, 35.7, 37.9),
    'SP 800-230 128-24':             (24, 24.1, 27.2, 29.3, 32.7),
    'FIPS q=2^24 (26,2,15,9)':       (24, 24.1, 27.7, 29.5, 32.0),
    'FIPS 2x q=2^20 (22,2,15,9)':    (20, 20.1, 23.7, 25.5, 28.0),
    'K&N W+C P+FP 2^20':             (20, 21.0, 25.1, 27.1, 29.9),
}
SINGLE_KEY_TYPES = ['pubkeyhash', 'witness_v0_keyhash', 'p2sh_p2wpkh', 'witness_v1_taproot', 'pubkey', 'eoa']


def load_hist(path, types):
    df = path if isinstance(path, pd.DataFrame) else pd.read_csv(path)
    if 'type' in df.columns and types:
        df = df[df['type'].isin(types)]
    g = df.groupby('bucket', as_index=False)['n_keys'].sum().sort_values('bucket')
    return g


def ccdf_at(g, x):
    """Number of keys with at least x signatures. Exact when x <= 1024 or x is a power of two."""
    return int(g.loc[g['bucket'] >= x, 'n_keys'].sum())


def percentile(g, p):
    total = g['n_keys'].sum()
    cum = g['n_keys'].cumsum()
    idx = (cum >= p * total).idxmax()
    return int(g.loc[idx, 'bucket'])


def fmt_frac(num, den):
    if num == 0:
        return '0'
    f = num / den
    return f'{f:.2e} ({num:,} keys)'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--all', help='one result CSV of btc_all.sql or eth_all.sql (hist, rate and tail combined)')
    ap.add_argument('--hist')
    ap.add_argument('--tail')
    ap.add_argument('--rate')
    ap.add_argument('--types', nargs='*', default=SINGLE_KEY_TYPES)
    ap.add_argument('--label', default='chain')
    ap.add_argument('--out', default='c3')
    ap.add_argument('--years', type=float, nargs='*', default=[10, 30])
    a = ap.parse_args()

    rate_df = tail_df = None
    if a.all:
        d = pd.read_csv(a.all)
        hist_df = d[d['kind'] == 'hist'][['type', 'bucket', 'n_keys']]
        rate_df = d[d['kind'] == 'rate'].rename(columns={'bucket': 'log2_rate_per_year'})[['type', 'log2_rate_per_year', 'n_keys']]
        tail_df = d[d['kind'] == 'tail'].rename(columns={'bucket': 'active_days', 'n_sigs': 'n_sig'})
        if 'n_mismatch' in d.columns:
            h = d[d['kind'] == 'hist']
            print(f"(consistency check) accounts whose nonce disagrees with the transaction count: {int(h['n_mismatch'].sum()):,} / {int(h['n_keys'].sum()):,}\n")
    else:
        if not a.hist:
            ap.error('either --all or --hist is required')
        hist_df = pd.read_csv(a.hist)
        rate_df = pd.read_csv(a.rate) if a.rate else None
        tail_df = pd.read_csv(a.tail) if a.tail else None

    g = load_hist(hist_df, a.types)
    total = int(g['n_keys'].sum())
    print(f'## {a.label}: {total:,} keys that signed\n')

    print('### Quantiles (on-chain signatures per key)\n')
    print('| Quantile | Signatures |\n| --- | --- |')
    for p in (0.5, 0.9, 0.99, 0.999, 0.9999, 0.99999):
        b = percentile(g, p)
        txt = f'{b:,}' if b <= 1024 else f'2^{int(math.log2(b))} ~ 2^{int(math.log2(b))+1}'
        print(f'| {p*100:g}% | {txt} |')
    print(f'| Maximum | at least 2^{int(math.log2(g["bucket"].max()))} |\n')

    print('### Share of keys with at least 2^k signatures\n')
    print('| k | Share |\n| --- | --- |')
    for k in (0, 1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30):
        print(f'| {k} | {fmt_frac(ccdf_at(g, 2**k), total)} |')
    print()

    print('### Overuse risk per parameter set (cumulative over the observed period)\n')
    print('| Set | Nominal budget | Keys over budget | Keys below 112 bits | Keys below 100 bits | Keys below 80 bits |')
    print('| --- | --- | --- | --- | --- | --- |')
    for name, (nom, t128, t112, t100, t80) in THRESHOLDS.items():
        cells = [fmt_frac(ccdf_at(g, 2 ** math.floor(t)), total) for t in (t128, t112, t100, t80)]
        print(f'| {name} | 2^{nom} | ' + ' | '.join(cells) + ' |')
    print('\n(Each threshold t is rounded down to 2^floor(t), a conservative approximation that slightly overstates the risk.)\n')

    if rate_df is not None and len(rate_df):
        r = rate_df
        if 'type' in r.columns and a.types:
            r = r[r['type'].isin(a.types)]
        r = r.groupby('log2_rate_per_year', as_index=False)['n_keys'].sum()
        r['log2_rate_per_year'] = r['log2_rate_per_year'].astype(int)
        rtot = int(r['n_keys'].sum())
        print('### Lifetime extrapolation: keys whose yearly rate times years of use exceeds the budget (keys with at least 2 signatures)\n')
        print('| Set | ' + ' | '.join(f'{y:g} years' for y in a.years) + ' |')
        print('| --- |' + ' --- |' * len(a.years))
        for name, (nom, t128, *_rest) in THRESHOLDS.items():
            cells = []
            for y in a.years:
                need = t128 - math.log2(y)      # lower bound on log2(yearly rate)
                n = int(r.loc[r['log2_rate_per_year'] >= math.floor(need), 'n_keys'].sum())
                cells.append(fmt_frac(n, rtot))
            print(f'| {name} | ' + ' | '.join(cells) + ' |')
        print()

    if tail_df is not None and len(tail_df):
        t = tail_df
        if 'type' in t.columns and a.types:
            t = t[t['type'].isin(a.types)]
        t = t.sort_values('n_sig', ascending=False)
        print('### Heaviest keys (tail)\n')
        print('| Rank | Signatures (log2) | Active days | Yearly rate (log2) |\n| --- | --- | --- | --- |')
        for i, row in enumerate(t.head(10).itertuples(), 1):
            days = max(getattr(row, 'active_days', 365), 30)
            print(f'| {i} | {math.log2(row.n_sig):.1f} | {days:,} | {math.log2(row.n_sig * 365 / days):.1f} |')
        print()

    # CCDF figure
    import logging
    logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams['font.family'] = ['DejaVu Sans']
    xs = [2 ** k for k in range(0, 33)]
    ys = [max(ccdf_at(g, x), 0.5) / total for x in xs]
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.step([math.log2(x) for x in xs], ys, where='post', color='#185FA5', label=a.label)
    ax.set_yscale('log')
    ax.set_xlabel('Signatures per key (log2)')
    ax.set_ylabel('Share of keys with at least that many signatures')
    for name, col in (('FIPS 2x q=2^20 (22,2,15,9)', '#0F6E56'), ('SP 800-230 128-24', '#854F0B'),
                      ('FIPS 2x q=2^30 (33,3,15,9)', '#534AB7'), ('SHRINCS stateless', '#993556')):
        ax.axvline(THRESHOLDS[name][0], color=col, ls='--', lw=1, label=f'{name} nominal budget')
    ax.legend(fontsize=7, loc='upper right')
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(f'{a.out}_ccdf.svg')
    fig.savefig(f'{a.out}_ccdf.png', dpi=150)
    print(f'Figure saved: {a.out}_ccdf.svg, {a.out}_ccdf.png')


if __name__ == '__main__':
    main()
