from dataclasses import FrozenInstanceError

import pytest

from rie.operator.operator_contract import ExitCode
from rie.operator.operator_contract import OperatorRequest
from rie.operator.operator_contract import OperatorStatus
from rie.operator.operator_contract import REQUIRED_COMMANDS
from rie.operator.operator_contract import make_result


def test_required_command_contract_is_exact() -> None:
    assert REQUIRED_COMMANDS == (
        "registry validate",
        "source inspect",
        "ingest pdf",
        "evidence build",
        "evidence inspect",
        "knowledge build",
        "knowledge inspect",
        "prompt-candidate build",
        "audit job",
        "export",
    )
    assert [value.value for value in ExitCode] == list(range(9))


def test_request_and_result_are_immutable() -> None:
    request = OperatorRequest(command="registry validate")
    result = make_result(
        command=request.command,
        status=OperatorStatus.SUCCEEDED,
        exit_code=ExitCode.SUCCESS,
        issue_code="",
        message="ok",
        dry_run=False,
    )
    with pytest.raises(FrozenInstanceError):
        request.command = "export"
    with pytest.raises(FrozenInstanceError):
        result.message = "changed"
