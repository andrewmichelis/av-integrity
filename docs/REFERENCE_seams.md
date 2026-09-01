# Seams (S1–S5) — interface specs

> **Track: Capture (the spec)** — *Read this when you want the precise seam requirements.*

The **seams** between subsystems, stated explicitly. Every boundary has a payload,
units, a rate, a frame, and an error behaviour. These seams are the point:
a system fails at the seams you assumed, so the seams are written down.

Conventions: SI units. World frame is a fixed 2D ENU-style plane (x east, y
north, metres); heading `theta` is radians CCW from +x. Time is seconds. All
readings carry the sim time `t` they were sampled at.

## S1 · GPS -> estimator
- **Payload:** `[px, py]` (world position, metres).
- **Rate:** 5 Hz (nominal). **Noise:** ~0.6 m/axis, gaussian.
- **Error behaviour:** may return `None` (dropout). The estimator must skip the
  update on `None`, never block. A returned value may be biased or jumped under
  fault; M1+ integrity decides whether to trust it.

## S2 · IMU -> estimator (process input)
- **Payload:** `[a, omega]` (longitudinal acceleration m/s^2, yaw rate rad/s).
- **Rate:** 50 Hz (drives the EKF `predict` step). **Noise:** ~0.10 (a), 0.005 (omega).
- **Error behaviour:** always returns a value (no dropout modelled). Bias/drift
  corrupt the prediction; catching a slow, persistent bias like that is future work.

## S3 · wheel-speed -> estimator
- **Payload:** `[v]` (speed, m/s). **Rate:** 25 Hz. **Noise:** ~0.12 m/s.
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
- **Behaviour:** the monitor consumes each innovation and decides whether the
  reading is trustworthy (`IntegrityMonitor.check(name, y, cov) -> bool`); a
  flagged reading is gated out of the fusion. M0 ships a passthrough reference
  (trust everything); M1 adds the innovation (NIS) check. A refined monitor can
  plug in behind this same interface without changing anything upstream (an
  open/closed boundary).
