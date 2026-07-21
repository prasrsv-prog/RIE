from __future__ import annotations

import json
import os
from pathlib import Path

from rie.knowledge_repository import (
    SqliteGovernedKnowledgeRepository,
    calculate_governed_knowledge_repository_payload_digest,
    deserialize_governed_knowledge_repository_payload,
    serialize_governed_knowledge_repository_payload,
)
from test_sqlite_governed_knowledge_repository import (
    build_fixture_bundle,
    build_transition_request,
)


def test_canonical_payload_round_trip_and_determinism(
    tmp_path: Path,
) -> None:
    bundle = build_fixture_bundle()
    governed = bundle["governed"]
    first = serialize_governed_knowledge_repository_payload(
        governed
    )
    second = serialize_governed_knowledge_repository_payload(
        governed
    )
    assert first == second
    assert first.endswith(b"}")
    assert not first.endswith(b"\n")
    restored = (
        deserialize_governed_knowledge_repository_payload(
            first
        )
    )
    assert restored == governed
    assert (
        calculate_governed_knowledge_repository_payload_digest(
            governed
        )
        == calculate_governed_knowledge_repository_payload_digest(
            restored
        )
    )


def test_fixed_repository_fixture_fingerprints(
    tmp_path: Path,
) -> None:
    bundle = build_fixture_bundle()
    repository = SqliteGovernedKnowledgeRepository(
        tmp_path / "fixture.sqlite3"
    )
    initial = repository.persist_initial(
        bundle["initial_request"]
    )
    transition = repository.append_lifecycle_transition(
        build_transition_request(
            initial,
            bundle["next_lifecycle"],
        )
    )
    initial_payload = (
        serialize_governed_knowledge_repository_payload(
            initial.governed_knowledge
        )
    )
    initial_lifecycle_payload = (
        serialize_governed_knowledge_repository_payload(
            initial.lifecycle_interpretation_result
        )
    )
    transition_lifecycle_payload = (
        serialize_governed_knowledge_repository_payload(
            transition.lifecycle_interpretation_result
        )
    )
    fingerprints = {
        "initial_governed_payload_bytes": len(
            initial_payload
        ),
        "initial_governed_payload_digest": (
            calculate_governed_knowledge_repository_payload_digest(
                initial.governed_knowledge
            )
        ),
        "initial_lifecycle_payload_bytes": len(
            initial_lifecycle_payload
        ),
        "initial_lifecycle_payload_digest": (
            initial.revision.lifecycle_interpretation_result_payload_digest
        ),
        "lineage_record_id": (
            initial.lineage_record.lineage_record_id
        ),
        "initial_revision_id": initial.revision.revision_id,
        "initial_audit_id": initial.audit_record.audit_id,
        "transition_lifecycle_payload_bytes": len(
            transition_lifecycle_payload
        ),
        "transition_lifecycle_payload_digest": (
            transition.revision.lifecycle_interpretation_result_payload_digest
        ),
        "transition_record_id": (
            transition.transition_record.transition_record_id
        ),
        "transition_revision_id": (
            transition.revision.revision_id
        ),
        "transition_audit_id": (
            transition.audit_record.audit_id
        ),
        "initial_replay_status": (
            repository.persist_initial(
                bundle["initial_request"]
            ).status
        ),
        "transition_replay_status": (
            repository.append_lifecycle_transition(
                build_transition_request(
                    initial,
                    bundle["next_lifecycle"],
                )
            ).status
        ),
    }
    assert fingerprints["initial_replay_status"] == (
        "unchanged_exact_replay"
    )
    assert fingerprints["transition_replay_status"] == (
        "unchanged_exact_replay"
    )
    for key in (
        "initial_governed_payload_digest",
        "initial_lifecycle_payload_digest",
        "transition_lifecycle_payload_digest",
    ):
        assert len(fingerprints[key]) == 64

    output_path = os.environ.get(
        "PR054D_FIXTURE_OUTPUT"
    )
    if output_path:
        Path(output_path).write_text(
            json.dumps(
                fingerprints,
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n",
            encoding="ascii",
            newline="\n",
        )
