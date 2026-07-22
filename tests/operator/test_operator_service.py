import json

from rie.operator.operator_configuration import load_configuration
from rie.operator.operator_contract import OperatorRequest
from rie.operator.operator_contract import OperatorStatus
from rie.operator.operator_contract import freeze_mapping
from rie.operator.operator_service import OperatorService


def _service(tmp_path):
    config_path = tmp_path / "operator.json"
    config_path.write_text(
        json.dumps(
            {
                "schema_version": "rie_operator_configuration_v1",
                "workspace_path": "workspace",
                "audit_path": "workspace/audit.jsonl",
            }
        ),
        encoding="ascii",
    )
    return OperatorService(load_configuration(config_path))


def test_evidence_to_prompt_candidate_pipeline_is_idempotent(tmp_path) -> None:
    extraction = tmp_path / "extraction.json"
    extraction.write_text(
        json.dumps(
            {
                "schema_version": "rie_pdf_ingestion_artifact_v1",
                "page_extractions": [
                    {
                        "source_path": "sample.pdf",
                        "size_bytes": 100,
                        "page_number": 1,
                        "extraction_index": 0,
                        "extraction_method": "embedded_text",
                        "content": "Controlled sample knowledge.",
                        "warnings": [],
                    }
                ],
            }
        ),
        encoding="ascii",
    )
    service = _service(tmp_path)
    evidence = tmp_path / "evidence.json"
    knowledge = tmp_path / "knowledge.json"
    prompt = tmp_path / "prompt.json"
    result = service.execute(
        OperatorRequest(
            command="evidence build",
            arguments=freeze_mapping({"input": extraction}),
            output_path=str(evidence),
        )
    )
    assert result.status is OperatorStatus.SUCCEEDED
    result = service.execute(
        OperatorRequest(
            command="knowledge build",
            arguments=freeze_mapping({"input": evidence}),
            output_path=str(knowledge),
        )
    )
    assert result.status is OperatorStatus.SUCCEEDED
    result = service.execute(
        OperatorRequest(
            command="prompt-candidate build",
            arguments=freeze_mapping({"input": knowledge}),
            output_path=str(prompt),
        )
    )
    assert result.status is OperatorStatus.SUCCEEDED
    rerun = service.execute(
        OperatorRequest(
            command="prompt-candidate build",
            arguments=freeze_mapping({"input": knowledge}),
            output_path=str(prompt),
        )
    )
    assert rerun.status is OperatorStatus.REUSED_EXISTING
    payload = json.loads(prompt.read_text(encoding="ascii"))
    assert payload["prompt_candidates"][0]["content"] == "Controlled sample knowledge."


def test_dry_run_does_not_create_output(tmp_path) -> None:
    extraction = tmp_path / "extraction.json"
    extraction.write_text('{"page_extractions":[]}', encoding="ascii")
    output = tmp_path / "evidence.json"
    result = _service(tmp_path).execute(
        OperatorRequest(
            command="evidence build",
            arguments=freeze_mapping({"input": extraction}),
            output_path=str(output),
            dry_run=True,
        )
    )
    assert result.status is OperatorStatus.DRY_RUN_VALID
    assert not output.exists()
def test_configuration_is_explicit_and_rejects_unknown_fields(tmp_path) -> None:
    from rie.operator.operator_configuration import OperatorConfigurationError
    from rie.operator.operator_configuration import load_configuration
    config_path = tmp_path / "operator.json"
    config_path.write_text(
        '{"schema_version":"rie_operator_configuration_v1",'
        '"workspace_path":"workspace","audit_path":"workspace/audit.jsonl"}',
        encoding="ascii",
    )
    config = load_configuration(config_path)
    assert len(config.digest) == 64
    assert not config.workspace_path.exists()
    config_path.write_text(
        '{"schema_version":"rie_operator_configuration_v1",'
        '"workspace_path":"workspace","audit_path":"workspace/audit.jsonl",'
        '"secret":"x"}',
        encoding="ascii",
    )
    import pytest
    with pytest.raises(OperatorConfigurationError):
        load_configuration(config_path)
