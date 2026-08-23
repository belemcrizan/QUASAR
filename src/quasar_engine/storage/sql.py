"""SQL metadata extension point; no database is required by the POC."""

RUN_METADATA_SCHEMA = {
    "run_id": "text primary key",
    "started_at": "timestamp with time zone",
    "domain": "text",
    "config_sha256": "text",
    "results_uri": "text",
}

