# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""M2 demo. Run each fault type through the safety layer and show the decision it
makes, then draw the escalating-drive figure. Run with: `python scripts/run_m2.py`.
"""
import os, sys as _s; _s.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from av_integrity.harness import scenario as S
from av_integrity.harness.runner import run
from av_integrity.harness.metrics import safety_states_in, isolated_sensors_in, rmse
from av_integrity.integrity.detector import SafetyMonitor


def show(name, scenario, window):
    r = run(scenario, monitor=SafetyMonitor())
    states = sorted(safety_states_in(r, window))
    isolated = sorted(isolated_sensors_in(r, window)) or ["-"]
    print(f"  {name:12s} -> state(s): {', '.join(states):20s} isolated: {', '.join(isolated):20s} "
          f"posRMSE: {rmse(r)['position_rmse_m']:.2f} m")


def main():
    print("Safety decisions by fault type:")
    show("nominal",    S.nominal(),                            (0, 30))
    show("gps jump",   S.gps_jump(),                           (12, 20))
    show("wheel slip", S.wheel_slip(),                         (8, 14))
    show("imu bias",   S.imu_bias(),                           (8, 14))
    show("dual fault", S.dual_fault(),                         (8, 14))
    try:
        from av_integrity.view.plot import plot_m2
        print("Saved:", plot_m2(run(S.fault_sequence(), monitor=SafetyMonitor())))
    except Exception as e:
        print("(plot skipped:", e, ")")


if __name__ == "__main__":
    main()
