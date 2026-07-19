import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from rie.ingestion.controlled_source_admission_job_contract import (
    CONTROLLED_SOURCE_ADMISSION_CHECKSUM_ALGORITHM,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    CONTROLLED_SOURCE_ADMISSION_EXECUTION_POLICY_ID,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    CONTROLLED_SOURCE_ADMISSION_EXECUTION_POLICY_VERSION,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    CONTROLLED_SOURCE_ADMISSION_JOB_CONTRACT_VERSION,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    ControlledSourceAdmissionIssueCode,
)
from rie.ingestion.controlled_source_admission_job_contract import IngestionJob
from rie.ingestion.controlled_source_admission_job_contract import (
    admitted_result,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    derive_ingestion_job_id,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    rejected_result,
)
from rie.ingestion.create_controlled_ingestion_job import main
from rie.ingestion.create_controlled_ingestion_job import (
    render_controlled_source_admission_report,
)


def _write_case(tmp_path, *, source_id="SRC-SYNTHETIC-001"):
    source_path = tmp_path / "synthetic-source.pdf"
    source_path.write_bytes(b"synthetic CLI source bytes")
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "official_sources": [
                    {
                        "source_id": source_id,
                        "source_path": source_path.name,
                        "source_type": "pdf",
                        "document_classification": "project_rulebook",
                        "authority_status": "official",
                        "lifecycle_status": "locked",
                        "evidence_eligibility": "eligible",
                        "version": "v1.0",
                        "review_notes": "Synthetic temporary CLI data.",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    return source_path, registry_path


def _job(tmp_path):
    values = {
        "contract_version": (
            CONTROLLED_SOURCE_ADMISSION_JOB_CONTRACT_VERSION
        ),
        "source_id": "SRC-SYNTHETIC-001",
        "source_path": str((tmp_path / "source.pdf").resolve()),
        "expected_source_type": "pdf",
        "authority_snapshot": "official",
        "lifecycle_snapshot": "locked",
        "eligibility_snapshot": "eligible",
        "source_checksum_algorithm": (
            CONTROLLED_SOURCE_ADMISSION_CHECKSUM_ALGORITHM
        ),
        "source_checksum": "a" * 64,
        "execution_policy_id": (
            CONTROLLED_SOURCE_ADMISSION_EXECUTION_POLICY_ID
        ),
        "execution_policy_version": (
            CONTROLLED_SOURCE_ADMISSION_EXECUTION_POLICY_VERSION
        ),
        "output_location": str((tmp_path / "job.json").resolve()),
    }
    return IngestionJob(
        job_id=derive_ingestion_job_id(**values),
        **values,
    )


def test_admitted_flow_exits_zero(tmp_path, capsys):
    _, registry_path = _write_case(tmp_path)
    output_path = tmp_path / "job.json"

    exit_code = main(
        [
            str(registry_path),
            "SRC-SYNTHETIC-001",
            str(output_path),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "status: admitted" in captured.out
    assert captured.err == ""
    assert output_path.exists()


def test_deterministic_rejection_exits_one(tmp_path, capsys):
    _, registry_path = _write_case(tmp_path)
    output_path = tmp_path / "job.json"

    exit_code = main(
        [
            str(registry_path),
            "SRC-UNKNOWN",
            str(output_path),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "status: rejected" in captured.out
    assert "issue_code: source_id_unknown" in captured.out
    assert captured.err == ""
    assert not output_path.exists()


def test_usage_error_exits_two():
    with pytest.raises(SystemExit) as exc_info:
        main([])

    assert exc_info.value.code == 2


def test_admitted_report_field_order_is_exact(tmp_path):
    report = render_controlled_source_admission_report(
        admitted_result(_job(tmp_path))
    )
    keys = [
        line.split(":", 1)[0]
        for line in report.splitlines()[1:]
    ]

    assert keys == [
        "contract_version",
        "status",
        "job_id",
        "source_id",
        "source_path",
        "expected_source_type",
        "source_checksum_algorithm",
        "source_checksum",
        "execution_policy",
        "output_location",
        "manifest_written",
    ]


def test_rejected_report_field_order_is_exact():
    report = render_controlled_source_admission_report(
        rejected_result(
            ControlledSourceAdmissionIssueCode.REGISTRY_INVALID,
            "Official Source registry is invalid.",
            upstream_issue_code="invalid_json",
        )
    )
    keys = [
        line.split(":", 1)[0]
        for line in report.splitlines()[1:]
    ]

    assert keys == [
        "contract_version",
        "status",
        "issue_code",
        "upstream_issue_code",
        "issue_message",
    ]


def test_no_traceback_or_raw_exception_text_is_printed(tmp_path, capsys):
    _, registry_path = _write_case(tmp_path)

    exit_code = main(
        [
            str(registry_path),
            "SRC-UNKNOWN",
            str(tmp_path / "job.json"),
        ]
    )
    output = capsys.readouterr()

    assert exit_code == 1
    assert "Traceback" not in output.out
    assert "Exception" not in output.out
    assert "synthetic" not in output.out.lower()
    assert output.err == ""


def test_module_runs_without_root_cli_routing_change(tmp_path):
    _, registry_path = _write_case(tmp_path)
    output_path = tmp_path / "job.json"
    repo_root = Path(__file__).resolve().parents[2]
    environment = os.environ.copy()
    source_root = str(repo_root / "src")
    existing_pythonpath = environment.get("PYTHONPATH", "")
    environment["PYTHONPATH"] = (
        source_root
        if existing_pythonpath == ""
        else source_root + os.pathsep + existing_pythonpath
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-S",
            "-m",
            "rie.ingestion.create_controlled_ingestion_job",
            str(registry_path),
            "SRC-SYNTHETIC-001",
            str(output_path),
        ],
        cwd=repo_root,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert "status: admitted" in completed.stdout
    assert completed.stderr == ""
    assert output_path.exists()
