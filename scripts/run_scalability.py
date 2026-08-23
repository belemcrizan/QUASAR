"""Backward-compatible wrapper for the registered scalability command."""

import sys

from quasar_engine.cli.main import main


if __name__ == "__main__":
    raise SystemExit(main(["scale", *sys.argv[1:]]))
