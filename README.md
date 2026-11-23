# Per-key signature counts on Bitcoin and Ethereum

Queries, results and analysis scripts for the measurement, and the cost model and parameter search, in

> J. Lee, "Post-Quantum Hash-Based Signatures for Blockchain Transactions: A Systematization and Measurement of Per-Key Signature Limits," submitted to *KSII Transactions on Internet and Information Systems*, 2026.

The measurement counts how many on-chain signatures each key has produced over the complete history of Bitcoin and Ethereum, up to the October 2026 partition of the public BigQuery datasets. The paper uses these counts to choose the per-key signature limit (signature budget) of hash-based signatures for transaction authorization.

## Contents

| Path | Description |
| --- | --- |
| `sql/btc_all.sql` | Bitcoin query: per-key histogram, yearly signing rate, and the 5,000 heaviest keys in one result |
| `sql/eth_all.sql` | Ethereum query: the same for externally owned accounts, plus a nonce consistency check |
| `data/btc_all.csv` | Result of `btc_all.sql` |
| `data/eth_all.csv` | Result of `eth_all.sql` |
| `analysis/analyze_c3.py` | Quantiles, CCDF and CCDF figure from a result CSV (Table 5, Fig. 2) |
| `analysis/fig1.py` | Waterfall decomposition of the signature size at a budget of 2^30, from the sizes of Table 3 (Fig. 1) |
| `analysis/table7.py` | Overuse thresholds against measured and projected per-key counts (Table 7, Sections 6.4 and 7) |
| `costmodel/model.py` | Size, compression-call costs and security of SLH-DSA, WOTS+C, FORS+C and PORS+FP (Sections 3.2, 3.3 and 5.1) |
| `costmodel/search.py` | Stage-wise exhaustive parameter search, stages S1 to S5 (Section 5.1) |
| `costmodel/octopus_pmf.py` | Size distribution of the Octopus authentication set, for the PORS+FP grinding work (MIT, from PORS-FP) |
| `costmodel/reproduce.py` | Checks the model and the search against the numbers of Sections 5 and 7 |
| `search/` | Parameter search for all stages S1 to S7 and the Table 7 thresholds, on the upstream SPHINCS-Parameters model; see `search/README.md` |
| `CORPUS.md` | The 46 works of the systematization, by category and search stage, with full references (Section 2.1) |

## Definitions

- **Bitcoin.** One signature is one transaction input with exactly one address; the key is that address. Bare multisig inputs are excluded. The analysis counts single-key output types by default (`pubkeyhash`, `witness_v0_keyhash`, `witness_v1_taproot`, `pubkey`). `scripthash` mixes multisig with P2SH-wrapped SegWit and is excluded unless requested with `--types`.
- **Ethereum.** One signature is one transaction included in a block, failed transactions included; the key is the sender address (EOA). `n_mismatch` counts accounts whose transaction count differs from the highest nonce plus one; it is 0.49% of accounts (1,551,008 of 319,435,354).
- **Buckets.** Counts up to 1,024 are exact; larger counts are grouped by powers of two.
- **Yearly rate.** For keys with at least two signatures, signatures × 365 / max(active days, 30), recorded as floor(log2). These `rate` rows describe the whole population; Table 7 does not use them.
- **Lifetime projection (Table 7).** For each of the 5,000 heaviest keys (`tail` rows) active for at least 365 days, signatures × 365 / active days × 30, that is, 30 years from the first signature, and never less than the current count. Keys active for fewer than 365 days keep their current count, because a few months of peak activity would overstate their lifetime load. The tail is complete for Table 7: its smallest count is 2^13.84 on Bitcoin (single-key types) and 2^14.89 on Ethereum, so no key outside it can reach the smallest threshold, 2^20.0, even after projection.
- **Thresholds (Table 7).** Each count is compared with the threshold in log2 to one decimal, as listed in Table 7, in both the measured and the projected columns. The thresholds are computed by `search/src/thresholds.py` (`search/results/thresholds.csv`).
- **Lower bound.** Only signatures included in blocks are visible. Replaced or abandoned transactions, Lightning channel updates and off-chain messages (for example EIP-712 orders and permits) are not counted.

