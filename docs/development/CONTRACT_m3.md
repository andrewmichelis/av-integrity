# M3 — A dynamics twin that catches what the instant check misses

> **Established method (selected + wired):** windowed change-detection (CUSUM-spirit). **Reproduce:** `python -m av_integrity report`.

## The blind spot in the first check

The surprise-based check (M1 and M2) is good at loud faults: a GPS jump produces a
huge, instantaneous surprise. It is deliberately blind to quiet ones. A slow bias
or drift is barely surprising from one reading to the next, so it slips under the
threshold. M2 even showed a moderate IMU bias sailing through as *healthy*: the
fusion absorbs it, the estimate stays fine, and nothing trips.

But "absorbed" is not the same as "fine". To absorb a biased prediction, the GPS
and wheel corrections have to keep pulling in the same direction, every single
step. That leaves a fingerprint: the innovations stop being random noise around
zero and pick up a persistent, one-sided bias, each one too small to notice on its
own.

## The idea: watch the accumulated gap, not each reading

The filter's prediction is, in effect, a running expectation of what each sensor
should read, a small dynamics twin. M1 compared one reading to that expectation.
M3 watches the *running average* of the gap over a window. A healthy sensor's
innovations average to zero; a persistent drift pushes the average off zero long
before any single reading looks odd. Statistically it is a windowed
innovation-mean consistency test (Bar-Shalom et al. 2001), in the spirit of CUSUM
(Page 1954); references in [../REFERENCE_references.md](../REFERENCE_references.md). See
`src/av_integrity/integrity/detector.py` (`DriftMonitor`).

## The result

I injected the exact IMU bias M2 called "healthy" (a moderate 3 m/s^2). The
instantaneous check never fires, and the estimate stays within about 0.3 m of
truth the whole time, it really is absorbed. But the drift monitor's statistic
climbs past its threshold about a second after the bias starts, reading the
persistent fingerprint on the wheel-speed innovations.

![Top: position error stays low (the bias is absorbed). Bottom: the wheel-speed drift statistic climbs past its threshold during the bias, which the instantaneous check never does.](../img/m3-drift.png)

Notice which sensor it flags: the wheel speed, not the IMU. The IMU only predicts,
so it has no innovation of its own; the bias shows up as a one-sided disagreement
on the sensor that keeps correcting for it. Isolating the true culprit from that
signature is a job for a later milestone.

## Honest limits

- **Slow to react, by design.** It trades speed for sensitivity: it needs a window
  of evidence, so it catches drifts seconds in, not instantly. That is the right
  trade for the quiet faults it targets, and the wrong tool for a sudden jump
  (which M1 already handles).
- **A slow GPS-only drift is genuinely hard.** If a GPS bias creeps and nothing
  else contradicts the position, the filter simply follows it and the innovations
  stay clean, so this method does not catch it. That is a real observability
  limit, not a bug, and worth saying plainly.
