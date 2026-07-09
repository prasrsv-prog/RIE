from dataclasses import dataclass
from enum import Enum


class SourceType(Enum):
    PDF = "pdf"
    MARKDOWN = "markdown"
    DOCX = "docx"
    IMAGE = "image"
    SPREADSHEET = "spreadsheet"
    DIRECTORY = "directory"
    UNKNOWN = "unknown"


class DocumentClassification(Enum):
    OFFICIAL_KNOWLEDGE_BASE = "official_knowledge_base"
    CREATIVE_LOGIC_SPECIFICATION = "creative_logic_specification"
    BRAND_KNOWLEDGE_SPECIFICATION = "brand_knowledge_specification"
    MASTER_ASSET_LIBRARY = "master_asset_library"
    PROJECT_RULEBOOK = "project_rulebook"
    ARCHITECTURE_BASELINE = "architecture_baseline"
    CONTINUITY_PACK = "continuity_pack"
    PROJECT_VISION_KIT = "project_vision_kit"
    WORKING_NOTE = "working_note"
    UNKNOWN = "unknown"


class AuthorityStatus(Enum):
    OFFICIAL = "official"
    SOURCE_OF_TRUTH_CANDIDATE = "source_of_truth_candidate"
    REFERENCE = "reference"
    DRAFT = "draft"
    UNKNOWN = "unknown"


class LifecycleStatus(Enum):
    ACTIVE = "active"
    LOCKED = "locked"
    FINAL = "final"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"
    UNKNOWN = "unknown"


class EvidenceEligibility(Enum):
    ELIGIBLE = "eligible"
    ELIGIBLE_WITH_REVIEW = "eligible_with_review"
    NOT_ELIGIBLE = "not_eligible"
    UNKNOWN = "unknown"


REQUIRED_STRING_FIELDS = (
    "source_id",
    "source_path",
)

OPTIONAL_STRING_FIELDS = (
    "version",
    "review_notes",
)

ENUM_FIELDS = (
    ("source_type", SourceType),
    ("document_classification", DocumentClassification),
    ("authority_status", AuthorityStatus),
    ("lifecycle_status", LifecycleStatus),
    ("evidence_eligibility", EvidenceEligibility),
)


@dataclass(frozen=True)
class OfficialSource:
    source_id: str
    source_path: str
    source_type: SourceType
    document_classification: DocumentClassification
    authority_status: AuthorityStatus
    lifecycle_status: LifecycleStatus
    evidence_eligibility: EvidenceEligibility
    version: str | None
    review_notes: str | None

    def __post_init__(self) -> None:
        for field_name in REQUIRED_STRING_FIELDS:
            value = getattr(self, field_name)

            if not isinstance(value, str) or value.strip() == "":
                raise ValueError(
                    f"{field_name} must be a non-empty string."
                )

        for field_name in OPTIONAL_STRING_FIELDS:
            value = getattr(self, field_name)

            if value is not None and not isinstance(value, str):
                raise ValueError(f"{field_name} must be a string or None.")

        for field_name, enum_type in ENUM_FIELDS:
            value = getattr(self, field_name)

            if not isinstance(value, enum_type):
                raise ValueError(f"{field_name} must be {enum_type.__name__}.")
