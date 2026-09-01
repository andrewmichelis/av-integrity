# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""IMU: reports how the vehicle is accelerating and turning.

On a real vehicle this is the inertial measurement unit (a small MEMS chip). We
use it to *predict* motion between GPS fixes. Its characteristic failure is
**drift**: a small error that slowly grows and, uncaught, bends the predicted
path. The IMU measures [acceleration, yaw_rate]; it does not see position.
"""
import numpy as np

from av_integrity.sensors.base import Sensor


class IMU(Sensor):
    name = "imu"

    def measure(self, true_state, true_controls, t):
        # A perfect IMU would read the true controls; a real one adds noise.
        reading = np.asarray(true_controls, float) + self._noise()

        for fault in self.faults:
            if not fault.active(t):
                continue
            if fault.kind == "bias":
                # A constant offset on the acceleration channel.
                reading = reading + np.array([fault.value, 0.0])
            elif fault.kind == "drift":
                # An offset that grows the longer the fault runs.
                reading = reading + np.array([fault.value * (t - fault.start), 0.0])

        return reading
