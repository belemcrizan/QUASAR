# Local data directory

Third-party datasets are not bundled with QUASAR.

Suggested local layout:

~~~text
data/
├── ieee-cis/       # Kaggle files; ignored by Git
├── nasa/           # Local NASA/MAST exports; ignored by Git
└── processed/      # Generated JSONL/CSV; ignored by Git
~~~

Keep dataset licenses, versions, source URLs, access dates, and SHA-256 checksums in the corresponding experiment record. Do not commit restricted or large raw files.

