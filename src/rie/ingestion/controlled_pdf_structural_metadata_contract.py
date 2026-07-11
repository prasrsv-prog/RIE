"""Value-only contract for controlled PDF structural metadata gating."""

from __future__ import annotations

from dataclasses import dataclass

from rie.ingestion.controlled_real_asset_fixture_contract import (
    ControlledRealAssetFixtureContractResult,
)


STRUCTURAL_METADATA_ONLY_MODE = "structural_metadata_only"
PRODUCT_SPEC_PDF_FIXTURE_TYPE = "product_spec_pdf"

PERMITTED_STRUCTURAL_FIELDS: tuple[str, ...] = (
    "encrypted",
    "page_count",
    "page_width_points",
    "page_height_points",
    "page_rotation_degrees",
)


@dataclass(frozen=True)
class ControlledPdfStructuralMetadataContractResult:
    allowed: bool
    reason: str
    fixture_id: str
    fixture_path: str
    fixture_type: str
    inspection_mode: str
    permitted_fields: tuple[str, ...]
    evidence_allowed: bool
    notes: str


class ControlledPdfStructuralMetadataContract:
    @staticmethod
    def evaluate(
        fixture_contract_result: ControlledRealAssetFixtureContractResult,
        fixture_id: str,
        inspection_mode: str = STRUCTURAL_METADATA_ONLY_MODE,
        permitted_fields: tuple[str, ...] = PERMITTED_STRUCTURAL_FIELDS,
        allow_evidence_creation: bool = False,
        notes: str = "",
    ) -> ControlledPdfStructuralMetadataContractResult:
        if not isinstance(
            fixture_contract_result,
            ControlledRealAssetFixtureContractResult,
        ):
            return _blocked_result(
                reason="fixture contract result is required",
                fixture_id=fixture_id,
                inspection_mode=inspection_mode,
                permitted_fields=permitted_fields,
                notes=notes,
            )

        if fixture_contract_result.allowed is False:
            return _blocked_result(
                reason="fixture contract is not allowed",
                fixture_id=fixture_id,
                inspection_mode=inspection_mode,
                permitted_fields=permitted_fields,
                notes=notes,
            )

        if not fixture_id.strip():
            return _blocked_result(
                reason="fixture_id is required",
                fixture_id=fixture_id,
                inspection_mode=inspection_mode,
                permitted_fields=permitted_fields,
                notes=notes,
            )

        matches = tuple(
            fixture
            for fixture in fixture_contract_result.fixtures
            if fixture.fixture_id == fixture_id
        )

        if len(matches) == 0:
            return _blocked_result(
                reason="fixture_id not found",
                fixture_id=fixture_id,
                inspection_mode=inspection_mode,
                permitted_fields=permitted_fields,
                notes=notes,
            )

        if len(matches) > 1:
            return _blocked_result(
                reason="duplicate fixture_id",
                fixture_id=fixture_id,
                inspection_mode=inspection_mode,
                permitted_fields=permitted_fields,
                notes=notes,
            )

        fixture = matches[0]

        if fixture.fixture_type != PRODUCT_SPEC_PDF_FIXTURE_TYPE:
            return _blocked_result(
                reason="fixture_type must be product_spec_pdf",
                fixture_id=fixture.fixture_id,
                fixture_path=fixture.fixture_path,
                fixture_type=fixture.fixture_type,
                inspection_mode=inspection_mode,
                permitted_fields=permitted_fields,
                notes=notes,
            )

        if fixture.allowed_for_metadata is False:
            return _blocked_result(
                reason="metadata access must be allowed",
                fixture_id=fixture.fixture_id,
                fixture_path=fixture.fixture_path,
                fixture_type=fixture.fixture_type,
                inspection_mode=inspection_mode,
                permitted_fields=permitted_fields,
                notes=notes,
            )

        if fixture.allowed_for_pdf_text_extraction is True:
            return _blocked_result(
                reason="fixture pdf text extraction flag must remain disabled",
                fixture_id=fixture.fixture_id,
                fixture_path=fixture.fixture_path,
                fixture_type=fixture.fixture_type,
                inspection_mode=inspection_mode,
                permitted_fields=permitted_fields,
                notes=notes,
            )

        if fixture.allowed_for_image_metadata is True:
            return _blocked_result(
                reason="fixture image metadata flag must remain disabled",
                fixture_id=fixture.fixture_id,
                fixture_path=fixture.fixture_path,
                fixture_type=fixture.fixture_type,
                inspection_mode=inspection_mode,
                permitted_fields=permitted_fields,
                notes=notes,
            )

        if fixture.allowed_for_evidence is True:
            return _blocked_result(
                reason="fixture evidence flag must remain disabled",
                fixture_id=fixture.fixture_id,
                fixture_path=fixture.fixture_path,
                fixture_type=fixture.fixture_type,
                inspection_mode=inspection_mode,
                permitted_fields=permitted_fields,
                notes=notes,
            )

        if inspection_mode != STRUCTURAL_METADATA_ONLY_MODE:
            return _blocked_result(
                reason="inspection_mode must be structural_metadata_only",
                fixture_id=fixture.fixture_id,
                fixture_path=fixture.fixture_path,
                fixture_type=fixture.fixture_type,
                inspection_mode=inspection_mode,
                permitted_fields=permitted_fields,
                notes=notes,
            )

        if not isinstance(permitted_fields, tuple):
            return _blocked_result(
                reason="permitted_fields must be a tuple",
                fixture_id=fixture.fixture_id,
                fixture_path=fixture.fixture_path,
                fixture_type=fixture.fixture_type,
                inspection_mode=inspection_mode,
                permitted_fields=(),
                notes=notes,
            )

        if permitted_fields != PERMITTED_STRUCTURAL_FIELDS:
            return _blocked_result(
                reason="permitted_fields must match the approved field set",
                fixture_id=fixture.fixture_id,
                fixture_path=fixture.fixture_path,
                fixture_type=fixture.fixture_type,
                inspection_mode=inspection_mode,
                permitted_fields=permitted_fields,
                notes=notes,
            )

        if allow_evidence_creation is True:
            return _blocked_result(
                reason="evidence creation is not allowed by this contract",
                fixture_id=fixture.fixture_id,
                fixture_path=fixture.fixture_path,
                fixture_type=fixture.fixture_type,
                inspection_mode=inspection_mode,
                permitted_fields=permitted_fields,
                notes=notes,
            )

        if notes is None:
            return _blocked_result(
                reason="notes is required",
                fixture_id=fixture.fixture_id,
                fixture_path=fixture.fixture_path,
                fixture_type=fixture.fixture_type,
                inspection_mode=inspection_mode,
                permitted_fields=permitted_fields,
                notes=notes,
            )

        return ControlledPdfStructuralMetadataContractResult(
            allowed=True,
            reason="pdf structural metadata contract allowed",
            fixture_id=fixture.fixture_id,
            fixture_path=fixture.fixture_path,
            fixture_type=fixture.fixture_type,
            inspection_mode=inspection_mode,
            permitted_fields=PERMITTED_STRUCTURAL_FIELDS,
            evidence_allowed=False,
            notes=notes,
        )


def _blocked_result(
    *,
    reason: str,
    fixture_id: str,
    inspection_mode: str,
    permitted_fields: tuple[str, ...],
    notes: str | None,
    fixture_path: str = "",
    fixture_type: str = "",
) -> ControlledPdfStructuralMetadataContractResult:
    return ControlledPdfStructuralMetadataContractResult(
        allowed=False,
        reason=reason,
        fixture_id=fixture_id,
        fixture_path=fixture_path,
        fixture_type=fixture_type,
        inspection_mode=inspection_mode,
        permitted_fields=permitted_fields,
        evidence_allowed=False,
        notes="" if notes is None else notes,
    )