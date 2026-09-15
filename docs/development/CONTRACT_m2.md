# M2 — A fault taxonomy, and degrading safely instead of dying

> **Established methods (selected + wired):** Fault Detection & Isolation + a safe-state machine. **Reproduce:** `python -m av_integrity report`.

## From one fault to many

M1 caught a single GPS jump. Real systems face more than one kind of fault, in
more than one sensor, sometimes at the same time. M2 adds two things: knowing
*which* sensor is at fault (isolation), and deciding *what to do* about it (a
safe-state). The full catalogue is in [REFERENCE_fault-taxonomy.md](../REFERENCE_fault-taxonomy.md).

## Detect, isolate, decide

The NIS check from M1 already runs per sensor, so it tells us which one is
inconsistent, not just that something is. On top of that, a safety layer turns
the picture into one of three decisions, moment to moment:

- one correcting sensor distrusted → gate it, **DEGRADED**, keep driving;
- every correcting sensor distrusted at once → **SAFE_STOP**, because there is no
  trustworthy way left even to check the estimate.

See `src/av_integrity/integrity/detector.py` (the `SafetyMonitor`).

## The surprising result: fusion shrugs off a biased IMU

Here is the finding I did not expect to be so clean. A moderate IMU bias, even a
few metres per second squared, never trips the check and never needs a safe-stop.
The healthy GPS and wheel corrections quietly absorb it. That is fusion doing its
job: it is robust to a bad *prediction* as long as the *measurements* are good.
The dangerous case is not a bad sensor the others can outvote; it is losing the
sensors that do the outvoting.

## What each fault does

| Scenario | Decision | Isolated | Position error |
|---|---|---|---|
| nominal | HEALTHY | – | 0.30 m |
| GPS jump | DEGRADED | GPS | 0.42 m |
| wheel slip | DEGRADED | wheel speed | 0.59 m |
| IMU bias (moderate) | HEALTHY (absorbed) | – | 0.30 m |
| GPS jump + wheel slip together | SAFE_STOP | GPS + wheel | diverges |

![Top: position error over an escalating drive. Bottom: the safety decision. A single GPS jump (8-12 s) is isolated and the system degrades but stays close; two faults at once (from 18 s) leave no trustworthy correction and it calls a safe-stop.](../img/m2-safety.png)

## Honest limits

- **No self-recovery yet.** Once the estimate has diverged far (the dual-fault
  case), even a now-healthy GPS looks wrong relative to it and keeps getting
  gated, so the system does not climb back on its own. On a real vehicle
  SAFE_STOP means stop and re-localize; automatic recovery is a later milestone.
- **Isolation lags the onset.** At the very first moment of a fault the picture
  can be ambiguous; it becomes clear as the fault develops.
