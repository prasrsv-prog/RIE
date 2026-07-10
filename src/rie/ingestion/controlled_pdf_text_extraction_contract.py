"""Value-only contract for controlled PDF text extraction gating."""

from __future__ import annotations

from dataclasses import dataclass

from rie.ingestion.controlled_real_asset_fixture_contract import (
    ControlledRealAssetFixtureContractResult,
)


TEXT_ONLY_MODE = "text_only"
PRODUCT_SPEC_PDF_FIXTURE_TYPE = "product_spec_pdf"


@dataclass(frozen=True)
class ControlledPdfTextExtractionContractResult:
    allowed: bool
    reason: str
    fixture_id: str
    fixture_path: str
    fixture_type: str
    extraction_mode: str
    evidence_allowed: bool
    notes: str


class ControlledPdfTextExtractionContract:
    @staticmethod
    def evaluate(
        fixture_contract_result: ControlledRealAssetFixtureContractResult,
        fixture_id: str,
        extraction_mode: str = TEXT_ONLY_MODE,
        allow_pdf_text_extraction: bool = False,
        allow_evidence_creation: bool = False,
        notes: str = "",
    ) -> ControlledPdfTextExtractionContractResult:
        if not isinstance(
            fixture_contract_result,
            ControlledRealAssetFixtureContractResult,
        ):
            return _blocked_result(
                reason="fixture contract result is required",
                fixture_id=fixture_id,
                extraction_mode=extraction_mode,
                notes=notes,
            )

        if fixture_contract_result.allowed is False:
            return _blocked_result(
                reason="fixture contract is not allowed",
                fixture_id=fixture_id,
                extraction_mode=extraction_mode,
                notes=notes,
            )

        if not fixture_id.strip():
            return _blocked_result(
                reason="fixture_id is required",
                fixture_id=fixture_id,
                extraction_mode=extraction_mode,
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
                extraction_mode=extraction_mode,
                notes=notes,
            )

        if len(matches) > 1:
            return _blocked_result(
                reason="duplicate fixture_id",
                fixture_id=fixture_id,
                extraction_mode=extraction_mode,
                notes=notes,
            )

        fixture = matches[0]

        if fixture.fixture_type != PRODUCT_SPEC_PDF_FIXTURE_TYPE:
            return _blocked_result(
                reason="fixture_type must be product_spec_pdf",
                fixture_id=fixture.fixture_id,
                fixture_path=fixture.fixture_path,
                fixture_type=fixture.fixture_type,
                extraction_mode=extraction_mode,
                notes=notes,
            )

        if fixture.allowed_for_metadata is False:
            return _blocked_result(
                reason="metadata access must be allowed",
                fixture_id=fixture.fixture_id,
                fixture_path=fixture.fixture_path,
                fixture_type=fixture.fixture_type,
                extraction_mode=extraction_mode,
                notes=notes,
            )

        if fixture.allowed_for_pdf_text_extraction is True:
            return _blocked_result(
                reason="fixture pdf text extraction flag must remain disabled",
                fixture_id=fixture.fixture_id,
                fixture_path=fixture.fixture_path,
                fixture_type=fixture.fixture_type,
                extraction_mode=extraction_mode,
                notes=notes,
            )

        if fixture.allowed_for_evidence is True:
            return _blocked_result(
                reason="fixture evidence flag must remain disabled",
                fixture_id=fixture.fixture_id,
                fixture_path=fixture.fixture_path,
                fixture_type=fixture.fixture_type,
                extraction_mode=extraction_mode,
                notes=notes,
            )

        if extraction_mode != TEXT_ONLY_MODE:
            return _blocked_result(
                reason="unsupported extraction_mode",
                fixture_id=fixture.fixture_id,
                fixture_path=fixture.fixture_path,
                fixture_type=fixture.fixture_type,
                extraction_mode=extraction_mode,
                notes=notes,
            )

        if allow_pdf_text_extraction is True:
            return _blocked_result(
                reason="pdf text extraction execution is not allowed by this contract",
                fixture_id=fixture.fixture_id,
                fixture_path=fixture.fixture_path,
                fixture_type=fixture.fixture_type,
                extraction_mode=extraction_mode,
                notes=notes,
            )

        if allow_evidence_creation is True:
            return _blocked_result(
                reason="evidence creation is not allowed by this contract",
                fixture_id=fixture.fixture_id,
                fixture_path=fixture.fixture_path,
                fixture_type=fixture.fixture_type,
                extraction_mode=extraction_mode,
                notes=notes,
            )

        if notes is None:
            return _blocked_result(
                reason="notes is required",
                fixture_id=fixture.fixture_id,
                fixture_path=fixture.fixture_path,
                fixture_type=fixture.fixture_type,
                extraction_mode=extraction_mode,
                notes=notes,
            )

        return ControlledPdfTextExtractionContractResult(
            allowed=True,
            reason="pdf text extraction contract allowed",
            fixture_id=fixture.fixture_id,
            fixture_path=fixture.fixture_path,
            fixture_type=fixture.fixture_type,
            extraction_mode=extraction_mode,
            evidence_allowed=False,
            notes=notes,
        )


def _blocked_result(
    *,
    reason: str,
    fixture_id: str,
    extraction_mode: str,
    notes: str | None,
    fixture_path: str = "",
    fixture_type: str = "",
) -> ControlledPdfTextExtractionContractResult:
    return ControlledPdfTextExtractionContractResult(
        allowed=False,
        reason=reason,
        fixture_id=fixture_id,
        fixture_path=fixture_path,
        fixture_type=fixture_type,
        extraction_mode=extraction_mode,
        evidence_allowed=False,
        notes="" if notes is None else notes,
    )
