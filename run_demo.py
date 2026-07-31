# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""M0 demo: run the nominal scenario, print fusion accuracy, save a plot."""
from av_integrity.harness.scenario import nominal
from av_integrity.harness.runner import run
from av_integrity.harness.metrics import rmse


def main():
    result = run(nominal())
    print("Nominal fusion accuracy (EKF estimate vs ground truth):")
    for k, v in rmse(result).items():
        print(f"  {k:20s} {v:.3f}")
    try:
        from av_integrity.view.plot import plot_result
        print(f"Saved plot: {plot_result(result)}")
    except Exception as e:
        print(f"(plot skipped: {e})")


if __name__ == "__main__":
    main()
