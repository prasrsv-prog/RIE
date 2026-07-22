"""Single installed Gate 11 RIE console."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from rie.operator.operator_configuration import OperatorConfigurationError
from rie.operator.operator_configuration import load_configuration
from rie.operator.operator_contract import ExitCode
from rie.operator.operator_contract import OperatorRequest
from rie.operator.operator_contract import OperatorStatus
from rie.operator.operator_contract import PACKAGE_VERSION
from rie.operator.operator_contract import freeze_mapping
from rie.operator.operator_contract import make_result
from rie.operator.operator_recovery import recovery_for
from rie.operator.operator_result import render
from rie.operator.operator_service import OperatorService


class OperatorArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        raise SystemExit(f"{self.prog}: error: {message}")


def build_parser() -> argparse.ArgumentParser:
    parser = OperatorArgumentParser(prog="rie", description="RIE Core v1 operator console")
    parser.add_argument("--version", action="version", version=f"rie {PACKAGE_VERSION}")
    parser.add_argument("--config", help="Explicit operator configuration JSON path.")
    parser.add_argument(
        "--format",
        choices=("human", "json"),
        default="human",
        dest="output_format",
    )
    groups = parser.add_subparsers(dest="group", required=True)

    registry = groups.add_parser("registry")
    registry_commands = registry.add_subparsers(dest="action", required=True)
    registry_validate = registry_commands.add_parser("validate")
    registry_validate.add_argument("registry")
    registry_validate.set_defaults(command="registry validate")

    source = groups.add_parser("source")
    source_commands = source.add_subparsers(dest="action", required=True)
    source_inspect = source_commands.add_parser("inspect")
    source_inspect.add_argument("registry")
    source_inspect.add_argument("source_id")
    source_inspect.set_defaults(command="source inspect")

    ingest = groups.add_parser("ingest")
    ingest_commands = ingest.add_subparsers(dest="action", required=True)
    ingest_pdf = ingest_commands.add_parser("pdf")
    ingest_pdf.add_argument("registry")
    ingest_pdf.add_argument("source_id")
    _add_output_and_dry_run(ingest_pdf)
    ingest_pdf.set_defaults(command="ingest pdf")

    evidence = groups.add_parser("evidence")
    evidence_commands = evidence.add_subparsers(dest="action", required=True)
    evidence_build = evidence_commands.add_parser("build")
    evidence_build.add_argument("input")
    _add_output_and_dry_run(evidence_build)
    evidence_build.set_defaults(command="evidence build")
    evidence_inspect = evidence_commands.add_parser("inspect")
    evidence_inspect.add_argument("input")
    evidence_inspect.set_defaults(command="evidence inspect")

    knowledge = groups.add_parser("knowledge")
    knowledge_commands = knowledge.add_subparsers(dest="action", required=True)
    knowledge_build = knowledge_commands.add_parser("build")
    knowledge_build.add_argument("input")
    _add_output_and_dry_run(knowledge_build)
    knowledge_build.set_defaults(command="knowledge build")
    knowledge_inspect = knowledge_commands.add_parser("inspect")
    knowledge_inspect.add_argument("input")
    knowledge_inspect.set_defaults(command="knowledge inspect")

    prompt_candidate = groups.add_parser("prompt-candidate")
    prompt_commands = prompt_candidate.add_subparsers(dest="action", required=True)
    prompt_build = prompt_commands.add_parser("build")
    prompt_build.add_argument("input")
    _add_output_and_dry_run(prompt_build)
    prompt_build.set_defaults(command="prompt-candidate build")

    audit = groups.add_parser("audit")
    audit_commands = audit.add_subparsers(dest="action", required=True)
    audit_job = audit_commands.add_parser("job")
    audit_job.add_argument("audit_id")
    audit_job.set_defaults(command="audit job")

    export = groups.add_parser("export")
    export.add_argument("input")
    export.add_argument("--output", required=True)
    export.add_argument("--overwrite", action="store_true")
    export.add_argument("--dry-run", action="store_true")
    export.set_defaults(command="export")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    try:
        namespace = parser.parse_args(argv)
    except SystemExit as exc:
        if isinstance(exc.code, int):
            return exc.code
        print(str(exc.code), file=sys.stderr)
        return int(ExitCode.CLI_USAGE_INVALID)

    command = namespace.command
    output_format = namespace.output_format
    if not namespace.config:
        result = make_result(
            command=command,
            status=OperatorStatus.REJECTED,
            exit_code=ExitCode.CONFIGURATION_INVALID,
            issue_code="CONFIGURATION_INVALID",
            message="An explicit --config path is required.",
            dry_run=bool(getattr(namespace, "dry_run", False)),
            audit={"persisted": "false", "preview": "configuration unavailable"},
            recovery=recovery_for("CONFIGURATION_INVALID"),
        )
        print(render(result, output_format))
        return int(result.exit_code)

    try:
        configuration = load_configuration(namespace.config)
    except OperatorConfigurationError as exc:
        result = make_result(
            command=command,
            status=OperatorStatus.REJECTED,
            exit_code=ExitCode.CONFIGURATION_INVALID,
            issue_code="CONFIGURATION_INVALID",
            message=str(exc),
            dry_run=bool(getattr(namespace, "dry_run", False)),
            audit={"persisted": "false", "preview": "configuration invalid"},
            recovery=recovery_for("CONFIGURATION_INVALID"),
        )
        print(render(result, output_format))
        return int(result.exit_code)

    arguments = {
        key: value
        for key, value in vars(namespace).items()
        if key
        not in {
            "command",
            "config",
            "output_format",
            "output",
            "dry_run",
            "group",
            "action",
        }
        and value is not None
    }
    request = OperatorRequest(
        command=command,
        arguments=freeze_mapping(arguments),
        output_format=output_format,
        output_path=getattr(namespace, "output", None),
        dry_run=bool(getattr(namespace, "dry_run", False)),
    )
    result = OperatorService(configuration).execute(request)
    print(render(result, output_format))
    return int(result.exit_code)


def _add_output_and_dry_run(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output", required=True)
    parser.add_argument("--dry-run", action="store_true")


__all__ = ("OperatorArgumentParser", "build_parser", "main")
