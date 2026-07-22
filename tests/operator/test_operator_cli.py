import json

from rie.operator.operator_cli import build_parser
from rie.operator.operator_cli import main


def test_parser_exposes_all_required_commands() -> None:
    parser = build_parser()
    help_text = parser.format_help()
    for group in (
        "registry",
        "source",
        "ingest",
        "evidence",
        "knowledge",
        "prompt-candidate",
        "audit",
        "export",
    ):
        assert group in help_text


def test_cli_rejects_missing_explicit_configuration(capsys) -> None:
    exit_code = main(["--format", "json", "registry", "validate", "registry.json"])
    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 3
    assert payload["status"] == "REJECTED"
    assert payload["issue_code"] == "CONFIGURATION_INVALID"
