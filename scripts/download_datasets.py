"""Dataset registry placeholder with an explicit no-download default.

Real dataset downloads must document license, checksum, source, and version.
This script intentionally performs no network action in POC v0.1.
"""


def main() -> None:
    print("No external dataset is registered in POC v0.1; use the synthetic generators.")


if __name__ == "__main__":
    main()

