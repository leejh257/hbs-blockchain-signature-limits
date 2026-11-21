# Per-key signature counts on Bitcoin and Ethereum

Queries, results and analysis script for the measurement in

> J. Lee, "Post-Quantum Hash-Based Signatures for Blockchain Transactions: A Systematization and Measurement of Per-Key Signature Limits," submitted to *KSII Transactions on Internet and Information Systems*, 2026.

The measurement counts how many on-chain signatures each key has produced over the complete history of Bitcoin and Ethereum, up to the October 2026 partition of the public BigQuery datasets. The paper uses these counts to choose the per-key signature limit (signature budget) of hash-based signatures for transaction authorization.

## Contents

| Path | Description |
| --- | --- |
| `sql/btc_all.sql` | Bitcoin query: per-key histogram, yearly signing rate, and the 5,000 heaviest keys in one result |
| `sql/eth_all.sql` | Ethereum query: the same for externally owned accounts, plus a nonce consistency check |
| `data/btc_all.csv` | Result of `btc_all.sql` |
| `data/eth_all.csv` | Result of `eth_all.sql` |
| `analysis/analyze_c3.py` | Quantiles, CCDF, overuse table, lifetime extrapolation and CCDF figure from a result CSV |

## Definitions

- **Bitcoin.** One signature is one transaction input with exactly one address; the key is that address. Bare multisig inputs are excluded. The analysis counts single-key output types by default (`pubkeyhash`, `witness_v0_keyhash`, `witness_v1_taproot`, `pubkey`). `scripthash` mixes multisig with P2SH-wrapped SegWit and is excluded unless requested with `--types`.
- **Ethereum.** One signature is one transaction included in a block, failed transactions included; the key is the sender address (EOA). `n_mismatch` counts accounts whose transaction count differs from the highest nonce plus one; it is 0.49% of accounts (1,551,008 of 319,435,354).
- **Buckets.** Counts up to 1,024 are exact; larger counts are grouped by powers of two.
- **Yearly rate.** For keys with at least two signatures, signatures × 365 / max(active days, 30), recorded as floor(log2).
- **Lower bound.** Only signatures included in blocks are visible. Replaced or abandoned transactions, Lightning channel updates and off-chain messages (for example EIP-712 orders and permits) are not counted.

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
3. Save each result as CSV and run:

```
pip install pandas matplotlib
python3 analysis/analyze_c3.py --all data/btc_all.csv --label Bitcoin  --out btc
python3 analysis/analyze_c3.py --all data/eth_all.csv --label Ethereum --out eth
```

The script prints Markdown tables and writes `btc_ccdf.svg/png` and `eth_ccdf.svg/png`.

Because the public datasets keep growing, a new run without the end date returns slightly larger counts. The queries fix the end at the October 2026 partition.

## Correspondence with the paper

| Paper | Source |
| --- | --- |
| Table 5 (distribution of signatures per key) | `hist` rows, quantile and CCDF output |
| Fig. 2 (share of keys with at least 2^k signatures) | `hist` rows |
| Table 6 (heaviest signers) | `tail` rows, labelled with public explorer labels |
| Table 7 (keys reaching overuse thresholds, now and over 30 years) | `hist` and `rate` rows |
| Section 6.1 nonce check | `n_mismatch` in `eth_all.csv` |

The overuse thresholds hard-coded in `analyze_c3.py` belong to an earlier set of reference parameters. The thresholds of the final parameter sets in Table 7 come from the paper's parameter search; the key counts are read from the same CSV files.

## License

Code and queries: MIT. Data: derived from the public `bigquery-public-data.crypto_bitcoin` and `crypto_ethereum` datasets.
