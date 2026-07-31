# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""GPS: measures world-frame position [px, py]. Faults: bias, jump (spoof), dropout."""
import numpy as np
from av_integrity.sensors.base import Sensor
from av_integrity.estimation.state import PX, PY


class GPS(Sensor):
    name = "gps"
    def measure(self, true_state, true_controls, t):
        for f in self.faults:
            if f.kind == "dropout" and f.active(t):
                return None
        z = true_state[[PX, PY]] + self._noise()
        for f in self.faults:
            if f.active(t) and f.kind in ("bias", "jump"):
                z = z + np.array([f.value, f.value])
        return z
