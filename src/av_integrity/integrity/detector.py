# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""The integrity layer: deciding when a sensor reading cannot be trusted.

M1 adds the detector (below): a per-sensor consistency test that flags a reading
which is far more surprising than the model allows, using the Normalized
Innovation Squared (NIS). See docs/TERMINOLOGY_glossary.md.

THE OPEN / CLOSED BOUNDARY
--------------------------
Everything here is a *reference* implementation, kept public. A tuned detector or
safety policy can drop in behind the same interfaces (shipped as a compiled
binary or a hosted API) without touching the rest of the system.
"""
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
