# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""What a sensor is here, and how we make one misbehave on purpose.

Every sensor takes the true state and returns a noisy, partial reading of it. A
`Fault` lets us corrupt that reading during a chosen time window, so we can test
whether the integrity layer notices. In normal (nominal) runs there are no
faults; the faults are the whole point of the later milestones.
"""
from dataclasses import dataclass

import numpy as np


@dataclass
class Fault:
    """One injected sensor failure, active during [start, end) seconds.

    `kind` names the failure ('bias', 'jump', 'dropout', 'drift', 'slip'); `value`
    is its magnitude, interpreted per sensor. See docs/REFERENCE_physical-mapping.md for
    what each kind means on a real vehicle.
    """
    kind: str
    start: float
    end: float
    value: float = 0.0

    def active(self, t):
        """True while this fault is in effect at time `t`."""
        return self.start <= t < self.end


class Sensor:
    """Base class: a sensor with a fixed sampling rate and gaussian noise.

    The runner decides *when* to sample each sensor (from its rate); this class
    decides *what* a sample looks like. Subclasses implement `measure`.
    """
    name = "sensor"

    def __init__(self, rate_hz, noise_std, rng, faults=None):
        self.rate_hz = rate_hz                          # how often it reports
        self.noise_std = np.atleast_1d(np.asarray(noise_std, float))  # jitter size
        self.rng = rng                                  # shared random generator
        self.faults = faults or []                      # injected faults, if any

    def _noise(self):
        """A fresh gaussian noise sample, one value per measured quantity."""
        return self.rng.normal(0.0, 1.0, self.noise_std.shape) * self.noise_std

    def measure(self, true_state, true_controls, t):
        raise NotImplementedError
