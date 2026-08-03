from dataclasses import FrozenInstanceError, MISSING, fields
from datetime import datetime, timezone

import pytest

from rie.domain.creative_result_candidate import (
    ALLOWED_ARTIFACT_TYPES,
    CANDIDATE_AUTHORITY_STATE,
    CreativeResultCandidate,
)


EXPECTED_FIELDS = (
    "creative_result_candidate_id",
    "workflow_request_reference",
    "project_context_reference",
    "campaign_context_reference",
    "creative_brief_reference",
    "instruction_reference",
    "originating_manual_handoff_reference",
    "candidate_content_checksum",
    "artifact_type",
    "admission_timestamp",
    "admitting_actor_reference",
    "deterministic_provenance",
    "authority_state",
    "official_source_claimed",
    "accepted_asset_claimed",
    "approved_asset_claimed",
)


def make_candidate(**overrides: object) -> CreativeResultCandidate:
    values: dict[str, object] = {
        "creative_result_candidate_id": "candidate-001",
        "workflow_request_reference": "workflow-request-001",
        "project_context_reference": "project-001",
        "campaign_context_reference": ("project-001", "campaign-001"),
        "creative_brief_reference": "brief-001",
        "instruction_reference": ("instruction-001", "APPROVED_INSTRUCTION"),
        "originating_manual_handoff_reference": None,
        "candidate_content_checksum": "a" * 64,
        "artifact_type": "IMAGE",
        "admission_timestamp": datetime(
            2026,
            8,
            3,
            8,
            0,
            tzinfo=timezone.utc,
        ),
        "admitting_actor_reference": "operator-001",
        "deterministic_provenance": (
            "workflow-request-001",
            "source-package-sha256:" + ("b" * 64),
        ),
        "authority_state": CANDIDATE_AUTHORITY_STATE,
        "official_source_claimed": False,
        "accepted_asset_claimed": False,
        "approved_asset_claimed": False,
    }
    values.update(overrides)
    return CreativeResultCandidate(**values)


def test_contract_has_exactly_sixteen_required_fields() -> None:
    model_fields = fields(CreativeResultCandidate)
    assert tuple(item.name for item in model_fields) == EXPECTED_FIELDS
    assert all(item.default is MISSING for item in model_fields)
    assert all(item.default_factory is MISSING for item in model_fields)


def test_valid_candidate_is_immutable() -> None:
    candidate = make_candidate()
    with pytest.raises(FrozenInstanceError):
        candidate.artifact_type = "VIDEO"  # type: ignore[misc]


@pytest.mark.parametrize(
    "authority_state",
    ["PROMPT_CANDIDATE", "APPROVED_INSTRUCTION"],
)
def test_each_instruction_authority_state_is_accepted(
    authority_state: str,
) -> None:
    candidate = make_candidate(
        instruction_reference=("instruction-001", authority_state)
    )
    assert candidate.instruction_reference[1] == authority_state


@pytest.mark.parametrize("artifact_type", sorted(ALLOWED_ARTIFACT_TYPES))
def test_each_supported_artifact_type_is_accepted(
    artifact_type: str,
) -> None:
    candidate = make_candidate(artifact_type=artifact_type)
    assert candidate.artifact_type == artifact_type


@pytest.mark.parametrize(
    "handoff_reference",
    [None, "manual-handoff-001"],
)
def test_optional_manual_handoff_reference_is_explicit(
    handoff_reference: str | None,
) -> None:
    candidate = make_candidate(
        originating_manual_handoff_reference=handoff_reference
    )
    assert candidate.originating_manual_handoff_reference == handoff_reference


