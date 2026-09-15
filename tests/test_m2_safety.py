# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

from av_integrity.harness.scenario import nominal, gps_jump, wheel_slip, imu_bias, dual_fault
from av_integrity.harness.runner import run
from av_integrity.harness.metrics import safety_states_in, isolated_sensors_in
from av_integrity.integrity.detector import SafetyMonitor

FULL = (0, 30)


def test_nominal_stays_healthy():
    r = run(nominal(), monitor=SafetyMonitor())
    assert safety_states_in(r, FULL) == {"healthy"}


def test_gps_jump_isolated_and_degraded():
    r = run(gps_jump(start=12, end=20), monitor=SafetyMonitor())
    assert "degraded" in safety_states_in(r, (12, 20))
    assert "safe_stop" not in safety_states_in(r, FULL)
    assert isolated_sensors_in(r, (12, 20)) == {"gps"}


def test_wheel_slip_isolated_and_degraded():
    r = run(wheel_slip(start=8, end=14), monitor=SafetyMonitor())
    assert "degraded" in safety_states_in(r, (8, 14))
    assert "safe_stop" not in safety_states_in(r, FULL)
    assert isolated_sensors_in(r, (8, 14)) == {"wheel_speed"}


def test_imu_bias_is_absorbed_by_fusion():
    # A moderate IMU bias is corrected by the healthy measurements: no safe-stop.
    r = run(imu_bias(start=8, end=14, value=3.0), monitor=SafetyMonitor())
    assert "safe_stop" not in safety_states_in(r, FULL)


def test_dual_fault_triggers_safe_stop():
    r = run(dual_fault(start=8, end=14), monitor=SafetyMonitor())
    assert "safe_stop" in safety_states_in(r, (8, 14))
