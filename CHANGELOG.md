# Changelog

All notable changes to **av-integrity**. Format: [Keep a Changelog](https://keepachangelog.com/).
This project ships by milestone — M0 = `0.1.0`, M1 = `0.2.0`, and so on.

## [0.2.0] — 2026-08-31 · M1 · the first integrity check
### Added
- Innovation-based integrity monitor: each measurement is scored by its normalized innovation
  squared (NIS, a standard consistency test); a reading that is too surprising is flagged and gated
  out of the fusion.
- A `gps_jump` scenario and a before/after detection view (`docs/img/m1-gps-jump.png`).
- M1 acceptance test (`tests/test_m1_integrity.py`).
### Changed
- Repository moved to a `src/` layout (`src/av_integrity/…`); install with `pip install -e .`.
### Result
- On an injected 8 m GPS jump: detected at the first bad reading, with zero false alarms thereafter;
  gated position error **0.42 m** versus **5.59 m** ungated.

## [0.1.0] — 2026-07-15 · M0 · the sensor-fusion foundation
### Added
- Vehicle simulation; three sensors (GPS / IMU / wheel-speed) with fault-injection hooks; an Extended
  Kalman Filter fusing them; and the integrity *interface* (a no-op reference monitor at M0).
- Nominal accuracy versus ground truth: position ~0.3 m, heading ~0.03 rad, speed ~0.09 m/s.
