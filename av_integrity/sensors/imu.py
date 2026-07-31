# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""IMU: measures the controls [a, omega]; used as the EKF process input.
Faults: bias, drift (ramp on the accel/omega channel 0)."""
import numpy as np
from av_integrity.sensors.base import Sensor


class IMU(Sensor):
    name = "imu"
    def measure(self, true_state, true_controls, t):
        z = np.asarray(true_controls, float) + self._noise()
        for f in self.faults:
            if not f.active(t):
                continue
            if f.kind == "bias":
                z = z + np.array([f.value, 0.0])
            elif f.kind == "drift":
                z = z + np.array([f.value * (t - f.start), 0.0])
        return z
