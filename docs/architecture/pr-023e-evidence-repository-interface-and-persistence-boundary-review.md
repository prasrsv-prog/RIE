# PR-023E — Evidence Repository Interface and Persistence Boundary Review

## 1. Gate identity

| Item | Value |
|---|---|
| Repository | `D:\PROJECT\RIE` |
| Branch | `phase-023-knowledge-governance-review` |
| Reviewed HEAD | `95d42b821c594d7b535858c6e4e81ff6dc979426` |
| Gate type | Documentation-only |
| Inherited PR-023D decision | `DETERMINISTIC EVIDENCE IDENTITY AND IDEMPOTENCY CONTRACT APPROVED; REPOSITORY IMPLEMENTATION DEFERRED` |
| Final PR-023E decision | **EVIDENCE REPOSITORY INTERFACE AND PERSISTENCE BOUNDARY APPROVED; IMPLEMENTATION DEFERRED** |
| Recommended next gate | **PR-023F - Accepted Evidence Prerequisite Closure and Knowledge Governance Readiness Reassessment** |
| Recommended next gate type | **Documentation-only** |

## 2. Purpose

PR-023E defines the EvidenceRepository interface, persistence adapter boundary, transaction and atomicity expectations, lookup/write result contracts, replay and collision mapping, failure behavior, and prohibited coupling.

This review creates no repository implementation, database, file store, serializer, migration, test, or accepted Evidence.

## 3. Checkpoint and preservation

PR-023D was verified as an exact one-file documentation commit:

- Commit: `95d42b821c594d7b535858c6e4e81ff6dc979426`
- Parent: `3b176d1f0f096603547905e0ea8b666d67250508`
- Subject: `docs: define deterministic evidence identity contract`
- File: `docs/architecture/pr-023d-deterministic-evidence-identity-and-idempotency-contract-review.md`
- File SHA-256: `8ed9ad0023759047b6ca5372fe763ce6b8dc608a1ea1139f1145492cd05f8dbb`

The Phase 23 branch is synchronized with its remote at divergence `0 0`.

Phase 22 remains preserved:

- Branch: `phase-022-evidence-candidate-boundary-review`
- Branch target: `e41269e764979f94f23f93692136c63cc603f2e2`
- Official tag: `v0.22.0-rcis-evidence-candidate-boundary-phase`
- Tag object: `1a7488e7cc2830aea2506182e6a6aba797cbebcf`
- Peeled target: `e41269e764979f94f23f93692136c63cc603f2e2`

The controlled PDF sandbox and `D:\PROJECT\pytest-temp` were verified empty. Real and synthetic PDF targets were absent. The known read-only `.pytest_cache` warning was not repaired or deleted.

## 4. Read-only repository observations

### 4.1 Interface paths

- `src/rie/interfaces/__init__.py`
- `src/rie/interfaces/batch_discovery.py`

### 4.2 Infrastructure paths

- `src/rie/infrastructure/__init__.py`
- `src/rie/infrastructure/repository_config.py`
- `src/rie/infrastructure/repository_explorer_batch_discovery.py`
- `src/rie/infrastructure/repository_scanner.py`

### 4.3 Repository-named paths

- `src/analysis/repository_statistics.py`
- `src/analyzer/repository_analyzer.py`
- `src/report/repository_insight.py`
- `src/report/repository_insight_builder.py`
- `src/report/repository_report.py`
- `src/report/repository_report_presenter.py`
- `src/rie/infrastructure/repository_config.py`
- `src/rie/infrastructure/repository_explorer_batch_discovery.py`
- `src/rie/infrastructure/repository_scanner.py`
- `src/rie/repository_explorer.py`
- `tests/infrastructure/test_repository_explorer_batch_discovery.py`
- `tests/repository_analyzer.py`
- `tests/test_repository_explorer_entrypoint.py`

### 4.4 Serializer paths

- `src/collection/pdf_text_extraction_evidence_collection_serializer.py`
- `src/collection/text_extraction_evidence_collection_serializer.py`
- `src/knowledge/official_knowledge_collection_serializer.py`
- `src/knowledge/text_knowledge_collection_serializer.py`
- `src/prompting/text_prompt_candidate_collection_serializer.py`
- `src/rie/extraction/pdf_text_extraction_report_serializer.py`
- `src/rie/extraction/text_asset_extraction_report_serializer.py`
- `src/rie/ingestion/creative_asset_scan_report_serializer.py`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py`
- `tests/extraction/test_text_asset_extraction_report_serializer.py`
- `tests/ingestion/test_creative_asset_scan_report_serializer.py`
- `tests/test_official_knowledge_collection_serializer.py`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py`
- `tests/test_text_extraction_evidence_collection_serializer.py`
- `tests/test_text_knowledge_collection_serializer.py`
- `tests/test_text_prompt_candidate_collection_serializer.py`

### 4.5 Interface and callable observations

