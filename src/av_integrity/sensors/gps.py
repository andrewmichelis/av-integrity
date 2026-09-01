# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""GPS: reports the vehicle's absolute position (east, north).

On a real vehicle this is the satellite receiver. Its characteristic failures are
a sudden **jump/spoof** (the fix shifts by metres and stays shifted) and
**dropout** (no fix for a while). GPS sees position only; it says nothing about
heading or speed.
"""
import numpy as np

from av_integrity.sensors.base import Sensor
from av_integrity.estimation.state import PX, PY


class GPS(Sensor):
    name = "gps"

    def measure(self, true_state, true_controls, t):
        # Dropout: no reading at all while the fault is active.
        for fault in self.faults:
            if fault.kind == "dropout" and fault.active(t):
                return None

        # Normal reading: the true position plus a little gaussian jitter.
        reading = true_state[[PX, PY]] + self._noise()

        # Jump / bias / spoof: shift the reported position while the fault is on.
        for fault in self.faults:
            if fault.active(t) and fault.kind in ("bias", "jump"):
                reading = reading + np.array([fault.value, fault.value])
            elif fault.active(t) and fault.kind == "drift":
                # A slowly growing bias: metres per second since the fault began.
                ramp = fault.value * (t - fault.start)
                reading = reading + np.array([ramp, ramp])

        return reading
