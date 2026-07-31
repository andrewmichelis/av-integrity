# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

from av_integrity.harness.scenario import nominal
from av_integrity.harness.runner import run
from av_integrity.harness.metrics import rmse


def test_estimate_tracks_truth_under_nominal():
    """M0 acceptance: with no faults, the fused estimate tracks ground truth."""
    m = rmse(run(nominal()))
    assert m["position_rmse_m"] < 2.0, m
    assert m["speed_rmse_mps"] < 0.5, m
    assert m["heading_rmse_rad"] < 0.1, m


def test_deterministic_given_seed():
    a = rmse(run(nominal(seed=7)))
    b = rmse(run(nominal(seed=7)))
    assert a == b
