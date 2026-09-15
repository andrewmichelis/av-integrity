# Seams (S1–S5) — interface specs

> **Track: Capture (the spec)** — *Read this when you want the precise seam requirements.*

The **seams** between subsystems, stated explicitly. Every boundary has a payload,
units, a rate, a frame, and an error behaviour. These seams are the point:
a system fails at the seams you assumed, so the seams are written down. (This is the
*interface* axis — the wires between the components; the machine form is
`interfaces/av-integrity.tag`. "Contract" is reserved for milestones, see `README.md`.)

Conventions: SI units. World frame is a fixed 2D ENU-style plane (x east, y
north, metres); heading `theta` is radians CCW from +x. Time is seconds. All
readings carry the sim time `t` they were sampled at.

## S1 · GPS -> estimator
- **Payload:** `[px, py]` (world position, metres).
- **Rate:** 5 Hz (nominal). **Noise:** ≈0.6 m/axis, gaussian.
- **Error behaviour:** may return `None` (dropout). The estimator must skip the
  update on `None`, never block. A returned value may be biased or jumped under
  fault; M1+ integrity decides whether to trust it.

## S2 · IMU -> estimator (process input)
- **Payload:** `[a, omega]` (longitudinal acceleration m/s^2, yaw rate rad/s).
- **Rate:** 50 Hz (drives the EKF `predict` step). **Noise:** ≈0.10 (a), 0.005 (omega).
- **Error behaviour:** always returns a value (no dropout modelled). Bias/drift
  corrupt the prediction; this is the failure the twin (M3) is meant to catch.

## S3 · wheel-speed -> estimator
- **Payload:** `[v]` (speed, m/s). **Rate:** 25 Hz. **Noise:** ≈0.12 m/s.
- **Error behaviour:** may return `None` (dropout). Slip makes it under-report;
  the value is a correction, never authoritative.

## S4 · estimator -> consumer
- **Payload:** state `x = [px, py, theta, v]` and covariance `P` (4x4).
- **Rate:** every sim step (50 Hz). **Frame:** world.
- **Error behaviour:** the estimate is always available; its *trustworthiness*
  is a separate signal owned by the integrity monitor (S5), not the estimator.

## S5 · estimator -> integrity monitor
- **Payload:** per-sensor innovations `y = z - H x` after each update
  (`ekf.last_innovation`), plus the state and covariance.
- **Behaviour (M0):** the monitor consumes these and returns an `IntegrityReport`
  (`healthy`, `flagged` sensor list, `notes`). M0 ships a no-op reference; M1
  adds innovation-based detection. The tuned core plugs in behind this same
  interface (open/closed boundary).
