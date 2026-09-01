# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

from av_integrity.harness.scenario import nominal, gps_jump
from av_integrity.harness.runner import run
from av_integrity.harness.metrics import rmse, detection_report
from av_integrity.integrity.detector import InnovationMonitor

WINDOW = (12.0, 20.0)


def test_no_false_alarms_under_nominal():
    res = run(nominal(seed=0), monitor=InnovationMonitor())
    assert [t for (t, s) in res["flags"] if s == "gps"] == []


def test_detects_and_isolates_gps_jump():
    res = run(gps_jump(start=WINDOW[0], end=WINDOW[1], offset=8.0), monitor=InnovationMonitor())
    det = detection_report(res, WINDOW)
    assert det["detected"]
    assert det["false_alarms"] == 0


def test_gating_keeps_estimate_cleaner_than_baseline():
    scn = gps_jump(start=WINDOW[0], end=WINDOW[1], offset=8.0)
    baseline = run(scn)                                  # follows the spoof
    guarded = run(scn, monitor=InnovationMonitor())      # gated
    assert rmse(guarded)["position_rmse_m"] < rmse(baseline)["position_rmse_m"]
