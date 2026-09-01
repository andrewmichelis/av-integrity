# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""Optional plots, saved as PNG files (no screen needed).

matplotlib is imported inside the functions, on purpose: the whole system runs
and the tests pass without it installed. Plotting is a convenience, not a
dependency of the core.
"""
import os


def plot_result(result, path=".sandbox/nominal.png"):
    """M0 picture: the estimated path and speed laid over the ground truth.

    If the estimate is doing its job, the dashed estimate line sits right on top
    of the solid truth line.
    """
    import matplotlib
    matplotlib.use("Agg")               # render to a file, not a window
    import matplotlib.pyplot as plt
    from av_integrity.estimation.state import PX, PY, V

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    truth, est, times = result["truth"], result["est"], result["times"]

    fig, (ax_path, ax_speed) = plt.subplots(1, 2, figsize=(11, 4.5))
    ax_path.plot(truth[:, PX], truth[:, PY], lw=2, label="truth")
    ax_path.plot(est[:, PX], est[:, PY], "--", label="EKF estimate")
    ax_path.set_title("Trajectory (world frame)")
    ax_path.set_xlabel("x [m]"); ax_path.set_ylabel("y [m]")
    ax_path.axis("equal"); ax_path.legend()

    ax_speed.plot(times, truth[:, V], label="truth v")
    ax_speed.plot(times, est[:, V], "--", label="EKF v")
    ax_speed.set_title("Speed")
    ax_speed.set_xlabel("t [s]"); ax_speed.set_ylabel("v [m/s]"); ax_speed.legend()

    fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)
    return path


def plot_m1(baseline, guarded, window, path=".sandbox/m1_gps_jump.png"):
    """M1 picture: what the integrity monitor buys us during a GPS jump.

    Left  the true path, the estimate WITHOUT the monitor (it follows the spoof),
          and the estimate WITH the monitor (it stays on truth).
    Right the GPS surprise score (NIS) over time: it sits low normally and spikes
          far above the threshold during the fault window (shaded).
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from av_integrity.estimation.state import PX, PY

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    truth = guarded["truth"]

    fig, (ax_path, ax_nis) = plt.subplots(1, 2, figsize=(12, 4.8))
    ax_path.plot(truth[:, PX], truth[:, PY], lw=2, label="truth")
    ax_path.plot(baseline["est"][:, PX], baseline["est"][:, PY], ":",
                 label="no monitor (follows spoof)")
    ax_path.plot(guarded["est"][:, PX], guarded["est"][:, PY], "--",
                 label="with monitor (gated)")
    ax_path.set_title("Trajectory under a GPS jump")
    ax_path.set_xlabel("x [m]"); ax_path.set_ylabel("y [m]")
    ax_path.axis("equal"); ax_path.legend()

    nis = guarded["gps_nis"]
    ax_nis.semilogy(nis[:, 0], nis[:, 1], ".-", ms=3, label="GPS NIS (surprise)")
    ax_nis.axhline(13.816, color="k", ls="--", lw=1, label="threshold")
    ax_nis.axvspan(window[0], window[1], color="orange", alpha=0.15, label="fault window")
    ax_nis.set_title("GPS innovation consistency (NIS)")
    ax_nis.set_xlabel("t [s]"); ax_nis.set_ylabel("NIS (log scale)"); ax_nis.legend()

    fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)
    return path
