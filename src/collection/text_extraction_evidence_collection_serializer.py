import json
from typing import Any

from collection.text_extraction_evidence_collection import (
    TextExtractionEvidenceCollection,
)


def to_json(
    collection: TextExtractionEvidenceCollection,
) -> str:
    return json.dumps(
        to_dict(collection),
        indent=2,
        ensure_ascii=False,
    )


def to_dict(
    collection: TextExtractionEvidenceCollection,
) -> dict[str, Any]:
    return {
        "evidences": [
            {
                "source_path": evidence.source_path,
                "content": evidence.content,
                "size_bytes": evidence.size_bytes,
            }
            for evidence in collection.evidences
        ],
    }
