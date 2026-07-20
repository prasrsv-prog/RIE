from __future__ import annotations

from typing import Protocol

from .evidence_repository_contract import (
    EvidenceRepositoryHistoryResult,
    EvidenceRepositoryLookupResult,
    EvidenceRepositoryWriteRequest,
    EvidenceRepositoryWriteResult,
)


class EvidenceCollectionRepository(Protocol):
    def persist(
        self,
        request: EvidenceRepositoryWriteRequest,
    ) -> EvidenceRepositoryWriteResult:
        ...

    def get_by_collection_id(
        self,
        collection_id: str,
    ) -> EvidenceRepositoryLookupResult:
        ...

    def get_by_source_revision(
        self,
        source_id: str,
        revision_number: int,
    ) -> EvidenceRepositoryLookupResult:
        ...

    def list_source_history(
        self,
        source_id: str,
    ) -> EvidenceRepositoryHistoryResult:
        ...

    def list_source_audit(
        self,
        source_id: str,
    ) -> EvidenceRepositoryHistoryResult:
        ...


__all__ = ("EvidenceCollectionRepository",)
