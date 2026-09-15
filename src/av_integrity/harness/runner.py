# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""Run one scenario end to end and collect what happened.

Each step: sample the sensors that are due, correct the estimate with them (an
optional integrity monitor may reject a reading first), then predict forward to
the next step using the IMU. If the monitor also does safety assessment (M2), we
record its safe-state over time. We keep the estimate, the flagged/rejected
readings, the GPS NIS, and the safety timeline for the metrics and plots.
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


def run(scenario, monitor=None, drift_monitor=None):
    """Run `scenario`. If a `monitor` is given, its `check` gates each reading;
    if it also has `assess` (a safety monitor), we record the safe-state each step.
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
    does_safety = monitor is not None and hasattr(monitor, "assess")

    estimate = np.zeros((n_steps, STATE_DIM))
    flags = []      # (time, sensor) each time a reading was flagged/rejected
    gps_nis = []    # (time, nis) at every GPS update
    safety = []     # (time, state, flagged_sensors) each step, if a safety monitor
    drift = []      # (time, sensor, drift_score, flagged) at each GPS update, if a drift monitor
    checks = {"gps": 0, "wheel_speed": 0}   # corrector readings actually applied (false-alarm-rate denominator)
    for k in range(n_steps):
        t = times[k]

        if k % gps_stride == 0:
            reading = gps.measure(truth[k], controls[k], t)
            if reading is not None:
                checks["gps"] += 1
                ekf.update_gps(reading, gate=gate)
                if monitor is not None:
                    gps_nis.append((t, monitor.nis.get("gps", 0.0)))
                    if monitor.flags.get("gps"):
                        flags.append((t, "gps"))
                if drift_monitor is not None:
                    drift_monitor.observe("gps", ekf.last_innovation["gps"],
                                          ekf.last_innovation_cov["gps"])
                    drift.append((t, "gps", drift_monitor.score["gps"],
                                  drift_monitor.flags["gps"]))

        if k % wheel_stride == 0:
            reading = wheel.measure(truth[k], controls[k], t)
            if reading is not None:
                checks["wheel_speed"] += 1
                ekf.update_wheel_speed(reading, gate=gate)
                if monitor is not None and monitor.flags.get("wheel_speed"):
                    flags.append((t, "wheel_speed"))
                if drift_monitor is not None:
                    drift_monitor.observe("wheel_speed", ekf.last_innovation["wheel_speed"],
                                          ekf.last_innovation_cov["wheel_speed"])
                    drift.append((t, "wheel_speed", drift_monitor.score["wheel_speed"],
                                  drift_monitor.flags["wheel_speed"]))

        if does_safety:
            state, flagged = monitor.assess()
            safety.append((t, state.value, tuple(sorted(flagged))))

        estimate[k] = ekf.x
        ekf.predict(imu.measure(truth[k], controls[k], t), scenario.dt)

    return {"times": times, "truth": truth, "est": estimate, "controls": controls,
            "flags": flags, "checks": checks,
            "gps_nis": np.array(gps_nis) if gps_nis else np.zeros((0, 2)),
            "safety": safety, "drift": drift}
