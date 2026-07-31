# Knowledge library

Plain-language docs for this project. No control-theory or heavy-maths background
needed. If you are new here, read them in this order:

1. **[concepts.md](concepts.md)** — what this project is and what it is trying to
   prove, in intuition rather than equations.
2. **[physical-mapping.md](physical-mapping.md)** — how every simulated piece
   maps to a real vehicle and real sensors, so the simulation is not abstract.
3. **[glossary.md](glossary.md)** — every term, in plain words, one at a time.
4. **[milestones/](milestones/)** — each build step told as a short story
   (m0 so far; one is added as each milestone ships).
5. **[references.md](references.md)** — the sources the methods are drawn from.

The code is written to be read the same way: open any file and the comments
explain *why*, not just *what*. Start with
[`av_integrity/estimation/ekf.py`](../av_integrity/estimation/ekf.py) — the
fusion filter, documented for a first-time reader.
