# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""M3 demo. Inject a moderate IMU bias, the kind the fusion absorbs so the
instantaneous check and the safe-state call it healthy, and show that the drift
monitor still reads its fingerprint in the innovations. Run: `python scripts/run_m3.py`.
"""
import os, sys as _s; _s.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from av_integrity.harness.scenario import imu_bias
from av_integrity.harness.runner import run
from av_integrity.harness.metrics import first_flag_time, first_drift_time, rmse
from av_integrity.integrity.detector import SafetyMonitor, DriftMonitor

WINDOW = (8.0, 28.0)


def main():
    scn = imu_bias(start=WINDOW[0], end=WINDOW[1], value=3.0)
    r = run(scn, monitor=SafetyMonitor(), drift_monitor=DriftMonitor())
    print("Moderate IMU bias (3 m/s^2), which fusion absorbs:")
    print(f"  instantaneous NIS flagged at: {first_flag_time(r, 'gps') or first_flag_time(r, 'wheel_speed')}  (None = missed)")
    print(f"  drift monitor caught it at:   {first_drift_time(r, 'wheel_speed')}  (on wheel speed)")
    print(f"  position RMSE:                {rmse(r)['position_rmse_m']:.2f} m  (estimate stays fine)")
    try:
        from av_integrity.view.plot import plot_m3
        print("  saved:", plot_m3(r, WINDOW, threshold=DriftMonitor.CHI2_99[1]))
    except Exception as e:
        print("  (plot skipped:", e, ")")


if __name__ == "__main__":
    main()
