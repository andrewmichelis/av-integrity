# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""Wheel speed: reports how fast the vehicle is moving, from the wheels.

On a real vehicle this comes from the wheel encoders (odometry). Its
characteristic failure is **slip**: on ice or gravel the wheel spins faster than
the vehicle actually moves, so the reading over-states the true speed. It can
also **drop out**. It sees speed only.
"""
import numpy as np

from av_integrity.sensors.base import Sensor
from av_integrity.estimation.state import V


class WheelSpeed(Sensor):
    name = "wheel_speed"

    def measure(self, true_state, true_controls, t):
        # Dropout: no reading while the fault is active.
        for fault in self.faults:
            if fault.kind == "dropout" and fault.active(t):
                return None

        # Normal reading: true speed plus a little jitter.
        speed = true_state[V] + self._noise()[0]

        # Slip: the wheels under-report the true speed while slipping.
        for fault in self.faults:
            if fault.active(t) and fault.kind == "slip":
                speed = speed - fault.value

        return np.array([speed])
