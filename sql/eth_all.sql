-- Ethereum measurement (runs in the BigQuery sandbox; one result file)
-- One signature = one transaction included in a block (failed transactions included). Key = sender address (EOA).
-- n_mismatch: number of accounts whose transaction count differs from (max nonce + 1) (consistency check).
-- Dry run: change the start date to TIMESTAMP '2026-09-01' to query one month and check the bytes processed.

WITH per_key AS (
  SELECT
    from_address AS addr,
    COUNT(*)       AS n_sig,
    MAX(nonce) + 1 AS nonce_next,
    MIN(block_timestamp) AS first_ts,
    MAX(block_timestamp) AS last_ts
  FROM `bigquery-public-data.crypto_ethereum.transactions`
  WHERE block_timestamp BETWEEN TIMESTAMP '2015-07-30' AND TIMESTAMP '2026-10-01'
  GROUP BY from_address
),
hist AS (
  SELECT 'hist' AS kind, 'eoa' AS type, CAST(NULL AS STRING) AS addr,
    IF(n_sig <= 1024, n_sig, CAST(POW(2, FLOOR(LOG(n_sig, 2))) AS INT64)) AS bucket,
    COUNT(*) AS n_keys, SUM(n_sig) AS n_sigs,
    COUNTIF(nonce_next <> n_sig) AS n_mismatch
  FROM per_key
  GROUP BY bucket
),
rate AS (
  SELECT 'rate' AS kind, 'eoa' AS type, CAST(NULL AS STRING) AS addr,
    CAST(FLOOR(LOG(n_sig * 365.0 / GREATEST(TIMESTAMP_DIFF(last_ts, first_ts, DAY), 30), 2)) AS INT64) AS bucket,
    COUNT(*) AS n_keys, SUM(n_sig) AS n_sigs, 0 AS n_mismatch
  FROM per_key
  WHERE n_sig >= 2
  GROUP BY bucket
),
tail AS (
  SELECT 'tail' AS kind, 'eoa' AS type, addr,
    TIMESTAMP_DIFF(last_ts, first_ts, DAY) AS bucket,   -- in tail rows, bucket = active days
    1 AS n_keys, n_sig AS n_sigs, IF(nonce_next <> n_sig, 1, 0) AS n_mismatch
  FROM per_key
  ORDER BY n_sig DESC
  LIMIT 5000
)
SELECT * FROM (
  SELECT * FROM hist UNION ALL SELECT * FROM rate UNION ALL SELECT * FROM tail
)
ORDER BY kind, type, bucket;
