#!/bin/sh
# Re-run every search behind Tables 3, 4 and 7 of the paper.
# Total run time is about one hour on one core.
set -e
cd "$(dirname "$0")/src"
python3 thresholds.py                 | tee ../results/thresholds.log
for cap in 2 1 4; do
  python3 stages_s1_s5.py V1 $cap     | tee ../results/s1_s5_V1_$cap.log
  python3 stages_s6_s7.py V1 $cap     | tee ../results/s6_s7_V1_$cap.log
done
for cap in 2 1 4; do
  python3 stages_s1_s5.py V2 $cap     | tee ../results/s1_s5_V2_$cap.log
done
python3 summary.py                    | tee ../results/summary.md
