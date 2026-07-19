import json
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from official_source.official_source_registry_loader import (
    OfficialSourceRegistryLoader,
)
from official_source.official_source_registry_validation import (
    OFFICIAL_SOURCE_REGISTRY_VALIDATION_CONTRACT_VERSION,
)
from official_source.official_source_registry_validation import (
    OfficialSourceRegistryValidationIssue,
)
from official_source.official_source_registry_validation import (
    OfficialSourceRegistryValidationIssueCode,
)
from official_source.official_source_registry_validation import (
    OfficialSourceRegistryValidationRequest,
)
from official_source.official_source_registry_validation import (
    OfficialSourceRegistryValidationResult,
)
from official_source.official_source_registry_validation import (
    OfficialSourceRegistryValidationStatus,
)
from official_source.official_source_registry_validation import (
    render_official_source_registry_validation_report,
)
from official_source.official_source_registry_validation import (
    validate_official_source_registry,
)


def _item(**overrides):
    item = {
        "source_id": "SRC-001",
        "source_path": "docs/synthetic-registry-source.pdf",
        "source_type": "pdf",
        "document_classification": "project_rulebook",
        "authority_status": "source_of_truth_candidate",
        "lifecycle_status": "locked",
        "evidence_eligibility": "eligible_with_review",
        "version": "v1.0",
        "review_notes": "Synthetic example only.",
    }
    item.update(overrides)
    return item


def _registry(items):
    return {
        "official_sources": items,
    }


def _write_registry(path, data):
    path.write_text(
        json.dumps(data),
        encoding="utf-8",
    )


def _validate(path):
    return validate_official_source_registry(
        OfficialSourceRegistryValidationRequest(path)
    )


def test_request_issue_and_result_contracts_are_frozen(tmp_path):
    request = OfficialSourceRegistryValidationRequest(
        tmp_path / "registry.json"
    )
    issue = OfficialSourceRegistryValidationIssue(
        code=OfficialSourceRegistryValidationIssueCode.REGISTRY_MISSING,
        message="Official Source registry file does not exist.",
    )
    result = OfficialSourceRegistryValidationResult(
        contract_version=(
            OFFICIAL_SOURCE_REGISTRY_VALIDATION_CONTRACT_VERSION
        ),
        status=OfficialSourceRegistryValidationStatus.INVALID,
        sources=(),
        issues=(issue,),
    )

    with pytest.raises(FrozenInstanceError):
        request.registry_path = Path("other.json")

    with pytest.raises(FrozenInstanceError):
        issue.message = "Changed."

    with pytest.raises(FrozenInstanceError):
        result.status = OfficialSourceRegistryValidationStatus.VALID


def test_valid_result_preserves_source_order_as_tuple(tmp_path):
    registry_path = tmp_path / "registry.json"
    _write_registry(
        registry_path,
        _registry([
            _item(source_id="SRC-003"),
            _item(source_id="SRC-001"),
            _item(source_id="SRC-002"),
        ]),
    )

    result = _validate(registry_path)

    assert result.contract_version == (
        OFFICIAL_SOURCE_REGISTRY_VALIDATION_CONTRACT_VERSION
    )
    assert result.status is OfficialSourceRegistryValidationStatus.VALID
    assert isinstance(result.sources, tuple)
    assert [source.source_id for source in result.sources] == [
        "SRC-003",
        "SRC-001",
        "SRC-002",
    ]
    assert result.issues == ()


def test_invalid_result_is_fail_fast_with_one_issue(tmp_path):
    registry_path = tmp_path / "registry.json"
    _write_registry(
        registry_path,
        _registry([
            _item(source_id="SRC-001"),
            _item(source_id="SRC-001"),
            _item(source_id="SRC-002", source_type="not-valid"),
        ]),
    )

    result = _validate(registry_path)

    assert result.status is OfficialSourceRegistryValidationStatus.INVALID
    assert result.sources == ()
    assert len(result.issues) == 1
    assert result.issues[0].code is (
        OfficialSourceRegistryValidationIssueCode.DUPLICATE_SOURCE_ID
    )


