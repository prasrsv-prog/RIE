from dataclasses import dataclass


@dataclass(frozen=True)
class OfficialKnowledgeItem:
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
    official_knowledge_index: int
