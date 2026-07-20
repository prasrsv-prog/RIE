from __future__ import annotations

import ast
import inspect
from pathlib import Path

import rie.evidence_repository as package
import rie.evidence_repository.evidence_repository_canonicalization as canonicalization_module
import rie.evidence_repository.evidence_repository_contract as contract_module
import rie.evidence_repository.evidence_repository_protocol as protocol_module
import rie.evidence_repository.sqlite_evidence_collection_repository as sqlite_module
from rie.evidence_repository.evidence_repository_protocol import (
    EvidenceCollectionRepository,
)

EXPECTED_PACKAGE_FILES = {
    "__init__.py",
    "evidence_repository_contract.py",
    "evidence_repository_canonicalization.py",
    "evidence_repository_protocol.py",
    "sqlite_evidence_collection_repository.py",
}
EXPECTED_PUBLIC_API = (
    "EVIDENCE_REPOSITORY_WRITE_REQUEST_CONTRACT_VERSION",
    "EVIDENCE_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION",
    "EVIDENCE_REPOSITORY_REVISION_CONTRACT_VERSION",
    "EVIDENCE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION",
    "EVIDENCE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION",
    "EVIDENCE_REPOSITORY_HISTORY_RESULT_CONTRACT_VERSION",
    "EVIDENCE_REPOSITORY_ISSUE_CONTRACT_VERSION",
    "EVIDENCE_COLLECTION_REPOSITORY_PAYLOAD_CANONICALIZATION_VERSION",
    "EVIDENCE_REPOSITORY_REVISION_IDENTITY_CANONICALIZATION_VERSION",
    "EVIDENCE_REPOSITORY_AUDIT_IDENTITY_CANONICALIZATION_VERSION",
    "EVIDENCE_REPOSITORY_REVISION_ID_PREFIX",
    "EVIDENCE_REPOSITORY_AUDIT_ID_PREFIX",
    "SQLITE_EVIDENCE_COLLECTION_REPOSITORY_SCHEMA_ID",
    "SQLITE_EVIDENCE_COLLECTION_REPOSITORY_SCHEMA_VERSION",
    "EVIDENCE_REPOSITORY_WRITE_STATUSES",
    "EVIDENCE_REPOSITORY_LOOKUP_STATUSES",
    "EVIDENCE_REPOSITORY_ISSUE_CODES",
    "EVIDENCE_REPOSITORY_ISSUE_MESSAGES",
    "EvidenceRepositoryIssue",
    "EvidenceRepositoryWriteRequest",
    "EvidenceRepositoryRevision",
    "EvidenceRepositoryAuditRecord",
    "EvidenceRepositoryWriteResult",
    "EvidenceRepositoryLookupResult",
    "EvidenceRepositoryHistoryResult",
    "serialize_evidence_collection_repository_payload",
    "deserialize_evidence_collection_repository_payload",
    "calculate_evidence_collection_repository_payload_digest",
    "calculate_evidence_repository_revision_id",
    "calculate_evidence_repository_audit_id",
    "EvidenceCollectionRepository",
    "SqliteEvidenceCollectionRepository",
)
EXPECTED_PROTOCOL_METHODS = (
    "persist",
    "get_by_collection_id",
    "get_by_source_revision",
    "list_source_history",
    "list_source_audit",
)
FORBIDDEN_IMPORT_PREFIXES = (
    "rie.infrastructure.evidence_repository_serialization",
    "rie.infrastructure.in_memory_evidence_repository",
    "rie.infrastructure.sqlite_evidence_repository",
    "rie.interfaces.evidence_repository",
    "rie.domain.accepted_evidence",
    "rie.domain.acceptance_record",
)
PRODUCTION_MODULES = (
    contract_module,
    canonicalization_module,
    protocol_module,
    sqlite_module,
)


def _source_tree(module) -> ast.Module:
    return ast.parse(inspect.getsource(module))


def _imported_names(module) -> tuple[str, ...]:
    result = []
    for node in ast.walk(_source_tree(module)):
        if isinstance(node, ast.Import):
            result.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            prefix = node.module or ""
            result.extend(
                f"{prefix}.{alias.name}" for alias in node.names
            )
    return tuple(result)


