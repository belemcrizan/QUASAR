"""Dataset registry placeholder with an explicit no-download default.

Real dataset downloads must document license, checksum, source, and version.
This script intentionally performs no network action in POC v0.2.
"""


def main() -> None:
    print(
        "QUASAR does not download third-party datasets. Download them under their own terms, "
        "then use: quasar prepare-data --dataset ieee-cis|nasa-lightcurve ..."
    )


if __name__ == "__main__":
    main()
