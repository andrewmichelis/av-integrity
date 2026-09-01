# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""Run one scenario end to end and collect what happened.

Each step: sample the sensors that are due, correct the estimate with them (an
optional integrity monitor may reject a reading first), then predict forward to
the next step using the IMU. We keep the estimate, the flagged/rejected readings,
and the GPS NIS for the metrics and plots.
"""
import numpy as np

from av_integrity.sim.vehicle import ground_truth
from av_integrity.sensors.gps import GPS
from av_integrity.sensors.imu import IMU
from av_integrity.sensors.wheel_speed import WheelSpeed
from av_integrity.estimation.ekf import VehicleEKF
from av_integrity.estimation.state import STATE_DIM


def _steps_between(rate_hz, dt):
    """How many simulation steps pass between two samples of a `rate_hz` sensor."""
    return max(1, int(round((1.0 / rate_hz) / dt)))


def run(scenario, monitor=None):
    """Run `scenario`. If a `monitor` is given, its `check` gates each reading
    (rejected when flagged) and per-sensor flags / GPS NIS are recorded.
    """
    rng = np.random.default_rng(scenario.seed)
    times, truth, controls = ground_truth(scenario.duration, scenario.dt)
    n_steps = len(times)

    gps = GPS(scenario.gps_rate, [0.6, 0.6], rng, scenario.gps_faults)
    imu = IMU(scenario.imu_rate, [0.10, 0.005], rng, scenario.imu_faults)
    wheel = WheelSpeed(scenario.wheel_rate, [0.12], rng, scenario.wheel_faults)
    gps_stride = _steps_between(scenario.gps_rate, scenario.dt)
    wheel_stride = _steps_between(scenario.wheel_rate, scenario.dt)

    initial_state = truth[0] + rng.normal(0, [1.0, 1.0, 0.05, 0.5])
    initial_uncertainty = np.diag([2.0, 2.0, 0.1, 1.0]) ** 2
    process_noise = np.diag([0.05, 0.05, 0.01, 0.10]) ** 2
    ekf = VehicleEKF(initial_state, initial_uncertainty, process_noise,
                     gps_noise=np.diag([0.6, 0.6]) ** 2,
                     wheel_speed_noise=np.diag([0.12]) ** 2)
    gate = monitor.check if monitor is not None else None

    estimate = np.zeros((n_steps, STATE_DIM))
    flags = []      # (time, sensor) each time a reading was flagged/rejected
    gps_nis = []    # (time, nis) at every GPS update
    for k in range(n_steps):
        t = times[k]

        if k % gps_stride == 0:
            reading = gps.measure(truth[k], controls[k], t)
            if reading is not None:
                ekf.update_gps(reading, gate=gate)
                if monitor is not None:
                    gps_nis.append((t, monitor.nis.get("gps", 0.0)))
                    if monitor.flags.get("gps"):
                        flags.append((t, "gps"))

        if k % wheel_stride == 0:
            reading = wheel.measure(truth[k], controls[k], t)
            if reading is not None:
                ekf.update_wheel_speed(reading, gate=gate)
                if monitor is not None and monitor.flags.get("wheel_speed"):
                    flags.append((t, "wheel_speed"))

        estimate[k] = ekf.x
        ekf.predict(imu.measure(truth[k], controls[k], t), scenario.dt)

    return {"times": times, "truth": truth, "est": estimate, "controls": controls,
            "flags": flags,
            "gps_nis": np.array(gps_nis) if gps_nis else np.zeros((0, 2))}
