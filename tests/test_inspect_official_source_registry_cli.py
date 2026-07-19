import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from rie.official_source.inspect_official_source_registry import main


def _item(**overrides):
    item = {
        "source_id": "SRC-001",
        "source_path": "docs/synthetic-registry-source.pdf",
        "source_type": "pdf",
        "document_classification": "project_rulebook",
        "authority_status": "source_of_truth_candidate",
        "lifecycle_status": "locked",
        "evidence_eligibility": "eligible_with_review",
        "version": "v1.0",
        "review_notes": "Synthetic example only.",
    }
    item.update(overrides)
    return item


def _registry(items):
    return {
        "official_sources": items,
    }


def _write_registry(path, data):
    path.write_text(
        json.dumps(data),
        encoding="utf-8",
    )


def _subprocess_environment():
    repo_root = Path(__file__).resolve().parents[1]
    environment = os.environ.copy()
    current_pythonpath = environment.get("PYTHONPATH")
    src_path = str(repo_root / "src")

    if current_pythonpath:
        environment["PYTHONPATH"] = os.pathsep.join(
            [src_path, current_pythonpath]
        )
    else:
        environment["PYTHONPATH"] = src_path

    return environment


def _run_module(registry_path):
    repo_root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "rie.official_source.inspect_official_source_registry",
            str(registry_path),
        ],
        cwd=repo_root,
        env=_subprocess_environment(),
        capture_output=True,
        text=True,
        check=False,
    )


def test_valid_synthetic_registry_returns_zero_with_exact_report(
    tmp_path,
    capsys,
):
    registry_path = tmp_path / "official-source-registry.json"
    _write_registry(
        registry_path,
        _registry([
            _item(
                source_id="SRC-002",
                source_type="pdf",
            ),
            _item(
                source_id="SRC-001",
                source_type="markdown",
            ),
        ]),
    )

    result = main([str(registry_path)])
    output = capsys.readouterr().out

    assert result == 0
    assert output == """Official Source Registry Validation Report
contract_version: official_source_registry_validation_contract_v1
status: valid
total_official_sources: 2
source_type:
  markdown: 1
  pdf: 1
document_classification:
  project_rulebook: 2
authority_status:
  source_of_truth_candidate: 2
lifecycle_status:
  locked: 2
evidence_eligibility:
  eligible_with_review: 2
"""


def test_cli_repeated_output_is_byte_identical(tmp_path, capsys):
    registry_path = tmp_path / "official-source-registry.json"
    _write_registry(registry_path, _registry([_item()]))

    first_result = main([str(registry_path)])
    first_output = capsys.readouterr().out
    second_result = main([str(registry_path)])
    second_output = capsys.readouterr().out

    assert first_result == 0
    assert second_result == 0
    assert first_output.encode("utf-8") == second_output.encode("utf-8")


def test_output_does_not_include_source_path(tmp_path, capsys):
    registry_path = tmp_path / "official-source-registry.json"
    source_path = "docs/synthetic-source-path-that-must-not-print.pdf"
    _write_registry(
        registry_path,
        _registry([_item(source_path=source_path)]),
    )

    result = main([str(registry_path)])
    output = capsys.readouterr().out

    assert result == 0
    assert source_path not in output
    assert "source_path" not in output


def test_missing_argument_exits_two_through_argparse():
    with pytest.raises(SystemExit) as exc_info:
        main([])

    assert exc_info.value.code == 2


def test_missing_registry_file_returns_one_with_stable_issue(
    tmp_path,
    capsys,
):
    result = main([str(tmp_path / "missing-registry.json")])
    output = capsys.readouterr().out

    assert result == 1
    assert output == """Official Source Registry Validation Report
contract_version: official_source_registry_validation_contract_v1
status: invalid
issue_code: registry_missing
issue_message: Official Source registry file does not exist.
"""


def test_invalid_json_returns_one_with_stable_issue(tmp_path, capsys):
    registry_path = tmp_path / "official-source-registry.json"
    registry_path.write_text("{invalid-json", encoding="utf-8")

    result = main([str(registry_path)])
    output = capsys.readouterr().out

    assert result == 1
    assert "status: invalid" in output
    assert "issue_code: invalid_json" in output


def test_invalid_registry_shape_returns_one_with_stable_issue(
    tmp_path,
    capsys,
):
    registry_path = tmp_path / "official-source-registry.json"
    _write_registry(registry_path, [])

    result = main([str(registry_path)])
    output = capsys.readouterr().out

    assert result == 1
    assert "issue_code: invalid_registry_structure" in output


def test_invalid_registry_entry_returns_location(tmp_path, capsys):
    registry_path = tmp_path / "official-source-registry.json"
    _write_registry(
        registry_path,
        _registry([_item(source_type="invalid")]),
    )

    result = main([str(registry_path)])
    output = capsys.readouterr().out

    assert result == 1
    assert "issue_code: invalid_registry_entry" in output
    assert "item_index: 0" in output
    assert "field_name: source_type" in output


def test_nonexistent_source_path_inside_registry_still_succeeds(
    tmp_path,
    capsys,
):
    registry_path = tmp_path / "official-source-registry.json"
    _write_registry(
        registry_path,
        _registry([
            _item(source_path="docs/not-a-real-synthetic-source.pdf"),
        ]),
    )

    result = main([str(registry_path)])
    output = capsys.readouterr().out

    assert result == 0
    assert "status: valid" in output
    assert "total_official_sources: 1" in output


def test_selected_module_command_accepts_official_config():
    repo_root = Path(__file__).resolve().parents[1]
    config_path = repo_root / "configs" / "official_source_registry.json"

    completed = _run_module(config_path)

    assert completed.returncode == 0
    assert completed.stdout == """Official Source Registry Validation Report
contract_version: official_source_registry_validation_contract_v1
status: valid
total_official_sources: 0
source_type:
document_classification:
authority_status:
lifecycle_status:
evidence_eligibility:
"""


def test_selected_module_command_returns_one_for_invalid_registry(tmp_path):
    registry_path = tmp_path / "official-source-registry.json"
    registry_path.write_text("{invalid-json", encoding="utf-8")

    completed = _run_module(registry_path)

    assert completed.returncode == 1
    assert "issue_code: invalid_json" in completed.stdout


def test_selected_module_command_usage_failure_is_two():
    repo_root = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "rie.official_source.inspect_official_source_registry",
        ],
        cwd=repo_root,
        env=_subprocess_environment(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 2
    assert completed.stdout == ""
    assert "usage:" in completed.stderr


def test_no_real_rsv_locked_content_is_used(tmp_path):
    registry_path = tmp_path / "official-source-registry.json"
    registry = _registry([_item()])
    _write_registry(registry_path, registry)

    raw_registry = registry_path.read_text(encoding="utf-8")
    assert "synthetic" in raw_registry
    assert "RSV" not in raw_registry
    assert "Creative Logic Specification" not in raw_registry
    assert "Official Knowledge Base" not in raw_registry