def test_missing_registry_maps_to_registry_missing(tmp_path):
    result = _validate(tmp_path / "missing.json")

    assert result.issues[0].code is (
        OfficialSourceRegistryValidationIssueCode.REGISTRY_MISSING
    )
    assert result.issues[0].item_index is None
    assert result.issues[0].field_name is None


def test_unreadable_registry_maps_to_registry_unreadable(
    tmp_path,
    monkeypatch,
):
    def _raise_permission_error(path):
        raise PermissionError("synthetic")

    monkeypatch.setattr(
        OfficialSourceRegistryLoader,
        "load_from_json_file",
        staticmethod(_raise_permission_error),
    )

    result = _validate(tmp_path / "registry.json")

    assert result.issues[0].code is (
        OfficialSourceRegistryValidationIssueCode.REGISTRY_UNREADABLE
    )


def test_malformed_json_maps_to_invalid_json(tmp_path):
    registry_path = tmp_path / "registry.json"
    registry_path.write_text("{invalid-json", encoding="utf-8")

    result = _validate(registry_path)

    assert result.issues[0].code is (
        OfficialSourceRegistryValidationIssueCode.INVALID_JSON
    )


@pytest.mark.parametrize(
    "registry",
    [
        [],
        {},
        {"official_sources": {}},
        {"official_sources": [], "unexpected": True},
    ],
)
def test_invalid_root_or_top_level_maps_to_invalid_structure(
    tmp_path,
    registry,
):
    registry_path = tmp_path / "registry.json"
    _write_registry(registry_path, registry)

    result = _validate(registry_path)

    assert result.issues[0].code is (
        OfficialSourceRegistryValidationIssueCode.INVALID_REGISTRY_STRUCTURE
    )
    assert result.issues[0].item_index is None


def test_invalid_item_maps_to_entry_with_index_and_field(tmp_path):
    registry_path = tmp_path / "registry.json"
    item = _item()
    del item["authority_status"]
    _write_registry(registry_path, _registry([_item(), item]))

    result = _validate(registry_path)
    issue = result.issues[0]

    assert issue.code is (
        OfficialSourceRegistryValidationIssueCode.INVALID_REGISTRY_ENTRY
    )
    assert issue.item_index == 1
    assert issue.field_name == "authority_status"


def test_non_mapping_item_maps_to_entry_without_field(tmp_path):
    registry_path = tmp_path / "registry.json"
    _write_registry(registry_path, _registry(["invalid-item"]))

    result = _validate(registry_path)
    issue = result.issues[0]

    assert issue.code is (
        OfficialSourceRegistryValidationIssueCode.INVALID_REGISTRY_ENTRY
    )
    assert issue.item_index == 0
    assert issue.field_name is None


def test_duplicate_source_id_maps_to_stable_issue(tmp_path):
    registry_path = tmp_path / "registry.json"
    _write_registry(
        registry_path,
        _registry([
            _item(source_id="SRC-001"),
            _item(source_id="SRC-001"),
        ]),
    )

    result = _validate(registry_path)
    issue = result.issues[0]

    assert issue.code is (
        OfficialSourceRegistryValidationIssueCode.DUPLICATE_SOURCE_ID
    )
    assert issue.message == (
        "Official Source registry contains a duplicate source_id."
    )
    assert issue.field_name == "source_id"


def test_same_registry_produces_identical_report_text(tmp_path):
    registry_path = tmp_path / "registry.json"
    _write_registry(
        registry_path,
        _registry([
            _item(source_id="SRC-002", source_type="markdown"),
            _item(source_id="SRC-001", source_type="pdf"),
        ]),
    )

    first = render_official_source_registry_validation_report(
        _validate(registry_path)
    )
    second = render_official_source_registry_validation_report(
        _validate(registry_path)
    )

    assert first == second


