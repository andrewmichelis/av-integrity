# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

import os

from av_integrity.integrity.core import load_monitor, describe, CORE_ENV
from av_integrity.integrity.detector import SafetyMonitor
from av_integrity.harness.report import text_report, regenerate_figures


def test_load_monitor_defaults_to_reference():
    # With no private core installed, the harness runs the public reference.
    os.environ.pop(CORE_ENV, None)
    mon = load_monitor()
    assert isinstance(mon, SafetyMonitor)
    assert hasattr(mon, "check") and hasattr(mon, "assess")   # satisfies the interface
    assert "reference" in describe(mon)


def test_load_monitor_uses_injected_factory():
    # A tuned core drops in behind the same interface via a factory (the seam).
    class TunedCore(SafetyMonitor):
        pass
    mon = load_monitor(factory=lambda **k: TunedCore())
    assert isinstance(mon, TunedCore)
    assert "tuned core" in describe(mon)


def test_text_report_covers_the_milestones():
    report = text_report(seeds=4)
    for marker in ("integrity core:", "M0", "M1", "M4", "false-alarm rate"):
        assert marker in report


def test_regenerate_figures_reproduces_all(tmp_path):
    paths = regenerate_figures(out_dir=str(tmp_path), seeds=4)
    assert len(paths) == 5
    for p in paths:
        assert os.path.exists(p)