- `src/analysis/repository_statistics.py` line 5: `class RepositoryStatistics:`
- `src/analyzer/repository_analyzer.py` line 11: `class RepositoryAnalyzer:`
- `src/analyzer/repository_analyzer.py` line 13: `def __init__(`
- `src/analyzer/repository_analyzer.py` line 26: `def analyze(`
- `src/collection/pdf_text_extraction_evidence_collection_serializer.py` line 9: `class PdfTextExtractionEvidenceCollectionSerializer:`
- `src/collection/pdf_text_extraction_evidence_collection_serializer.py` line 12: `def to_dict(`
- `src/collection/pdf_text_extraction_evidence_collection_serializer.py` line 32: `def to_json(`
- `src/collection/text_extraction_evidence_collection_serializer.py` line 9: `def to_json(`
- `src/collection/text_extraction_evidence_collection_serializer.py` line 19: `def to_dict(`
- `src/knowledge/official_knowledge_collection_serializer.py` line 7: `class OfficialKnowledgeCollectionSerializer:`
- `src/knowledge/official_knowledge_collection_serializer.py` line 10: `def to_dict(`
- `src/knowledge/official_knowledge_collection_serializer.py` line 36: `def to_json(`
- `src/knowledge/text_knowledge_collection_serializer.py` line 7: `def to_json(`
- `src/knowledge/text_knowledge_collection_serializer.py` line 17: `def to_dict(`
- `src/prompting/text_prompt_candidate_collection_serializer.py` line 9: `class TextPromptCandidateCollectionSerializer:`
- `src/prompting/text_prompt_candidate_collection_serializer.py` line 12: `def to_dict(`
- `src/prompting/text_prompt_candidate_collection_serializer.py` line 29: `def to_json(`
- `src/report/repository_insight.py` line 5: `class RepositoryInsight:`
- `src/report/repository_insight_builder.py` line 19: `class RepositoryInsightBuilder:`
- `src/report/repository_insight_builder.py` line 22: `def build(`
- `src/report/repository_insight_builder.py` line 64: `def _largest_category(`
- `src/report/repository_insight_builder.py` line 76: `def _most_common_extension(`
- `src/report/repository_insight_builder.py` line 88: `def _repository_health(`
- `src/report/repository_report.py` line 9: `class RepositoryReport:`
- `src/report/repository_report_presenter.py` line 4: `class RepositoryReportPresenter:`
- `src/report/repository_report_presenter.py` line 7: `def present(report: RepositoryReport) -> None:`
- `src/rie/extraction/pdf_text_extraction_report_serializer.py` line 7: `class PdfTextExtractionReportSerializer:`
- `src/rie/extraction/pdf_text_extraction_report_serializer.py` line 10: `def to_dict(`
- `src/rie/extraction/pdf_text_extraction_report_serializer.py` line 41: `def to_json(`
- `src/rie/extraction/text_asset_extraction_report_serializer.py` line 9: `def load_json(path: Path) -> TextAssetExtractionReport:`
- `src/rie/extraction/text_asset_extraction_report_serializer.py` line 13: `def from_dict(data: dict[str, Any]) -> TextAssetExtractionReport:`
- `src/rie/extraction/text_asset_extraction_report_serializer.py` line 42: `def to_dict(report: TextAssetExtractionReport) -> dict[str, Any]:`
- `src/rie/extraction/text_asset_extraction_report_serializer.py` line 59: `def write_json(`
- `src/rie/extraction/text_asset_extraction_report_serializer.py` line 73: `def _extraction_from_dict(data: Any) -> TextAssetExtraction:`
- `src/rie/extraction/text_asset_extraction_report_serializer.py` line 102: `def _required(data: dict[str, Any], key: str) -> Any:`
- `src/rie/infrastructure/repository_config.py` line 6: `class RepositoryConfig:`
- `src/rie/infrastructure/repository_explorer_batch_discovery.py` line 2: `from typing import Protocol`
- `src/rie/infrastructure/repository_explorer_batch_discovery.py` line 12: `class _RepositoryExplorerLike(Protocol):`
- `src/rie/infrastructure/repository_explorer_batch_discovery.py` line 14: `def explore(self, repository_path: Path) -> RepositoryExploration:`
- `src/rie/infrastructure/repository_explorer_batch_discovery.py` line 18: `class RepositoryExplorerBatchDiscovery(BatchDiscovery):`
- `src/rie/infrastructure/repository_explorer_batch_discovery.py` line 20: `def __init__(`
- `src/rie/infrastructure/repository_explorer_batch_discovery.py` line 28: `def discover(self, root: Path) -> Batch:`
- `src/rie/infrastructure/repository_explorer_batch_discovery.py` line 59: `def _asset_path(self, root: Path, node_path: Path) -> Path:`
- `src/rie/infrastructure/repository_scanner.py` line 4: `class RepositoryScanner:`
- `src/rie/infrastructure/repository_scanner.py` line 6: `def scan(self, root: Path) -> list[Path]:`
- `src/rie/ingestion/creative_asset_scan_report_serializer.py` line 9: `def load_json(path: Path) -> dict[str, Any]:`
- `src/rie/ingestion/creative_asset_scan_report_serializer.py` line 13: `def to_dict(report: CreativeAssetScanReport) -> dict[str, Any]:`
- `src/rie/ingestion/creative_asset_scan_report_serializer.py` line 39: `def write_json(`
- `src/rie/interfaces/batch_discovery.py` line 1: `from abc import ABC, abstractmethod`
- `src/rie/interfaces/batch_discovery.py` line 7: `class BatchDiscovery(ABC):`
- `src/rie/interfaces/batch_discovery.py` line 9: `@abstractmethod`
- `src/rie/interfaces/batch_discovery.py` line 10: `def discover(`
- `src/rie/repository_explorer.py` line 4: `def main() -> None:`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 36: `def _report(`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 47: `def test_serializer_produces_expected_top_level_keys():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 60: `def test_serializer_serializes_empty_report():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 73: `def test_serializer_serializes_one_page_extraction_correctly():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 110: `def test_serializer_serializes_multiple_page_extractions_in_order():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 158: `def test_serializer_preserves_exact_content():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 179: `def test_serializer_preserves_non_ascii_content():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 202: `def test_serializer_preserves_newline_content():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 223: `def test_serializer_preserves_empty_content():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 243: `def test_serializer_preserves_warnings():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 267: `def test_serializer_preserves_asset_errors():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 289: `def test_serializer_preserves_total_pdf_assets():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 316: `def test_serializer_preserves_total_page_extractions():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 345: `def test_serializer_preserves_failed_pdf_assets():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 361: `def test_serializer_does_not_include_forbidden_fields():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 409: `def test_to_json_output_is_deterministic():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 430: `def test_to_json_output_can_be_parsed_back_with_json_loads():`
- `tests/extraction/test_text_asset_extraction_report_serializer.py` line 9: `def test_to_dict_serializes_text_asset_extraction_report(tmp_path):`
- `tests/extraction/test_text_asset_extraction_report_serializer.py` line 51: `def test_write_json_writes_utf8_json_and_preserves_non_ascii_content(tmp_path):`
- `tests/infrastructure/test_repository_explorer_batch_discovery.py` line 15: `class FakeRepositoryExplorer:`
- `tests/infrastructure/test_repository_explorer_batch_discovery.py` line 17: `def __init__(self, exploration: RepositoryExploration) -> None:`
- `tests/infrastructure/test_repository_explorer_batch_discovery.py` line 21: `def explore(self, repository_path: Path) -> RepositoryExploration:`
- `tests/infrastructure/test_repository_explorer_batch_discovery.py` line 27: `def test_repository_explorer_batch_discovery_maps_exploration_to_batch(tmp_path):`
- `tests/ingestion/test_creative_asset_scan_report_serializer.py` line 10: `def test_to_dict_serializes_scan_report(tmp_path):`
- `tests/ingestion/test_creative_asset_scan_report_serializer.py` line 63: `def test_write_json_writes_valid_json(tmp_path):`
- `tests/repository_analyzer.py` line 6: `def test_should_analyze_repository():`
- `tests/test_official_knowledge_collection_serializer.py` line 13: `def make_source_item(`
- `tests/test_official_knowledge_collection_serializer.py` line 42: `def test_serializes_one_official_knowledge_item_to_expected_dict_shape():`
- `tests/test_official_knowledge_collection_serializer.py` line 67: `def test_serializes_optional_none_fields_as_none():`
- `tests/test_official_knowledge_collection_serializer.py` line 97: `def test_serializes_multiple_items_preserving_order_and_indexes():`
- `tests/test_official_knowledge_collection_serializer.py` line 124: `def test_serializes_empty_collection():`
- `tests/test_official_knowledge_collection_serializer.py` line 134: `def test_serializer_output_includes_no_forbidden_fields():`
- `tests/test_official_knowledge_collection_serializer.py` line 171: `def test_to_json_preserves_none_as_json_null_and_non_ascii_content():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 34: `def _evidence(**overrides):`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 49: `def test_serializer_produces_top_level_pdf_text_evidences_key():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 57: `def test_serializer_serializes_empty_collection():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 65: `def test_serializer_serializes_one_evidence_correctly():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 99: `def test_serializer_serializes_multiple_evidences_in_order():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 118: `def test_serializer_preserves_exact_content():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 132: `def test_serializer_preserves_non_ascii_content():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 150: `def test_serializer_preserves_newline_content():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 164: `def test_serializer_preserves_empty_content():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 176: `def test_serializer_preserves_warnings():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 193: `def test_serializer_preserves_source_path():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 205: `def test_serializer_preserves_size_bytes():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 217: `def test_serializer_preserves_page_number():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 229: `def test_serializer_preserves_extraction_index():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 241: `def test_serializer_preserves_extraction_method():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 255: `def test_serializer_preserves_evidence_index():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 267: `def test_serializer_does_not_include_forbidden_fields():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 286: `def test_to_json_output_is_deterministic():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 304: `def test_to_json_output_can_be_parsed_back_with_json_loads():`
- `tests/test_repository_explorer_entrypoint.py` line 4: `class FakeEngine:`
- `tests/test_repository_explorer_entrypoint.py` line 6: `def __init__(self) -> None:`
- `tests/test_repository_explorer_entrypoint.py` line 9: `def run(self) -> None:`
- `tests/test_repository_explorer_entrypoint.py` line 13: `def test_repository_explorer_main_runs_composed_engine(monkeypatch):`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 12: `def test_serializes_empty_text_extraction_evidence_collection():`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 22: `def test_serializes_one_text_extraction_evidence():`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 46: `def test_serializes_multiple_evidences_deterministically():`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 80: `def test_preserves_non_ascii_content_with_ensure_ascii_false():`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 99: `def test_serialized_output_contains_only_evidence_fields():`
- `tests/test_text_knowledge_collection_serializer.py` line 8: `def test_serializes_empty_text_knowledge_collection():`
- `tests/test_text_knowledge_collection_serializer.py` line 18: `def test_serializes_one_text_knowledge_item():`
- `tests/test_text_knowledge_collection_serializer.py` line 44: `def test_serializes_multiple_text_knowledge_items_deterministically():`
- `tests/test_text_knowledge_collection_serializer.py` line 82: `def test_preserves_non_ascii_content_with_ensure_ascii_false():`
- `tests/test_text_knowledge_collection_serializer.py` line 102: `def test_preserves_newline_content_exactly():`
- `tests/test_text_knowledge_collection_serializer.py` line 120: `def test_preserves_evidence_index():`
- `tests/test_text_knowledge_collection_serializer.py` line 137: `def test_serialized_output_contains_only_knowledge_fields():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 12: `def test_serializer_produces_top_level_prompt_candidates_key():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 22: `def test_serializer_serializes_one_candidate_correctly():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 50: `def test_serializer_serializes_multiple_candidates_in_order():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 90: `def test_serializer_preserves_exact_content():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 111: `def test_serializer_preserves_non_ascii_content():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 132: `def test_serializer_preserves_newline_content():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 151: `def test_serializer_preserves_empty_content():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 169: `def test_serializer_preserves_evidence_index():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 187: `def test_serializer_preserves_knowledge_index():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 205: `def test_serializer_does_not_include_forbidden_fields():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 255: `def test_to_json_output_is_deterministic():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 274: `def test_to_json_output_can_be_parsed_back_with_json_loads():`

### 4.6 Persistence-related token observations

- `src/rie/extraction/export_pdf_text_evidence.py` line 68: `print(f"Failed to write PDF text evidence file: {exc}")`
- `src/rie/extraction/export_pdf_text_extractions.py` line 59: `print(f"Failed to write PDF text extraction file: {exc}")`
- `src/rie/extraction/export_text_extraction_evidence.py` line 61: `print(f"Failed to write evidence file: {exc}")`
- `src/rie/extraction/extract_text_assets.py` line 47: `print(f"Failed to write extraction report: {exc}")`
- `src/rie/extraction/pdf_text_extraction_report.py` line 25: `source_paths.update(`
- `src/rie/ingestion/scan_assets.py` line 48: `print(f"Failed to write report: {exc}")`
- `src/rie/knowledge/export_official_knowledge.py` line 70: `print(f"Failed to write Official Knowledge file: {exc}")`
- `src/rie/knowledge/export_text_knowledge.py` line 56: `print(f"Failed to write knowledge file: {exc}")`
- `src/rie/prompt/export_text_prompt_candidates.py` line 64: `print(f"Failed to write prompt candidates file: {exc}")`
- `tests/application/test_evidence_candidate.py` line 39: `values.update(overrides)`
- `tests/application/test_evidence_candidate.py` line 341: `assert not hasattr(candidate, "insert")`
- `tests/application/test_evidence_candidate.py` line 356: `assert not hasattr(_candidate(), "save")`
- `tests/extraction/test_export_pdf_text_evidence.py` line 57: `page.update(overrides)`
- `tests/extraction/test_extract_text_assets.py` line 168: `raise OSError("cannot write extraction")`
- `tests/extraction/test_extract_text_assets.py` line 184: `"Failed to write extraction report: cannot write extraction"`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 24: `evidence.update(overrides)`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 41: `artifact.update(overrides)`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 144: `_valid_evidence(prompt="Do not write prompts here."),`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 23: `page.update(overrides)`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 33: `asset_error.update(overrides)`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 48: `artifact.update(overrides)`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 228: `_valid_page(prompt="Do not write prompts here."),`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 253: `_valid_page(prompt="Do not write prompts here."),`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 20: `page.update(overrides)`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 30: `asset_error.update(overrides)`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 45: `artifact.update(overrides)`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 150: `_valid_page(prompt="Do not write prompts here."),`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 320: `_valid_page(prompt="Do not write prompts here."),`
- `tests/ingestion/test_controlled_metadata_only_dry_run_smoke_flow.py` line 65: `collection_values.update(collection_overrides)`
- `tests/ingestion/test_controlled_metadata_only_dry_run_smoke_flow.py` line 81: `safety_values.update(safety_overrides)`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 194: `values.update(overrides)`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 97: `values.update(overrides)`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 29: `values.update(overrides)`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 29: `values.update(overrides)`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 48: `values.update(overrides)`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 85: `values.update(overrides)`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 108: `values.update(overrides)`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 36: `values.update(overrides)`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 59: `values.update(overrides)`
- `tests/ingestion/test_controlled_pdf_text_extraction_synthetic_parser_execution.py` line 32: `writer.write(str(pdf_path))`
- `tests/ingestion/test_controlled_pdf_text_extraction_text_bearing_synthetic_pdf.py` line 57: `writer.write(str(pdf_path))`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 26: `values.update(overrides)`
- `tests/ingestion/test_real_asset_dry_run_contract.py` line 15: `values.update(overrides)`
- `tests/ingestion/test_real_asset_dry_run_contract.py` line 27: `values.update(overrides)`
- `tests/ingestion/test_real_asset_metadata_collection_contract.py` line 24: `values.update(overrides)`
- `tests/ingestion/test_real_asset_metadata_collection_contract.py` line 36: `values.update(overrides)`
- `tests/ingestion/test_real_asset_metadata_collector.py` line 36: `values.update(overrides)`
- `tests/ingestion/test_real_asset_metadata_collector.py` line 50: `values.update(overrides)`
- `tests/ingestion/test_real_asset_metadata_collector.py` line 59: `values.update(overrides)`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 32: `values.update(overrides)`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 46: `values.update(overrides)`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 55: `values.update(overrides)`
- `tests/ingestion/test_real_asset_sandbox_policy.py` line 14: `values.update(overrides)`
- `tests/ingestion/test_real_filesystem_metadata_adapter_safety_contract.py` line 21: `values.update(overrides)`
- `tests/ingestion/test_scan_assets.py` line 102: `raise OSError("cannot write report")`
- `tests/ingestion/test_scan_assets.py` line 117: `assert "Failed to write report: cannot write report" in output`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 176: `"prompt": "Do not write prompts here.",`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 204: `"prompt": "Do not write prompts here.",`
- `tests/prompt/test_text_prompt_candidate_smoke_flow.py` line 67: `"prompt": "Do not write prompts here.",`
- `tests/test_export_official_knowledge_cli.py` line 27: `item.update(overrides)`
- `tests/test_inspect_evidence_eligibility_cli.py` line 20: `item.update(overrides)`
- `tests/test_inspect_official_knowledge_cli.py` line 28: `item.update(overrides)`
- `tests/test_inspect_official_source_registry_cli.py` line 20: `item.update(overrides)`
- `tests/test_official_knowledge_source_input_loader.py` line 27: `item.update(overrides)`
- `tests/test_official_source_evidence_eligibility_gate.py` line 27: `values.update(overrides)`
- `tests/test_official_source_evidence_eligibility_policy.py` line 24: `values.update(overrides)`
- `tests/test_official_source_evidence_workflow_gate.py` line 26: `values.update(overrides)`
- `tests/test_official_source_registry_loader.py` line 29: `item.update(overrides)`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 21: `evidence.update(overrides)`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 31: `artifact.update(overrides)`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 110: `_valid_evidence(prompt="Do not write prompts here."),`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 228: `_valid_evidence(prompt="Do not write prompts here."),`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 18: `page.update(overrides)`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 45: `evidence.update(overrides)`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 43: `page.update(overrides)`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 56: `artifact.update(overrides)`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 121: `"prompt": "Do not write prompts here.",`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 286: `"prompt": "Do not write prompts here.",`

### 4.7 Existing EvidenceRepository symbol observations

- No matching tracked lines found.

### 4.8 Serializer observations

- `src/collection/pdf_text_extraction_evidence_collection_serializer.py` line 1: `import json`
- `src/collection/pdf_text_extraction_evidence_collection_serializer.py` line 9: `class PdfTextExtractionEvidenceCollectionSerializer:`
- `src/collection/pdf_text_extraction_evidence_collection_serializer.py` line 12: `def to_dict(`
- `src/collection/pdf_text_extraction_evidence_collection_serializer.py` line 32: `def to_json(`
- `src/collection/pdf_text_extraction_evidence_collection_serializer.py` line 35: `return json.dumps(`
- `src/collection/text_extraction_evidence_collection_serializer.py` line 1: `import json`
- `src/collection/text_extraction_evidence_collection_serializer.py` line 9: `def to_json(`
- `src/collection/text_extraction_evidence_collection_serializer.py` line 12: `return json.dumps(`
- `src/collection/text_extraction_evidence_collection_serializer.py` line 19: `def to_dict(`
- `src/knowledge/official_knowledge_collection_serializer.py` line 1: `import json`
- `src/knowledge/official_knowledge_collection_serializer.py` line 7: `class OfficialKnowledgeCollectionSerializer:`
- `src/knowledge/official_knowledge_collection_serializer.py` line 10: `def to_dict(`
- `src/knowledge/official_knowledge_collection_serializer.py` line 36: `def to_json(`
- `src/knowledge/official_knowledge_collection_serializer.py` line 39: `return json.dumps(`
- `src/knowledge/text_knowledge_collection_serializer.py` line 1: `import json`
- `src/knowledge/text_knowledge_collection_serializer.py` line 7: `def to_json(`
- `src/knowledge/text_knowledge_collection_serializer.py` line 10: `return json.dumps(`
- `src/knowledge/text_knowledge_collection_serializer.py` line 17: `def to_dict(`
- `src/prompting/text_prompt_candidate_collection_serializer.py` line 1: `import json`
- `src/prompting/text_prompt_candidate_collection_serializer.py` line 9: `class TextPromptCandidateCollectionSerializer:`
- `src/prompting/text_prompt_candidate_collection_serializer.py` line 12: `def to_dict(`
- `src/prompting/text_prompt_candidate_collection_serializer.py` line 29: `def to_json(`
- `src/prompting/text_prompt_candidate_collection_serializer.py` line 32: `return json.dumps(`
- `src/rie/extraction/pdf_text_extraction_report_serializer.py` line 1: `import json`
- `src/rie/extraction/pdf_text_extraction_report_serializer.py` line 7: `class PdfTextExtractionReportSerializer:`
- `src/rie/extraction/pdf_text_extraction_report_serializer.py` line 10: `def to_dict(`
- `src/rie/extraction/pdf_text_extraction_report_serializer.py` line 41: `def to_json(`
- `src/rie/extraction/pdf_text_extraction_report_serializer.py` line 44: `return json.dumps(`
- `src/rie/extraction/text_asset_extraction_report_serializer.py` line 1: `import json`
- `src/rie/extraction/text_asset_extraction_report_serializer.py` line 9: `def load_json(path: Path) -> TextAssetExtractionReport:`
- `src/rie/extraction/text_asset_extraction_report_serializer.py` line 10: `return from_dict(json.loads(path.read_text(encoding="utf-8")))`
- `src/rie/extraction/text_asset_extraction_report_serializer.py` line 13: `def from_dict(data: dict[str, Any]) -> TextAssetExtractionReport:`
- `src/rie/extraction/text_asset_extraction_report_serializer.py` line 42: `def to_dict(report: TextAssetExtractionReport) -> dict[str, Any]:`
- `src/rie/extraction/text_asset_extraction_report_serializer.py` line 59: `def write_json(`
- `src/rie/extraction/text_asset_extraction_report_serializer.py` line 64: `json.dumps(`
- `src/rie/extraction/text_asset_extraction_report_serializer.py` line 73: `def _extraction_from_dict(data: Any) -> TextAssetExtraction:`
- `src/rie/extraction/text_asset_extraction_report_serializer.py` line 102: `def _required(data: dict[str, Any], key: str) -> Any:`
- `src/rie/ingestion/creative_asset_scan_report_serializer.py` line 1: `import json`
- `src/rie/ingestion/creative_asset_scan_report_serializer.py` line 9: `def load_json(path: Path) -> dict[str, Any]:`
- `src/rie/ingestion/creative_asset_scan_report_serializer.py` line 10: `return json.loads(path.read_text(encoding="utf-8"))`
- `src/rie/ingestion/creative_asset_scan_report_serializer.py` line 13: `def to_dict(report: CreativeAssetScanReport) -> dict[str, Any]:`
- `src/rie/ingestion/creative_asset_scan_report_serializer.py` line 39: `def write_json(`
- `src/rie/ingestion/creative_asset_scan_report_serializer.py` line 44: `json.dumps(to_dict(report), indent=2),`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 1: `import json`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 36: `def _report(`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 47: `def test_serializer_produces_expected_top_level_keys():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 60: `def test_serializer_serializes_empty_report():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 73: `def test_serializer_serializes_one_page_extraction_correctly():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 110: `def test_serializer_serializes_multiple_page_extractions_in_order():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 158: `def test_serializer_preserves_exact_content():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 179: `def test_serializer_preserves_non_ascii_content():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 199: `assert json.loads(result)["page_extractions"][0]["content"] == content`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 202: `def test_serializer_preserves_newline_content():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 220: `assert json.loads(result)["page_extractions"][0]["content"] == content`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 223: `def test_serializer_preserves_empty_content():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 243: `def test_serializer_preserves_warnings():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 267: `def test_serializer_preserves_asset_errors():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 289: `def test_serializer_preserves_total_pdf_assets():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 316: `def test_serializer_preserves_total_page_extractions():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 345: `def test_serializer_preserves_failed_pdf_assets():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 361: `def test_serializer_does_not_include_forbidden_fields():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 409: `def test_to_json_output_is_deterministic():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 430: `def test_to_json_output_can_be_parsed_back_with_json_loads():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 446: `data = json.loads(result)`
- `tests/extraction/test_text_asset_extraction_report_serializer.py` line 1: `import json`
- `tests/extraction/test_text_asset_extraction_report_serializer.py` line 9: `def test_to_dict_serializes_text_asset_extraction_report(tmp_path):`
- `tests/extraction/test_text_asset_extraction_report_serializer.py` line 51: `def test_write_json_writes_utf8_json_and_preserves_non_ascii_content(tmp_path):`
- `tests/extraction/test_text_asset_extraction_report_serializer.py` line 63: `output_path = tmp_path / "text-extractions.json"`
- `tests/extraction/test_text_asset_extraction_report_serializer.py` line 68: `data = json.loads(raw_json)`
- `tests/ingestion/test_creative_asset_scan_report_serializer.py` line 1: `import json`
- `tests/ingestion/test_creative_asset_scan_report_serializer.py` line 10: `def test_to_dict_serializes_scan_report(tmp_path):`
- `tests/ingestion/test_creative_asset_scan_report_serializer.py` line 63: `def test_write_json_writes_valid_json(tmp_path):`
- `tests/ingestion/test_creative_asset_scan_report_serializer.py` line 74: `output_path = tmp_path / "report.json"`
- `tests/ingestion/test_creative_asset_scan_report_serializer.py` line 78: `data = json.loads(output_path.read_text(encoding="utf-8"))`
- `tests/test_official_knowledge_collection_serializer.py` line 1: `import json`
- `tests/test_official_knowledge_collection_serializer.py` line 13: `def make_source_item(`
- `tests/test_official_knowledge_collection_serializer.py` line 42: `def test_serializes_one_official_knowledge_item_to_expected_dict_shape():`
- `tests/test_official_knowledge_collection_serializer.py` line 45: `serialized = OfficialKnowledgeCollectionSerializer.to_dict(collection)`
- `tests/test_official_knowledge_collection_serializer.py` line 47: `assert serialized == {`
- `tests/test_official_knowledge_collection_serializer.py` line 67: `def test_serializes_optional_none_fields_as_none():`
- `tests/test_official_knowledge_collection_serializer.py` line 82: `serialized_item = (`
- `tests/test_official_knowledge_collection_serializer.py` line 88: `assert serialized_item["knowledge_id"] is None`
- `tests/test_official_knowledge_collection_serializer.py` line 89: `assert serialized_item["source_section"] is None`
- `tests/test_official_knowledge_collection_serializer.py` line 90: `assert serialized_item["source_page"] is None`
- `tests/test_official_knowledge_collection_serializer.py` line 91: `assert serialized_item["status"] is None`
- `tests/test_official_knowledge_collection_serializer.py` line 92: `assert serialized_item["governance_level"] is None`
- `tests/test_official_knowledge_collection_serializer.py` line 93: `assert serialized_item["pdf_evidence_index"] is None`
- `tests/test_official_knowledge_collection_serializer.py` line 94: `assert serialized_item["extraction_index"] is None`
- `tests/test_official_knowledge_collection_serializer.py` line 97: `def test_serializes_multiple_items_preserving_order_and_indexes():`
- `tests/test_official_knowledge_collection_serializer.py` line 106: `serialized_items = OfficialKnowledgeCollectionSerializer.to_dict(`
- `tests/test_official_knowledge_collection_serializer.py` line 112: `for item in serialized_items`
- `tests/test_official_knowledge_collection_serializer.py` line 120: `for item in serialized_items`
- `tests/test_official_knowledge_collection_serializer.py` line 124: `def test_serializes_empty_collection():`
- `tests/test_official_knowledge_collection_serializer.py` line 134: `def test_serializer_output_includes_no_forbidden_fields():`
- `tests/test_official_knowledge_collection_serializer.py` line 137: `serialized = OfficialKnowledgeCollectionSerializer.to_dict(collection)`
- `tests/test_official_knowledge_collection_serializer.py` line 165: `assert not forbidden_fields.intersection(serialized)`
- `tests/test_official_knowledge_collection_serializer.py` line 167: `for item in serialized["official_knowledge_items"]:`
- `tests/test_official_knowledge_collection_serializer.py` line 171: `def test_to_json_preserves_none_as_json_null_and_non_ascii_content():`
- `tests/test_official_knowledge_collection_serializer.py` line 181: `serialized_json = OfficialKnowledgeCollectionSerializer.to_json(`
- `tests/test_official_knowledge_collection_serializer.py` line 185: `assert '"knowledge_id": null' in serialized_json`
- `tests/test_official_knowledge_collection_serializer.py` line 186: `assert "café" in serialized_json`
- `tests/test_official_knowledge_collection_serializer.py` line 187: `assert json.loads(serialized_json) == (`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 1: `import json`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 34: `def _evidence(**overrides):`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 49: `def test_serializer_produces_top_level_pdf_text_evidences_key():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 57: `def test_serializer_serializes_empty_collection():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 65: `def test_serializer_serializes_one_evidence_correctly():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 99: `def test_serializer_serializes_multiple_evidences_in_order():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 118: `def test_serializer_preserves_exact_content():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 132: `def test_serializer_preserves_non_ascii_content():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 145: `assert json.loads(json_output)["pdf_text_evidences"][0]["content"] == (`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 150: `def test_serializer_preserves_newline_content():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 164: `def test_serializer_preserves_empty_content():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 176: `def test_serializer_preserves_warnings():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 193: `def test_serializer_preserves_source_path():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 205: `def test_serializer_preserves_size_bytes():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 217: `def test_serializer_preserves_page_number():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 229: `def test_serializer_preserves_extraction_index():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 241: `def test_serializer_preserves_extraction_method():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 255: `def test_serializer_preserves_evidence_index():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 267: `def test_serializer_does_not_include_forbidden_fields():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 286: `def test_to_json_output_is_deterministic():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 304: `def test_to_json_output_can_be_parsed_back_with_json_loads():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 315: `assert json.loads(json_output) == (`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 1: `import json`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 12: `def test_serializes_empty_text_extraction_evidence_collection():`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 17: `assert json.loads(result) == {`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 22: `def test_serializes_one_text_extraction_evidence():`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 35: `assert json.loads(result) == {`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 46: `def test_serializes_multiple_evidences_deterministically():`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 66: `assert json.loads(first)["evidences"] == [`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 80: `def test_preserves_non_ascii_content_with_ensure_ascii_false():`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 94: `assert json.loads(result)["evidences"][0]["content"] == (`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 99: `def test_serialized_output_contains_only_evidence_fields():`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 111: `data = json.loads(result)`
- `tests/test_text_knowledge_collection_serializer.py` line 1: `import json`
- `tests/test_text_knowledge_collection_serializer.py` line 8: `def test_serializes_empty_text_knowledge_collection():`
- `tests/test_text_knowledge_collection_serializer.py` line 13: `assert json.loads(result) == {`
- `tests/test_text_knowledge_collection_serializer.py` line 18: `def test_serializes_one_text_knowledge_item():`
- `tests/test_text_knowledge_collection_serializer.py` line 32: `assert json.loads(result) == {`
- `tests/test_text_knowledge_collection_serializer.py` line 44: `def test_serializes_multiple_text_knowledge_items_deterministically():`
- `tests/test_text_knowledge_collection_serializer.py` line 66: `assert json.loads(first)["knowledge_items"] == [`
- `tests/test_text_knowledge_collection_serializer.py` line 82: `def test_preserves_non_ascii_content_with_ensure_ascii_false():`
- `tests/test_text_knowledge_collection_serializer.py` line 99: `assert json.loads(result)["knowledge_items"][0]["content"] == content`
- `tests/test_text_knowledge_collection_serializer.py` line 102: `def test_preserves_newline_content_exactly():`
- `tests/test_text_knowledge_collection_serializer.py` line 117: `assert json.loads(result)["knowledge_items"][0]["content"] == content`
- `tests/test_text_knowledge_collection_serializer.py` line 120: `def test_preserves_evidence_index():`
- `tests/test_text_knowledge_collection_serializer.py` line 134: `assert json.loads(result)["knowledge_items"][0]["evidence_index"] == 7`
- `tests/test_text_knowledge_collection_serializer.py` line 137: `def test_serialized_output_contains_only_knowledge_fields():`
- `tests/test_text_knowledge_collection_serializer.py` line 150: `data = json.loads(result)`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 1: `import json`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 12: `def test_serializer_produces_top_level_prompt_candidates_key():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 22: `def test_serializer_serializes_one_candidate_correctly():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 50: `def test_serializer_serializes_multiple_candidates_in_order():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 90: `def test_serializer_preserves_exact_content():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 111: `def test_serializer_preserves_non_ascii_content():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 129: `assert json.loads(result)["prompt_candidates"][0]["content"] == content`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 132: `def test_serializer_preserves_newline_content():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 148: `assert json.loads(result)["prompt_candidates"][0]["content"] == content`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 151: `def test_serializer_preserves_empty_content():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 169: `def test_serializer_preserves_evidence_index():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 187: `def test_serializer_preserves_knowledge_index():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 205: `def test_serializer_does_not_include_forbidden_fields():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 255: `def test_to_json_output_is_deterministic():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 274: `def test_to_json_output_can_be_parsed_back_with_json_loads():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 288: `data = json.loads(result)`

These observations do not establish an authoritative EvidenceRepository. Existing serializers, repository-named classes, configuration objects, adapters, or write-like functions may belong to unrelated subsystems.

## 5. Authoritative repository ownership

The future authoritative interface is:

- Name: `EvidenceRepository`
- Ownership: RIE application-facing interface boundary
- Intended module: `src/rie/interfaces/evidence_repository.py`
- Implementation ownership: infrastructure adapter
- Domain ownership: none; the domain owns `AcceptedEvidence` and identity contracts, not persistence
- Knowledge coupling: prohibited
- Parser/asset coupling: prohibited

The interface must not expose database sessions, file handles, ORM entities, infrastructure exceptions, serializer implementations, or retry controls.

## 6. Repository responsibilities

The interface is responsible only for:

1. retrieving accepted factual Evidence by `evidence_id`;
2. retrieving acceptance records by `acceptance_record_id`;
3. listing acceptance records for one factual Evidence;
4. classifying one proposed write against current repository state;
5. atomically storing one new factual Evidence and its acceptance record;
6. atomically appending a new acceptance record for an existing factual Evidence;
7. returning explicit replay, collision, conflict-candidate, or failure results;
8. preserving immutable canonical digests and contract versions.

The interface is not responsible for:

- candidate construction;
- eligibility evaluation;
- identity calculation;
- materialization;
- payload parsing;
- source discovery;
- Knowledge construction;
- semantic duplicate detection;
- conflict winner selection;
- Prompt Candidate generation;
- business decisions;
- automatic retry.

## 7. EvidenceRepository method contract

The future interface contains exactly these methods:

`	ext
get_evidence(evidence_id: str) -> EvidenceLookupResult
get_acceptance_record(acceptance_record_id: str) -> AcceptanceRecordLookupResult
list_acceptance_records(evidence_id: str) -> AcceptanceRecordListResult
classify_write(request: EvidenceWriteRequest) -> EvidenceWriteClassificationResult
write(request: EvidenceWriteRequest) -> EvidenceWriteResult
`

No update, delete, replace, upsert, merge, compact, or bulk-write method is approved.

`write` must perform the same classification rules as `classify_write` inside its atomic transaction. A prior classification result is advisory and must not be trusted after concurrent repository changes.

## 8. EvidenceWriteRequest contract

| Field | Type | Required | Rule |
|---|---|---:|---|
| `accepted_evidence` | `AcceptedEvidence` | Yes | Structurally valid PR-023C contract |
| `canonical_evidence_bytes_digest` | `str` | Yes | Canonical factual bytes digest from PR-023D |
| `acceptance_record` | immutable acceptance record | Yes | Must match the accepted Evidence materialization record |
| `canonical_acceptance_bytes_digest` | `str` | Yes | Canonical governance bytes digest |
| `repository_contract_version` | `str` | Yes | Explicit supported interface version |
| `expected_identity_policy_id` | `str` | Yes | Must match the accepted Evidence |
| `expected_identity_policy_version` | `str` | Yes | Must match the accepted Evidence |

The request contains no repository adapter, database session, transaction handle, retry count, clock, parser, file handle, Knowledge object, or Prompt Candidate.

## 9. EvidenceLookupResult contract

| Field | Type | Required | Rule |
|---|---|---:|---|
| `status` | `found`, `not_found`, or `failed` | Yes | Explicit outcome |
| `accepted_evidence` | `AcceptedEvidence` or null | Yes | Present only for `found` |
| `canonical_evidence_bytes_digest` | `str` or null | Yes | Present only for `found` |
| `acceptance_record_ids` | `tuple[str, ...]` | Yes | May be empty only when not found/failed |
| `reason_codes` | `tuple[str, ...]` | Yes | Explicit |
| `diagnostics` | immutable tuple | Yes | No infrastructure exception objects |

Lookup does not mutate access timestamps, counters, record order, or Evidence content.

## 10. AcceptanceRecordLookupResult contract

| Field | Type | Required | Rule |
|---|---|---:|---|
| `status` | `found`, `not_found`, or `failed` | Yes | Explicit outcome |
| `acceptance_record` | immutable acceptance record or null | Yes | Present only for `found` |
| `canonical_acceptance_bytes_digest` | `str` or null | Yes | Present only for `found` |
| `evidence_id` | `str` or null | Yes | Present only for `found` |
| `reason_codes` | `tuple[str, ...]` | Yes | Explicit |
| `diagnostics` | immutable tuple | Yes | Infrastructure-neutral |

## 11. AcceptanceRecordListResult contract

| Field | Type | Required | Rule |
|---|---|---:|---|
| `status` | `found`, `not_found`, or `failed` | Yes | Explicit |
| `evidence_id` | `str` | Yes | Requested identity |
| `acceptance_records` | immutable ordered tuple | Yes | Ordered by canonical governance key, not insertion timestamp |
| `reason_codes` | `tuple[str, ...]` | Yes | Explicit |
| `diagnostics` | immutable tuple | Yes | Infrastructure-neutral |

Pagination is not approved in this phase because repository implementation and expected scale are not yet reviewed. A later review may add pagination without changing Evidence identity.

## 12. EvidenceWriteClassificationResult contract

| Field | Type | Required | Rule |
|---|---|---:|---|
| `classification` | controlled classification token | Yes | One PR-023D classification |
| `evidence_id` | `str` | Yes | Requested factual identity |
| `acceptance_record_id` | `str` | Yes | Requested governance identity |
| `existing_evidence_digest` | `str` or null | Yes | Present when factual identity exists |
| `existing_acceptance_digest` | `str` or null | Yes | Present when governance identity exists |
| `reason_codes` | `tuple[str, ...]` | Yes | Explicit |
| `diagnostics` | immutable tuple | Yes | No mutation |

Controlled classification tokens:

- `new_evidence`
- `exact_replay`
- `governance_replay`
- `same_fact_new_acceptance`
- `identity_collision`
- `acceptance_collision`
- `semantic_duplicate_candidate`
- `conflicting_evidence_candidate`
- `superseding_evidence_candidate`
- `rejected`

The repository does not determine semantic equivalence itself. The three candidate classifications require an explicit pre-existing governance marker supplied by a later reviewed workflow; otherwise the repository treats the request by deterministic identity only.

## 13. EvidenceWriteResult contract

| Field | Type | Required | Rule |
|---|---|---:|---|
| `status` | controlled write status | Yes | Explicit outcome |
| `classification` | controlled classification token | Yes | Final in-transaction classification |
| `evidence_id` | `str` | Yes | Requested factual identity |
| `acceptance_record_id` | `str` | Yes | Requested governance identity |
| `mutation_performed` | `bool` | Yes | Explicit |
| `reason_codes` | `tuple[str, ...]` | Yes | Explicit |
| `diagnostics` | immutable tuple | Yes | Infrastructure-neutral |

Controlled write statuses:

- `inserted_new_evidence`
- `appended_acceptance_record`
- `unchanged_exact_replay`
- `unchanged_governance_replay`
- `rejected_identity_collision`
- `rejected_acceptance_collision`
- `rejected_invalid_request`
- `failed_repository_operation`

No ambiguous `success` or silent upsert result is allowed.

## 14. Exact write semantics

### 14.1 New factual Evidence

For `new_evidence`:

1. verify the factual key is absent;
2. verify the governance key is absent;
3. insert immutable factual Evidence;
4. insert its acceptance record;
5. commit both atomically;
6. return `inserted_new_evidence` with `mutation_performed=True`.

A partial factual insert without its acceptance record is forbidden.

### 14.2 Exact replay

For `exact_replay`:

- perform no mutation;
- preserve original bytes and metadata;
- return `unchanged_exact_replay`;
- set `mutation_performed=False`.

### 14.3 Governance replay

For `governance_replay`:

- perform no mutation;
- return `unchanged_governance_replay`;
- set `mutation_performed=False`.

### 14.4 Same fact, new acceptance

For `same_fact_new_acceptance`:

1. preserve existing factual Evidence unchanged;
2. verify the new acceptance key is absent;
3. append one immutable acceptance record atomically;
4. return `appended_acceptance_record` with `mutation_performed=True`.

### 14.5 Collisions

For factual or acceptance collisions:

- reject;
- perform no mutation;
- return both existing and requested canonical digests in diagnostics;
- never overwrite;
- never generate a replacement ID;
- never retry automatically.

## 15. Transaction and atomicity expectations

The infrastructure adapter owns transaction mechanics.

Required guarantees:

- classification and mutation occur in one transaction;
- unique-key checks and inserts are atomic;
- new factual Evidence plus first acceptance record commit together;
- collision detection sees a consistent snapshot;
- a failed transaction leaves no partial mutation;
- commit failure returns `failed_repository_operation`;
- rollback failure is surfaced explicitly;
- no hidden second attempt;
- no retry loop;
- no last-write-wins.

The interface does not prescribe a specific database, file format, ORM, or storage engine.

## 16. Concurrency behavior

Concurrent identical requests must result in:

- one insertion and one idempotent replay, or
- two deterministic replay results after one committed insertion.

Concurrent conflicting requests for the same identity must result in:

- at most one committed canonical record;
- explicit collision rejection for the non-equivalent request;
- no overwrite;
- no merged record;
- no generated suffix.

Concurrency control may use transactions, locks, compare-and-set, or unique constraints, but the exact technology is deferred to implementation review.

## 17. Persistence model requirements

A future persistence adapter must represent at least two logical record sets.

### 17.1 Accepted Evidence records

Required persisted values:

- `evidence_id` primary factual key;
- accepted-Evidence contract version;
- complete immutable accepted-Evidence snapshot;
- canonical evidence bytes digest;
- identity policy identifier/version;
- canonicalization version;
- creation persistence audit metadata separate from Evidence identity.

### 17.2 Acceptance records

Required persisted values:

- `acceptance_record_id` primary governance key;
- `evidence_id` foreign/reference key;
- complete immutable acceptance record;
- canonical acceptance bytes digest;
- governance identity policy/version;
- persistence audit metadata separate from governance identity.

No Knowledge, Prompt Candidate, semantic summary, source file bytes, parser output stream, or mutable runtime object belongs in these record sets.

## 18. Interface versus infrastructure ownership

| Concern | Interface/application boundary | Infrastructure adapter |
|---|---|---|
| Accepted input/result contracts | Owns | Implements |
| Classification vocabulary | Owns | Enforces |
| Identity semantics | Receives from PR-023D | Must not recalculate differently |
| Transaction implementation | Does not expose | Owns |
| Storage schema/format | Does not prescribe | Owns after approval |
| Unique constraints | Requires semantics | Implements |
| Serialization | Defines canonical preservation requirement | Implements exact storage encoding |
| Infrastructure exceptions | Must not expose | Maps to controlled diagnostics |
| Retry | Prohibited by default | Must not hide |
| Logging/metrics | Outside identity | May implement without mutating records |
| Knowledge coupling | Prohibited | Prohibited |

## 19. Serialization boundary

Persistence serialization is not factual identity canonicalization.

Rules:

1. the adapter stores the approved canonical digest;
2. storage encoding may differ from identity canonical JSON only when round-trip preservation is exact;
3. deserialization must reproduce the same immutable contract values;
4. field loss, coercion, reordering of semantic tuples, timezone loss, Unicode drift, and float drift are forbidden;
5. serializer version must be explicit;
6. serializer migration must not change `evidence_id`;
7. storage compression must be transparent;
8. storage encryption must not alter domain identity;
9. serializers do not calculate authority, eligibility, Knowledge, or Prompt content.

## 20. Error model

Controlled repository reason codes include:

- `evidence_not_found`
- `acceptance_record_not_found`
- `request_contract_unsupported`
- `identity_policy_mismatch`
- `evidence_digest_mismatch`
- `acceptance_digest_mismatch`
- `exact_replay_detected`
- `governance_replay_detected`
- `same_fact_new_acceptance`
- `identity_collision_detected`
- `acceptance_collision_detected`
- `transaction_begin_failed`
- `transaction_commit_failed`
- `transaction_rollback_failed`
- `storage_read_failed`
- `storage_write_failed`
- `serialization_failed`
- `deserialization_failed`
- `repository_unavailable`

Raw database error objects, file-system exceptions, credentials, connection strings, and stack traces must not cross the interface.

## 21. No-retry behavior

The repository interface performs exactly one operation attempt per method call.

Forbidden:

- hidden transaction retries;
- reconnect loops;
- exponential backoff;
- silent fallback storage;
- in-memory fallback after persistence failure;
- queueing without explicit result;
- swallowing transient errors;
- converting failure into replay.

Any future retry policy must be an explicit outer application concern reviewed separately.

## 22. Immutability and lifecycle

Accepted Evidence and acceptance records are append-only.

Not approved:

- update;
- patch;
- replace;
- delete;
- purge;
- compact;
- mutable status flags;
- latest-record overwrite;
- soft delete inside Evidence;
- authority mutation;
- lifecycle mutation.

Correction, conflict, and supersession use new immutable records and explicit relationships in a later boundary.

## 23. Retrieval ordering

Acceptance records for one Evidence identity are ordered deterministically by `acceptance_record_id`.

Insertion time is not the default ordering because clock and storage timing are not governance authority.

A caller may later request alternate explicit ordering only through a separately reviewed query contract.

## 24. Knowledge governance boundary

Knowledge construction remains prohibited from:

- reading repository infrastructure directly;
- reading database rows or files directly;
- consuming `EvidenceCandidate`;
- consuming failed/rejected write results;
- treating replay as new Evidence;
- selecting one conflicting Evidence silently;
- using persistence order as authority;
- creating Knowledge during repository write.

A future Knowledge construction boundary may consume only explicitly retrieved accepted Evidence through an approved application service after Phase 23 readiness reassessment.

## 25. Security and integrity boundary

The adapter must eventually support:

- integrity verification against stored canonical digests;
- fail-closed deserialization;
- no credential exposure through domain results;
- no path traversal in file-backed storage;
- no mutable shared object references;
- explicit corruption diagnostics;
- no automatic repair or record rewriting.

Encryption, access control, backup, and disaster recovery are important but outside this interface contract and require later infrastructure review.

## 26. Options reviewed

### Option A — Repository returns ORM/database entities

**Rejected.** This leaks infrastructure into application and domain boundaries.

### Option B — Repository uses generic `save` or `upsert`

**Rejected.** Generic mutation hides replay, collision, and append-only semantics.

### Option C — File serializer acts as the repository interface

**Rejected.** Serialization does not define transaction, identity, concurrency, or idempotency behavior.

### Option D — Repository calculates identity and materializes Evidence

**Rejected.** This collapses PR-023C and PR-023D boundaries into persistence.

### Option E — Explicit EvidenceRepository interface with controlled requests/results and deferred adapter

**Selected.** This preserves accepted Evidence, identity, idempotency, and infrastructure separation.

## 27. Final architecture decision

# EVIDENCE REPOSITORY INTERFACE AND PERSISTENCE BOUNDARY APPROVED; IMPLEMENTATION DEFERRED

The EvidenceRepository interface, request/result contracts, classification mapping, transaction expectations, concurrency behavior, append-only persistence model, serialization boundary, error model, and no-retry behavior are approved at documentation level.

No repository implementation, adapter, serializer, migration, database, file store, or test is authorized by this gate.

## 28. Exact next safe gate

**PR-023F - Accepted Evidence Prerequisite Closure and Knowledge Governance Readiness Reassessment**

Type: **Documentation-only**

The next gate must reassess, without coding:

1. whether PR-023C accepted-Evidence contract is sufficiently closed;
2. whether PR-023D identity/idempotency contract is sufficiently closed;
3. whether PR-023E repository boundary is sufficiently closed;
4. remaining compatibility risks with historical Evidence/Knowledge modules;
5. whether materialization and repository implementation should precede Knowledge governance;
6. whether Phase 23 should remain deferred;
7. exact next implementation or review gate;
8. exactly one final decision;
9. exactly one next gate.

## 29. Acceptance assessment

| Acceptance area | Result |
|---|---|
| PR-023D commit/push checkpoint | PASSED |
| Phase 22 branch/tag preservation | PASSED |
| Sandbox/temp preservation | PASSED |
| Read-only repository/interface inspection | PASSED |
| Exact interface methods | PASSED |
| Write/lookup result contracts | PASSED |
| Replay/collision mapping | PASSED |
| Transaction/atomicity expectations | PASSED |
| Concurrency behavior | PASSED |
| Persistence record-set boundary | PASSED |
| Interface/infrastructure ownership | PASSED |
| Serialization boundary | PASSED |
| Error and no-retry behavior | PASSED |
| Append-only lifecycle | PASSED |
| Knowledge boundary | PASSED |
| Five architecture options | PASSED |
| Exactly one final decision | PASSED — `EVIDENCE REPOSITORY INTERFACE AND PERSISTENCE BOUNDARY APPROVED; IMPLEMENTATION DEFERRED` |
| Exactly one next review-only gate | PASSED |
| Code/test/asset boundary | PASSED |

## 30. Action truth table

| Action | Performed |
|---|---|
| Read-only checkpoint verification | True |
| Read-only repository/interface/infrastructure inspection | True |
| One repository review document created | True |
| One external output created | True |
| Production code modified | False |
| Test code modified | False |
| Tests executed | False |
| Project Python interpreter executed | False |
| Dependency/venv/pyproject/config changed | False |
| PDF/image/OCR/parser/ingestion executed | False |
| Real asset processed | False |
| Accepted Evidence created | False |
| Identity implementation created | False |
| EvidenceRepository implementation created | False |
| Persistence adapter created | False |
| Serializer or migration created | False |
| Database/file store created | False |
| EvidenceRelationship created | False |
| Knowledge or Prompt Candidate created | False |
| AI/LLM inference executed | False |
| Repository file staged | False |
| Commit created | False |
| Push performed | False |
| Merge/history rewrite performed | False |
| Tag action performed | False |
| Automatic retry performed | False |

## 31. Gate conclusion

PR-023E concludes **EVIDENCE REPOSITORY INTERFACE AND PERSISTENCE BOUNDARY APPROVED; IMPLEMENTATION DEFERRED**.

Only `PR-023F - Accepted Evidence Prerequisite Closure and Knowledge Governance Readiness Reassessment` is recommended. No production implementation is authorized.
