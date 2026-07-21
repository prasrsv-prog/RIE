import inspect

from rie.knowledge_repository import (
    GovernedKnowledgeRepository,
    SqliteGovernedKnowledgeRepository,
)

EXPECTED = (
    "persist_initial",
    "append_lifecycle_transition",
    "get_by_revision_id",
    "get_by_governed_knowledge_revision",
    "list_governed_knowledge_history",
)


def test_protocol_exact_methods_and_backend_conformance(
    tmp_path,
) -> None:
    methods = tuple(
        name
        for name, value in (
            GovernedKnowledgeRepository.__dict__.items()
        )
        if callable(value) and not name.startswith("_")
    )
    assert methods == EXPECTED
    repository = SqliteGovernedKnowledgeRepository(
        tmp_path / "protocol.sqlite3"
    )
    assert isinstance(
        repository,
        GovernedKnowledgeRepository,
    )
    for name in EXPECTED:
        assert inspect.signature(
            getattr(
                GovernedKnowledgeRepository,
                name,
            )
        )
