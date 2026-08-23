"""Cloud storage extension point.

Implement ``ArtifactStore`` here for S3, GCS, or Azure Blob. It is intentionally
not active in the local POC and therefore requires no cloud credential.
"""

from quasar_engine.storage.base import ArtifactStore

__all__ = ["ArtifactStore"]

