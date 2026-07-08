from dataclasses import dataclass


REQUIRED_STRING_FIELDS = (
    "source_path",
    "source_document",
    "title",
    "content",
)


@dataclass(frozen=True)
class OfficialKnowledgeSourceItem:
    knowledge_id: str | None
    source_path: str
    source_document: str
    source_section: str | None
    source_page: int | None
    title: str
    content: str
    status: str | None
    governance_level: str | None
    pdf_evidence_index: int | None
    extraction_index: int | None

    def __post_init__(self) -> None:
        for field_name in REQUIRED_STRING_FIELDS:
            value = getattr(self, field_name)

            if not isinstance(value, str) or value.strip() == "":
                raise ValueError(
                    f"{field_name} must be a non-empty string."
                )
