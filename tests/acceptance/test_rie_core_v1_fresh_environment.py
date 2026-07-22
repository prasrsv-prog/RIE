from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


def test_fresh_environment_installed_end_to_end_workflow(tmp_path) -> None:
    repository = Path(__file__).resolve().parents[2]
    source_copy = tmp_path / "source-copy"
    shutil.copytree(
        repository,
        source_copy,
        ignore=shutil.ignore_patterns(
            ".git",
            ".pytest_cache",
            "__pycache__",
            "*.pyc",
            ".venv",
            "venv",
            "dist",
            "build",
            "*.egg-info",
        ),
    )

    wheel_dir = tmp_path / "wheel"
    wheel_dir.mkdir()
    _run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--no-deps",
            "--no-build-isolation",
            "--wheel-dir",
            str(wheel_dir),
            str(source_copy),
        ]
    )
    wheels = sorted(wheel_dir.glob("rie-*.whl"))
    assert len(wheels) == 1

    environment = tmp_path / "environment"
    _run(
        [
            sys.executable,
            "-m",
            "venv",
            "--system-site-packages",
            str(environment),
        ]
    )
    python_executable = (
        environment / "Scripts" / "python.exe"
        if sys.platform == "win32"
        else environment / "bin" / "python"
    )
    rie_executable = (
        environment / "Scripts" / "rie.exe"
        if sys.platform == "win32"
        else environment / "bin" / "rie"
    )
    _run(
        [
            str(python_executable),
            "-m",
            "pip",
            "install",
            "--no-deps",
            str(wheels[0]),
        ]
    )

    version = _run([str(rie_executable), "--version"])
    assert version.stdout.strip() == "rie 0.1.0"
    help_result = _run([str(rie_executable), "--help"])
    for command in (
        "registry",
        "source",
        "ingest",
        "evidence",
        "knowledge",
        "prompt-candidate",
        "audit",
        "export",
    ):
        assert command in help_result.stdout

    sample_source = source_copy / "samples" / "rie-core-v1"
    sample = tmp_path / "sample"
    shutil.copytree(sample_source, sample)
    workspace = tmp_path / "operator-workspace"
    config = tmp_path / "operator.json"
    config.write_text(
        json.dumps(
            {
                "schema_version": "rie_operator_configuration_v1",
                "workspace_path": str(workspace),
                "audit_path": str(workspace / "operator-audit.jsonl"),
            },
            indent=2,
        )
        + "\n",
        encoding="ascii",
    )

    registry = sample / "official-source-registry.json"
    extraction = workspace / "extraction.json"
    evidence = workspace / "evidence.json"
    knowledge = workspace / "knowledge.json"
    prompt = workspace / "prompt-candidates.json"
    exported = workspace / "exported-prompt-candidates.json"

    validation = _json_command(
        rie_executable,
        config,
        ["registry", "validate", str(registry)],
    )
    assert validation["status"] == "SUCCEEDED"

    source_inspection = _json_command(
        rie_executable,
        config,
        ["source", "inspect", str(registry), "RIE-SAMPLE-PDF-001"],
    )
    assert source_inspection["status"] == "SUCCEEDED"

    ingestion = _json_command(
        rie_executable,
        config,
        [
            "ingest",
            "pdf",
            str(registry),
            "RIE-SAMPLE-PDF-001",
            "--output",
            str(extraction),
        ],
    )
    assert ingestion["status"] == "SUCCEEDED"

    evidence_result = _json_command(
        rie_executable,
        config,
        ["evidence", "build", str(extraction), "--output", str(evidence)],
    )
    assert evidence_result["status"] == "SUCCEEDED"

    knowledge_result = _json_command(
        rie_executable,
        config,
        ["knowledge", "build", str(evidence), "--output", str(knowledge)],
    )
    assert knowledge_result["status"] == "SUCCEEDED"

    prompt_result = _json_command(
        rie_executable,
        config,
        [
            "prompt-candidate",
            "build",
            str(knowledge),
            "--output",
            str(prompt),
        ],
    )
    assert prompt_result["status"] == "SUCCEEDED"

    export_result = _json_command(
        rie_executable,
        config,
        ["export", str(prompt), "--output", str(exported)],
    )
    assert export_result["status"] == "SUCCEEDED"

    before = {
        path.name: _digest(path)
        for path in (extraction, evidence, knowledge, prompt, exported)
    }
    rerun = _json_command(
        rie_executable,
        config,
        [
            "ingest",
            "pdf",
            str(registry),
            "RIE-SAMPLE-PDF-001",
            "--output",
            str(extraction),
        ],
    )
    assert rerun["status"] == "REUSED_EXISTING"
    after = {
        path.name: _digest(path)
        for path in (extraction, evidence, knowledge, prompt, exported)
    }
    assert before == after

    json_inspection = _json_command(
        rie_executable,
        config,
        ["evidence", "inspect", str(evidence)],
    )
    human_inspection = _run(
        [
            str(rie_executable),
            "--config",
            str(config),
            "--format",
            "human",
            "evidence",
            "inspect",
            str(evidence),
        ]
    )
    assert f"status: {json_inspection['status']}" in human_inspection.stdout
    assert f"exit_code: {json_inspection['exit_code']}" in human_inspection.stdout
    assert (
        f"issue_code: {json_inspection['issue_code']}"
        in human_inspection.stdout
    )

    audit_id = validation["audit"]["audit_id"]
    audit_result = _json_command(
        rie_executable,
        config,
        ["audit", "job", audit_id],
    )
    assert audit_result["identifiers"]["audit_id"] == audit_id

    rejection = _run(
        [
            str(rie_executable),
            "--config",
            str(config),
            "--format",
            "json",
            "source",
            "inspect",
            str(registry),
            "UNKNOWN-SOURCE",
        ],
        expected_exit=4,
    )
    rejected_payload = json.loads(rejection.stdout)
    assert rejected_payload["status"] == "REJECTED"
    assert rejected_payload["recovery"]["safe_to_repeat"] == "true"

    prompt_payload = json.loads(prompt.read_text(encoding="ascii"))
    assert prompt_payload["prompt_candidates"]
    audit_lines = (
        workspace / "operator-audit.jsonl"
    ).read_text(encoding="ascii").splitlines()
    assert len(audit_lines) >= 12


def _json_command(
    executable: Path,
    config: Path,
    arguments: list[str],
) -> dict:
    completed = _run(
        [
            str(executable),
            "--config",
            str(config),
            "--format",
            "json",
            *arguments,
        ]
    )
    return json.loads(completed.stdout)


def _run(
    command: list[str],
    *,
    expected_exit: int = 0,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert completed.returncode == expected_exit, (
        command,
        completed.returncode,
        completed.stdout,
        completed.stderr,
    )
    return completed


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
