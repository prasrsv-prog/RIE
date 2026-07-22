import json

from rie.operator.operator_contract import ExitCode
from rie.operator.operator_contract import OperatorStatus
from rie.operator.operator_contract import make_result
from rie.operator.operator_result import render_human
from rie.operator.operator_result import render_json
from rie.operator.operator_result import to_dict


def test_human_and_json_preserve_equivalent_semantics() -> None:
    result = make_result(
        command="evidence inspect",
        status=OperatorStatus.SUCCEEDED,
        exit_code=ExitCode.SUCCESS,
        issue_code="",
        message="inspected",
        dry_run=False,
        identifiers={"item_count": 2},
        provenance={"input_path": "artifact.json"},
        audit={"audit_id": "abc", "persisted": "true"},
        outputs={"output_path": ""},
        recovery={},
    )
    payload = json.loads(render_json(result))
    human = render_human(result)
    assert payload == to_dict(result)
    for value in (
        payload["command"],
        payload["status"],
        str(payload["exit_code"]),
        payload["message"],
        payload["identifiers"]["item_count"],
        payload["audit"]["audit_id"],
    ):
        assert value in human
