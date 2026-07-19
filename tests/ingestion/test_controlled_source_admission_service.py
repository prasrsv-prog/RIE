import hashlib
import inspect
import json
from pathlib import Path

import pytest

from rie.ingestion.controlled_source_admission_job_contract import (
    ControlledSourceAdmissionIssueCode,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    ControlledSourceAdmissionRequest,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    ControlledSourceAdmissionStatus,
)
from rie.ingestion import controlled_source_admission_service as service
from rie.ingestion.controlled_source_admission_service import (
    admit_controlled_source,
)


def _item(source_path="synthetic-source.pdf", **overrides):
    item = {
        "source_id": "SRC-SYNTHETIC-001",
        "source_path": str(source_path),
        "source_type": "pdf",
        "document_classification": "project_rulebook",
        "authority_status": "source_of_truth_candidate",
        "lifecycle_status": "locked",
        "evidence_eligibility": "eligible",
        "version": "v1.0",
        "review_notes": "Synthetic temporary test data only.",
    }
    item.update(overrides)
    return item


def _write_registry(tmp_path, item):
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(
        json.dumps({"official_sources": [item]}),
        encoding="utf-8",
    )
    return registry_path


def _request(registry_path, output_path, source_id="SRC-SYNTHETIC-001"):
    return ControlledSourceAdmissionRequest(
        registry_path=registry_path,
        source_id=source_id,
        output_location=output_path,
    )


def _prepare(tmp_path, **item_overrides):
    source_path = tmp_path / "synthetic-source.pdf"
    source_path.write_bytes(b"synthetic controlled source bytes")
    item = _item(**item_overrides)
    registry_path = _write_registry(tmp_path, item)
    output_path = tmp_path / "job.json"
    return source_path, registry_path, output_path


def test_request_type_and_empty_value_rejection(tmp_path):
    with pytest.raises(TypeError):
        admit_controlled_source(object())

    with pytest.raises(ValueError):
        ControlledSourceAdmissionRequest(
            tmp_path / "registry.json",
            " ",
            tmp_path / "job.json",
        )


def test_wildcard_and_recursion_syntax_rejection(tmp_path):
    source_path, registry_path, output_path = _prepare(tmp_path)

    registry_result = admit_controlled_source(
        _request(tmp_path / "*.json", output_path)
    )
    source_result = admit_controlled_source(
        _request(registry_path, output_path, "SRC-*")
    )
    output_result = admit_controlled_source(
        _request(registry_path, tmp_path / "**" / "job.json")
    )

    assert registry_result.issue.code is (
        ControlledSourceAdmissionIssueCode.REGISTRY_INVALID
    )
    assert source_result.issue.code is (
        ControlledSourceAdmissionIssueCode.SOURCE_ID_UNKNOWN
    )
    assert output_result.issue.code is (
        ControlledSourceAdmissionIssueCode.OUTPUT_LOCATION_INVALID
    )
    assert source_path.read_bytes() == b"synthetic controlled source bytes"


def test_invalid_gate_two_registry_rejects_before_source_read(
    tmp_path,
    monkeypatch,
):
    registry_path = tmp_path / "registry.json"
    registry_path.write_text("{invalid", encoding="utf-8")

    def fail_if_called(_path):
        raise AssertionError("source bytes must not be read")

    monkeypatch.setattr(
        service,
        "_calculate_source_sha256",
        fail_if_called,
    )

    result = admit_controlled_source(
        _request(registry_path, tmp_path / "job.json")
    )

    assert result.issue.code is (
        ControlledSourceAdmissionIssueCode.REGISTRY_INVALID
    )
    assert result.issue.upstream_issue_code == "invalid_json"


def test_unknown_source_id_rejection(tmp_path):
    _, registry_path, output_path = _prepare(tmp_path)

    result = admit_controlled_source(
        _request(registry_path, output_path, "SRC-UNKNOWN")
    )

    assert result.issue.code is (
        ControlledSourceAdmissionIssueCode.SOURCE_ID_UNKNOWN
    )
    assert not output_path.exists()


