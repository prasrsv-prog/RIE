"""Value-only contract for controlled PDF structural metadata results."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from rie.ingestion.controlled_pdf_structural_metadata_contract import (
    PERMITTED_STRUCTURAL_FIELDS,
    PRODUCT_SPEC_PDF_FIXTURE_TYPE,
    STRUCTURAL_METADATA_ONLY_MODE,
)
from rie.ingestion.controlled_pdf_structural_metadata_execution_contract import (
    MAX_INSPECTED_PAGES_LIMIT,
    ControlledPdfStructuralMetadataExecutionContractResult,
)


MAX_INSPECTION_ERROR_CHARACTERS = 500
PARTIAL_INSPECTION_ERROR = (
    "one or more pages could not be structurally inspected"
)

ENCRYPTED_ERROR = "pdf is encrypted"
UNREADABLE_ERROR = "pdf file is unreadable"
PARSER_UNAVAILABLE_ERROR = "pdf parser dependency is unavailable"
PARSER_ERROR = "pdf parser error"
SAFETY_CHECK_ERROR = "implementation safety checks failed"
REQUEST_REQUIRED_ERROR = "implementation request is required"

ALLOWED_PAGE_INSPECTION_STATUSES = frozenset(
    {
        "inspected",
        "page_error",
    }
)

ALLOWED_INSPECTION_STATUSES = frozenset(
    {
        "not_run",
        "inspected",
        "bounded",
        "partial",
        "encrypted",
        "unreadable",
        "parser_unavailable",
        "parser_error",
        "blocked",
    }
)

NON_FATAL_INSPECTION_STATUSES = frozenset(
    {
        "not_run",
        "inspected",
        "bounded",
        "partial",
    }
)

FATAL_INSPECTION_STATUSES = frozenset(
    {
        "encrypted",
        "unreadable",
        "parser_unavailable",
        "parser_error",
        "blocked",
    }
)

ALLOWED_ROTATIONS = frozenset(
    {
        0,
        90,
        180,
        270,
    }
)

APPROVED_FATAL_ERRORS = {
    "encrypted": frozenset({ENCRYPTED_ERROR}),
    "unreadable": frozenset({UNREADABLE_ERROR}),
    "parser_unavailable": frozenset({PARSER_UNAVAILABLE_ERROR}),
    "parser_error": frozenset({PARSER_ERROR}),
    "blocked": frozenset(
        {
            SAFETY_CHECK_ERROR,
            REQUEST_REQUIRED_ERROR,
        }
    ),
}


@dataclass(frozen=True)
class ControlledPdfStructuralMetadataPageItem:
    page_index: int
    width_points: float
    height_points: float
    rotation_degrees: int
    inspection_status: str


@dataclass(frozen=True)
class ControlledPdfStructuralMetadataResultInput:
    fixture_id: str
    source_label: str
    fixture_path: str
    fixture_type: str
    inspection_mode: str
    inspection_status: str
    encrypted: bool
    page_count: int
    inspected_page_count: int
    page_details_truncated: bool
    page_details: tuple[ControlledPdfStructuralMetadataPageItem, ...]
    max_inspected_pages: int
    inspection_error: str
    evidence_allowed: bool
    notes: str


@dataclass(frozen=True)
class ControlledPdfStructuralMetadataResultContractResult:
    allowed: bool
    reason: str
    fixture_id: str
    source_label: str
    fixture_path: str
    fixture_type: str
    inspection_mode: str
    inspection_status: str
    encrypted: bool
    page_count: int
    inspected_page_count: int
    page_details_truncated: bool
    page_details: tuple[ControlledPdfStructuralMetadataPageItem, ...]
    max_inspected_pages: int
    inspection_error: str
    evidence_allowed: bool
    notes: str


class ControlledPdfStructuralMetadataResultContract:
    @staticmethod
    def evaluate(
        execution_contract_result:
            ControlledPdfStructuralMetadataExecutionContractResult,
        result_input: ControlledPdfStructuralMetadataResultInput,
    ) -> ControlledPdfStructuralMetadataResultContractResult:
        if not isinstance(
            execution_contract_result,
            ControlledPdfStructuralMetadataExecutionContractResult,
        ):
            return _blocked_result(
                reason="execution contract result is required",
            )

        if execution_contract_result.allowed is False:
            return _blocked_from_execution(
                reason="execution contract is not allowed",
                execution_contract_result=execution_contract_result,
            )

        if execution_contract_result.execution_allowed is False:
            return _blocked_from_execution(
                reason="execution approval is required",
                execution_contract_result=execution_contract_result,
            )

        if execution_contract_result.allow_content_extraction is True:
            return _blocked_from_execution(
                reason="content extraction must remain disabled",
                execution_contract_result=execution_contract_result,
            )

        if execution_contract_result.allow_output_file_creation is True:
            return _blocked_from_execution(
                reason="output file creation must remain disabled",
                execution_contract_result=execution_contract_result,
            )

        if execution_contract_result.evidence_allowed is True:
            return _blocked_from_execution(
                reason="upstream evidence flag must remain disabled",
                execution_contract_result=execution_contract_result,
            )

        if (
            execution_contract_result.permitted_fields
            != PERMITTED_STRUCTURAL_FIELDS
        ):
            return _blocked_from_execution(
                reason="upstream permitted_fields are not approved",
                execution_contract_result=execution_contract_result,
            )

        if execution_contract_result.max_inspected_pages <= 0:
            return _blocked_from_execution(
                reason="max_inspected_pages must be greater than zero",
                execution_contract_result=execution_contract_result,
            )

        if (
            execution_contract_result.max_inspected_pages
            > MAX_INSPECTED_PAGES_LIMIT
        ):
            return _blocked_from_execution(
                reason="max_inspected_pages exceeds result contract limit",
                execution_contract_result=execution_contract_result,
            )

        if not isinstance(
            result_input,
            ControlledPdfStructuralMetadataResultInput,
        ):
            return _blocked_from_execution(
                reason="result input is required",
                execution_contract_result=execution_contract_result,
            )

        if result_input.fixture_id != execution_contract_result.fixture_id:
            return _blocked_from_input(
                reason="fixture_id mismatch",
                result_input=result_input,
            )

        if result_input.fixture_path != execution_contract_result.fixture_path:
            return _blocked_from_input(
                reason="fixture_path mismatch",
                result_input=result_input,
            )

        if result_input.fixture_type != execution_contract_result.fixture_type:
            return _blocked_from_input(
                reason="fixture_type mismatch",
                result_input=result_input,
            )

        if (
            result_input.inspection_mode
            != execution_contract_result.inspection_mode
        ):
            return _blocked_from_input(
                reason="inspection_mode mismatch",
                result_input=result_input,
            )

        if (
            result_input.max_inspected_pages
            != execution_contract_result.max_inspected_pages
        ):
            return _blocked_from_input(
                reason="max_inspected_pages mismatch",
                result_input=result_input,
            )

        if not isinstance(result_input.fixture_id, str):
            return _blocked_from_input(
                reason="fixture_id must be a string",
                result_input=result_input,
            )

        if not result_input.fixture_id.strip():
            return _blocked_from_input(
                reason="fixture_id is required",
                result_input=result_input,
            )

        if not isinstance(result_input.source_label, str):
            return _blocked_from_input(
                reason="source_label must be a string",
                result_input=result_input,
            )

        if not result_input.source_label.strip():
            return _blocked_from_input(
                reason="source_label is required",
                result_input=result_input,
            )

        if not isinstance(result_input.fixture_path, str):
            return _blocked_from_input(
                reason="fixture_path must be a string",
                result_input=result_input,
            )

        if not result_input.fixture_path.strip():
            return _blocked_from_input(
                reason="fixture_path is required",
                result_input=result_input,
            )

        if result_input.fixture_type != PRODUCT_SPEC_PDF_FIXTURE_TYPE:
            return _blocked_from_input(
                reason="fixture_type must be product_spec_pdf",
                result_input=result_input,
            )

        if result_input.inspection_mode != STRUCTURAL_METADATA_ONLY_MODE:
            return _blocked_from_input(
                reason="inspection_mode must be structural_metadata_only",
                result_input=result_input,
            )

        if (
            result_input.inspection_status
            not in ALLOWED_INSPECTION_STATUSES
        ):
            return _blocked_from_input(
                reason="unsupported inspection_status",
                result_input=result_input,
            )

        if not isinstance(result_input.encrypted, bool):
            return _blocked_from_input(
                reason="encrypted must be a boolean",
                result_input=result_input,
            )

        if not _is_integer(result_input.page_count):
            return _blocked_from_input(
                reason="page_count must be an integer",
                result_input=result_input,
            )

        if result_input.page_count < 0:
            return _blocked_from_input(
                reason="page_count must not be negative",
                result_input=result_input,
            )

        if not _is_integer(result_input.inspected_page_count):
            return _blocked_from_input(
                reason="inspected_page_count must be an integer",
                result_input=result_input,
            )

        if result_input.inspected_page_count < 0:
            return _blocked_from_input(
                reason="inspected_page_count must not be negative",
                result_input=result_input,
            )

        if not isinstance(result_input.page_details_truncated, bool):
            return _blocked_from_input(
                reason="page_details_truncated must be a boolean",
                result_input=result_input,
            )

        if not isinstance(result_input.page_details, tuple):
            return _blocked_from_input(
                reason="page_details must be a tuple",
                result_input=result_input,
            )

        if not _is_integer(result_input.max_inspected_pages):
            return _blocked_from_input(
                reason="max_inspected_pages must be an integer",
                result_input=result_input,
            )

        if result_input.max_inspected_pages <= 0:
            return _blocked_from_input(
                reason="max_inspected_pages must be greater than zero",
                result_input=result_input,
            )

        if result_input.max_inspected_pages > MAX_INSPECTED_PAGES_LIMIT:
            return _blocked_from_input(
                reason="max_inspected_pages exceeds result contract limit",
                result_input=result_input,
            )

        if not isinstance(result_input.inspection_error, str):
            return _blocked_from_input(
                reason="inspection_error must be a string",
                result_input=result_input,
            )

        if (
            len(result_input.inspection_error)
            > MAX_INSPECTION_ERROR_CHARACTERS
        ):
            return _blocked_from_input(
                reason="inspection_error exceeds result contract limit",
                result_input=result_input,
            )

        if result_input.evidence_allowed is True:
            return _blocked_from_input(
                reason="evidence creation is not allowed by this contract",
                result_input=result_input,
            )

        if not isinstance(result_input.evidence_allowed, bool):
            return _blocked_from_input(
                reason="evidence_allowed must be a boolean",
                result_input=result_input,
            )

        if result_input.notes is None:
            return _blocked_from_input(
                reason="notes is required",
                result_input=result_input,
            )

        if not isinstance(result_input.notes, str):
            return _blocked_from_input(
                reason="notes must be a string",
                result_input=result_input,
            )

        if (
            result_input.inspected_page_count
            != len(result_input.page_details)
        ):
            return _blocked_from_input(
                reason="inspected_page_count must match page_details count",
                result_input=result_input,
            )

        if result_input.inspected_page_count > result_input.page_count:
            return _blocked_from_input(
                reason="inspected_page_count exceeds page_count",
                result_input=result_input,
            )

        if (
            result_input.inspected_page_count
            > result_input.max_inspected_pages
        ):
            return _blocked_from_input(
                reason="inspected_page_count exceeds inspection limit",
                result_input=result_input,
            )

        page_validation_error = _validate_page_details(
            page_details=result_input.page_details,
            page_count=result_input.page_count,
        )

        if page_validation_error is not None:
            return _blocked_from_input(
                reason=page_validation_error,
                result_input=result_input,
            )

        status_validation_error = _validate_status_rules(result_input)

        if status_validation_error is not None:
            return _blocked_from_input(
                reason=status_validation_error,
                result_input=result_input,
            )

        return ControlledPdfStructuralMetadataResultContractResult(
            allowed=True,
            reason="pdf structural metadata result contract allowed",
            fixture_id=result_input.fixture_id,
            source_label=result_input.source_label,
            fixture_path=result_input.fixture_path,
            fixture_type=result_input.fixture_type,
            inspection_mode=result_input.inspection_mode,
            inspection_status=result_input.inspection_status,
            encrypted=result_input.encrypted,
            page_count=result_input.page_count,
            inspected_page_count=result_input.inspected_page_count,
            page_details_truncated=result_input.page_details_truncated,
            page_details=result_input.page_details,
            max_inspected_pages=result_input.max_inspected_pages,
            inspection_error=result_input.inspection_error,
            evidence_allowed=False,
            notes=result_input.notes,
        )


def _validate_page_details(
    *,
    page_details: tuple[ControlledPdfStructuralMetadataPageItem, ...],
    page_count: int,
) -> str | None:
    for page_item in page_details:
        if not isinstance(
            page_item,
            ControlledPdfStructuralMetadataPageItem,
        ):
            return (
                "page_details must contain "
                "ControlledPdfStructuralMetadataPageItem values"
            )

    page_indices = tuple(
        page_item.page_index for page_item in page_details
    )

    if page_indices != tuple(range(len(page_details))):
        return "page indices must form a contiguous zero-based prefix"

    for page_item in page_details:
        if not _is_integer(page_item.page_index):
            return "page_index must be an integer"

        if page_item.page_index < 0:
            return "page_index must not be negative"

        if page_item.page_index >= page_count:
            return "page_index must be less than page_count"

        if (
            page_item.inspection_status
            not in ALLOWED_PAGE_INSPECTION_STATUSES
        ):
            return "unsupported page inspection_status"

        if not _is_finite_number(page_item.width_points):
            return "page width must be a finite numeric value"

        if not _is_finite_number(page_item.height_points):
            return "page height must be a finite numeric value"

        if not _is_integer(page_item.rotation_degrees):
            return "page rotation must be an integer"

        if page_item.inspection_status == "inspected":
            if page_item.width_points <= 0:
                return "inspected page width must be greater than zero"

            if page_item.height_points <= 0:
                return "inspected page height must be greater than zero"

            if page_item.rotation_degrees not in ALLOWED_ROTATIONS:
                return "unsupported page rotation"

        if page_item.inspection_status == "page_error":
            if page_item.width_points != 0:
                return "page_error width must be zero"

            if page_item.height_points != 0:
                return "page_error height must be zero"

            if page_item.rotation_degrees != 0:
                return "page_error rotation must be zero"

    return None


def _validate_status_rules(
    result_input: ControlledPdfStructuralMetadataResultInput,
) -> str | None:
    status = result_input.inspection_status

    if status == "encrypted":
        if result_input.encrypted is False:
            return "encrypted status requires encrypted true"
    elif result_input.encrypted is True:
        return "encrypted must be false for non-encrypted status"

    if status == "not_run":
        if result_input.page_count != 0:
            return "not_run status requires zero page_count"

        if result_input.inspected_page_count != 0:
            return "not_run status requires zero inspected_page_count"

        if result_input.page_details:
            return "not_run status requires empty page_details"

        if result_input.page_details_truncated is True:
            return "not_run status must not be truncated"

        if result_input.inspection_error != "":
            return "not_run status requires empty inspection_error"

        return None

    if status in {"inspected", "bounded", "partial"}:
        expected_count = min(
            result_input.page_count,
            result_input.max_inspected_pages,
        )

        if result_input.inspected_page_count != expected_count:
            return (
                "successful status requires the full bounded page prefix"
            )

        expected_truncation = (
            result_input.page_count
            > result_input.max_inspected_pages
        )

        if result_input.page_details_truncated != expected_truncation:
            return "page_details_truncated does not match page boundary"

    if status == "inspected":
        if (
            result_input.page_count
            > result_input.max_inspected_pages
        ):
            return "inspected status must not exceed page limit"

        if any(
            page.inspection_status != "inspected"
            for page in result_input.page_details
        ):
            return "inspected status requires all pages inspected"

        if result_input.inspection_error != "":
            return "inspected status requires empty inspection_error"

        return None

    if status == "bounded":
        if (
            result_input.page_count
            <= result_input.max_inspected_pages
        ):
            return "bounded status requires page_count above page limit"

        if any(
            page.inspection_status != "inspected"
            for page in result_input.page_details
        ):
            return "bounded status requires all bounded pages inspected"

        if result_input.inspection_error != "":
            return "bounded status requires empty inspection_error"

        return None

    if status == "partial":
        if result_input.page_count <= 0:
            return "partial status requires positive page_count"

        page_statuses = {
            page.inspection_status
            for page in result_input.page_details
        }

        if page_statuses != {"inspected", "page_error"}:
            return "partial status requires mixed page statuses"

        if result_input.inspection_error != PARTIAL_INSPECTION_ERROR:
            return "partial status requires approved inspection_error"

        return None

    if status in FATAL_INSPECTION_STATUSES:
        if result_input.page_count != 0:
            return "fatal status requires zero page_count"

        if result_input.inspected_page_count != 0:
            return "fatal status requires zero inspected_page_count"

        if result_input.page_details:
            return "fatal status requires empty page_details"

        if result_input.page_details_truncated is True:
            return "fatal status must not be truncated"

        if not result_input.inspection_error.strip():
            return "fatal status requires inspection_error"

        approved_errors = APPROVED_FATAL_ERRORS[status]

        if result_input.inspection_error not in approved_errors:
            return "fatal status requires approved inspection_error"

        return None

    return "unsupported inspection_status"


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_finite_number(value: object) -> bool:
    if isinstance(value, bool):
        return False

    if not isinstance(value, (int, float)):
        return False

    return isfinite(value)


def _blocked_from_execution(
    *,
    reason: str,
    execution_contract_result:
        ControlledPdfStructuralMetadataExecutionContractResult,
) -> ControlledPdfStructuralMetadataResultContractResult:
    return _blocked_result(
        reason=reason,
        fixture_id=execution_contract_result.fixture_id,
        fixture_path=execution_contract_result.fixture_path,
        fixture_type=execution_contract_result.fixture_type,
        inspection_mode=execution_contract_result.inspection_mode,
        max_inspected_pages=(
            execution_contract_result.max_inspected_pages
        ),
        evidence_allowed=False,
        notes=execution_contract_result.notes,
    )


def _blocked_from_input(
    *,
    reason: str,
    result_input: ControlledPdfStructuralMetadataResultInput,
) -> ControlledPdfStructuralMetadataResultContractResult:
    page_details = (
        result_input.page_details
        if isinstance(result_input.page_details, tuple)
        else ()
    )

    return _blocked_result(
        reason=reason,
        fixture_id=(
            result_input.fixture_id
            if isinstance(result_input.fixture_id, str)
            else ""
        ),
        source_label=(
            result_input.source_label
            if isinstance(result_input.source_label, str)
            else ""
        ),
        fixture_path=(
            result_input.fixture_path
            if isinstance(result_input.fixture_path, str)
            else ""
        ),
        fixture_type=(
            result_input.fixture_type
            if isinstance(result_input.fixture_type, str)
            else ""
        ),
        inspection_mode=(
            result_input.inspection_mode
            if isinstance(result_input.inspection_mode, str)
            else ""
        ),
        inspection_status=(
            result_input.inspection_status
            if isinstance(result_input.inspection_status, str)
            else ""
        ),
        encrypted=(
            result_input.encrypted
            if isinstance(result_input.encrypted, bool)
            else False
        ),
        page_count=(
            result_input.page_count
            if _is_integer(result_input.page_count)
            else 0
        ),
        inspected_page_count=(
            result_input.inspected_page_count
            if _is_integer(result_input.inspected_page_count)
            else 0
        ),
        page_details_truncated=(
            result_input.page_details_truncated
            if isinstance(result_input.page_details_truncated, bool)
            else False
        ),
        page_details=page_details,
        max_inspected_pages=(
            result_input.max_inspected_pages
            if _is_integer(result_input.max_inspected_pages)
            else 0
        ),
        inspection_error=(
            result_input.inspection_error
            if isinstance(result_input.inspection_error, str)
            else ""
        ),
        evidence_allowed=False,
        notes=(
            result_input.notes
            if isinstance(result_input.notes, str)
            else ""
        ),
    )


def _blocked_result(
    *,
    reason: str,
    fixture_id: str = "",
    source_label: str = "",
    fixture_path: str = "",
    fixture_type: str = "",
    inspection_mode: str = "",
    inspection_status: str = "",
    encrypted: bool = False,
    page_count: int = 0,
    inspected_page_count: int = 0,
    page_details_truncated: bool = False,
    page_details: tuple[ControlledPdfStructuralMetadataPageItem, ...] = (),
    max_inspected_pages: int = 0,
    inspection_error: str = "",
    evidence_allowed: bool = False,
    notes: str = "",
) -> ControlledPdfStructuralMetadataResultContractResult:
    return ControlledPdfStructuralMetadataResultContractResult(
        allowed=False,
        reason=reason,
        fixture_id=fixture_id,
        source_label=source_label,
        fixture_path=fixture_path,
        fixture_type=fixture_type,
        inspection_mode=inspection_mode,
        inspection_status=inspection_status,
        encrypted=encrypted,
        page_count=page_count,
        inspected_page_count=inspected_page_count,
        page_details_truncated=page_details_truncated,
        page_details=page_details,
        max_inspected_pages=max_inspected_pages,
        inspection_error=inspection_error,
        evidence_allowed=False,
        notes=notes,
    )