import json

from rie.extraction.export_text_extraction_evidence import main as export_main
from rie.extraction.inspect_text_extraction_evidence import main as inspect_main


def test_text_extraction_evidence_artifact_smoke_flow_exports_then_inspects(
    tmp_path,
    capsys,
):
    normal_path = tmp_path / "normal.dat"
    non_ascii_path = tmp_path / "non-ascii.dat"
    empty_path = tmp_path / "empty.dat"
    failed_path = tmp_path / "failed.dat"
    report_path = tmp_path / "text-extractions.json"
    evidence_path = tmp_path / "text-evidence.json"
    non_ascii_content = "Café racer helm: Rancang konsep."

    report_path.write_text(
        json.dumps(
            {
                "root": str(tmp_path),
                "total_text_assets": 4,
                "failed": 1,
                "extractions": [
                    {
                        "path": str(normal_path),
                        "size": 12,
                        "content": "First prompt",
                        "error": None,
                    },
                    {
                        "path": str(non_ascii_path),
                        "size": 34,
                        "content": non_ascii_content,
                        "error": None,
                    },
                    {
                        "path": str(empty_path),
                        "size": 0,
                        "content": "",
                        "error": None,
                    },
                    {
                        "path": str(failed_path),
                        "size": 0,
                        "content": "",
                        "error": "cannot read file",
                    },
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    export_result = export_main([
        str(report_path),
        "--output",
        str(evidence_path),
    ])

    export_output = capsys.readouterr().out
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    records = evidence["evidences"]

    assert export_result == 0
    assert evidence_path.exists()
    assert "Evidence Count    : 3" in export_output
    assert len(records) == 3
    assert [record["source_path"] for record in records] == [
        str(normal_path),
        str(non_ascii_path),
        str(empty_path),
    ]
    assert str(failed_path) not in [
        record["source_path"]
        for record in records
    ]
    assert records[1]["content"] == non_ascii_content
    assert records[2]["content"] == ""

    for record in records:
        assert set(record) == {
            "source_path",
            "content",
            "size_bytes",
        }
        assert not any(
            field in record
            for field in {
                "evidence_type",
                "metadata",
                "source_stage",
                "analysis",
                "size_class",
                "category",
                "summary",
                "knowledge",
                "prompt",
                "embedding",
            }
        )

    inspect_result = inspect_main([str(evidence_path)])

    inspection_output = capsys.readouterr().out
    expected_character_count = len("First prompt") + len(non_ascii_content)

    assert inspect_result == 0
    assert "Total Evidences          : 3" in inspection_output
    assert (
        f"Total Content Characters : {expected_character_count}"
        in inspection_output
    )
    assert "Empty Content Count      : 1" in inspection_output
    assert "Invalid Record Count     : 0" in inspection_output
    assert "Forbidden Field Count    : 0" in inspection_output