@pytest.mark.parametrize(
    "field_name",
    [
        "creative_result_candidate_id",
        "workflow_request_reference",
        "project_context_reference",
        "creative_brief_reference",
        "admitting_actor_reference",
    ],
)
@pytest.mark.parametrize("invalid_value", [None, 7, "", "   "])
def test_required_text_fields_fail_closed(
    field_name: str,
    invalid_value: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        make_candidate(**{field_name: invalid_value})


@pytest.mark.parametrize(
    "field_name",
    [
        "creative_result_candidate_id",
        "workflow_request_reference",
        "project_context_reference",
        "creative_brief_reference",
        "admitting_actor_reference",
    ],
)
def test_required_text_fields_reject_non_ascii(field_name: str) -> None:
    with pytest.raises(ValueError, match="ASCII"):
        make_candidate(**{field_name: "nilai-\u00e9"})


@pytest.mark.parametrize(
    "invalid_reference",
    [
        None,
        ["project-001", "campaign-001"],
        (),
        ("project-001",),
        ("project-001", "campaign-001", "extra"),
        ("", "campaign-001"),
        ("project-001", ""),
        ("project-\u00e9", "campaign-001"),
    ],
)
def test_campaign_reference_fails_closed(
    invalid_reference: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        make_candidate(campaign_context_reference=invalid_reference)


def test_campaign_reference_must_bind_to_exact_project() -> None:
    with pytest.raises(ValueError, match="project binding"):
        make_candidate(
            campaign_context_reference=("another-project", "campaign-001")
        )


@pytest.mark.parametrize(
    "invalid_reference",
    [
        None,
        ["instruction-001", "APPROVED_INSTRUCTION"],
        (),
        ("instruction-001",),
        ("instruction-001", "APPROVED_INSTRUCTION", "extra"),
        ("", "APPROVED_INSTRUCTION"),
        ("instruction-001", ""),
        ("instruction-\u00e9", "APPROVED_INSTRUCTION"),
        ("instruction-001", "INFERRED"),
    ],
)
def test_instruction_reference_fails_closed(
    invalid_reference: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        make_candidate(instruction_reference=invalid_reference)


@pytest.mark.parametrize("invalid_handoff", [7, "", "   ", "handoff-\u00e9"])
def test_optional_manual_handoff_reference_fails_closed(
    invalid_handoff: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        make_candidate(
            originating_manual_handoff_reference=invalid_handoff
        )


@pytest.mark.parametrize(
    "invalid_checksum",
    [
        None,
        7,
        "",
        "a" * 63,
        "a" * 65,
        "A" * 64,
        "g" * 64,
        ("a" * 63) + " ",
    ],
)
def test_candidate_content_checksum_fails_closed(
    invalid_checksum: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        make_candidate(candidate_content_checksum=invalid_checksum)


@pytest.mark.parametrize(
    "invalid_artifact_type",
    [None, 7, "", "image", "MODEL", "IMAGE/PNG"],
)
def test_artifact_type_fails_closed(
    invalid_artifact_type: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        make_candidate(artifact_type=invalid_artifact_type)


@pytest.mark.parametrize(
    "invalid_timestamp",
    [None, "2026-08-03T08:00:00Z", datetime(2026, 8, 3, 8, 0)],
)
def test_admission_timestamp_rejects_invalid_or_naive_value(
    invalid_timestamp: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        make_candidate(admission_timestamp=invalid_timestamp)


@pytest.mark.parametrize(
    "invalid_provenance",
    [
        None,
        [],
        (),
        ("",),
        ("provenance-\u00e9",),
        ("same", "same"),
    ],
)
def test_deterministic_provenance_fails_closed(
    invalid_provenance: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        make_candidate(deterministic_provenance=invalid_provenance)


@pytest.mark.parametrize(
    "invalid_authority",
    [None, "", "APPROVED", "ACCEPTED_ASSET", "OFFICIAL_SOURCE"],
)
def test_authority_state_must_be_exactly_candidate(
    invalid_authority: object,
) -> None:
    with pytest.raises(ValueError, match="exactly CANDIDATE"):
        make_candidate(authority_state=invalid_authority)


@pytest.mark.parametrize(
    "field_name",
    [
        "official_source_claimed",
        "accepted_asset_claimed",
        "approved_asset_claimed",
    ],
)
@pytest.mark.parametrize("invalid_value", [None, 0, 1, "False"])
def test_authority_claim_flags_require_boolean(
    field_name: str,
    invalid_value: object,
) -> None:
    with pytest.raises(TypeError, match="boolean"):
        make_candidate(**{field_name: invalid_value})


@pytest.mark.parametrize(
    "field_name",
    [
        "official_source_claimed",
        "accepted_asset_claimed",
        "approved_asset_claimed",
    ],
)
def test_candidate_rejects_premature_authority_claim(
    field_name: str,
) -> None:
    with pytest.raises(ValueError, match="must not claim"):
        make_candidate(**{field_name: True})


def test_candidate_preserves_exact_context_and_provenance() -> None:
    candidate = make_candidate()
    assert candidate.project_context_reference == "project-001"
    assert candidate.campaign_context_reference == (
        "project-001",
        "campaign-001",
    )
    assert candidate.deterministic_provenance == (
        "workflow-request-001",
        "source-package-sha256:" + ("b" * 64),
    )
    assert candidate.authority_state == "CANDIDATE"
    assert candidate.official_source_claimed is False
    assert candidate.accepted_asset_claimed is False
    assert candidate.approved_asset_claimed is False
