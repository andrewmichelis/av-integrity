# References

This project implements standard, well-established algorithms. It does not claim
them as novel: the contribution is the *integration* of them into an honest,
testable whole, not the methods themselves. The sources below are the ones the
code draws on, cited so credit sits where it belongs. Each implementation in the
code points back here in its module docstring.

## Estimation and sensor fusion

- **Kalman, R. E. (1960).** "A New Approach to Linear Filtering and Prediction Problems." *Journal of Basic Engineering*, 82(1), 35–45. — the Kalman filter.
- **Thrun, S., Burgard, W., & Fox, D. (2005).** *Probabilistic Robotics*. MIT Press. — the Extended Kalman Filter and its use for vehicle state estimation (Ch. 3). Used in `av_integrity/estimation/ekf.py`.
- **Simon, D. (2006).** *Optimal State Estimation: Kalman, H-infinity, and Nonlinear Approaches*. Wiley. — EKF derivation and practical notes.

## Fault detection and integrity

- **Bar-Shalom, Y., Li, X.-R., & Kirubarajan, T. (2001).** *Estimation with Applications to Tracking and Navigation*. Wiley. — the innovation, the Normalized Innovation Squared (NIS), and the chi-square consistency test used to flag inconsistent measurements. Used in `av_integrity/integrity/detector.py` (`InnovationMonitor`).
- **Mehra, R. K., & Peschon, J. (1971).** "An innovations approach to fault detection and diagnosis in dynamic systems." *Automatica*, 7(5), 637–640. — innovation-based fault detection, the idea behind the integrity check here.
- **Page, E. S. (1954).** "Continuous Inspection Schemes." *Biometrika*, 41(1/2), 100–115. — CUSUM, the classic test for detecting small persistent shifts. Basis for the slow-drift detector (`DriftMonitor`, M3).
- *For context:* GNSS Receiver Autonomous Integrity Monitoring (RAIM) applies the same consistency idea to satellite navigation; the "integrity monitoring" language used here is borrowed from that tradition.

## Software

- **Harris, C. R., et al. (2020).** "Array programming with NumPy." *Nature*, 585, 357–362.
- **Hunter, J. D. (2007).** "Matplotlib: A 2D Graphics Environment." *Computing in Science & Engineering*, 9(3), 90–95.

## Citing this project

Machine-readable metadata is in [`CITATION.cff`](../CITATION.cff) at the repo
root (GitHub renders a "Cite this repository" button from it).

*Note on accuracy: these are the canonical references for the methods used;
please verify bibliographic details against the originals before formal reuse.*
