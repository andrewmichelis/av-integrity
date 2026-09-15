# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""Consolidated metrics + figure regeneration for the public harness (M5).

One place that runs the standard scenarios and turns them into the numbers the
README and milestone docs quote, so any reader can reproduce them from a clean
checkout. Detection runs through `integrity.core.load_monitor`, so a tuned core
(if installed) is measured by the exact same harness as the reference - the
open/closed boundary is honoured end to end.
"""
import os

from av_integrity.harness.scenario import (
    nominal, gps_jump, imu_bias, fault_sequence,
)
from av_integrity.harness.runner import run
from av_integrity.harness.metrics import rmse, detection_report
from av_integrity.harness.evaluation import (
    false_alarm_rate, sweep_gps_jump, sweep_imu_bias,
)
from av_integrity.integrity.core import load_monitor, describe
from av_integrity.integrity.detector import DriftMonitor

M1_WINDOW = (12.0, 20.0)


def _ttd(point):
    return "-" if point.mean_time_to_detect_s is None else f"{point.mean_time_to_detect_s:.2f}s"


def text_report(seeds=20):
    """Return the consolidated M0-M4 metrics as printable text."""
    lines = [f"integrity core: {describe(load_monitor())}"]

    acc = rmse(run(nominal()))
    lines += ["", "M0  nominal fusion accuracy (EKF vs truth):",
              f"    position {acc['position_rmse_m']:.2f} m   "
              f"heading {acc['heading_rmse_rad']:.3f} rad   speed {acc['speed_rmse_mps']:.2f} m/s"]

    scn = gps_jump(start=M1_WINDOW[0], end=M1_WINDOW[1], offset=8.0)
    det = detection_report(run(scn, monitor=load_monitor()), M1_WINDOW)
    base = rmse(run(scn))["position_rmse_m"]
    gated = rmse(run(scn, monitor=load_monitor()))["position_rmse_m"]
    lines += ["", f"M1  GPS jump (8 m): detected={det['detected']} "
              f"first@{det['first_detection_t']}s   "
              f"position RMSE {base:.1f} m -> {gated:.1f} m with gating"]

    far = false_alarm_rate(seeds=range(seeds * 3))
    lines += ["", "M4  robustness:",
              f"    false-alarm rate (nominal): {far['per_check'] * 100:.3f}% / check "
              f"({far['total_flags']}/{far['total_checks']} readings)",
              "    GPS jump detection (instantaneous NIS check):"]
    for p in sweep_gps_jump([1.0, 2.0, 3.0, 5.0, 8.0], seeds=range(seeds)):
        lines.append(f"      {p.magnitude:>4.1f} m    rate {p.detection_rate:.2f}   ttd {_ttd(p)}")
    lines.append("    absorbed IMU bias detection (drift monitor):")
    for p in sweep_imu_bias([0.5, 1.0, 2.0, 4.0], seeds=range(seeds)):
        lines.append(f"      {p.magnitude:>4.1f} m/s2  rate {p.detection_rate:.2f}   ttd {_ttd(p)}")
    return "\n".join(lines)


def regenerate_figures(out_dir="docs/img", seeds=20):
    """Regenerate every figure from real runs into `out_dir`. Returns the paths.

    Reproducibility check for the whole pipeline: with the default `out_dir` it
    refreshes the committed figures; tests point it at a temp dir so they exercise
    the pipeline without touching the repo's images.
    """
    from av_integrity.view.plot import (
        plot_result, plot_m1, plot_m2, plot_m3, plot_m4_robustness,
    )
    os.makedirs(out_dir, exist_ok=True)
    out = lambda name: os.path.join(out_dir, name)
    paths = []

    paths.append(plot_result(run(nominal()), path=out("m0-nominal.png")))

    scn1 = gps_jump(start=M1_WINDOW[0], end=M1_WINDOW[1], offset=8.0)
    paths.append(plot_m1(run(scn1), run(scn1, monitor=load_monitor()), M1_WINDOW,
                         path=out("m1-gps-jump.png")))

    paths.append(plot_m2(run(fault_sequence(), monitor=load_monitor()),
                         path=out("m2-safety.png")))

    w3 = (8.0, 28.0)
    r3 = run(imu_bias(start=w3[0], end=w3[1], value=3.0),
             monitor=load_monitor(), drift_monitor=DriftMonitor())
    paths.append(plot_m3(r3, w3, path=out("m3-drift.png")))

    far = false_alarm_rate(seeds=range(seeds * 3))
    jump = sweep_gps_jump([0.3, 0.6, 1.0, 1.5, 2.0, 3.0, 5.0, 8.0], seeds=range(seeds))
    bias = sweep_imu_bias([0.5, 1.0, 1.5, 2.0, 3.0, 4.0], seeds=range(seeds))
    paths.append(plot_m4_robustness(jump, bias, far, path=out("m4-robustness.png")))
    return paths