## Cost model and parameter search

`costmodel/` reimplements the public cost model of [SPHINCS-Parameters](https://github.com/BlockstreamResearch/SPHINCS-Parameters) (reference [9] of the paper) in Python, and adds the stage-wise search of Section 5.1.

- **Version of the reference model.** Costs follow SPHINCS-Parameters at commit `3172178` (2026-11-16), before the "top layer saving" change of 2026-11-17. With that version the baseline SLH-DSA-SHA2-128s costs 2,218,486 compressions to sign, as in the paper. `TOP_SAVE = True` in `model.py` follows the later version (2,218,200).
- **Costs.** SHA-256 compression calls with the PK.seed midstate cached. Verification is the mean over messages (2,193 for the baseline).
- **Security.** Equation (2) of the paper for FORS and FORS+C, and the subset-forgery bound of SPHINCS-Parameters for PORS+FP, capped at 128 bits.
- **Pruning budget.** The search uses the rule of Section 5.1: the smallest `mmax` that keeps signing within the cap. `model.wc_porsfp_kn` applies the rule of Kudinov and Nick (the first `mmax` from (k−1)·a − 22 whose signing costs less than 1.11 times signing with FORS+C), which reproduces their published sets.
- **Grid.** h from q − 12 to q + 14; d from 1 to 25 with h/d ≤ 22; a from 3 to 24; w ∈ {4, 16, 256} (16 only in S1); for each (h, a) the smallest k that reaches 128 bits, and for PORS+FP also the next three.
- **S6 and S7.** BPORS+FP and BPORS-C+BFP need the coverage bounds of references [6] and [7]. They are searched in `search/`, which runs on the upstream model itself (see below).

Run from the repository root:

```
pip install numpy scipy
python3 costmodel/reproduce.py --quick      # under a minute
python3 costmodel/reproduce.py              # with the PORS+FP searches, about 10 minutes
python3 costmodel/search.py 30 2 V1 1,4,5   # one search: log2 q, signing cap, policy, stages
```

`reproduce.py` compares the baseline costs, S1 and S4 of Table 3, the budget shares of Table 4, the SHRINCS stateless set, the Section 5.4 comparison, the thresholds of Table 7 and the published sets of Kudinov and Nick with the paper, and prints S5 for every budget.

## Search for stages S1 to S7 (`search/`)

`search/` runs the stage-wise search on the upstream SPHINCS-Parameters model, fetched at commit `3172178` by `search/setup_upstream.sh`, and adds the coverage bounds of BPORS+FP [6] and BPORS-C+BFP [7] for S6 and S7. It produces Tables 3 and 4 (`search/results/summary.md`) and the thresholds of Table 7 (`search/results/thresholds.csv`). See `search/README.md` for the model, grids and run time.

The two searches agree on S1 to S4 for every budget and signing cap. For S5 (PORS+FP), `search/src/stages_s1_s5.py` uses a narrower grid and gives larger signatures; the S5 sizes and the policy V2 figures in Section 5.2 of the paper come from `costmodel/search.py`, whose grid is the one described in Section 5.1.

## Result files

Each CSV has a `kind` column:

| `kind` | `bucket` means | Other columns |
| --- | --- | --- |
| `hist` | signatures per key (exact up to 1,024, then 2^k) | `n_keys`, `n_sigs` |
| `rate` | floor(log2 of yearly signing rate) | `n_keys`, `n_sigs` |
| `tail` | active days of the key | `addr`, `n_sigs` = signatures of that key |

`eth_all.csv` has the extra column `n_mismatch`.

## Reproducing

1. Open the BigQuery console with a Google account; the free sandbox is enough and needs no billing account.
2. Run `sql/btc_all.sql` and `sql/eth_all.sql`. They process about 208 GB and 211 GB, within the 1 TiB monthly free tier. To check the cost first, change the start date to `2026-09-01` and look at the estimate.
3. Save the results as `data/btc_all.csv` and `data/eth_all.csv`, and run from the repository root:

```
pip install pandas numpy matplotlib
python3 analysis/analyze_c3.py --all data/btc_all.csv --label Bitcoin  --out btc
python3 analysis/analyze_c3.py --all data/eth_all.csv --label Ethereum --out eth
python3 analysis/table7.py --data data
```

`analyze_c3.py` prints Markdown tables and writes `btc_ccdf.svg/png` and `eth_ccdf.svg/png`. `table7.py` prints Table 7 and the heaviest projected keys used for the margins in Sections 6.4 and 7. With `--rule published` it reproduces Table 7 of an earlier draft of the paper, which rounded the measured columns down to powers of two and left short-lived keys out of the projected columns.

Because the public datasets keep growing, a new run without the end date returns slightly larger counts. The queries fix the end at the October 2026 partition.

## Correspondence with the paper

| Paper | Source |
| --- | --- |
| Table 5 (distribution of signatures per key) | `hist` rows, quantile and CCDF output |
| Fig. 2 (share of keys with at least 2^k signatures) | `hist` rows |
| Table 6 (heaviest signers) | `tail` rows, labelled with public explorer labels |
| Section 6.4 (projection to a key's lifetime) | `tail` rows, `table7.py` |
| Table 7 (keys reaching overuse thresholds, now and over 30 years) | `tail` rows, `table7.py` |
| Table 8 (recommended budgets by user type) | `table7.py` output |
| Section 6.1 nonce check | `n_mismatch` in `eth_all.csv` |
| Section 2.1 (literature corpus) | `CORPUS.md` |
| Section 5.1 (baseline costs, validation) | `costmodel/reproduce.py` |
| Tables 3 and 4, stages S1, S4, S6 and S7 | `search/results/summary.md` (S1 and S4 also `costmodel/search.py`) |
| Section 5.2, S3, S5 and policy V2; Fig. 1 | `costmodel/search.py`; `analysis/fig1.py` |
| Section 5.1, validation of S6 and S7 | `search/src/bpors.py` (see `search/README.md`) |
| Section 5.4 (SP 800-230 comparison) | `costmodel/model.py`, checked by `reproduce.py` |
| Table 7 thresholds t128 and t112 | `search/results/thresholds.csv`; all rows except K&N at 2^20, S6 and S7 also checked by `costmodel/reproduce.py` |

The overuse table and lifetime extrapolation printed by `analyze_c3.py` use an earlier set of reference parameters and the coarse `rate` rows; they are kept for reference and do not correspond to Table 7. The thresholds of the final parameter sets are listed in `table7.py`, from `search/results/thresholds.csv`.

## Versions

| Release | Changes |
| --- | --- |
| v1.0 | Queries, results and `analyze_c3.py` |
| v1.1 | `table7.py` added; Table 7 computed from `tail` rows with unrounded thresholds; README updated. Data and queries unchanged. |
| v1.2 | `costmodel/` added: cost model, parameter search (S1 to S5) and reproduction checks for Sections 5 and 7. Data, queries and analysis scripts unchanged. |
| v1.3 | `CORPUS.md` added: the literature corpus of the systematization, moved from the appendix of the paper. Code and data unchanged. |
| v1.4 | Reference numbers and comments synced with the paper; `analysis/fig1.py` added. Data and results unchanged. |
| v1.5 | `search/` added: parameter search for S1 to S7 and the Table 7 thresholds. The S6 and S7 thresholds in `table7.py` corrected to the computed values (S6 and S7 at 2^20: t128 2^20.0; S7 at 2^20: t112 2^24.0; S7 at 2^30: t112 2^34.5). |

## License

Code and queries: MIT. `costmodel/octopus_pmf.py` is adapted from [PORS-FP](https://github.com/MehdiAbri/PORS-FP) (MIT). `search/` fetches SPHINCS-Parameters and does not redistribute it. Data: derived from the public `bigquery-public-data.crypto_bitcoin` and `crypto_ethereum` datasets.
