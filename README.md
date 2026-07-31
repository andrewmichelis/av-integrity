# AV Sensor-Integrity Monitor (simulation)

An open, **simulation-only** study of a hard problem in autonomy: **how a system knows when it can't trust its own sensors, and fails safe instead of failing.**

An automated vehicle fuses several noisy sensors into one estimate of its own state and then acts on that estimate. When a sensor degrades or lies (a GPS fix that jumps, an IMU that drifts, a wheel that slips), two questions decide whether the system is safe: does it notice, and does it degrade safely? This project builds an answer, one honest increment at a time, and puts the reasoning in the open.

It is built and narrated in public at **[knackmentor.com](https://knackmentor.com)** by Andrew Michelis (systems integration & technical delivery).

> **Build log for this milestone (M0):** [Building a Sensor-Fusion Testbed You Can Trust](https://knackmentor.com/blog/building-a-sensor-fusion-testbed.html) — the write-up on the KnackMentor blog.

## Honest boundary

This is a **simulation**. It proves the reasoning, the architecture, and the method, not real-world performance. Faults are **injected**, so ground truth is always known and evaluation is non-circular. Where the model's fidelity ends is stated, not hidden. A physical proof-of-concept is a possible later step, not a claim made here.

## What's here (M0)

The foundation: a vehicle simulation, three sensors, and an Extended Kalman Filter that fuses them, with the estimate tracking ground truth under nominal conditions. The fault-injection hooks and the integrity *interface* exist; the detection logic itself arrives in M1.

```
av_integrity/
  sim/          kinematic vehicle model + ground-truth trajectory
  sensors/      GPS / IMU / wheel-speed, each with fault-injection hooks
  estimation/   the EKF (state = [x, y, heading, speed]) + state definition
  integrity/    the fault-detection interface (+ an M0 no-op reference monitor)
  harness/      scenario runner + accuracy metrics
  view/         matplotlib plot of estimate vs truth
interfaces/     the interface contracts between subsystems (the seams)
docs/           plain-language knowledge library (concepts, mapping, glossary, references)
tests/          pytest
```

The EKF is driven by the IMU (`predict`) and corrected by GPS and wheel-speed (`update`). Standard stuff: the point of this project is the **integration and the integrity layer around it**, not the filter.

On a clean drive, the fused estimate tracks ground truth to within about **0.3 m** in position, **0.03 rad** in heading, and **0.09 m/s** in speed, measured against the true trajectory rather than eyeballed.

![The fused estimate (dashed) sits on top of the true trajectory and speed (solid) on a clean drive.](docs/img/m0-nominal.png)

## Documentation

A plain-language knowledge library lives in [`docs/`](docs/) — no control-theory or heavy-maths background needed:

- **[docs/concepts.md](docs/concepts.md)** — what this project is and what it proves, in intuition rather than equations.
- **[docs/physical-mapping.md](docs/physical-mapping.md)** — how every simulated piece maps to a real vehicle and real sensors.
- **[docs/glossary.md](docs/glossary.md)** — every term, in plain words, one at a time.
- **[docs/milestones/m0.md](docs/milestones/m0.md)** — this milestone told as a short story.
- **[docs/references.md](docs/references.md)** — the sources the methods are drawn from.

The code is written to be read the same way: open any file and the comments explain *why*, not just *what*. Start with [`av_integrity/estimation/ekf.py`](av_integrity/estimation/ekf.py), the fusion filter, documented for a first-time reader.

## Run it

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python run_demo.py          # prints fusion accuracy, writes out/nominal.png
pytest -q                   # M0 acceptance: estimate tracks truth
```

## Open / closed

This public repo carries the simulation, the scenarios, the validation harness, and a **reference (non-tuned) integrity monitor**. The refined detection/integrity core is developed separately and is intended to plug in behind the `integrity.IntegrityMonitor` interface (as a binary or a hosted, testable API). The boundary is deliberate.

## Roadmap

- **M0** — vehicle sim + sensors + EKF fusion + live view *(this release)*
- **M1** — first integrity check: innovation monitoring; inject a GPS jump; detect it
- **M2** — fault taxonomy + fault detection & isolation across sensors + safe-state
- **M3** — the dynamics twin: model-based prediction + drift detection
- **M4** — robustness evaluation: detection rate, false-alarm rate, time-to-detect
- **M5** — public harness + the gated integrity core

Each milestone ships with a build log on the [KnackMentor blog](https://knackmentor.com/blog/).

## References and citation

The methods used here (Kalman / Extended Kalman filtering for the fusion) are standard, and are cited to their sources in [`docs/references.md`](docs/references.md). The contribution of this project is the integration and the honest evaluation, not the algorithms. To cite the project itself, see [`CITATION.cff`](CITATION.cff) (GitHub renders a "Cite this repository" button from it).

## License

[Apache-2.0](LICENSE). Copyright 2026 Andrew Michelis. See also [NOTICE](NOTICE).
