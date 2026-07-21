import ast
from pathlib import Path
from types import ModuleType

import rie.persisted_evidence_knowledge_construction as package
import rie.persisted_evidence_knowledge_construction.persisted_evidence_knowledge_construction_canonicalization as canonicalization_module
import rie.persisted_evidence_knowledge_construction.persisted_evidence_knowledge_construction_contract as contract_module
import rie.persisted_evidence_knowledge_construction.persisted_evidence_knowledge_construction_service as service_module


EXPECTED_PUBLIC_API = (
    "PersistedEvidenceKnowledgeConstructionRequest",
    "PersistedEvidenceKnowledgeCompatibilityRecord",
    "PersistedEvidenceKnowledgeConstructionResult",
    "PersistedEvidenceKnowledgeConstructionIssue",
    "canonicalize_persisted_evidence_knowledge_compatibility_identity",
    "derive_persisted_evidence_knowledge_compatibility_record_id",
    "construct_knowledge_from_persisted_evidence",
    "PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_REQUEST_CONTRACT_VERSION",
    "PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_RECORD_CONTRACT_VERSION",
    "PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_RESULT_CONTRACT_VERSION",
    "PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_ISSUE_CONTRACT_VERSION",
    "PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_IDENTITY_CANONICALIZATION_VERSION",
    "PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_RECORD_ID_PREFIX",
    "PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_ID",
    "PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_VERSION",
    "PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_DIGEST_ALGORITHM",
    "PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_STATUS_CONSTRUCTED",
    "PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_STATUS_REJECTED",
    "PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_ISSUE_CODES",
)
EXPECTED_PACKAGE_FILES = {
    "__init__.py",
    "persisted_evidence_knowledge_construction_contract.py",
    "persisted_evidence_knowledge_construction_canonicalization.py",
    "persisted_evidence_knowledge_construction_service.py",
}


def _public_names(module: object) -> set[str]:
    return {
        name
        for name in vars(module)
        if not name.startswith("_") and name != "annotations"
    }


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def test_package_contains_exact_four_python_files() -> None:
    package_path = Path(package.__file__).parent
    assert {
        path.name
        for path in package_path.iterdir()
        if path.is_file() and path.suffix == ".py"
    } == EXPECTED_PACKAGE_FILES


def test_package_public_api_is_exactly_nineteen_symbols() -> None:
    assert package.__all__ == EXPECTED_PUBLIC_API
    assert len(package.__all__) == 19
    assert {
        name
        for name in _public_names(package)
        if not isinstance(getattr(package, name), ModuleType)
    } == set(EXPECTED_PUBLIC_API)


def test_internal_module_public_surfaces_are_exact() -> None:
    assert _public_names(contract_module) == {
        name
        for name in EXPECTED_PUBLIC_API
        if name.startswith("PERSISTED_")
        or name.startswith("PersistedEvidence")
    }
    assert _public_names(canonicalization_module) == {
        "canonicalize_persisted_evidence_knowledge_compatibility_identity",
        "derive_persisted_evidence_knowledge_compatibility_record_id",
    }
    assert _public_names(service_module) == {
        "construct_knowledge_from_persisted_evidence",
    }


def test_production_import_boundary_excludes_repository_access_and_gate9() -> None:
    package_path = Path(package.__file__).parent
    forbidden_modules = {
        "rie.evidence_repository.evidence_repository_protocol",
        "rie.evidence_repository.sqlite_evidence_collection_repository",
        "sqlite3",
        "pathlib",
        "os",
        "random",
        "uuid",
        "secrets",
        "time",
        "subprocess",
        "socket",
        "requests",
        "openai",
        "rie.infrastructure",
        "rie.interfaces",
        "rie.prompt",
        "rie.knowledge",
    }
    for path in sorted(package_path.glob("*.py")):
        imported = _imported_modules(path)
        assert imported.isdisjoint(forbidden_modules)
        source = path.read_text(encoding="utf-8-sig")
        tree = ast.parse(source)
        called_names = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
        }
        called_attributes = {
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
        }
        assert called_names.isdisjoint(
            {
                "open",
                "exec",
                "eval",
                "compile",
                "__import__",
            }
        )
        assert called_attributes.isdisjoint(
            {
                "now",
                "utcnow",
                "open",
                "read_text",
                "read_bytes",
                "write_text",
                "write_bytes",
                "run",
                "Popen",
                "connect",
                "persist",
                "get_by_collection_id",
                "get_by_source_revision",
                "list_source_history",
                "list_source_audit",
            }
        )


def test_existing_source_layers_do_not_import_new_namespace() -> None:
    source_root = Path("src/rie")
    new_root = Path(package.__file__).parent.resolve()
    for path in source_root.rglob("*.py"):
        if new_root in path.resolve().parents or path.resolve() == new_root:
            continue
        assert not any(
            module == "rie.persisted_evidence_knowledge_construction"
            or module.startswith(
                "rie.persisted_evidence_knowledge_construction."
            )
            for module in _imported_modules(path)
        )
