from __future__ import annotations

import argparse

from rie.ingestion.controlled_source_admission_job_contract import (
    ControlledSourceAdmissionRequest,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    ControlledSourceAdmissionResult,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    ControlledSourceAdmissionStatus,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    ControlledSourceAdmissionIssueCode,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    rejected_result,
)
from rie.ingestion.controlled_source_admission_service import (
    admit_controlled_source,
)


def render_controlled_source_admission_report(
    result: ControlledSourceAdmissionResult,
) -> str:
    if not isinstance(result, ControlledSourceAdmissionResult):
        raise TypeError(
            "result must be ControlledSourceAdmissionResult."
        )

    lines = [
        "Controlled Source Admission Report",
        f"contract_version: {result.contract_version}",
        f"status: {result.status.value}",
    ]

    if result.status is ControlledSourceAdmissionStatus.ADMITTED:
        job = result.job
        assert job is not None
        lines.extend(
            [
                f"job_id: {job.job_id}",
                f"source_id: {job.source_id}",
                f"source_path: {job.source_path}",
                f"expected_source_type: {job.expected_source_type}",
                (
                    "source_checksum_algorithm: "
                    f"{job.source_checksum_algorithm}"
                ),
                f"source_checksum: {job.source_checksum}",
                (
                    "execution_policy: "
                    f"{job.execution_policy_id}@"
                    f"{job.execution_policy_version}"
                ),
                f"output_location: {job.output_location}",
                "manifest_written: true",
            ]
        )
    else:
        issue = result.issue
        assert issue is not None
        lines.extend(
            [
                f"issue_code: {issue.code.value}",
                (
                    "upstream_issue_code: "
                    f"{issue.upstream_issue_code or ''}"
                ),
                f"issue_message: {issue.message}",
            ]
        )

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Create one controlled ingestion job.",
    )
    parser.add_argument("registry_json_path")
    parser.add_argument("source_id")
    parser.add_argument("output_json_path")

    args = parser.parse_args(argv)

    try:
        request = ControlledSourceAdmissionRequest(
            registry_path=args.registry_json_path,
            source_id=args.source_id,
            output_location=args.output_json_path,
        )
        result = admit_controlled_source(request)
    except (TypeError, ValueError):
        result = rejected_result(
            ControlledSourceAdmissionIssueCode.JOB_VALIDATION_FAILED,
            "Controlled admission request is invalid.",
        )

    print(render_controlled_source_admission_report(result))

    if result.status is ControlledSourceAdmissionStatus.ADMITTED:
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = (
    "main",
    "render_controlled_source_admission_report",
)
