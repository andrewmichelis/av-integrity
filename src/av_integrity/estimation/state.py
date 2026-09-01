# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""The vehicle state and how it is laid out in one array.

The whole system estimates four numbers about the vehicle. We keep them together
in a single array, `x = [px, py, heading, speed]`, and use these named indices so
the code can say `x[THETA]` instead of a bare, meaningless `x[2]`.
"""
PX = 0       # position east, in metres
PY = 1       # position north, in metres
THETA = 2    # heading: the direction the vehicle faces, in radians (THETA is the
             # usual maths name; read it as "heading" everywhere)
V = 3        # speed, in metres per second

STATE_DIM = 4                                    # number of state numbers
STATE_NAMES = ("px", "py", "heading", "speed")   # human labels, same order
