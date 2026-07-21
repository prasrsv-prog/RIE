from __future__ import annotations

from typing import Protocol, runtime_checkable

from .knowledge_repository_contract import (
    KnowledgeRepositoryHistoryResult,
    KnowledgeRepositoryInitialWriteRequest,
    KnowledgeRepositoryLifecycleTransitionRequest,
    KnowledgeRepositoryLookupResult,
    KnowledgeRepositoryWriteResult,
)


@runtime_checkable
class GovernedKnowledgeRepository(Protocol):
    def persist_initial(
        self,
        request: KnowledgeRepositoryInitialWriteRequest,
    ) -> KnowledgeRepositoryWriteResult:
        ...

    def append_lifecycle_transition(
        self,
        request: KnowledgeRepositoryLifecycleTransitionRequest,
    ) -> KnowledgeRepositoryWriteResult:
        ...

    def get_by_revision_id(
        self,
        revision_id: str,
    ) -> KnowledgeRepositoryLookupResult:
        ...

    def get_by_governed_knowledge_revision(
        self,
        governed_knowledge_id: str,
        revision_number: int,
    ) -> KnowledgeRepositoryLookupResult:
        ...

    def list_governed_knowledge_history(
        self,
        governed_knowledge_id: str,
    ) -> KnowledgeRepositoryHistoryResult:
        ...
