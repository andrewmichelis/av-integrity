# Fault taxonomy

Every sensor fault the system reasons about, what it looks like, how it is
detected, and what the safety layer does. This is the catalogue the integrity
layer works from (see docs/TERMINOLOGY_glossary.md for FDI, NIS, and gating).

| Sensor | Fault | What it looks like | Detected by | Response |
|---|---|---|---|---|
| GPS | jump / spoof | position shifts several metres and holds | GPS innovation (NIS) spikes | isolate + gate GPS → DEGRADED |
| GPS | dropout | no fix for a while | reading absent | skip the update; DEGRADED if prolonged |
| Wheel speed | slip | reported speed below the true speed | speed innovation (NIS) spikes | isolate + gate wheels → DEGRADED |
| Wheel speed | dropout | no reading | reading absent | skip the update |
| IMU | bias / drift | acceleration or turn-rate off by a constant or growing amount | moderate: absorbed by GPS + wheel corrections; large: several innovations disagree at once | small: none needed; large / common-mode → SAFE_STOP |
| (multiple) | correctors lost together | GPS and wheels both inconsistent at once | every correcting sensor flagged in the same picture | SAFE_STOP (no trustworthy correction remains) |

## The three outcomes

- **HEALTHY** — nothing distrusted; drive normally. A modest IMU bias lives here: fusion absorbs it.
- **DEGRADED** — one correcting sensor is distrusted and gated; the estimate is still constrained by the other, so keep driving.
- **SAFE_STOP** — no trustworthy correction remains, so the estimate can no longer be checked. Fail safe rather than act on a guess.

## The line that matters

The important boundary is not "is a sensor faulty" but "can I still check my estimate". One faulty sensor is a nuisance the fusion handles. Losing the *ability to check* the estimate is the dangerous state, and it is the one that earns a safe-stop.
