## Table 3 (policy V1, signing cap 2)

| q | SLH-DSA-128s | S1 FIPS 205 re-optimized | S4 WOTS+C, FORS+C | S6 BPORS+FP | S7 BPORS-C+BFP | Saved by budget | Saved by variants | Budget share |
|---|---|---|---|---|---|---|---|---|
| 2^64 | 7,856 | 7,296 | 6,668 | 6,024 | 5,704 | 560 | 1,592 | 26% |
| 2^40 | 7,856 | 5,344 | 4,864 | 4,320 | 3,984 | 2,512 | 1,360 | 65% |
| 2^30 | 7,856 | 4,528 | 4,140 | 3,612 | 3,276 | 3,328 | 1,252 | 73% |
| 2^20 | 7,856 | 3,792 | 3,448 | 2,920 | 2,584 | 4,064 | 1,208 | 77% |

## Table 4 (policy V1)

| Cap | Budget share (2^40 / 2^30 / 2^20) | Saved by variants (2^40 / 2^30 / 2^20) | S7 at 2^30 |
|---|---|---|---|
| 1 | 59% / 67% / 74% | 1,472 / 1,476 / 1,336 | 3,388 |
| 2 | 65% / 73% / 77% | 1,360 / 1,252 / 1,208 | 3,276 |
| 4 | 65% / 74% / 78% | 1,444 / 1,220 / 1,176 | 3,212 |

## Policy V2, signing cap 2 (cross-check)

This search uses a narrower grid than Section 5.1 for S5 (PORS+FP). The S5 sizes and the
policy V2 figures of Section 5.2 come from costmodel/search.py, which reports a largest
further saving of 396 B and verification costs of 6,272 to 12,492 compressions.

- Largest further saving from w = 256: 428 B (30|S5 +PORS+FP)
- Verification cost of the w = 256 sets: 6,274 to 12,492 compressions