def test_eligible_with_review_rejection(tmp_path):
    _, registry_path, output_path = _prepare(
        tmp_path,
        evidence_eligibility="eligible_with_review",
    )

    result = admit_controlled_source(
        _request(registry_path, output_path)
    )

    assert result.issue.code is (
        ControlledSourceAdmissionIssueCode.SOURCE_REVIEW_REQUIRED
    )


def test_not_eligible_rejection(tmp_path):
    _, registry_path, output_path = _prepare(
        tmp_path,
        evidence_eligibility="not_eligible",
    )

    result = admit_controlled_source(
        _request(registry_path, output_path)
    )

    assert result.issue.code is (
        ControlledSourceAdmissionIssueCode.SOURCE_INELIGIBLE
    )


def test_unknown_eligibility_rejection(tmp_path):
    _, registry_path, output_path = _prepare(
        tmp_path,
        evidence_eligibility="unknown",
    )

    result = admit_controlled_source(
        _request(registry_path, output_path)
    )

    assert result.issue.code is (
        ControlledSourceAdmissionIssueCode.SOURCE_INELIGIBLE
    )


def test_directory_and_unknown_source_type_rejection(tmp_path):
    for source_type in ("directory", "unknown"):
        case = tmp_path / source_type
        case.mkdir()
        registry_path = _write_registry(
            case,
            _item(source_type=source_type),
        )
        result = admit_controlled_source(
            _request(registry_path, case / "job.json")
        )

        assert result.issue.code is (
            ControlledSourceAdmissionIssueCode.SOURCE_TYPE_UNSUPPORTED
        )


def test_relative_source_path_resolves_against_registry_parent(tmp_path):
    source_path, registry_path, output_path = _prepare(tmp_path)

    result = admit_controlled_source(
        _request(registry_path, output_path)
    )

    assert result.status is ControlledSourceAdmissionStatus.ADMITTED
    assert result.job.source_path == str(source_path.resolve())
    assert output_path.exists()


def test_absolute_source_path_is_preserved(tmp_path):
    source_path = tmp_path / "absolute-source.pdf"
    source_path.write_bytes(b"absolute synthetic bytes")
    registry_path = _write_registry(
        tmp_path,
        _item(source_path=source_path.resolve()),
    )
    output_path = tmp_path / "job.json"

    result = admit_controlled_source(
        _request(registry_path, output_path)
    )

    assert result.status is ControlledSourceAdmissionStatus.ADMITTED
    assert result.job.source_path == str(source_path.resolve())


def test_missing_source_rejection(tmp_path):
    registry_path = _write_registry(tmp_path, _item())
    output_path = tmp_path / "job.json"

    result = admit_controlled_source(
        _request(registry_path, output_path)
    )

    assert result.issue.code is (
        ControlledSourceAdmissionIssueCode.SOURCE_MISSING
    )


def test_non_file_source_rejection(tmp_path):
    source_directory = tmp_path / "synthetic-source.pdf"
    source_directory.mkdir()
    registry_path = _write_registry(tmp_path, _item())
    output_path = tmp_path / "job.json"

    result = admit_controlled_source(
        _request(registry_path, output_path)
    )

    assert result.issue.code is (
        ControlledSourceAdmissionIssueCode.SOURCE_NOT_FILE
    )


