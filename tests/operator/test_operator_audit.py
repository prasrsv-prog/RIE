import json

from rie.operator.operator_audit import find_audit
from rie.operator.operator_audit import persist_audit
from rie.operator.operator_audit import read_audit_records
from rie.operator.operator_configuration import load_configuration
from rie.operator.operator_contract import ExitCode
from rie.operator.operator_contract import OperatorRequest
from rie.operator.operator_contract import OperatorStatus
from rie.operator.operator_contract import make_result


def test_audit_records_every_invocation_and_links_rerun(tmp_path) -> None:
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
    config = load_configuration(config_path)
    request = OperatorRequest(command="registry validate")
    result = make_result(
        command=request.command,
        status=OperatorStatus.SUCCEEDED,
        exit_code=ExitCode.SUCCESS,
        issue_code="",
        message="ok",
        dry_run=False,
    )
    first = persist_audit(request=request, configuration=config, result=result)
    second = persist_audit(request=request, configuration=config, result=result)
    records = tuple(read_audit_records(config.audit_path))
    assert len(records) == 2
    assert first["operation_id"] == second["operation_id"]
    assert second["prior_audit_id"] == first["audit_id"]
    assert find_audit(config.audit_path, second["audit_id"]) == records[1]
