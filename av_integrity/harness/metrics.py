# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""Accuracy metrics: estimate vs ground truth."""
import numpy as np
from av_integrity.estimation.state import PX, PY, THETA, V


def rmse(result):
    truth, est = result["truth"], result["est"]
    pos = np.linalg.norm(est[:, [PX, PY]] - truth[:, [PX, PY]], axis=1)
    dth = est[:, THETA] - truth[:, THETA]
    head = np.abs(np.arctan2(np.sin(dth), np.cos(dth)))
    spd = np.abs(est[:, V] - truth[:, V])
    return {
        "position_rmse_m": float(np.sqrt(np.mean(pos ** 2))),
        "heading_rmse_rad": float(np.sqrt(np.mean(head ** 2))),
        "speed_rmse_mps": float(np.sqrt(np.mean(spd ** 2))),
    }
