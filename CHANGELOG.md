# Changelog

All notable changes to **av-integrity**. Format: [Keep a Changelog](https://keepachangelog.com/).
This project ships by milestone — M0 = `0.1.0`, M1 = `0.2.0`, and so on.

## [0.6.0] — 2026-09-15 · M2–M5 · isolation, safe-state, drift, robustness, and a reproducible open/closed harness

> This cut brings milestones **M2–M5** public together (0.3.0–0.5.0 were internal milestone increments). It
> completes the five-step arc: from a single integrity check (M1) to isolation, safe-state, a drift twin,
> measured detection rates, and a reproducible harness with a clean private-core seam.

### Added
- **M2 — fault taxonomy + safe-state** (`SafetyMonitor`): fault detection & isolation plus a safe-state machine
  (DEGRADED when one correcting sensor is gated; SAFE_STOP when no trustworthy correction remains). New
  `docs/REFERENCE_fault-taxonomy.md`. Honest finding: the fusion absorbs a modest biased IMU while measurements stay good.
- **M3 — the dynamics twin** (`DriftMonitor`): a windowed innovation-mean consistency test (CUSUM-spirit
  change-detection) that watches the accumulated gap; catches the slow absorbed IMU bias within seconds, where the
  instantaneous check never trips.
- **M4 — robustness**: a Monte-Carlo evaluation harness reporting detection rate, false-alarm rate, and
  time-to-detect. GPS-jump detection climbs to 1.0 above a few metres, time-to-detect ≈1 sample; absorbed-bias
  detection floors near 1 m/s² (small biases correctly not flagged).
- **M5 — reproducible harness + open/closed seam**: `python -m av_integrity report` recomputes every quoted number
  and `figures` rebuilds every PNG from a clean checkout; `integrity/core.py` `load_monitor()` resolves the active
  monitor so a tuned private core plugs in behind the `IntegrityMonitor` interface (via `AV_INTEGRITY_CORE`) without
  entering this repo.

### Result
- The five-step arc (M0–M5) is complete and self-verifying; the private-core boundary is one testable line of code.

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
- Nominal accuracy versus ground truth: position ≈0.3 m, heading ≈0.03 rad, speed ≈0.09 m/s.
