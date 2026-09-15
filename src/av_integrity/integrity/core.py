# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""The open/closed seam, made concrete (M5).

Everything in this public repo is a *reference* implementation. A tuned detector
or safety policy - the part worth keeping private - can drop in behind the same
`IntegrityMonitor` interface without touching the sim, the sensors, the EKF, or
the harness. This module is the single place that decides which monitor the
harness runs, so the swap is one testable boundary, not a scatter of imports.

Resolution order (first that succeeds wins):
  1. an explicit factory passed in code: `load_monitor(factory=...)`;
  2. a module named by the env var `AV_INTEGRITY_CORE`, exposing `make_monitor()`
     - this is how a private package or binary plugs in, out of tree;
  3. the public reference `SafetyMonitor` - what ships here.

The public repo never contains the tuned core; it ships the interface, the
reference, and this loader. `describe()` names which monitor is active, so a run
is never ambiguous about what produced its numbers.
"""
import importlib
import os

from av_integrity.integrity.detector import SafetyMonitor

CORE_ENV = "AV_INTEGRITY_CORE"


def load_monitor(factory=None, **kwargs):
    """Return an `IntegrityMonitor`: the tuned core if one is installed behind the
    interface, otherwise the public reference `SafetyMonitor`."""
    if factory is not None:
        return factory(**kwargs)
    module_name = os.environ.get(CORE_ENV)
    if module_name:
        module = importlib.import_module(module_name)   # private core, out of tree
        return module.make_monitor(**kwargs)
    return SafetyMonitor(**kwargs)


def describe(monitor):
    """A short label for which monitor is active, for honest run provenance."""
    qualified = f"{type(monitor).__module__}.{type(monitor).__name__}"
    if type(monitor) is SafetyMonitor:
        return f"reference SafetyMonitor ({qualified})"
    return f"tuned core ({qualified})"
