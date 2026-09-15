# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""A scenario: one self-contained test run (the drive + which faults to inject).

The scenarios below exercise the three outcomes the safety layer distinguishes:
a single lying sensor (isolate -> DEGRADED), a biased IMU that fusion absorbs
(-> HEALTHY), and two correctors lost at once (-> SAFE_STOP).
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


def wheel_slip(seed=0, start=8.0, end=14.0, value=1.5):
    """A single lying sensor: the wheels under-report speed (slip)."""
    return Scenario(name="wheel_slip", seed=seed,
                    wheel_faults=[Fault("slip", start, end, value)])


def imu_bias(seed=0, start=8.0, end=14.0, value=3.0):
    """A prediction fault: a constant bias on the IMU acceleration. A moderate
    bias like this is absorbed by the healthy GPS and wheel corrections; it is
    here to show that fusion is robust to it, not to trip the safety layer."""
    return Scenario(name="imu_bias", seed=seed,
                    imu_faults=[Fault("bias", start, end, value)])


def dual_fault(seed=0, start=8.0, end=14.0, gps_offset=8.0, wheel_slip_value=2.0):
    """Both correcting sensors compromised at once: GPS jumps AND the wheels slip.
    With no trustworthy correction left, the honest response is SAFE_STOP."""
    return Scenario(name="dual_fault", seed=seed,
                    gps_faults=[Fault("jump", start, end, gps_offset)],
                    wheel_faults=[Fault("slip", start, end, wheel_slip_value)])


def fault_sequence(seed=0):
    """One escalating drive for the M2 figure: a single GPS jump (isolated ->
    DEGRADED), then GPS and wheels compromised together (-> SAFE_STOP)."""
    return Scenario(name="fault_sequence", seed=seed,
                    gps_faults=[Fault("jump", 8.0, 12.0, 8.0),
                                Fault("jump", 18.0, 23.0, 8.0)],
                    wheel_faults=[Fault("slip", 18.0, 23.0, 2.0)])


def gps_drift(seed=0, start=10.0, end=30.0, rate=0.10):
    """A slow, sustained GPS position drift: a bias that grows at `rate` m/s.
    Each step it is barely surprising, so the instantaneous NIS check misses it;
    the accumulated drift is what the M3 drift monitor catches."""
    return Scenario(name="gps_drift", seed=seed,
                    gps_faults=[Fault("drift", start, end, rate)])
