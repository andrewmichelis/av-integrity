# Glossary

> **Track: Capture (glossary)** — *Read this when you want a plain-word definition of a term used elsewhere in the docs.*

Every term used in this project, in plain words. Ordered roughly from the basics
outward, not alphabetically, so it reads like an explanation.

### State
The handful of numbers that describe the vehicle right now: position east,
position north, heading (which way it faces), and speed. Everything the system
does is about estimating these four.

### State estimate
The system's *best guess* of the state. It is never exactly right, because it is
built from imperfect sensors; the whole game is keeping it close and knowing how
close.

### Ground truth
The *actual* state, which in the real world you never fully know, but in a
simulation you do (you defined it). We keep it beside the estimate to score how
well the estimate is doing.

### Sensor fusion
Combining several sensors into one estimate that is better than any single sensor
alone. GPS knows position but jitters; the wheels know speed; the IMU knows
turning. Fused, they cover for each other.

### Kalman filter
The standard recipe for sensor fusion. It keeps a running estimate *and* a
running measure of how uncertain that estimate is, and updates both every time a
sensor reports. An **Extended** Kalman filter (EKF) is the version that handles
motion that curves rather than going in a straight line.

### Predict step
Using the motion sensor (IMU), guess where the vehicle will be a moment later.
Done repeatedly on its own, prediction **drifts** — small errors accumulate.

### Update / correction step
When a GPS or wheel-speed reading arrives, pull the prediction toward it. How far
depends on trust: an uncertain estimate moves a lot toward the reading, a
confident one barely moves.

### Measurement
A single sensor reading (a GPS position, a wheel speed).

### Uncertainty / covariance
A number (really a small matrix) for *how wrong the estimate might be*, and how
its errors in position, heading, and speed relate to each other. Written `P`. It
grows during prediction and shrinks when a trusted reading corrects the estimate.

### Process noise (`Q`)
How much fresh uncertainty each predict step adds, standing in for everything the
simple motion model does not capture. Bigger `Q` = "trust the model less".

### Measurement noise (`R`)
How jittery a particular sensor is. Bigger `R` = "trust that sensor less".

### Innovation
The heart of the fault check. It is the **reading minus what we expected to
read**. A small innovation means the sensor agrees with us; a large one is a
surprise that either means our estimate was off or the sensor is wrong.

### Innovation covariance (`S`)
How big an innovation we should expect *just by chance*, given our own
uncertainty and the sensor's noise. It is the yardstick the innovation is
measured against.

### Kalman gain (`K`)
The dial the update step turns: how far to move the estimate toward a reading,
from 0 (ignore) to 1 (fully trust). It is set automatically from the
uncertainties.

### NIS (Normalized Innovation Squared)
A single "surprise score" for a reading: the innovation measured against `S`.
Under normal operation it stays small and predictable. When a sensor lies, it
spikes. Comparing it to a threshold is how the system decides a sensor is
untrustworthy.

### Chi-square threshold
The line NIS has to cross to count as "too surprising to be chance". It comes
from statistics (the chi-square distribution) and is set so that a healthy sensor
almost never trips it (here, a 99.9% line), keeping false alarms rare.

### Gating
Acting on the decision: when a reading is flagged as untrustworthy, **gate it
out** — do not fold it into the estimate. This keeps a lying sensor from
corrupting the guess.

### Fault detection and isolation (FDI)
The general name for the job of noticing that something has gone wrong (detection)
and pinning down *which* part (isolation). Here: noticing a sensor is
inconsistent, and knowing it is the GPS rather than the wheels.

### Fault injection
Deliberately making a simulated sensor misbehave (a GPS jump, an IMU drift) so we
can test whether the system catches it. Because we injected it, we know the truth
and can measure detection honestly.

### Dead reckoning
Estimating position purely by adding up motion (speed and turning) from a known
start, with no outside fix like GPS. It works briefly but drifts, which is why we
correct it with GPS and wheel-speed.

### Safe state / fail-safe
What a system does once it can no longer trust part of its input: fall back to a
known-safe behaviour rather than acting on a bad estimate. (Built out in a later
milestone.)

### IMU, GPS, wheel odometry
The three sensors. **IMU** (inertial measurement unit): a chip that senses
acceleration and turn rate. **GPS**: the satellite position receiver. **Wheel
odometry**: speed inferred from how fast the wheels turn.

### Heading and yaw rate
**Heading** is the direction the vehicle faces. **Yaw rate** is how fast that
direction is changing (how quickly it is turning). The IMU measures yaw rate; the
filter adds it up over time to track heading.
