# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""Kinematic vehicle model + ground-truth trajectory.

State x = [px, py, theta, v]; controls u = [a (accel), omega (yaw rate)].
Motion (unicycle):  px' = v cos(theta);  py' = v sin(theta);  theta' = omega;  v' = a
"""
import numpy as np
from av_integrity.estimation.state import STATE_DIM


def step_true(x, u, dt):
    """Integrate the true state one step (Euler)."""
    px, py, th, v = x
    a, omega = u
    return np.array([
        px + v * np.cos(th) * dt,
        py + v * np.sin(th) * dt,
        th + omega * dt,
        v + a * dt,
    ])


def controls_at(t):
    """Nominal drive profile -> u = [a, omega]."""
    if t < 4.0:   return np.array([1.0, 0.0])    # accelerate
    if t < 10.0:  return np.array([0.0, 0.0])    # cruise straight
    if t < 16.0:  return np.array([0.0, 0.15])   # steady left curve
    if t < 24.0:  return np.array([0.0, 0.0])    # cruise straight
    if t < 28.0:  return np.array([-1.0, 0.0])   # brake
    return np.array([0.0, 0.0])


def ground_truth(duration, dt, x0=None):
    """Generate the true trajectory. Returns (times, states[N,4], controls[N,2])."""
    x = np.array([0.0, 0.0, 0.0, 0.0]) if x0 is None else np.asarray(x0, float).copy()
    n = int(round(duration / dt))
    times = np.arange(n) * dt
    states = np.zeros((n, STATE_DIM))
    controls = np.zeros((n, 2))
    for k in range(n):
        states[k] = x
        controls[k] = controls_at(times[k])
        x = step_true(x, controls[k], dt)
    return times, states, controls
