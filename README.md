# AV Sensor-Integrity Monitor (simulation)

An open, **simulation-only** study of a hard problem in autonomy: **how a system knows when it can't trust its own sensors, and fails safe instead of failing.**

An automated vehicle fuses several noisy sensors into one estimate of its own state and then acts on that estimate. When a sensor degrades or lies (a GPS fix that jumps, an IMU that drifts, a wheel that slips), two questions decide whether the system is safe: does it notice, and does it degrade safely? This project builds an answer, one honest increment at a time, and puts the reasoning in the open.

It is built and narrated in public at **[knackmentor.com](https://knackmentor.com)** by Andrew Michelis (systems integration & technical delivery).

> **Build logs** live on the [KnackMentor blog](https://knackmentor.com/blog/) — one write-up per milestone.

## Honest boundary

This is a **simulation**. It proves the reasoning, the architecture, and the method, not real-world performance. Faults are **injected**, so ground truth is always known and evaluation is non-circular. Where the model's fidelity ends is stated, not hidden. A physical proof-of-concept is a possible later step, not a claim made here.

## What's here (M0–M1)

**M0 — the foundation:** a vehicle simulation, three sensors, and an Extended Kalman Filter that fuses them, with the estimate tracking ground truth under nominal conditions. On a clean drive the fused estimate tracks truth to within about **0.3 m** in position, **0.03 rad** in heading, and **0.09 m/s** in speed, measured against the true trajectory rather than eyeballed.

![The fused estimate (dashed) sits on top of the true trajectory and speed (solid) on a clean drive.](docs/img/m0-nominal.png)

**M1 — the first integrity check.** Each measurement is scored by how surprising it is given the uncertainty we expect (a standard consistency check, the normalized innovation squared); a reading that scores too far out is flagged and gated out of the fusion. On an injected **8 m GPS jump**, the monitor detects it at the very first bad reading with **zero false alarms** for the rest of the run, and gating holds position error at **0.42 m** where the ungated estimate follows the spoof out to **5.59 m**.

![Under a GPS jump: the gated estimate stays on truth while the ungated one follows the spoof; the GPS surprise score (NIS) spikes above threshold exactly during the fault window.](docs/img/m1-gps-jump.png)

```
src/av_integrity/
  sim/          kinematic vehicle model + ground-truth trajectory
  sensors/      GPS / IMU / wheel-speed, each with fault-injection hooks
  estimation/   the EKF (state = [x, y, heading, speed]) + state definition
  integrity/    the detection interface + the reference monitors (passthrough, innovation check)
  harness/      scenario runner + accuracy / detection metrics
  view/         matplotlib plots (estimate vs truth, the GPS-jump detection view)
tests/          pytest (M0 + M1 acceptance)
```

The interface contracts between subsystems (the seams) are specified in [`docs/REFERENCE_seams.md`](docs/REFERENCE_seams.md). The EKF is driven by the IMU (`predict`) and corrected by GPS and wheel-speed (`update`). Standard stuff: the point of this project is the **integration and the integrity layer around it**, not the filter.

## Documentation

A plain-language knowledge library lives in [`docs/`](docs/) — no control-theory or heavy-maths background needed:

- **[docs/GUIDE_concepts.md](docs/GUIDE_concepts.md)** — what this project is and what it proves, in intuition rather than equations.
- **[docs/REFERENCE_physical-mapping.md](docs/REFERENCE_physical-mapping.md)** — how every simulated piece maps to a real vehicle and real sensors.
- **[docs/TERMINOLOGY_glossary.md](docs/TERMINOLOGY_glossary.md)** — every term, in plain words, one at a time (incl. innovation, NIS).
- **[docs/development/CONTRACT_m0.md](docs/development/CONTRACT_m0.md)** · **[CONTRACT_m1.md](docs/development/CONTRACT_m1.md)** — each milestone's scope + acceptance, told as a short story.
- **[docs/REFERENCE_references.md](docs/REFERENCE_references.md)** — the sources the methods are drawn from.

The code is written to be read the same way: open any file and the comments explain *why*, not just *what*. Start with [`src/av_integrity/estimation/ekf.py`](src/av_integrity/estimation/ekf.py), the fusion filter, documented for a first-time reader.

## Run it

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e .                     # deps come from pyproject.toml

python scripts/run_demo.py           # M0: prints fusion accuracy, writes .sandbox/nominal.png
python scripts/run_m1.py             # M1: GPS-jump detection, writes .sandbox/m1_gps_jump.png
pytest -q                            # M0 + M1 acceptance
```

## Open / closed

This public repo carries the simulation, the scenarios, the validation harness, and a **reference (non-tuned) integrity monitor**. A refined detection/integrity core is developed separately and is intended to plug in behind the `integrity.IntegrityMonitor` interface (as a binary or a hosted, testable API), so a private variant can be graded by the same scenarios without entering this repo. The boundary is deliberate.

## Roadmap

- **M0** — vehicle sim + sensors + EKF fusion + live view *(done)*
- **M1** — first integrity check: innovation monitoring; inject a GPS jump, detect and gate it *(this release)*
- **M2** — fault taxonomy + fault detection & isolation across sensors + safe-state
- **M3** — the dynamics twin: model-based prediction + drift detection
- **M4** — robustness evaluation: detection rate, false-alarm rate, time-to-detect
- **M5** — public harness + the gated integrity core

Each milestone ships with a build log on the [KnackMentor blog](https://knackmentor.com/blog/).

## References and citation

The methods used here (Kalman / Extended Kalman filtering for the fusion, the innovation / NIS consistency test for the integrity check) are standard, and are cited to their sources in [`docs/REFERENCE_references.md`](docs/REFERENCE_references.md). The contribution of this project is the integration and the honest evaluation, not the algorithms. To cite the project itself, see [`CITATION.cff`](CITATION.cff) (GitHub renders a "Cite this repository" button from it).

## License

[Apache-2.0](LICENSE). Copyright 2026 Andrew Michelis. See also [NOTICE](NOTICE).
