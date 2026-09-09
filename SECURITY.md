# Security Policy

`av-integrity` is a **simulation-only** research testbed. It runs local simulations and writes
figures and reports; it has no network services, no authentication, and processes no user data. The
realistic security surface is therefore small, but reports are taken seriously.

## Reporting a vulnerability

If you find a security issue (for example a dependency vulnerability, or a way the code could be made
to write outside its working directory), please report it **privately**:

- Email **andrew.michelis@knackmentor.com** with the details and, if possible, a minimal reproduction.
- Please do **not** open a public issue for a security report.

You can expect an acknowledgement within a few working days. Once a fix is available it is released
in the normal way, and the report is credited unless you prefer to stay anonymous.

## Scope

- **In scope:** the code in this repository and its declared dependencies.
- **Out of scope:** the simulation's *modelling* fidelity (documented limitations are not security
  issues), and any third-party service.

## Supported versions

Only the latest released version is supported. Please reproduce any report against the current state
of the released repository before filing.

See also "Verifying a release" in the [README](README.md) for provenance and release-authenticity.
