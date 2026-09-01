# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""The simulated vehicle: how it moves, and the true path we drive it along.

This is the "world". It produces the ground truth (the real trajectory) that the
rest of the system only gets to observe through noisy sensors. Because we own the
truth here, we can later score exactly how good the estimate was.

The vehicle is a simple kinematic model: a point that drives forward at some
speed in some heading, and can accelerate and turn. That is enough to exercise
the sensor fusion and the fault checks without drowning the example in
tyre-and-suspension detail.
"""
import numpy as np

from av_integrity.estimation.state import STATE_DIM


def step_true(state, controls, dt):
    """Advance the true state by one small time step `dt`.

    controls = [acceleration, yaw_rate]. This is the same motion model the filter
    uses to predict, applied here to generate reality.
    """
    px, py, heading, speed = state
    acceleration, yaw_rate = controls
    return np.array([
        px + speed * np.cos(heading) * dt,   # move east according to heading+speed
        py + speed * np.sin(heading) * dt,   # move north according to heading+speed
        heading + yaw_rate * dt,             # turn at the commanded yaw rate
        speed + acceleration * dt,           # speed up / slow down
    ])


def controls_at(t):
    """The drive profile: what the vehicle is doing at time `t` (in seconds).

    A simple, legible manoeuvre so the plots are easy to read: accelerate, cruise
    straight, take a steady left curve, cruise, then brake to a stop. Returns
    [acceleration, yaw_rate].
    """
    if t < 4.0:    return np.array([1.0, 0.0])    # accelerate
    if t < 10.0:   return np.array([0.0, 0.0])    # cruise straight
    if t < 16.0:   return np.array([0.0, 0.15])   # steady left curve
    if t < 24.0:   return np.array([0.0, 0.0])    # cruise straight
    if t < 28.0:   return np.array([-1.0, 0.0])   # brake
    return np.array([0.0, 0.0])                   # stopped


def ground_truth(duration, dt, start_state=None):
    """Roll the drive profile forward to get the whole true trajectory.

    Returns three arrays, all the same length:
      times      the time of each step
      states     the true [px, py, heading, speed] at each step
      controls   the [acceleration, yaw_rate] applied at each step (this is also
                 what a perfect IMU would read)
    """
    state = np.array([0.0, 0.0, 0.0, 0.0]) if start_state is None \
        else np.asarray(start_state, float).copy()

    n_steps = int(round(duration / dt))
    times = np.arange(n_steps) * dt
    states = np.zeros((n_steps, STATE_DIM))
    controls = np.zeros((n_steps, 2))

    for k in range(n_steps):
        states[k] = state
        controls[k] = controls_at(times[k])
        state = step_true(state, controls[k], dt)   # advance to the next step

    return times, states, controls
