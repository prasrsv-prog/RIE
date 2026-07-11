"""Controlled parser implementation for bounded PDF structural metadata."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

from rie.ingestion.controlled_pdf_structural_metadata_contract import (
    PERMITTED_STRUCTURAL_FIELDS,
    PRODUCT_SPEC_PDF_FIXTURE_TYPE,
    STRUCTURAL_METADATA_ONLY_MODE,
)
from rie.ingestion.controlled_pdf_structural_metadata_execution_contract import (
    MAX_INSPECTED_PAGES_LIMIT,
    ControlledPdfStructuralMetadataExecutionContractResult,
)
from rie.ingestion.controlled_pdf_structural_metadata_result_contract import (
    ENCRYPTED_ERROR,
    PARSER_ERROR,
    PARSER_UNAVAILABLE_ERROR,
    PARTIAL_INSPECTION_ERROR,
    REQUEST_REQUIRED_ERROR,
    SAFETY_CHECK_ERROR,
    UNREADABLE_ERROR,
    ControlledPdfStructuralMetadataPageItem,
    ControlledPdfStructuralMetadataResultContract,
    ControlledPdfStructuralMetadataResultContractResult,
    ControlledPdfStructuralMetadataResultInput,
)


@dataclass(frozen=True)
class ControlledPdfStructuralMetadataImplementationRequest:
    execution_contract_result: ControlledPdfStructuralMetadataExecutionContractResult
    source_label: str
    allow_implementation_execution: bool
    notes: str


class ControlledPdfStructuralMetadataImplementation:
    @staticmethod
    def execute(
        request: object,
    ) -> ControlledPdfStructuralMetadataResultContractResult:
        if not isinstance(
            request,
            ControlledPdfStructuralMetadataImplementationRequest,
        ):
            return _blocked_result(
                request=request,
                inspection_error=SAFETY_CHECK_ERROR,
            )

        execution_contract_result = request.execution_contract_result

        if not isinstance(
            execution_contract_result,
            ControlledPdfStructuralMetadataExecutionContractResult,
        ):
            return _blocked_result(
                request=request,
                inspection_error=SAFETY_CHECK_ERROR,
            )

        if not isinstance(
            request.allow_implementation_execution,
            bool,
        ):
            return _blocked_result(
                request=request,
                inspection_error=SAFETY_CHECK_ERROR,
            )

        if request.allow_implementation_execution is False:
            return _blocked_result(
                request=request,
                inspection_error=REQUEST_REQUIRED_ERROR,
            )

        if not _execution_contract_is_safe(execution_contract_result):
            return _blocked_result(
                request=request,
                inspection_error=SAFETY_CHECK_ERROR,
            )

        if not isinstance(request.source_label, str):
            return _blocked_result(
                request=request,
                inspection_error=SAFETY_CHECK_ERROR,
            )

        if not request.source_label.strip():
            return _blocked_result(
                request=request,
                inspection_error=SAFETY_CHECK_ERROR,
            )

        if not isinstance(request.notes, str):
            return _blocked_result(
                request=request,
                inspection_error=SAFETY_CHECK_ERROR,
            )

        if PdfReader is None:
            return _finalize_result(
                execution_contract_result=execution_contract_result,
                source_label=request.source_label,
                notes=request.notes,
                inspection_status="parser_unavailable",
                encrypted=False,
                page_count=0,
                page_details=(),
                page_details_truncated=False,
                inspection_error=PARSER_UNAVAILABLE_ERROR,
            )

        try:
            reader = PdfReader(execution_contract_result.fixture_path)

            if reader.is_encrypted:
                return _finalize_result(
                    execution_contract_result=execution_contract_result,
                    source_label=request.source_label,
                    notes=request.notes,
                    inspection_status="encrypted",
                    encrypted=True,
                    page_count=0,
                    page_details=(),
                    page_details_truncated=False,
                    inspection_error=ENCRYPTED_ERROR,
                )

            page_count = len(reader.pages)

            detail_count = min(
                page_count,
                execution_contract_result.max_inspected_pages,
            )

            page_details = []

            for page_index in range(detail_count):
                try:
                    page = reader.pages[page_index]
                    media_box = page.mediabox

                    width_points = _validated_dimension(
                        media_box.width
                    )
                    height_points = _validated_dimension(
                        media_box.height
                    )
                    rotation_degrees = _normalized_rotation(
                        page.rotation
                    )

                    page_details.append(
                        ControlledPdfStructuralMetadataPageItem(
                            page_index=page_index,
                            width_points=width_points,
                            height_points=height_points,
                            rotation_degrees=rotation_degrees,
                            inspection_status="inspected",
                        )
                    )
                except Exception:
                    page_details.append(
                        ControlledPdfStructuralMetadataPageItem(
                            page_index=page_index,
                            width_points=0,
                            height_points=0,
                            rotation_degrees=0,
                            inspection_status="page_error",
                        )
                    )

            immutable_page_details = tuple(page_details)

            if (
                detail_count > 0
                and all(
                    page.inspection_status == "page_error"
                    for page in immutable_page_details
                )
            ):
                return _finalize_result(
                    execution_contract_result=execution_contract_result,
                    source_label=request.source_label,
                    notes=request.notes,
                    inspection_status="parser_error",
                    encrypted=False,
                    page_count=0,
                    page_details=(),
                    page_details_truncated=False,
                    inspection_error=PARSER_ERROR,
                )

            has_page_error = any(
                page.inspection_status == "page_error"
                for page in immutable_page_details
            )

            page_details_truncated = (
                page_count
                > execution_contract_result.max_inspected_pages
            )

            if has_page_error:
                inspection_status = "partial"
                inspection_error = PARTIAL_INSPECTION_ERROR
            elif page_details_truncated:
                inspection_status = "bounded"
                inspection_error = ""
            else:
                inspection_status = "inspected"
                inspection_error = ""

            return _finalize_result(
                execution_contract_result=execution_contract_result,
                source_label=request.source_label,
                notes=request.notes,
                inspection_status=inspection_status,
                encrypted=False,
                page_count=page_count,
                page_details=immutable_page_details,
                page_details_truncated=page_details_truncated,
                inspection_error=inspection_error,
            )

        except OSError:
            return _finalize_result(
                execution_contract_result=execution_contract_result,
                source_label=request.source_label,
                notes=request.notes,
                inspection_status="unreadable",
                encrypted=False,
                page_count=0,
                page_details=(),
                page_details_truncated=False,
                inspection_error=UNREADABLE_ERROR,
            )
        except Exception:
            return _finalize_result(
                execution_contract_result=execution_contract_result,
                source_label=request.source_label,
                notes=request.notes,
                inspection_status="parser_error",
                encrypted=False,
                page_count=0,
                page_details=(),
                page_details_truncated=False,
                inspection_error=PARSER_ERROR,
            )


def _execution_contract_is_safe(
    execution_contract_result: ControlledPdfStructuralMetadataExecutionContractResult,
) -> bool:
    if execution_contract_result.allowed is not True:
        return False

    if execution_contract_result.execution_allowed is not True:
        return False

    if (
        execution_contract_result.fixture_type
        != PRODUCT_SPEC_PDF_FIXTURE_TYPE
    ):
        return False

    if (
        execution_contract_result.inspection_mode
        != STRUCTURAL_METADATA_ONLY_MODE
    ):
        return False

    if (
        execution_contract_result.permitted_fields
        != PERMITTED_STRUCTURAL_FIELDS
    ):
        return False

    if execution_contract_result.allow_content_extraction is not False:
        return False

    if (
        execution_contract_result.allow_output_file_creation
        is not False
    ):
        return False

    if execution_contract_result.evidence_allowed is not False:
        return False

    if not isinstance(
        execution_contract_result.fixture_id,
        str,
    ):
        return False

    if not execution_contract_result.fixture_id.strip():
        return False

    if not isinstance(
        execution_contract_result.fixture_path,
        str,
    ):
        return False

    if not execution_contract_result.fixture_path.strip():
        return False

    if not _is_integer(
        execution_contract_result.max_inspected_pages
    ):
        return False

    if execution_contract_result.max_inspected_pages <= 0:
        return False

    if (
        execution_contract_result.max_inspected_pages
        > MAX_INSPECTED_PAGES_LIMIT
    ):
        return False

    return True


def _validated_dimension(value: object) -> float:
    if isinstance(value, bool):
        raise ValueError("boolean dimension is not allowed")

    if not isinstance(value, (int, float)):
        raise ValueError("dimension must be numeric")

    normalized_value = float(value)

    if not isfinite(normalized_value):
        raise ValueError("dimension must be finite")

    if normalized_value <= 0:
        raise ValueError("dimension must be greater than zero")

    return normalized_value


def _normalized_rotation(value: object) -> int:
    if value is None:
        return 0

    if not _is_integer(value):
        raise ValueError("rotation must be an integer")

    if value % 90 != 0:
        raise ValueError("rotation must be divisible by 90")

    normalized_value = value % 360

    if normalized_value not in {0, 90, 180, 270}:
        raise ValueError("unsupported normalized rotation")

    return normalized_value


def _finalize_result(
    *,
    execution_contract_result: ControlledPdfStructuralMetadataExecutionContractResult,
    source_label: str,
    notes: str,
    inspection_status: str,
    encrypted: bool,
    page_count: int,
    page_details: tuple[ControlledPdfStructuralMetadataPageItem, ...],
    page_details_truncated: bool,
    inspection_error: str,
) -> ControlledPdfStructuralMetadataResultContractResult:
    result_input = ControlledPdfStructuralMetadataResultInput(
        fixture_id=execution_contract_result.fixture_id,
        source_label=source_label,
        fixture_path=execution_contract_result.fixture_path,
        fixture_type=execution_contract_result.fixture_type,
        inspection_mode=execution_contract_result.inspection_mode,
        inspection_status=inspection_status,
        encrypted=encrypted,
        page_count=page_count,
        inspected_page_count=len(page_details),
        page_details_truncated=page_details_truncated,
        page_details=page_details,
        max_inspected_pages=(
            execution_contract_result.max_inspected_pages
        ),
        inspection_error=inspection_error,
        evidence_allowed=False,
        notes=notes,
    )

    return ControlledPdfStructuralMetadataResultContract.evaluate(
        execution_contract_result=execution_contract_result,
        result_input=result_input,
    )


def _blocked_result(
    *,
    request: object,
    inspection_error: str,
) -> ControlledPdfStructuralMetadataResultContractResult:
    execution_contract_result = None
    source_label = ""
    notes = ""

    if isinstance(
        request,
        ControlledPdfStructuralMetadataImplementationRequest,
    ):
        source_label = (
            request.source_label
            if isinstance(request.source_label, str)
            else ""
        )
        notes = (
            request.notes
            if isinstance(request.notes, str)
            else ""
        )

        if isinstance(
            request.execution_contract_result,
            ControlledPdfStructuralMetadataExecutionContractResult,
        ):
            execution_contract_result = (
                request.execution_contract_result
            )

    fixture_id = ""
    fixture_path = ""
    fixture_type = ""
    inspection_mode = ""
    max_inspected_pages = 0

    if execution_contract_result is not None:
        fixture_id = execution_contract_result.fixture_id
        fixture_path = execution_contract_result.fixture_path
        fixture_type = execution_contract_result.fixture_type
        inspection_mode = execution_contract_result.inspection_mode

        if _is_integer(
            execution_contract_result.max_inspected_pages
        ):
            max_inspected_pages = (
                execution_contract_result.max_inspected_pages
            )

    return ControlledPdfStructuralMetadataResultContractResult(
        allowed=False,
        reason=inspection_error,
        fixture_id=fixture_id,
        source_label=source_label,
        fixture_path=fixture_path,
        fixture_type=fixture_type,
        inspection_mode=inspection_mode,
        inspection_status="blocked",
        encrypted=False,
        page_count=0,
        inspected_page_count=0,
        page_details_truncated=False,
        page_details=(),
        max_inspected_pages=max_inspected_pages,
        inspection_error=inspection_error,
        evidence_allowed=False,
        notes=notes,
    )


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)