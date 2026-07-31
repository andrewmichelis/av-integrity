# References

This project implements standard, well-established algorithms. It does not claim
them as novel: the contribution is the *integration* of them into an honest,
testable whole, not the methods themselves. The sources below are the ones the
code draws on, cited so credit sits where it belongs. Each implementation in the
code points back here from its module docstring.

## Estimation and sensor fusion (used in M0)

- **Kalman, R. E. (1960).** "A New Approach to Linear Filtering and Prediction Problems." *Journal of Basic Engineering*, 82(1), 35–45. — the Kalman filter.
- **Thrun, S., Burgard, W., & Fox, D. (2005).** *Probabilistic Robotics*. MIT Press. — the Extended Kalman Filter and its use for vehicle state estimation (Ch. 3). Used in `av_integrity/estimation/ekf.py`.
- **Simon, D. (2006).** *Optimal State Estimation: Kalman, H-infinity, and Nonlinear Approaches*. Wiley. — EKF derivation and practical notes.

## Software

- **Harris, C. R., et al. (2020).** "Array programming with NumPy." *Nature*, 585, 357–362.
- **Hunter, J. D. (2007).** "Matplotlib: A 2D Graphics Environment." *Computing in Science & Engineering*, 9(3), 90–95.

## Coming with later milestones

As the integrity layer is built (fault detection from M1 onward), its sources will
be cited here alongside the code that uses them — the innovation / Normalized
Innovation Squared (NIS) consistency test (Bar-Shalom, Li & Kirubarajan, 2001;
Mehra & Peschon, 1971), CUSUM for slow-drift detection (Page, 1954), and the GNSS
Receiver Autonomous Integrity Monitoring (RAIM) tradition the "integrity
monitoring" language is borrowed from. They are noted now so the intellectual
debt is acknowledged from the start; the code that applies them is not in this M0
release.

## Citing this project

Machine-readable metadata is in [`CITATION.cff`](../CITATION.cff) at the repo
root (GitHub renders a "Cite this repository" button from it).

*Note on accuracy: these are the canonical references for the methods used;
please verify bibliographic details against the originals before formal reuse.*
