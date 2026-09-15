# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

from av_integrity.harness.scenario import nominal, imu_bias
from av_integrity.harness.runner import run
from av_integrity.harness.metrics import first_flag_time, first_drift_time
from av_integrity.integrity.detector import SafetyMonitor, DriftMonitor

BIAS_WINDOW = (8, 28)


def test_no_drift_flag_under_nominal():
    r = run(nominal(), monitor=SafetyMonitor(), drift_monitor=DriftMonitor())
    assert first_drift_time(r, "wheel_speed") is None
    assert first_drift_time(r, "gps") is None


def test_drift_monitor_catches_absorbed_imu_bias():
    scn = imu_bias(start=BIAS_WINDOW[0], end=BIAS_WINDOW[1], value=3.0)
    r = run(scn, monitor=SafetyMonitor(), drift_monitor=DriftMonitor())
    # The instantaneous check misses this bias entirely (fusion absorbs it)...
    assert first_flag_time(r, "gps") is None
    assert first_flag_time(r, "wheel_speed") is None
    # ...but the drift monitor reads its persistent-innovation fingerprint.
    assert first_drift_time(r, "wheel_speed") is not None
