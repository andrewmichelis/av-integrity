# The idea, in plain words

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

This project builds, in the open, a small system that does two jobs. **Milestone
M0 (this release) delivers the first; the second is what the milestones after it
add.**

**1. Fuse the sensors into one honest estimate.** *(M0, done here.)*
Combine the noisy, partial sensors into a single running guess of the vehicle's
state, and, crucially, keep track of *how sure* it is. The tool for this is a
**Kalman filter** (see the glossary). Think of it as a loop:
- *predict*: using the motion sensor, guess where we will be a moment from now.
  On its own this slowly drifts.
- *correct*: when GPS or wheel-speed arrives, nudge the guess toward it — a lot
  if we were unsure, barely at all if we were already confident.

**2. Notice when a sensor is lying, and stop trusting it.** *(the next milestones.)*
Every time a reading arrives, the filter already has an expectation of what it
*should* say. If the reading is wildly different from that expectation, given how
uncertain we are, it is suspicious. Measuring that "surprise" and acting on it is
the point of the project — and it is exactly what M1 onward build. M0 deliberately
stops at the honest foundation, because **you cannot prove you caught a lying
sensor until the estimate is trustworthy when nothing is wrong.**

## What M0 proves (and what it does not)

M0 proves an engineering thing, not a maths thing: that you can take several
imperfect sensors and an estimator, wire them together cleanly across their
boundaries, and end up with one estimate that tracks the truth, measured against a
known ground truth rather than asserted. Proving that the system *knows when it
can't trust its own inputs* is the job of the milestones that follow; the
interface those milestones plug into already exists here.

It is a **simulation**. It proves the reasoning and the method, not real-world
performance. Because the faults are injected on purpose (from M1), we always know
the true answer, so detection can be measured honestly. Where the simulation stops
being realistic is stated openly; it is not hidden.

## Why it matters

Every autonomous system — a car, a drone, a robot — faces exactly this problem.
The hard part is rarely one clever algorithm. It is making all the pieces work
together and making the system honest about its own confidence. That is systems
integration, and that is what this repository is a worked example of.
