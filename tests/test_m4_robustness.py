# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

from av_integrity.harness.evaluation import (
    false_alarm_rate, sweep_gps_jump, sweep_imu_bias,
)


def test_false_alarm_rate_near_zero_under_nominal():
    far = false_alarm_rate(seeds=range(20))
    assert far["total_checks"] > 0
    # The 99.9% chi-square gate should false-alarm on well under 1% of checks.
    assert far["per_check"] < 0.01


def test_large_gps_jump_always_detected_at_onset():
    pt = sweep_gps_jump([8.0], seeds=range(8))[0]
    assert pt.detection_rate == 1.0
    # caught within a GPS sample or two of onset (5 Hz -> 0.2 s spacing).
    assert pt.mean_time_to_detect_s is not None
    assert pt.mean_time_to_detect_s <= 0.5


def test_tiny_gps_jump_mostly_missed():
    # A sub-metre jump sits inside GPS noise; the honest floor is that we miss it.
    pt = sweep_gps_jump([0.3], seeds=range(8))[0]
    assert pt.detection_rate <= 0.5


def test_time_to_detect_shrinks_with_magnitude():
    small, large = sweep_gps_jump([2.0, 8.0], seeds=range(8))
    assert large.detection_rate >= small.detection_rate
    if small.mean_time_to_detect_s is not None and large.mean_time_to_detect_s is not None:
        assert large.mean_time_to_detect_s <= small.mean_time_to_detect_s + 1e-9


def test_drift_monitor_has_a_higher_floor():
    small, large = sweep_imu_bias([0.5, 3.0], seeds=range(6))
    # A big absorbed bias is caught by the drift monitor...
    assert large.detection_rate >= 0.5
    # ...a tiny one is (mostly) below its floor.
    assert small.detection_rate <= large.detection_rate
