# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""The integrity layer: deciding when a sensor reading cannot be trusted, and
what the vehicle should do about it.

M1 added the detector (below): a per-sensor consistency test that flags a reading
which is far more surprising than the model allows, using the Normalized
Innovation Squared (NIS). See docs/TERMINOLOGY_glossary.md.

M2 adds two things on top:
  - Isolation: not just "something is wrong" but *which* sensor.
  - A safe-state decision: what to do about it. If a single sensor is
    inconsistent we can gate it out and keep driving (DEGRADED). If *every*
    sensor that reported disagrees at the same time, the common cause is almost
    certainly the prediction itself (a bad IMU), which we cannot isolate away, so
    the honest move is to fail safe (SAFE_STOP).

THE OPEN / CLOSED BOUNDARY
--------------------------
Everything here is a *reference* implementation, kept public. A tuned detector or
safety policy can drop in behind the same interfaces (shipped as a compiled
binary or a hosted API) without touching the rest of the system.
"""
from collections import deque
from enum import Enum

import numpy as np


class IntegrityMonitor:
    """Interface. The estimator calls `check` once per reading, before applying
    it, and skips (gates) the reading if `check` returns False."""

    def check(self, sensor_name, innovation, innovation_cov) -> bool:
        raise NotImplementedError


class PassthroughMonitor(IntegrityMonitor):
    """Baseline: trust every reading, flag nothing. The plain filter, used to show
    what happens *without* any integrity checking."""

    def check(self, sensor_name, innovation, innovation_cov):
        return True


class InnovationMonitor(IntegrityMonitor):
    """The NIS consistency check (M1): reject readings that are too surprising.

    Reference: the innovation and the Normalized Innovation Squared / chi-square
    consistency test (Bar-Shalom, Li & Kirubarajan 2001); innovation-based fault
    detection (Mehra & Peschon 1971). See docs/REFERENCE_references.md.
    """

    # The threshold NIS must cross to count as "too surprising to be chance":
    # the chi-square 99.9% points for a 1-number reading (wheel speed) and a
    # 2-number reading (GPS). A healthy sensor trips it ~0.1% of the time.
    CHI2_999 = {1: 10.828, 2: 13.816}

    def __init__(self, thresholds=None):
        self.thresholds = dict(self.CHI2_999)
        if thresholds:
            self.thresholds.update(thresholds)
        self.flags = {}   # per sensor: was it flagged on its last check?
        self.nis = {}     # per sensor: its NIS on its last check

    def check(self, sensor_name, innovation, innovation_cov):
        innovation = np.atleast_1d(innovation)
        nis = float(innovation @ np.linalg.solve(innovation_cov, innovation))
        threshold = self.thresholds.get(len(innovation), 13.816)
        trustworthy = nis <= threshold
        self.nis[sensor_name] = nis
        self.flags[sensor_name] = not trustworthy
        return trustworthy


class SafetyState(Enum):
    HEALTHY = "healthy"       # nothing flagged; drive normally
    DEGRADED = "degraded"     # one sensor distrusted and gated; still drivable
    SAFE_STOP = "safe_stop"   # cannot isolate the fault / cannot trust the estimate


class SafetyMonitor:
    """Detection + isolation + a safe-state decision (M2).

    Wraps the per-sensor NIS detector. Its `check` is the gate the estimator
    calls; its `assess`, called each step by the runner, turns the current
    per-sensor trust picture into a `SafetyState`:

      - no correcting sensor distrusted            -> HEALTHY
      - some, but not all, correctors distrusted   -> DEGRADED (gate them, keep
        driving on the rest)
      - every correcting sensor distrusted at once -> SAFE_STOP (there is no
        trustworthy way left to correct or even check the estimate, so fail safe)

    Note what this does NOT flag: a modest IMU bias, which the healthy GPS and
    wheel corrections simply absorb. Fusion is robust to a bad prediction as long
    as the measurements are good; the dangerous case is losing the measurements.
    """

    # The measurement sensors that can correct/check the estimate (the IMU only
    # predicts, so losing trust in it is handled by the fusion, not a safe-stop).
    CORRECTORS = ("gps", "wheel_speed")

    def __init__(self, thresholds=None):
        self.detector = InnovationMonitor(thresholds)
        self.state = SafetyState.HEALTHY

    def check(self, sensor_name, innovation, innovation_cov):
        """Gate one reading (the per-sensor NIS test)."""
        return self.detector.check(sensor_name, innovation, innovation_cov)

    def assess(self):
        """Decide the safe state from the current per-sensor trust picture.

        Returns (state, frozenset_of_distrusted_correctors).
        """
        flags = self.detector.flags
        known = [s for s in self.CORRECTORS if s in flags]      # have reported
        distrusted = [s for s in known if flags[s]]             # currently flagged
        if not distrusted:
            self.state = SafetyState.HEALTHY
        elif known and len(distrusted) >= len(known):
            self.state = SafetyState.SAFE_STOP
        else:
            self.state = SafetyState.DEGRADED
        return self.state, frozenset(distrusted)

    # Expose the detector's per-sensor NIS / flags for plotting.
    @property
    def nis(self):
        return self.detector.nis

    @property
    def flags(self):
        return self.detector.flags


class DriftMonitor:
    """Catches a slow, persistent bias/drift that the instantaneous NIS check
    misses (M3), by treating the filter's prediction as a running expectation (a
    dynamics twin) and watching the *accumulated* gap rather than each single
    reading.

    A healthy sensor's innovations are zero-mean, so their running average stays
    near zero. A slow drift pushes that average off zero long before any single
    reading looks surprising on its own.

    Statistic: whiten each innovation (w = L^-1 * innovation, where S = L L^T), so
    w ~ N(0, I) under a healthy sensor. The window mean W = mean(w) then has
    covariance I/N, so window * |W|^2 is chi-square distributed with `dof` degrees
    of freedom. Flag when it exceeds the chi-square threshold. This is a windowed
    innovation-mean consistency test (Bar-Shalom et al. 2001), in the spirit of
    CUSUM (Page 1954) for detecting small persistent shifts. Like the EKF, this is a
    standard, off-the-shelf statistical test — the project's contribution is selecting,
    wiring, and honestly validating it, not deriving it. See docs/REFERENCE_references.md.
    """

    CHI2_99 = {1: 6.635, 2: 9.210}   # chi-square 99% points (dof 1 and 2)

    def __init__(self, window=120, thresholds=None):
        self.window = window
        self.thresholds = dict(self.CHI2_99)
        if thresholds:
            self.thresholds.update(thresholds)
        self.history = {}   # sensor -> deque of recent whitened innovations
        self.score = {}     # sensor -> current drift statistic
        self.flags = {}     # sensor -> drift confirmed on the last observation?

    def observe(self, sensor_name, innovation, innovation_cov):
        """Feed one innovation in. Does not gate; it raises a slower, surer flag."""
        innovation = np.atleast_1d(innovation)
        chol = np.linalg.cholesky(innovation_cov)
        whitened = np.linalg.solve(chol, innovation)      # ~ N(0, I) if healthy

        window = self.history.setdefault(sensor_name, deque(maxlen=self.window))
        window.append(whitened)
        if len(window) < self.window:
            self.score[sensor_name] = 0.0
            self.flags[sensor_name] = False
            return

        mean_whitened = np.mean(np.array(window), axis=0)
        statistic = self.window * float(mean_whitened @ mean_whitened)  # ~ chi2(dof)
        self.score[sensor_name] = statistic
        self.flags[sensor_name] = statistic > self.thresholds.get(len(innovation), 9.210)
