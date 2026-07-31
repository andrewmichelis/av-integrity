# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""Wheel-speed: measures [v]. Faults: slip (under-reads), dropout."""
import numpy as np
from av_integrity.sensors.base import Sensor
from av_integrity.estimation.state import V


class WheelSpeed(Sensor):
    name = "wheel_speed"
    def measure(self, true_state, true_controls, t):
        for f in self.faults:
            if f.kind == "dropout" and f.active(t):
                return None
        v = true_state[V] + self._noise()[0]
        for f in self.faults:
            if f.active(t) and f.kind == "slip":
                v = v - f.value
        return np.array([v])
