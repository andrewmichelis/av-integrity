# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Andrew Michelis

"""Public harness entry point (M5): reproduce every number and figure from a
clean checkout.

    python -m av_integrity report      # print the M0-M4 metrics
    python -m av_integrity figures      # regenerate all docs/img figures from real runs

Both run through `integrity.core.load_monitor`, so they measure whatever
integrity core is installed behind the interface; with none installed they use
the public reference monitor, which is what ships here.
"""
import sys

from av_integrity.harness.report import text_report, regenerate_figures


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    command = argv[0] if argv else "report"
    if command == "report":
        print(text_report())
    elif command == "figures":
        for path in regenerate_figures():
            print("wrote", path)
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
