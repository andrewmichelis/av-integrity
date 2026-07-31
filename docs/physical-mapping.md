# How the simulation maps to the real world

Nothing here is abstract. Every piece stands for a real thing on a real vehicle.
This page is the bridge.

## The vehicle

The simulated vehicle is a point that drives and turns on a flat plane. Its
**state** is four numbers: position east (`px`), position north (`py`), the
direction it faces (`heading`), and how fast it moves (`speed`). A real car has
far more going on, but for "where am I and where am I going" these four are the
core, and they keep the example honest and readable.

## The sensors

| In the sim | On a real vehicle | What it actually measures | How it fails, for real |
|---|---|---|---|
| **GPS** | the satellite receiver | absolute position | fixes jump near tall buildings ("multipath"), or can be spoofed; can drop out in tunnels |
| **IMU** | the inertial measurement unit (a MEMS chip) | acceleration and turn rate | slowly **drifts**: a tiny constant error that piles up over time |
| **Wheel speed** | wheel encoders / the odometry | how fast the wheels turn | over-reads on **wheel slip** (ice, gravel, spin) because the wheel turns but the car does not move as much |

The IMU is used to *predict* motion (dead-reckoning); GPS and wheel-speed are
used to *correct* the prediction. That split matches how real vehicle navigation
is built.

## The faults (from M1 onward)

The simulation carries **fault-injection hooks** for each real failure mode below.
M0 runs the **nominal** (fault-free) scenario to prove the fusion foundation;
injecting and catching these faults begins at M1. Each fault is a real failure
mode with a name engineers use:

- **GPS jump / spoof** — the position reading suddenly shifts by several metres
  and stays shifted. Real causes: reflections off buildings, or a deliberate
  spoofing signal. This is the fault milestone M1 catches.
- **IMU bias / drift** — the turn-rate or acceleration reading is off by a small
  constant (bias) or a slowly growing amount (drift). Uncaught, it bends the
  predicted path.
- **Wheel slip** — the wheel-speed reading over-states the real speed while the
  tyre is slipping.
- **Dropout** — a sensor simply stops reporting for a while.

Because these are *injected* on purpose, we always hold the true trajectory next
to the estimate, so detection can be measured exactly: whether the system noticed
and how much error it prevented. That is what makes a simulation result
trustworthy rather than a nice-looking demo.

## "Trust" and "the estimate", physically

- **The estimate** is the vehicle's own belief about its state — the number it
  would steer and brake by.
- **Trust** is not a feeling here; it is meant to be measured. The filter always
  has an *expectation* for the next reading. When a real reading disagrees with
  that expectation far more than the known noise can explain, that sensor has, in
  effect, said something that cannot be true — so a safe system stops believing
  it. Turning that judgement into a concrete, testable number is what the
  integrity layer does. M0 ships the *interface* for that layer
  (`av_integrity/integrity/detector.py`) with a no-op reference monitor; the
  detection itself begins at M1.
