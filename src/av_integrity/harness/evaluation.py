# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""M4 - robustness evaluation: turn single-run anecdotes into rates.

M1-M3 each proved a point on one scenario ("detected at onset", "caught ~1s in").
That is a demonstration, not a measurement. This module runs the monitors across
many seeds and a sweep of fault magnitudes and reports the three numbers that
actually characterise a detector:

  detection rate     of the runs with a fault, how many did we catch
  false-alarm rate   under nominal (no fault), how often do we flag anyway
  time-to-detect     once caught, how long after the fault began

Because faults are injected, ground truth (did a fault occur, and when) is known,
so every number here is a real measurement, not a guess. The sweep also exposes
the honest floor: below some fault size nothing fires, and one fault type - a
slow GPS-only drift - is a blind spot we report rather than hide (see M3).

The integrity monitor is resolved through `integrity.core.load_monitor`, so these
numbers reflect whatever integrity core is installed behind the interface - the
public reference by default, a tuned core if one is present (open/closed, M5).
"""
from dataclasses import dataclass
from typing import Optional

import numpy as np

from av_integrity.harness.runner import run
from av_integrity.harness.scenario import nominal, gps_jump, imu_bias
from av_integrity.harness.metrics import detection_report, first_drift_time
from av_integrity.integrity.detector import DriftMonitor
from av_integrity.integrity.core import load_monitor

CORRECTORS = ("gps", "wheel_speed")


@dataclass
class SweepPoint:
    """Aggregated detection performance at one fault magnitude, over N seeds."""
    magnitude: float
    detection_rate: float                    # fraction of seeds where the fault was caught
    mean_time_to_detect_s: Optional[float]   # mean over caught runs; None if never caught
    n_seeds: int


def false_alarm_rate(seeds=range(40)):
    """How often the instantaneous monitor cries wolf on a clean (nominal) drive.

    Reported per *check* (per corrector reading) - the honest denominator. A run
    makes hundreds of checks, so a per-run count would overstate a per-check
    threshold; both are returned so the difference is visible. With the
    chi-square 99.9% gate the per-check rate should sit near 0.1%.
    """
    total_flags = total_checks = runs_with_flag = n = 0
    for s in seeds:
        r = run(nominal(seed=s), monitor=load_monitor())
        flags = [f for f in r["flags"] if f[1] in CORRECTORS]
        checks = sum(r["checks"][c] for c in CORRECTORS)
        total_flags += len(flags)
        total_checks += checks
        runs_with_flag += 1 if flags else 0
        n += 1
    return {
        "per_check": total_flags / total_checks if total_checks else 0.0,
        "per_run": runs_with_flag / n if n else 0.0,
        "total_flags": total_flags,
        "total_checks": total_checks,
        "n_runs": n,
    }


def sweep_gps_jump(offsets, seeds=range(12), window=(12.0, 20.0)):
    """Loud fault: a sustained GPS position jump of increasing size, caught by the
    instantaneous NIS check. Returns one SweepPoint per offset (metres)."""
    points = []
    seeds = list(seeds)
    for offset in offsets:
        caught, ttds = 0, []
        for s in seeds:
            r = run(gps_jump(seed=s, start=window[0], end=window[1], offset=offset),
                    monitor=load_monitor())
            report = detection_report(r, window, sensor="gps")
            if report["detected"]:
                caught += 1
                ttds.append(report["first_detection_t"] - window[0])
        points.append(SweepPoint(
            magnitude=float(offset),
            detection_rate=caught / len(seeds),
            mean_time_to_detect_s=(float(np.mean(ttds)) if ttds else None),
            n_seeds=len(seeds),
        ))
    return points


def sweep_imu_bias(biases, seeds=range(12), window=(8.0, 28.0)):
    """Quiet fault: an IMU acceleration bias the fusion absorbs, caught (if at all)
    by the slower drift monitor via its wheel-speed fingerprint. Returns one
    SweepPoint per bias magnitude (m/s^2)."""
    points = []
    seeds = list(seeds)
    for bias in biases:
        caught, ttds = 0, []
        for s in seeds:
            r = run(imu_bias(seed=s, start=window[0], end=window[1], value=bias),
                    monitor=load_monitor(), drift_monitor=DriftMonitor())
            t_detect = first_drift_time(r, "wheel_speed")
            if t_detect is not None and window[0] <= t_detect <= window[1]:
                caught += 1
                ttds.append(t_detect - window[0])
        points.append(SweepPoint(
            magnitude=float(bias),
            detection_rate=caught / len(seeds),
            mean_time_to_detect_s=(float(np.mean(ttds)) if ttds else None),
            n_seeds=len(seeds),
        ))
    return points
