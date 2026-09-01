# The idea, in plain words

> **Track: Engagement (concepts)** — *Read this when you want to learn the core concepts hands-on.*

## The problem

An automated vehicle has to answer one question, continuously: *where am I, and
how fast and which way am I going?* It cannot look this up. It has to work it out
from sensors, and every sensor is imperfect. GPS jitters and occasionally jumps.
The motion sensor (IMU) slowly drifts. The wheels can slip. None of them, alone,
is good enough to drive on.

So the vehicle builds a **best guess** by combining all of them, and then it
*acts* on that guess: steering, braking, planning. Here is the danger this whole
project is about: **if one sensor quietly starts lying, the guess goes wrong, and
the vehicle acts confidently on a wrong answer.** The screen still looks fine.
That is when autonomy hurts someone.

## The two jobs

This project builds, in the open, a small system that does two jobs:

**1. Fuse the sensors into one honest estimate.**
Combine the noisy, partial sensors into a single running guess of the vehicle's
state, and, crucially, keep track of *how sure* it is. The tool for this is a
**Kalman filter** (see the glossary). Think of it as a loop:
- *predict*: using the motion sensor, guess where we will be a moment from now.
  On its own this slowly drifts.
- *correct*: when GPS or wheel-speed arrives, nudge the guess toward it — a lot
  if we were unsure, barely at all if we were already confident.

**2. Notice when a sensor is lying, and stop trusting it.**
Every time a reading arrives, the filter already has an expectation of what it
*should* say. If the reading is wildly different from that expectation, given how
uncertain we are, it is suspicious. We measure that "surprise" with a number
(see *innovation* and *NIS* in the glossary). If the surprise is too big to be
chance, we **flag** the sensor and **stop feeding its readings into the guess**
until it behaves again. This second job is the point of the project.

## What this proves (and what it does not)

It proves an engineering thing, not a maths thing: that you can take several
imperfect sensors, an estimator, and a fault check, wire them together cleanly
across their boundaries, and end up with a system that *knows when it can't trust
its own inputs* and stays safe.

It is a **simulation**. It proves the reasoning and the method, not real-world
performance. Because the faults are injected on purpose, we always know the true
answer, so we can measure honestly whether the system caught the problem. Where
the simulation stops being realistic is stated openly; it is not hidden.

## Why it matters

Every autonomous system — a car, a drone, a robot — faces exactly this problem.
The hard part is rarely one clever algorithm. It is making all the pieces work
together and making the system honest about its own confidence. That is systems
integration, and that is what this repository is a worked example of.