def test_unreadable_and_checksum_failure_rejections(tmp_path, monkeypatch):
    _, registry_path, output_path = _prepare(tmp_path)

    def unreadable(_path):
        raise PermissionError("synthetic permission failure")

    monkeypatch.setattr(
        service,
        "_calculate_source_sha256",
        unreadable,
    )
    unreadable_result = admit_controlled_source(
        _request(registry_path, output_path)
    )

    def checksum_failure(_path):
        raise OSError("synthetic checksum failure")

    monkeypatch.setattr(
        service,
        "_calculate_source_sha256",
        checksum_failure,
    )
    checksum_result = admit_controlled_source(
        _request(registry_path, output_path)
    )

    assert unreadable_result.issue.code is (
        ControlledSourceAdmissionIssueCode.SOURCE_UNREADABLE
    )
    assert checksum_result.issue.code is (
        ControlledSourceAdmissionIssueCode.CHECKSUM_FAILED
    )
    assert "synthetic" not in unreadable_result.issue.message
    assert "synthetic" not in checksum_result.issue.message


def test_exact_read_only_sha256_calculation(tmp_path):
    source_path, registry_path, output_path = _prepare(tmp_path)
    expected = hashlib.sha256(source_path.read_bytes()).hexdigest()

    result = admit_controlled_source(
        _request(registry_path, output_path)
    )

    assert result.job.source_checksum == expected
    assert result.job.source_checksum_algorithm == "sha256"


def test_invalid_output_location_rejection(tmp_path):
    _, registry_path, _ = _prepare(tmp_path)

    wrong_suffix = admit_controlled_source(
        _request(registry_path, tmp_path / "job.txt")
    )
    missing_parent = admit_controlled_source(
        _request(registry_path, tmp_path / "missing" / "job.json")
    )

    assert wrong_suffix.issue.code is (
        ControlledSourceAdmissionIssueCode.OUTPUT_LOCATION_INVALID
    )
    assert missing_parent.issue.code is (
        ControlledSourceAdmissionIssueCode.OUTPUT_LOCATION_INVALID
    )


def test_source_and_output_path_equality_rejection(tmp_path):
    source_path = tmp_path / "synthetic-source.json"
    source_path.write_bytes(b"synthetic source and output equality")
    registry_path = _write_registry(
        tmp_path,
        _item(source_path=source_path.name),
    )

    result = admit_controlled_source(
        _request(registry_path, source_path)
    )

    assert result.issue.code is (
        ControlledSourceAdmissionIssueCode.OUTPUT_LOCATION_INVALID
    )
    assert source_path.read_bytes() == (
        b"synthetic source and output equality"
    )


def test_exact_authority_lifecycle_and_eligibility_snapshots(tmp_path):
    _, registry_path, output_path = _prepare(
        tmp_path,
        authority_status="official",
        lifecycle_status="final",
        evidence_eligibility="eligible",
    )

    result = admit_controlled_source(
        _request(registry_path, output_path)
    )

    assert result.job.authority_snapshot == "official"
    assert result.job.lifecycle_snapshot == "final"
    assert result.job.eligibility_snapshot == "eligible"


def test_deterministic_job_identity_construction(tmp_path):
    _, registry_path, output_path = _prepare(tmp_path)

    first = admit_controlled_source(
        _request(registry_path, output_path)
    )
    output_path.unlink()
    second = admit_controlled_source(
        _request(registry_path, output_path)
    )

    assert first.job.job_id == second.job.job_id
    assert first.job == second.job


def test_source_bytes_and_filesystem_metadata_remain_unchanged(tmp_path):
    source_path, registry_path, output_path = _prepare(tmp_path)
    before_bytes = source_path.read_bytes()
    before_stat = source_path.stat()

    result = admit_controlled_source(
        _request(registry_path, output_path)
    )
    after_stat = source_path.stat()

    assert result.status is ControlledSourceAdmissionStatus.ADMITTED
    assert source_path.read_bytes() == before_bytes
    assert after_stat.st_size == before_stat.st_size
    assert after_stat.st_mtime_ns == before_stat.st_mtime_ns


def test_no_parser_or_gate_four_invocation_is_present():
    source = inspect.getsource(service)

    assert "rie.extraction" not in source
    assert "controlled_pdf" not in source
    assert "parser" not in source.lower()
    assert "gate_4" not in source.lower()
