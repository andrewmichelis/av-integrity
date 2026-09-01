# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""
The sensor-fusion filter: turning noisy, partial sensor readings into one best
guess of where the vehicle is, and how sure we are of that guess.

WHAT THIS IS, IN PLAIN WORDS
----------------------------
The vehicle never directly knows its own position, heading, or speed. It only
has sensors, and each one is noisy and sees just part of the picture: GPS gives a
jittery position, the IMU gives how fast we are turning and accelerating, the
wheels give speed. This class fuses them into a single running estimate of the
state, and, just as importantly, tracks *how uncertain* that estimate is.

It is an Extended Kalman Filter (EKF). "Kalman filter" is the standard recipe for
this fuse-and-track-uncertainty job; "extended" just means it copes with the fact
that our motion is not a straight line (the vehicle turns).

THE LOOP: PREDICT, THEN CORRECT
-------------------------------
Every cycle does two things:
  1. predict():   guess where we will be a moment later, using the IMU (how we
                  are accelerating and turning). On its own this drifts, like
                  navigating with your eyes closed.
  2. update_*():  when a GPS or wheel-speed reading arrives, nudge the guess
                  toward it, by an amount that depends on how much we trust the
                  guess versus the reading. A confident guess barely moves; an
                  uncertain one moves a lot.

THE SYMBOLS (standard Kalman notation, spelled out once here)
-------------------------------------------------------------
  x   the state estimate: [px, py, heading, speed]
  P   how uncertain we are about x (a covariance: how wrong x might be, and how
      its errors are correlated across position/heading/speed)
  Q   process noise: fresh uncertainty each predict step adds, for the parts of
      reality the motion model does not capture
  R   measurement noise: how jittery a given sensor is
  F   how an error in the old state becomes an error in the new state through one
      predict step (the Jacobian, i.e. the slope, of the motion model)
  H   which parts of the state a sensor actually sees (GPS sees position; the
      wheels see speed)
  y   the "innovation": the reading minus what we expected to read. Small means
      the reading agrees with us; large means a surprise.
  S   how big an innovation we should expect just by chance (its covariance)
  K   the Kalman gain: how far to move x toward a reading, from 0 (ignore it) to
      1 (trust it completely)

The innovation y and its expected size S are also handed to the integrity layer.
A reading far more surprising than S says it should be is probably a sensor
lying; see av_integrity/integrity/detector.py.

Reference: the Kalman filter (Kalman 1960) and its extended form for nonlinear
motion (Thrun, Burgard & Fox 2005, Ch. 3; Simon 2006). Full citations in
docs/REFERENCE_references.md. This is a standard, textbook filter; the project's
contribution is the integration and the integrity layer around it, not the EKF.
"""
import numpy as np

from av_integrity.estimation.state import PX, PY, THETA, V, STATE_DIM


class VehicleEKF:
    def __init__(self, initial_state, initial_uncertainty,
                 process_noise, gps_noise, wheel_speed_noise):
        # Our current best guess of [px, py, heading, speed], and how unsure we
        # are about it (P).
        self.x = np.asarray(initial_state, float).copy()
        self.P = np.asarray(initial_uncertainty, float).copy()

        # Fixed noise models. Q is added every predict step; R is each sensor's
        # own jitter, used when we fold that sensor's reading in.
        self.Q = np.asarray(process_noise, float)
        self.R_gps = np.asarray(gps_noise, float)
        self.R_wheel_speed = np.asarray(wheel_speed_noise, float)

        # The most recent innovation and its covariance, kept per sensor. The
        # integrity monitor reads these to judge whether a sensor is trustworthy.
        self.last_innovation = {}
        self.last_innovation_cov = {}

    def predict(self, imu_reading, dt):
        """Dead-reckon one step forward using the IMU.

        imu_reading is [acceleration, yaw_rate]. We move the estimate along the
        motion model and then grow its uncertainty, because a prediction is never
        exact.
        """
        acceleration, yaw_rate = imu_reading
        px, py, heading, speed = self.x

        # Where the motion model says we go next: a vehicle driving forward at
        # `speed` in the direction `heading`, while turning and accelerating.
        self.x = np.array([
            px + speed * np.cos(heading) * dt,   # east position
            py + speed * np.sin(heading) * dt,   # north position
            heading + yaw_rate * dt,             # heading turns at the yaw rate
            speed + acceleration * dt,            # speed changes with acceleration
        ])

        # F captures how a small error in the old state turns into an error in
        # the new one (the slope of the motion model above). Only the two
        # position rows depend on heading and speed; heading and speed carry
        # straight across, so the rest of F is the identity.
        F = np.eye(STATE_DIM)
        F[PX, THETA] = -speed * np.sin(heading) * dt
        F[PX, V]     =  np.cos(heading) * dt
        F[PY, THETA] =  speed * np.cos(heading) * dt
        F[PY, V]     =  np.sin(heading) * dt

        # Grow the uncertainty: push the old uncertainty through F, then add the
        # fresh process noise Q for what the model leaves out.
        self.P = F @ self.P @ F.T + self.Q

    def _correct(self, reading, H, R, sensor_name, gate=None):
        """Nudge the estimate toward one sensor reading (the shared update maths).

        H says which parts of the state this sensor observes; R is its noise. The
        integrity `gate`, if provided, may veto an untrustworthy reading before we
        apply it. Returns (innovation, accepted).
        """
        reading = np.atleast_1d(np.asarray(reading, float))

        # Innovation: how far the actual reading is from what we expected to see.
        expected = H @ self.x
        innovation = reading - expected

        # How large an innovation we should expect purely by chance: our own
        # uncertainty seen through the sensor, plus the sensor's own noise.
        innovation_cov = H @ self.P @ H.T + R

        # Hand both to the integrity monitor (via last_* and the gate below).
        self.last_innovation[sensor_name] = innovation
        self.last_innovation_cov[sensor_name] = innovation_cov

        # Ask the integrity layer whether to trust this reading. No gate = trust
        # every reading (the plain filter).
        accepted = True if gate is None else bool(gate(sensor_name, innovation, innovation_cov))
        if accepted:
            # Kalman gain: how far to move toward the reading. It is large when we
            # are unsure (P big) or the sensor is precise (R small), and small
            # when we already trust our own estimate.
            kalman_gain = self.P @ H.T @ np.linalg.inv(innovation_cov)
            self.x = self.x + kalman_gain @ innovation
            self.P = (np.eye(STATE_DIM) - kalman_gain @ H) @ self.P
        return innovation, accepted

    def update_gps(self, position_reading, gate=None):
        """Fold in a GPS fix. GPS observes position only (px, py)."""
        H = np.zeros((2, STATE_DIM))
        H[0, PX] = 1.0
        H[1, PY] = 1.0
        return self._correct(position_reading, H, self.R_gps, "gps", gate)

    def update_wheel_speed(self, speed_reading, gate=None):
        """Fold in a wheel-speed reading. The wheels observe speed only."""
        H = np.zeros((1, STATE_DIM))
        H[0, V] = 1.0
        return self._correct(speed_reading, H, self.R_wheel_speed, "wheel_speed", gate)
