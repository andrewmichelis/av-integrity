# Contributing

Thanks for your interest in **av-integrity**. This is an open, **simulation-only** testbed, built and
narrated in public at [knackmentor.com](https://knackmentor.com). Its value is the *integration and
the honest evaluation* — a clean assembly of standard, well-sourced methods — so contributions are
welcome, within a few boundaries.

## Ground rules

- **Simulation-only, honest boundary.** Keep the honest-boundary stance (see the README): faults are
  injected, ground truth is known, and the limits of the model are stated, not hidden. Please don't
  add claims of real-world performance the simulation can't support.
- **Standard methods, cited.** The algorithms here are established techniques, cited in
  [`docs/REFERENCE_references.md`](docs/REFERENCE_references.md). New methods should be similarly
  standard and sourced — the project doesn't claim to invent algorithms.
- **The open/closed seam is fixed.** The integrity monitor is resolved behind one seam
  (`integrity.core.load_monitor()`), specified in
  [`docs/REFERENCE_seams.md`](docs/REFERENCE_seams.md). Contributions
  should keep that seam intact rather than hard-wire a specific monitor.

## How to contribute

1. Open an issue describing the change (a bug, a scenario, a doc improvement) before a large PR, so
   the approach can be agreed first.
2. Keep the tree green: `pip install -e .`, then `pytest -q` (the suite covers M0–M1). Add a test for
   any behaviour you change or fix.
3. Match the surrounding style; every file is written to be read (comments explain *why*, not just
   *what*).
4. Keep commits focused, with descriptive messages.

## Reporting bugs and asking questions

Use the issue tracker. For a suspected security issue, follow [`SECURITY.md`](SECURITY.md) instead.

By contributing, you agree that your contributions are licensed under the project's
[Apache-2.0](LICENSE) license.
