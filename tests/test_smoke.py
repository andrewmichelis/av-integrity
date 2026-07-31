# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

import numpy as np
from av_integrity.sim.vehicle import ground_truth
from av_integrity.sensors.gps import GPS
from av_integrity.sensors.base import Fault


def test_ground_truth_shape():
    t, x, u = ground_truth(5.0, 0.02)
    assert x.shape[1] == 4 and len(t) == len(x) == len(u)


def test_gps_dropout_returns_none():
    g = GPS(5.0, [0.5, 0.5], np.random.default_rng(0), [Fault("dropout", 0.0, 10.0)])
    assert g.measure(np.zeros(4), np.zeros(2), 1.0) is None
