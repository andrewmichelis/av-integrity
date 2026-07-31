# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""Optional matplotlib view (Agg backend; imported lazily so the core runs without it)."""
import os


def plot_result(result, path="out/nominal.png"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from av_integrity.estimation.state import PX, PY, V
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    truth, est, times = result["truth"], result["est"], result["times"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    ax1.plot(truth[:, PX], truth[:, PY], lw=2, label="truth")
    ax1.plot(est[:, PX], est[:, PY], "--", label="EKF estimate")
    ax1.set_title("Trajectory (world frame)"); ax1.set_xlabel("x [m]"); ax1.set_ylabel("y [m]")
    ax1.axis("equal"); ax1.legend()
    ax2.plot(times, truth[:, V], label="truth v")
    ax2.plot(times, est[:, V], "--", label="EKF v")
    ax2.set_title("Speed"); ax2.set_xlabel("t [s]"); ax2.set_ylabel("v [m/s]"); ax2.legend()
    fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)
    return path
