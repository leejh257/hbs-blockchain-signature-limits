-- Bitcoin measurement (runs in the BigQuery sandbox; one result file)
-- Outputs the histogram (hist), yearly signing rate (rate) and the 5,000 heaviest keys (tail) together.
-- One signature = one input. Only inputs with a single address are counted (bare multisig inputs excluded).
-- type values: pubkeyhash (P2PKH), witness_v0_keyhash (P2WPKH), witness_v1_taproot (P2TR), pubkey (P2PK),
--          scripthash (P2SH: multisig mixed with P2SH-P2WPKH), witness_v0_scripthash (P2WSH), and others.
-- Dry run: change the start date below to DATE '2026-09-01' to query one month and check the bytes processed.

WITH per_key AS (
  SELECT
    i.type AS type,
    addr,
    COUNT(*)             AS n_sig,
    MIN(t.block_timestamp) AS first_ts,
    MAX(t.block_timestamp) AS last_ts
  FROM `bigquery-public-data.crypto_bitcoin.transactions` AS t,
       UNNEST(t.inputs) AS i,
       UNNEST(i.addresses) AS addr
  WHERE t.block_timestamp_month BETWEEN DATE '2009-01-01' AND DATE '2026-10-01'
    AND ARRAY_LENGTH(i.addresses) = 1
  GROUP BY 1, addr
),
hist AS (
  SELECT 'hist' AS kind, type, CAST(NULL AS STRING) AS addr,
    IF(n_sig <= 1024, n_sig, CAST(POW(2, FLOOR(LOG(n_sig, 2))) AS INT64)) AS bucket,
    COUNT(*) AS n_keys, SUM(n_sig) AS n_sigs
  FROM per_key
  GROUP BY type, bucket
),
rate AS (
  SELECT 'rate' AS kind, type, CAST(NULL AS STRING) AS addr,
    CAST(FLOOR(LOG(n_sig * 365.0 / GREATEST(TIMESTAMP_DIFF(last_ts, first_ts, DAY), 30), 2)) AS INT64) AS bucket,
    COUNT(*) AS n_keys, SUM(n_sig) AS n_sigs
  FROM per_key
  WHERE n_sig >= 2
  GROUP BY type, bucket
),
tail AS (
  SELECT 'tail' AS kind, type, addr,
    TIMESTAMP_DIFF(last_ts, first_ts, DAY) AS bucket,   -- in tail rows, bucket = active days
    1 AS n_keys, n_sig AS n_sigs
  FROM per_key
  ORDER BY n_sig DESC
  LIMIT 5000
)
SELECT * FROM (
  SELECT * FROM hist UNION ALL SELECT * FROM rate UNION ALL SELECT * FROM tail
)
ORDER BY kind, type, bucket;