def test_valid_report_is_exact_and_sorted(tmp_path):
    registry_path = tmp_path / "registry.json"
    _write_registry(
        registry_path,
        _registry([
            _item(
                source_id="SRC-002",
                source_type="pdf",
                document_classification="working_note",
                authority_status="reference",
                lifecycle_status="superseded",
                evidence_eligibility="not_eligible",
            ),
            _item(
                source_id="SRC-001",
                source_type="markdown",
                document_classification="project_rulebook",
                authority_status="source_of_truth_candidate",
                lifecycle_status="locked",
                evidence_eligibility="eligible_with_review",
            ),
        ]),
    )

    report = render_official_source_registry_validation_report(
        _validate(registry_path)
    )

    assert report == """Official Source Registry Validation Report
contract_version: official_source_registry_validation_contract_v1
status: valid
total_official_sources: 2
source_type:
  markdown: 1
  pdf: 1
document_classification:
  project_rulebook: 1
  working_note: 1
authority_status:
  reference: 1
  source_of_truth_candidate: 1
lifecycle_status:
  locked: 1
  superseded: 1
evidence_eligibility:
  eligible_with_review: 1
  not_eligible: 1"""


def test_invalid_report_is_exact_with_item_location(tmp_path):
    registry_path = tmp_path / "registry.json"
    _write_registry(
        registry_path,
        _registry([_item(source_type="invalid")]),
    )

    report = render_official_source_registry_validation_report(
        _validate(registry_path)
    )

    assert report == """Official Source Registry Validation Report
contract_version: official_source_registry_validation_contract_v1
status: invalid
issue_code: invalid_registry_entry
issue_message: Official Source registry item is invalid.
item_index: 0
field_name: source_type"""


def test_reports_never_print_referenced_source_path(tmp_path):
    registry_path = tmp_path / "registry.json"
    source_path = "docs/private-synthetic-source.pdf"
    _write_registry(
        registry_path,
        _registry([_item(source_path=source_path)]),
    )

    valid_report = render_official_source_registry_validation_report(
        _validate(registry_path)
    )

    invalid_registry_path = tmp_path / "invalid.json"
    invalid_item = _item(source_path=source_path)
    del invalid_item["source_id"]
    _write_registry(
        invalid_registry_path,
        _registry([invalid_item]),
    )
    invalid_report = render_official_source_registry_validation_report(
        _validate(invalid_registry_path)
    )

    assert source_path not in valid_report
    assert source_path not in invalid_report
    assert "source_path" not in valid_report
    assert "source_path" not in invalid_report


def test_empty_official_registry_config_validates_successfully():
    repo_root = Path(__file__).resolve().parents[1]
    config_path = repo_root / "configs" / "official_source_registry.json"

    result = _validate(config_path)
    report = render_official_source_registry_validation_report(result)

    assert result.status is OfficialSourceRegistryValidationStatus.VALID
    assert result.sources == ()
    assert report == """Official Source Registry Validation Report
contract_version: official_source_registry_validation_contract_v1
status: valid
total_official_sources: 0
source_type:
document_classification:
authority_status:
lifecycle_status:
evidence_eligibility:"""


def test_result_contract_rejects_invalid_state_combinations():
    issue = OfficialSourceRegistryValidationIssue(
        code=OfficialSourceRegistryValidationIssueCode.INVALID_JSON,
        message="Official Source registry file contains invalid JSON.",
    )

    with pytest.raises(ValueError, match="must not contain issues"):
        OfficialSourceRegistryValidationResult(
            contract_version=(
                OFFICIAL_SOURCE_REGISTRY_VALIDATION_CONTRACT_VERSION
            ),
            status=OfficialSourceRegistryValidationStatus.VALID,
            sources=(),
            issues=(issue,),
        )

    with pytest.raises(ValueError, match="exactly one issue"):
        OfficialSourceRegistryValidationResult(
            contract_version=(
                OFFICIAL_SOURCE_REGISTRY_VALIDATION_CONTRACT_VERSION
            ),
            status=OfficialSourceRegistryValidationStatus.INVALID,
            sources=(),
            issues=(),
        )
