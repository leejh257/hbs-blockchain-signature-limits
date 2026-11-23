# Parameter search (Sections 5 and 7)

Code behind the decomposition of signature size (Tables 3 and 4) and the overuse thresholds (Table 7) of the paper. It is a cost and security model with an exhaustive parameter search, not an implementation of the signature schemes.

## Model

- **Cost.** Sizes are in bytes; signing, verification and key generation are counted in SHA-256 compressions. Sizes and costs of SLH-DSA, WOTS+C, FORS+C and PORS+FP come from the Blockstream SPHINCS-Parameters model, fetched at a fixed commit by `setup_upstream.sh`.
- **Baseline and constraints.** The baseline is SLH-DSA-SHA2-128s: 7,856 B, 2,218,486 compressions to sign and 2,193 to verify. Every candidate keeps 128-bit security at its nominal budget q and signs in at most c times the baseline (c = 1, 2, 4). Policy V1 verifies in no more compressions than the baseline; policy V2 allows at most 2.6 compressions per signature byte.
- **Security of the few-time layer.** It is averaged over the number of signatures that share one few-time key, approximating Bin(q, 2^-h) by a Poisson distribution.
  - S6 (BPORS+FP) uses the coverage bound of Ren, Zhang and Yu (ePrint 2026/1328, Theorem 1).
  - S7 (BPORS-C+BFP) uses the generic generating-function bound of Wang et al. (ePrint 2026/2374, Theorem 1) with a single pruning block, so S7 sizes are upper bounds.

## Stages

| Stage | Search space |
| --- | --- |
| S1 | FIPS 205 algorithms, w = 16 |
| S2 | adds the choice of w in {4, 16, 256} |
| S3 | adds WOTS+C |
| S4 | adds FORS+C |
| S5 | replaces FORS+C by PORS+FP |
| S6 | WOTS+C with BPORS+FP (bucket thinning) |
| S7 | WOTS+C with BPORS-C+BFP (hash chains, blockwise forced pruning) |

## Files

| Path | Purpose |
| --- | --- |
| `setup_upstream.sh` | Clones BlockstreamResearch/SPHINCS-Parameters at commit `03949dd` into `third_party/` |
| `src/engine.py` | Shared cost model and FORS / PORS+FP security |
| `src/bpors.py` | Acceptance probability, coverage bounds and security of BPORS+FP and BPORS-C+BFP |
| `src/stages_s1_s5.py` | Search for stages S1 to S5 |
| `src/stages_s6_s7.py` | Search for stages S6 and S7 (PORS+FP* is the single-bucket case, kept as a check) |
| `src/thresholds.py` | Overuse thresholds t128 and t112 (Table 7) |
| `src/summary.py` | Builds Tables 3 and 4 from the JSON results |
| `results/` | Results of the run used in the paper |

## Running

Requires Python 3.10 or later, NumPy and git.

```
./setup_upstream.sh
./reproduce.sh          # about one hour on one core
```

Single runs: `python3 src/stages_s6_s7.py V1 2 30` searches S6 and S7 at q = 2^30, policy V1, signing cap 2. A single run overwrites the matching file in `results/`.

## Correspondence with the paper

| Paper | Source |
| --- | --- |
| Table 3 | `results/summary.md`, from `s1_s5_V1_2.json` and `s6_s7_V1_2.json` |
| Table 4 | `results/summary.md`, from the V1 results at caps 1, 2 and 4 |
| Fig. 1 | the q = 2^30 row of Table 3 and the S3 stage of `s1_s5_V1_2.json` |
| Table 7, thresholds | `results/thresholds.csv` |
| Section 5.2, policy V2 | `results/summary.md`, from `s1_s5_V2_2.json` (caps 1 and 4 are included for completeness) |

## Validation

- The model reproduces the published sizes of SLH-DSA-128s, the SP 800-230 128-24 set, the SHRINCS stateless set and the three W+C P+FP sets of Kudinov and Nick.
- `bpors.py` reproduces the published figures of the two 2026 constructions. For BPORS+FP 128-24 it gives an acceptance probability of 2.20e-8 at 128 bits or more. For BPORS-C+BFP 128-24 it gives a coverage of 128.019 bits with an acceptance probability of 2.52e-8.

## Third-party code

`third_party/SPHINCS-Parameters` is fetched, not redistributed. Its `third_party/octopus_pmf.py` comes from Abri and Katz's PORS-FP repository under the MIT license.
