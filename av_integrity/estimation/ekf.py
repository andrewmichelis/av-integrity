# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""Compact Extended Kalman Filter for the vehicle state.

Prediction is driven by the IMU (u = [a, omega]); GPS and wheel-speed are
measurement updates. The EKF itself is commodity; the value of this project is
the integration and the integrity layer around it (see av_integrity/integrity).
"""
import numpy as np
from av_integrity.estimation.state import PX, PY, THETA, V, STATE_DIM


class VehicleEKF:
    def __init__(self, x0, P0, Q, R_gps, R_ws):
        self.x = np.asarray(x0, float).copy()
        self.P = np.asarray(P0, float).copy()
        self.Q = np.asarray(Q, float)
        self.R_gps = np.asarray(R_gps, float)
        self.R_ws = np.asarray(R_ws, float)
        self.last_innovation = {}  # sensor -> innovation (consumed by the integrity layer)

    def predict(self, imu, dt):
        """imu = [a, omega]; propagate with the kinematic model."""
        a, omega = imu
        px, py, th, v = self.x
        self.x = np.array([
            px + v * np.cos(th) * dt,
            py + v * np.sin(th) * dt,
            th + omega * dt,
            v + a * dt,
        ])
        F = np.eye(STATE_DIM)
        F[PX, THETA] = -v * np.sin(th) * dt
        F[PX, V]     =  np.cos(th) * dt
        F[PY, THETA] =  v * np.cos(th) * dt
        F[PY, V]     =  np.sin(th) * dt
        self.P = F @ self.P @ F.T + self.Q

    def _update(self, z, H, R, name):
        z = np.atleast_1d(np.asarray(z, float))
        y = z - H @ self.x                 # innovation
        S = H @ self.P @ H.T + R
        K = self.P @ H.T @ np.linalg.inv(S)
        self.x = self.x + K @ y
        self.P = (np.eye(STATE_DIM) - K @ H) @ self.P
        self.last_innovation[name] = y
        return y

    def update_gps(self, z):
        H = np.zeros((2, STATE_DIM)); H[0, PX] = 1.0; H[1, PY] = 1.0
        return self._update(z, H, self.R_gps, "gps")

    def update_wheel_speed(self, z):
        H = np.zeros((1, STATE_DIM)); H[0, V] = 1.0
        return self._update(z, H, self.R_ws, "wheel_speed")
