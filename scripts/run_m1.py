# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""M1 demo. Inject a GPS jump, then compare the estimate with and without the
integrity monitor, and report whether the fault was detected. Run with:
`python scripts/run_m1.py`.
"""
import os, sys as _s; _s.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from av_integrity.harness.scenario import gps_jump
from av_integrity.harness.runner import run
from av_integrity.harness.metrics import rmse, detection_report
from av_integrity.integrity.detector import InnovationMonitor

FAULT_WINDOW = (12.0, 20.0)


def main():
    scenario = gps_jump(start=FAULT_WINDOW[0], end=FAULT_WINDOW[1], offset=8.0)
    without_monitor = run(scenario)                          # follows the spoof
    with_monitor = run(scenario, monitor=InnovationMonitor())  # detects + gates it

    detection = detection_report(with_monitor, FAULT_WINDOW)
    print(f"GPS jump (8 m offset, window {FAULT_WINDOW}):")
    print(f"  detected={detection['detected']}  first@t={detection['first_detection_t']}  "
          f"in-window flags={detection['flags_in_window']}  false alarms={detection['false_alarms']}")
    print(f"  position RMSE   no-monitor: {rmse(without_monitor)['position_rmse_m']:.2f} m"
          f"   with-monitor: {rmse(with_monitor)['position_rmse_m']:.2f} m")
    try:
        from av_integrity.view.plot import plot_m1
        print("  saved:", plot_m1(without_monitor, with_monitor, FAULT_WINDOW))
    except Exception as e:
        print("  (plot skipped:", e, ")")


if __name__ == "__main__":
    main()
