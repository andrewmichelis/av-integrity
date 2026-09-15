# M5 — A public harness, and a clean seam for the private core

> **Established methods (selected + wired):** plugin/strategy pattern + open-closed IP-boundary design. **Reproduce:** `python -m av_integrity report`.

M5 adds no new detection idea. It does the two things that turn four increments
into something a stranger can trust and a business can build on: it makes every
result **reproducible from a clean checkout**, and it draws the **open/closed
boundary** as one real, testable line of code rather than a promise in a README.

## One command reproduces everything

The numbers in this repo are only worth as much as a reader's ability to
regenerate them. The harness is the entry point that does exactly that:

```
python -m av_integrity report      # prints the M0–M4 metrics, from real runs
python -m av_integrity figures      # regenerates every figure in docs/img
```

`report` reruns the standard scenarios and prints the fusion accuracy, the
GPS-jump detection and gating benefit, the false-alarm rate, and the detection
sweeps — the same figures quoted in the docs, computed on the spot. `figures`
rebuilds each PNG from the same runs. Nothing here is a stored result that could
drift away from the code that supposedly produced it. (`report.py` +
`__main__.py`; the per-milestone `run_m*.py` scripts remain as focused demos.)

## The open/closed boundary, made concrete

Everything public here is a *reference* implementation. The value worth keeping
private is a tuned detector or safety policy — better thresholds, a learned
residual model, a smarter isolation rule. M5 makes the place it plugs in a single
function, `integrity.core.load_monitor()`:

1. an explicit factory passed in code (used in tests), else
2. a module named by the env var `AV_INTEGRITY_CORE` that exposes `make_monitor()`
   — how a private package or compiled binary drops in, entirely out of tree, else
3. the public reference `SafetyMonitor`, which is what ships here.

The whole harness resolves its monitor through that one call and reports which
one is active (`describe()`), so a run is never ambiguous about what produced its
numbers. Two properties follow, and both matter:

- **The public repo is complete and reproducible on its own** — the reference
  monitor makes every milestone runnable and every number checkable.
- **The tuned core never has to enter this repo.** It is measured by the exact
  same scenarios and metrics as the reference, through the same interface, so an
  improvement is an honest, like-for-like comparison — not a different harness
  quietly grading its own homework.

That is the systems-integration point of the whole project in miniature: the seam
is written down, owned, and verified, so the two sides can evolve independently
without either one lying to the other.

## Honest limits

- **No tuned core is published.** By design: this repo ships the interface and the
  reference. The loader proves the seam works (a factory-injected monitor is
  exercised in the tests); it does not ship private IP.
- **`AV_INTEGRITY_CORE` imports a module by name.** That is a deliberate local
  plugin hook for the author's own out-of-tree core, not a sandbox. Point it only
  at code you trust — the same footing as any Python entry-point plugin.
- **Still simulation.** The harness reproduces the *simulation's* numbers honestly;
  it does not turn them into a claim about real hardware. That boundary is the
  same one stated in the top-level README.