def test_package_contains_exact_authorized_python_files():
    package_path = Path(package.__file__).parent
    actual = {
        item.name
        for item in package_path.iterdir()
        if item.is_file() and item.suffix == ".py"
    }
    assert actual == EXPECTED_PACKAGE_FILES


def test_package_public_api_is_exact_and_ordered():
    assert package.__all__ == EXPECTED_PUBLIC_API
    assert tuple(name for name in package.__all__ if hasattr(package, name)) == (
        EXPECTED_PUBLIC_API
    )


def test_module_public_api_counts_are_exact():
    assert len(contract_module.__all__) == 25
    assert len(canonicalization_module.__all__) == 5
    assert protocol_module.__all__ == ("EvidenceCollectionRepository",)
    assert sqlite_module.__all__ == ("SqliteEvidenceCollectionRepository",)


def test_protocol_has_exact_method_names():
    actual = tuple(
        name
        for name, value in EvidenceCollectionRepository.__dict__.items()
        if callable(value) and not name.startswith("_")
    )
    assert actual == EXPECTED_PROTOCOL_METHODS


def test_no_legacy_repository_imports():
    for module in PRODUCTION_MODULES:
        imports = _imported_names(module)
        for imported in imports:
            assert not imported.startswith(FORBIDDEN_IMPORT_PREFIXES)


def test_only_reviewed_gate6_imports_are_used():
    imports = set()
    for module in PRODUCTION_MODULES:
        imports.update(_imported_names(module))
    gate6_imports = {
        value
        for value in imports
        if value.startswith("rie.evidence_materialization")
    }
    assert gate6_imports
    assert all(
        "EvidenceCollection" in value
        or "evidence_materialization_canonicalization" in value
        or "evidence_materialization_contract" in value
        for value in gate6_imports
    )


def test_no_current_clock_random_uuid_or_environment_identity_calls():
    forbidden_attributes = {
        "now",
        "utcnow",
        "today",
        "uuid4",
        "token_hex",
        "getenv",
    }
    forbidden_names = {"random", "uuid", "secrets"}
    for module in PRODUCTION_MODULES:
        tree = _source_tree(module)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    assert node.func.attr not in forbidden_attributes
                elif isinstance(node.func, ast.Name):
                    assert node.func.id not in forbidden_attributes
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imported = _imported_names(module)
                assert not any(
                    value.split(".", 1)[0] in forbidden_names
                    for value in imported
                )


def test_sqlite_source_has_exact_three_create_table_statements():
    source = inspect.getsource(sqlite_module)
    assert source.count("CREATE TABLE ") == 3
    assert "CREATE TABLE evidence_collection_records" in source
    assert "CREATE TABLE evidence_revision_records" in source
    assert "CREATE TABLE evidence_audit_records" in source


def test_sqlite_source_has_no_update_delete_or_retry_statements():
    tree = _source_tree(sqlite_module)
    sql_strings = tuple(
        node.value.upper()
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    )
    assert not any("DELETE FROM" in value for value in sql_strings)
    assert not any(
        value.lstrip().startswith("UPDATE ")
        for value in sql_strings
    )
    source = inspect.getsource(sqlite_module).lower()
    assert "retry" not in source
    assert "sleep(" not in source


def test_sqlite_write_uses_begin_immediate_and_no_generic_execute_api():
    source = inspect.getsource(sqlite_module)
    assert 'connection.execute("BEGIN IMMEDIATE")' in source
    public_methods = tuple(
        name
        for name, value in (
            sqlite_module.SqliteEvidenceCollectionRepository.__dict__.items()
        )
        if callable(value) and not name.startswith("_")
    )
    assert public_methods == EXPECTED_PROTOCOL_METHODS
    assert "execute" not in public_methods


def test_no_gate8_knowledge_prompt_or_semantic_behavior():
    for module in PRODUCTION_MODULES:
        source = inspect.getsource(module).lower()
        assert "prompt_candidate" not in source
        assert "knowledge_repository" not in source
        assert "semantic_duplicate" not in source
        assert "supersed" not in source


def test_all_production_modules_resolve_inside_new_namespace():
    for module in PRODUCTION_MODULES:
        assert module.__name__.startswith("rie.evidence_repository.")
