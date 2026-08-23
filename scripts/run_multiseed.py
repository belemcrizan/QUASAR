"""Backward-compatible wrapper for the registered multi-seed command."""

import sys

from quasar_engine.cli.main import main


if __name__ == "__main__":
    raise SystemExit(main(["benchmark", *sys.argv[1:]]))
