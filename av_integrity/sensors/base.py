# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""Sensor base + fault-injection hooks.

A Fault has a kind, an active window [start, end), and a magnitude. Sensors
apply active faults to an otherwise-clean, noisy reading (or drop it). This is
the substrate the M1+ integrity layer is tested against; M0 runs nominal.
"""
from dataclasses import dataclass
import numpy as np


@dataclass
class Fault:
    kind: str            # 'bias' | 'jump' | 'dropout' | 'drift' | 'slip'
    start: float         # seconds
    end: float
    value: float = 0.0
    def active(self, t):
        return self.start <= t < self.end


class Sensor:
    """Sampled by the runner at its own rate; adds gaussian noise + faults."""
    name = "sensor"
    def __init__(self, rate_hz, noise_std, rng, faults=None):
        self.rate_hz = rate_hz
        self.noise_std = np.atleast_1d(np.asarray(noise_std, float))
        self.rng = rng
        self.faults = faults or []
    def _noise(self):
        return self.rng.normal(0.0, 1.0, self.noise_std.shape) * self.noise_std
    def measure(self, true_state, true_controls, t):
        raise NotImplementedError
