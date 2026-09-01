# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""A scenario: one self-contained test run (the drive + which faults to inject).

`nominal` is a clean drive with all sensors healthy; `gps_jump` injects a
sustained GPS position offset (a spoof) for the integrity monitor to catch.
"""
from dataclasses import dataclass, field

from av_integrity.sensors.base import Fault


@dataclass
class Scenario:
    name: str
    duration: float = 30.0
    dt: float = 0.02
    seed: int = 0
    gps_rate: float = 5.0
    imu_rate: float = 50.0
    wheel_rate: float = 25.0
    gps_faults: list = field(default_factory=list)
    imu_faults: list = field(default_factory=list)
    wheel_faults: list = field(default_factory=list)


def nominal(seed=0):
    """A clean run: all sensors healthy."""
    return Scenario(name="nominal", seed=seed)


def gps_jump(seed=0, start=12.0, end=20.0, offset=8.0):
    """A single lying sensor: a sustained GPS position offset (spoof)."""
    return Scenario(name="gps_jump", seed=seed,
                    gps_faults=[Fault("jump", start, end, offset)])
