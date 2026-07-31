# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""Run a scenario: ground truth -> sensors -> EKF -> collect estimate vs truth."""
import numpy as np
from av_integrity.sim.vehicle import ground_truth
from av_integrity.sensors.gps import GPS
from av_integrity.sensors.imu import IMU
from av_integrity.sensors.wheel_speed import WheelSpeed
from av_integrity.estimation.ekf import VehicleEKF
from av_integrity.estimation.state import STATE_DIM
from av_integrity.integrity.detector import ReferenceMonitor


def _decim(rate, dt):
    return max(1, int(round((1.0 / rate) / dt)))


def run(scn):
    rng = np.random.default_rng(scn.seed)
    times, truth, controls = ground_truth(scn.duration, scn.dt)
    n = len(times)

    gps = GPS(scn.gps_rate, [0.6, 0.6], rng, scn.gps_faults)
    imu = IMU(scn.imu_rate, [0.10, 0.005], rng, scn.imu_faults)
    wheel = WheelSpeed(scn.wheel_rate, [0.12], rng, scn.wheel_faults)
    d_gps, d_wheel = _decim(scn.gps_rate, scn.dt), _decim(scn.wheel_rate, scn.dt)

    x0 = truth[0] + rng.normal(0, [1.0, 1.0, 0.05, 0.5])
    P0 = np.diag([2.0, 2.0, 0.1, 1.0]) ** 2
    Q = np.diag([0.05, 0.05, 0.01, 0.10]) ** 2
    R_gps = np.diag([0.6, 0.6]) ** 2
    R_ws = np.diag([0.12]) ** 2
    ekf = VehicleEKF(x0, P0, Q, R_gps, R_ws)
    monitor = ReferenceMonitor()

    est = np.zeros((n, STATE_DIM))
    for k in range(n):
        t = times[k]
        if k % d_gps == 0:
            z = gps.measure(truth[k], controls[k], t)
            if z is not None:
                ekf.update_gps(z)
        if k % d_wheel == 0:
            z = wheel.measure(truth[k], controls[k], t)
            if z is not None:
                ekf.update_wheel_speed(z)
        monitor.update(ekf, t)
        est[k] = ekf.x
        ekf.predict(imu.measure(truth[k], controls[k], t), scn.dt)  # -> truth[k+1]

    return {"times": times, "truth": truth, "est": est,
            "controls": controls, "monitor": monitor}
