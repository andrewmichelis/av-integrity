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


def plot_m2(result, path=".sandbox/m2_safety.png"):
    """M2 picture: position error and the safe-state over an escalating drive.

    Top: how far the estimate is from truth over time. Bottom: the safety layer's
    decision at each moment (healthy / degraded / safe-stop). A single fault is
    isolated and the system degrades but stays close; two faults at once leave no
    trustworthy correction, and it calls a safe-stop.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from av_integrity.estimation.state import PX, PY

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    times, truth, est = result["times"], result["truth"], result["est"]
    position_error = np.linalg.norm(est[:, [PX, PY]] - truth[:, [PX, PY]], axis=1)

    level = {"healthy": 0, "degraded": 1, "safe_stop": 2}
    s_t = np.array([t for (t, _, _) in result["safety"]])
    s_level = np.array([level[s] for (_, s, _) in result["safety"]])

    fig, (ax_err, ax_state) = plt.subplots(2, 1, figsize=(11, 6), sharex=True)
    ax_err.plot(times, position_error, lw=1.5)
    ax_err.set_ylabel("position error [m]")
    ax_err.set_title("Estimate error and the safety decision over an escalating drive")

    ax_state.step(s_t, s_level, where="post", lw=1.8)
    ax_state.set_yticks([0, 1, 2])
    ax_state.set_yticklabels(["healthy", "degraded", "safe-stop"])
    ax_state.set_ylim(-0.3, 2.3)
    ax_state.set_xlabel("t [s]")
    ax_state.grid(True, axis="y", alpha=0.3)

    fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)
    return path


def plot_m3(result, window, threshold=6.635, path=".sandbox/m3_drift.png"):
    """M3 picture: an absorbed IMU bias leaves the estimate looking fine but the
    drift monitor reads its fingerprint.

    Top: position error stays low (fusion absorbs the bias). Bottom: the
    wheel-speed drift statistic climbs above its threshold during the fault, which
    the instantaneous check never does.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from av_integrity.estimation.state import PX, PY

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    times, truth, est = result["times"], result["truth"], result["est"]
    position_error = np.linalg.norm(est[:, [PX, PY]] - truth[:, [PX, PY]], axis=1)
    wd = np.array([(t, sc) for (t, s, sc, _f) in result["drift"] if s == "wheel_speed"])

    fig, (ax_err, ax_drift) = plt.subplots(2, 1, figsize=(11, 6), sharex=True)
    ax_err.plot(times, position_error, lw=1.5)
    ax_err.axvspan(window[0], window[1], color="orange", alpha=0.12, label="IMU bias active")
    ax_err.set_ylabel("position error [m]")
    ax_err.set_title("An IMU bias the fusion absorbs: the estimate looks fine, but leaves a fingerprint")
    ax_err.legend(loc="upper left")

    ax_drift.plot(wd[:, 0], wd[:, 1], lw=1.5, label="wheel-speed drift statistic")
    ax_drift.axhline(threshold, color="k", ls="--", lw=1, label="threshold")
    ax_drift.axvspan(window[0], window[1], color="orange", alpha=0.12)
    ax_drift.set_xlabel("t [s]"); ax_drift.set_ylabel("drift statistic")
    ax_drift.legend(loc="upper left")

    fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)
    return path


def plot_m4_robustness(jump_points, bias_points, far, path=".sandbox/m4_robustness.png"):
    """M4 picture: detection as a curve over fault size, not a single anecdote.

    Left  loud fault (GPS jump), instantaneous NIS check: detection rate climbs to
          1.0 above a small size, and time-to-detect collapses to about one sample.
    Right quiet fault (absorbed IMU bias), drift monitor: detection needs a bigger
          push and takes longer - a higher, slower floor. The nominal false-alarm
          rate is annotated to keep the detection numbers honest.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fig, (ax_jump, ax_bias) = plt.subplots(1, 2, figsize=(12, 4.8))

    # Left: GPS jump - detection rate (left axis) and time-to-detect (right axis).
    xs = [p.magnitude for p in jump_points]
    ax_jump.plot(xs, [p.detection_rate for p in jump_points], "o-", color="C0",
                 label="detection rate")
    ax_jump.set_ylim(-0.05, 1.05)
    ax_jump.set_xlabel("GPS jump size [m]"); ax_jump.set_ylabel("detection rate")
    ax_jump.set_title("Loud fault: GPS jump (instantaneous NIS check)")
    ax_ttd = ax_jump.twinx()
    tx = [p.magnitude for p in jump_points if p.mean_time_to_detect_s is not None]
    ty = [p.mean_time_to_detect_s for p in jump_points if p.mean_time_to_detect_s is not None]
    ax_ttd.plot(tx, ty, "s--", color="C1", label="time-to-detect")
    ax_ttd.set_ylabel("time-to-detect [s]")
    lines = ax_jump.get_lines() + ax_ttd.get_lines()
    ax_jump.legend(lines, [l.get_label() for l in lines], loc="center right")
    ax_jump.text(0.03, 0.06,
                 f"false-alarm rate (nominal): {far['per_check'] * 100:.2f}% / check",
                 transform=ax_jump.transAxes, fontsize=9, color="0.35")

    # Right: IMU bias - detection rate for the drift monitor.
    ax_bias.plot([p.magnitude for p in bias_points],
                 [p.detection_rate for p in bias_points], "o-", color="C2",
                 label="detection rate")
    ax_bias.set_ylim(-0.05, 1.05)
    ax_bias.set_xlabel("IMU bias [m/s$^2$]"); ax_bias.set_ylabel("detection rate")
    ax_bias.set_title("Quiet fault: absorbed IMU bias (drift monitor)")
    ax_bias.legend(loc="lower right")

    fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)
    return path
