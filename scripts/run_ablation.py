"""Backward-compatible wrapper for the registered ablation command."""

import sys

from quasar_engine.cli.main import main


if __name__ == "__main__":
    raise SystemExit(main(["ablate", *sys.argv[1:]]))
