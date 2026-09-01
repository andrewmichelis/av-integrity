# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""M0 demo. Run a clean drive, print how well the fused estimate tracks the true
trajectory, and save a picture. Run with: `python scripts/run_demo.py`.
"""
import os, sys as _s; _s.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from av_integrity.harness.scenario import nominal
from av_integrity.harness.runner import run
from av_integrity.harness.metrics import rmse


def main():
    result = run(nominal())
    print("Nominal fusion accuracy (EKF estimate vs ground truth):")
    for name, value in rmse(result).items():
        print(f"  {name:20s} {value:.3f}")
    try:
        from av_integrity.view.plot import plot_result
        print(f"Saved plot: {plot_result(result)}")
    except Exception as e:
        print(f"(plot skipped: {e})")


if __name__ == "__main__":
    main()
