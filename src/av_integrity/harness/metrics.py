# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""Turning a run into numbers: how accurate was the estimate, and did we detect
the fault. Because we hold the ground truth, these are real measurements, not
guesses.
"""
import numpy as np

from av_integrity.estimation.state import PX, PY, THETA, V


def rmse(result):
    """Root-mean-square error of the estimate against ground truth.

    RMSE is just "typical size of the error": average the squared errors over the
    whole run, then square-root. Lower is better. We report it for position,
    heading, and speed.
    """
    truth, est = result["truth"], result["est"]
    position_error = np.linalg.norm(est[:, [PX, PY]] - truth[:, [PX, PY]], axis=1)

    # Heading is an angle, so wrap the difference into [-pi, pi] before measuring.
    heading_diff = est[:, THETA] - truth[:, THETA]
    heading_error = np.abs(np.arctan2(np.sin(heading_diff), np.cos(heading_diff)))

    speed_error = np.abs(est[:, V] - truth[:, V])
    return {
        "position_rmse_m": float(np.sqrt(np.mean(position_error ** 2))),
        "heading_rmse_rad": float(np.sqrt(np.mean(heading_error ** 2))),
        "speed_rmse_mps": float(np.sqrt(np.mean(speed_error ** 2))),
    }


def detection_report(result, window, sensor="gps"):
    """How well did we detect a fault in a known window (start, end) seconds.

    detected        did we flag the sensor at all during the fault?
    flags_in_window how many flags landed inside the fault window (good)
    false_alarms    how many flags landed outside it (bad)
    first_detection_t  when we first caught it
    """
    start, end = window
    flag_times = [t for (t, s) in result["flags"] if s == sensor]
    inside = [t for t in flag_times if start <= t < end]
    outside = [t for t in flag_times if not (start <= t < end)]
    return {
        "detected": len(inside) > 0,
        "flags_in_window": len(inside),
        "false_alarms": len(outside),
        "first_detection_t": (min(inside) if inside else None),
    }


def first_flag_time(result, sensor):
    """When the instantaneous (NIS) check first flagged `sensor`, or None."""
    ts = [t for (t, s) in result["flags"] if s == sensor]
    return min(ts) if ts else None
