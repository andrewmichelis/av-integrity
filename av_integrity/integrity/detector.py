# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""Integrity / fault-detection interface (the open/closed boundary).

M0 ships the interface + a no-op reference monitor. The actual fault detection
and isolation is M1+ and, in its tuned form, is the private core that plugs in
behind this interface (shipped as a binary/API); the public repo carries only a
reference implementation.
"""
from dataclasses import dataclass, field


@dataclass
class IntegrityReport:
    healthy: bool = True
    flagged: list = field(default_factory=list)   # sensor names currently distrusted
    notes: str = ""


class IntegrityMonitor:
    """Interface: consumes the EKF's innovations after each cycle -> a report."""
    def update(self, ekf, t) -> IntegrityReport:
        raise NotImplementedError


class ReferenceMonitor(IntegrityMonitor):
    """M0 placeholder: records innovations, flags nothing. M1 adds innovation FDI."""
    def __init__(self):
        self.history = []
    def update(self, ekf, t):
        self.history.append((t, {k: v.copy() for k, v in ekf.last_innovation.items()}))
        return IntegrityReport(healthy=True, notes="reference monitor (M0): no detection yet")
