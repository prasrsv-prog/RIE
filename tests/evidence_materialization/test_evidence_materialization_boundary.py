import ast
import inspect
from pathlib import Path

import rie.evidence_materialization as package
import rie.evidence_materialization.evidence_materialization_canonicalization as canonicalization_module
import rie.evidence_materialization.evidence_materialization_contract as contract_module
import rie.evidence_materialization.evidence_materialization_service as service_module


EXPECTED_PACKAGE_FILES = {
    "__init__.py",
    "evidence_materialization_contract.py",
    "evidence_materialization_canonicalization.py",
    "evidence_materialization_service.py",
}

EXPECTED_PUBLIC_API = (
    "EVIDENCE_MATERIALIZATION_RESULT_CONTRACT_VERSION",
    "EVIDENCE_COLLECTION_CONTRACT_VERSION",
    "TRACEABLE_EVIDENCE_CONTRACT_VERSION",
    "EVIDENCE_ELIGIBILITY_SNAPSHOT_CONTRACT_VERSION",
    "EVIDENCE_ELIGIBILITY_SNAPSHOT_CANONICALIZATION_VERSION",
    "TRACEABLE_EVIDENCE_IDENTITY_CANONICALIZATION_VERSION",
    "EVIDENCE_COLLECTION_IDENTITY_CANONICALIZATION_VERSION",
    "TRACEABLE_EVIDENCE_CONTENT_TYPE",
    "TRACEABLE_EVIDENCE_ID_PREFIX",
    "EVIDENCE_COLLECTION_ID_PREFIX",
    "EVIDENCE_ELIGIBILITY_FIELD_ORDER",
    "TRACEABLE_EVIDENCE_PROVENANCE_FIELD_ORDER",
    "TRACEABLE_EVIDENCE_FIELD_ORDER",
    "TRACEABLE_EVIDENCE_IDENTITY_FIELD_ORDER",
    "EVIDENCE_COLLECTION_FIELD_ORDER",
    "EVIDENCE_COLLECTION_IDENTITY_FIELD_ORDER",
    "EVIDENCE_MATERIALIZATION_ISSUE_FIELD_ORDER",
    "EVIDENCE_MATERIALIZATION_RESULT_FIELD_ORDER",
    "EvidenceMaterializationStatus",
    "EvidenceMaterializationIssueCode",
    "EvidenceMaterializationIssue",
    "EvidenceMaterializationContractError",
    "EvidenceEligibilitySnapshot",
    "TraceableEvidenceProvenance",
    "TraceableEvidence",
    "EvidenceCollection",
    "EvidenceMaterializationResult",
    "evidence_materialization_issue",
    "raise_evidence_materialization_error",
    "canonicalize_evidence_eligibility_snapshot",
    "derive_evidence_eligibility_snapshot_digest",
    "canonicalize_traceable_evidence_identity",
    "derive_traceable_evidence_id",
    "canonicalize_evidence_collection_identity",
    "derive_evidence_collection_id",
    "materialize_evidence_collection",
)

FORBIDDEN_IMPORT_PREFIXES = (
    "rie.application.evidence_candidate",
    "rie.application.evidence_candidate_snapshot",
    "rie.application.evidence_materializer",
    "rie.domain.accepted_evidence",
    "rie.domain.evidence_identity",
    "official_source",
    "rie.infrastructure",
    "sqlite3",
    "requests",
    "urllib",
    "socket",
    "subprocess",
    "pathlib",
    "random",
    "uuid",
    "datetime",
)

ALLOWED_SERVICE_GATE5_IMPORTS = {
    "EXTRACTION_ARTIFACT_CONTRACT_VERSION",
    "ExtractionArtifact",
}


def _source_tree(module) -> ast.Module:
    return ast.parse(inspect.getsource(module))


def _imported_names(module) -> tuple[str, ...]:
    names: list[str] = []
    for node in ast.walk(_source_tree(module)):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module is not None:
                names.append(node.module)
    return tuple(names)


def test_package_contains_exact_reviewed_python_files() -> None:
    package_dir = Path(package.__file__).parent
    observed = {
        path.name
        for path in package_dir.iterdir()
        if path.is_file() and path.suffix == ".py"
    }
    assert observed == EXPECTED_PACKAGE_FILES


def test_package_public_api_is_exact_and_ordered() -> None:
    assert package.__all__ == EXPECTED_PUBLIC_API
    assert len(package.__all__) == 36
    assert len(set(package.__all__)) == 36
    assert all(hasattr(package, name) for name in package.__all__)


def test_contract_module_public_api_has_exact_count() -> None:
    assert len(contract_module.__all__) == 29
    assert len(set(contract_module.__all__)) == 29


def test_canonicalization_module_public_api_has_exact_count() -> None:
    assert len(canonicalization_module.__all__) == 6
    assert len(set(canonicalization_module.__all__)) == 6


def test_service_module_public_api_is_exact() -> None:
    assert service_module.__all__ == ("materialize_evidence_collection",)
    signature = inspect.signature(
        service_module.materialize_evidence_collection
    )
    assert tuple(signature.parameters) == (
        "artifact",
        "eligibility_snapshot",
    )


def test_no_forbidden_runtime_imports() -> None:
    modules = (
        contract_module,
        canonicalization_module,
        service_module,
    )
    for module in modules:
        for imported in _imported_names(module):
            assert not imported.startswith(FORBIDDEN_IMPORT_PREFIXES)


def test_service_gate5_import_is_exactly_reviewed_boundary() -> None:
    tree = _source_tree(service_module)
    observed: set[str] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ImportFrom)
            and node.module
            == "rie.extraction.extraction_artifact_contract"
        ):
            observed.update(alias.name for alias in node.names)
    assert observed == ALLOWED_SERVICE_GATE5_IMPORTS


def test_no_file_network_process_clock_or_random_calls() -> None:
    prohibited_call_names = {
        "open",
        "Path",
        "connect",
        "urlopen",
        "request",
        "run",
        "Popen",
        "system",
        "time",
        "now",
        "utcnow",
        "uuid4",
        "randint",
        "random",
    }
    for module in (
        contract_module,
        canonicalization_module,
        service_module,
    ):
        for node in ast.walk(_source_tree(module)):
            if isinstance(node, ast.Call):
                function = node.func
                if isinstance(function, ast.Name):
                    assert function.id not in prohibited_call_names
                elif isinstance(function, ast.Attribute):
                    assert function.attr not in prohibited_call_names


def test_no_repository_persistence_or_gate7_symbols() -> None:
    forbidden_tokens = (
        "repository",
        "sqlite",
        "persist",
        "save(",
        "load(",
        "audit_store",
        "idempotency_record",
        "revision_history",
        "gate7",
        "gate_7",
    )
    combined = "\n".join(
        inspect.getsource(module).lower()
        for module in (
            contract_module,
            canonicalization_module,
            service_module,
        )
    )
    for token in forbidden_tokens:
        assert token not in combined


def test_no_legacy_evidence_symbols_are_reexported() -> None:
    forbidden = {
        "EvidenceCandidate",
        "AcceptedEvidence",
        "EvidenceIdentityResult",
        "EvidenceMaterializationRequest",
        "materialize_accepted_evidence",
    }
    assert not forbidden.intersection(package.__all__)


def test_all_production_modules_resolve_inside_new_namespace() -> None:
    for module in (
        package,
        contract_module,
        canonicalization_module,
        service_module,
    ):
        assert module.__name__.startswith(
            "rie.evidence_materialization"
        )
