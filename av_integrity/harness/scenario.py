# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""Scenario definition: trajectory + sensor rates + fault schedules."""
from dataclasses import dataclass, field


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
    return Scenario(name="nominal", seed=seed)
