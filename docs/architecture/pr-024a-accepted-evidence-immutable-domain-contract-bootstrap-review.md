# PR-024A — AcceptedEvidence Immutable Domain Contract Bootstrap Review

## 1. Gate identity

| Item | Value |
|---|---|
| Repository | `D:\PROJECT\RIE` |
| Branch | `phase-024-accepted-evidence-implementation` |
| Reviewed HEAD | `96fbbea9067a84635e1df8ff5e1a4f5b90270205` |
| Gate type | Documentation-only |
| Final decision | **PHASE 24 BOOTSTRAP BOUNDARY APPROVED; ACCEPTED EVIDENCE IMMUTABLE DOMAIN CONTRACT IMPLEMENTATION AUTHORIZED AS THE NEXT CONTROLLED GATE** |
| Next gate | **PR-024B - AcceptedEvidence Immutable Domain Contract Implementation** |
| Next gate type | **Implementation** |

## 2. Purpose

PR-024A establishes the first implementation boundary for Phase 24 without creating production or test code.

The review confirms the exact closed Phase 23 checkpoint, preserves prior phase references, inspects repository conventions, fixes the implementation file scope, and limits the next gate to the immutable `AcceptedEvidence` domain contract plus focused tests.

## 3. Verified Phase 24 entry checkpoint

Verified:

- current branch: `phase-024-accepted-evidence-implementation`;
- local/tracking/remote Phase 24 HEAD: `96fbbea9067a84635e1df8ff5e1a4f5b90270205`;
- local/tracking/remote `main` HEAD: `96fbbea9067a84635e1df8ff5e1a4f5b90270205`;
- local/tracking/remote Phase 23 branch: `96fbbea9067a84635e1df8ff5e1a4f5b90270205`;
- Phase 24 divergence: `0 0`;
- Phase 24 versus main divergence: `0 0`;
- working tree clean before document creation.

Phase 24 therefore begins from the exact published Phase 23 closure checkpoint.

## 4. Preserved closure references

Phase 23 tag:

- name: `v0.23.0-rcis-accepted-evidence-prerequisite-contract-review-phase`;
- type: annotated tag;
- object: `caa43202d3095bc779415846024582550d4554dc`;
- peeled target: `96fbbea9067a84635e1df8ff5e1a4f5b90270205`;
- annotation: `RCIS Phase 23 - Accepted Evidence Prerequisite Contract Review`.

Phase 22 remains preserved:

- branch target: `e41269e764979f94f23f93692136c63cc603f2e2`;
- tag: `v0.22.0-rcis-evidence-candidate-boundary-phase`;
- tag object: `1a7488e7cc2830aea2506182e6a6aba797cbebcf`;
- peeled target: `e41269e764979f94f23f93692136c63cc603f2e2`.

The controlled PDF sandbox and `D:\PROJECT\pytest-temp` remain empty. Real and synthetic PDF targets remain absent.

## 5. Governing architecture documents

| Gate | Document | Lines | Bytes | SHA-256 |
|---|---|---:|---:|---|
| PR-023C | `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` | 638 | 31378 | `6459c0309242ed1d08b0cd4d6bb5ba1dd70ca356199b5c7ee0f02c3348b5457c` |
| PR-023D | `docs/architecture/pr-023d-deterministic-evidence-identity-and-idempotency-contract-review.md` | 603 | 26716 | `8ed9ad0023759047b6ca5372fe763ce6b8dc608a1ea1139f1145492cd05f8dbb` |
| PR-023E | `docs/architecture/pr-023e-evidence-repository-interface-and-persistence-boundary-review.md` | 1001 | 68531 | `07088e8777aaedc3d033c9eb72902d95b3430e4d2a13a516caf52bf8ee7e6e08` |
| PR-023F | `docs/architecture/pr-023f-accepted-evidence-prerequisite-closure-and-knowledge-governance-readiness-reassessment.md` | 450 | 18555 | `68c090bc323f42f31043be27879c2ea580dce055bf64b4a1a97b2bc65808594c` |
| PR-023G | `docs/architecture/pr-023g-phase-23-closure-and-accepted-evidence-implementation-phase-entry-review.md` | 364 | 15251 | `53fcce12f89c01201629940ac3290b0ee0f2ce882998819c2318ef7110c58a1d` |
| PR-023H | `docs/architecture/pr-023h-phase-23-controlled-merge-and-tag-readiness-review.md` | 322 | 13264 | `2c02f9ce11cca246319f567afd7dfc653bfdee16aed666dafc31e35c4c04e742` |

These documents remain authoritative for the first implementation slice.

## 6. Existing repository evidence surfaces

- `src/collection/evidence_collection.py`
- `src/collection/evidence_collector.py`
- `src/collection/pdf_text_extraction_evidence_collection.py`
- `src/collection/pdf_text_extraction_evidence_collection_serializer.py`
- `src/collection/pdf_text_extraction_evidence_collector.py`
- `src/collection/text_extraction_evidence_artifact_inspector.py`
- `src/collection/text_extraction_evidence_collection.py`
- `src/collection/text_extraction_evidence_collection_serializer.py`
- `src/collection/text_extraction_evidence_collector.py`
- `src/evidence/evidence.py`
- `src/evidence/evidence_builder.py`
- `src/evidence/pdf_text_extraction_evidence.py`
- `src/evidence/pdf_text_extraction_evidence_artifact_inspector.py`
- `src/evidence/pdf_text_extraction_evidence_builder.py`
- `src/evidence/text_extraction_evidence.py`
- `src/evidence/text_extraction_evidence_builder.py`
- `src/official_source/official_source_evidence_eligibility_gate.py`
- `src/official_source/official_source_evidence_eligibility_policy.py`
- `src/official_source/official_source_evidence_workflow_gate.py`
- `src/official_source/official_source_evidence_workflow_preflight.py`
- `src/rie/application/evidence_candidate.py`
- `src/rie/extraction/export_pdf_text_evidence.py`
- `src/rie/extraction/export_text_extraction_evidence.py`
- `src/rie/extraction/inspect_pdf_text_evidence.py`
- `src/rie/extraction/inspect_text_extraction_evidence.py`
- `src/rie/official_source/inspect_evidence_eligibility.py`
- `tests/application/test_evidence_candidate.py`
- `tests/extraction/test_export_pdf_text_evidence.py`
- `tests/extraction/test_export_text_extraction_evidence.py`
- `tests/extraction/test_inspect_pdf_text_evidence.py`
- `tests/extraction/test_inspect_text_extraction_evidence.py`
- `tests/extraction/test_pdf_text_evidence_smoke_flow.py`
- `tests/extraction/test_text_extraction_evidence_smoke_flow.py`
- `tests/test_evidence_builder.py`
- `tests/test_evidence_collector.py`
- `tests/test_inspect_evidence_eligibility_cli.py`
- `tests/test_official_source_evidence_eligibility_gate.py`
- `tests/test_official_source_evidence_eligibility_policy.py`
- `tests/test_official_source_evidence_workflow_gate.py`
- `tests/test_official_source_evidence_workflow_preflight.py`
- `tests/test_pdf_text_extraction_evidence.py`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py`
- `tests/test_pdf_text_extraction_evidence_builder.py`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py`
- `tests/test_pdf_text_extraction_evidence_collector.py`
- `tests/test_text_extraction_evidence_artifact_inspector.py`
- `tests/test_text_extraction_evidence_builder.py`
- `tests/test_text_extraction_evidence_collection_serializer.py`
- `tests/test_text_extraction_evidence_collector.py`

These paths are compatibility surfaces. They are not automatically reusable as the new accepted-Evidence domain contract.

The existing Phase 22 candidate files remain:

- `src/rie/application/evidence_candidate.py` — SHA-256 `b42bdd6da7ea8fb3e5c293a7760c22a6a302ac2c9f0c693653e206bc870df894`;
- `tests/application/test_evidence_candidate.py` — SHA-256 `1039d2965bc20da7e6e76b7b0cc8738dd76a0fb6d62dd61022660f9870feb947`.

`EvidenceCandidate` remains an application DTO and must not be renamed, replaced, or promoted automatically.

## 7. Existing domain package observations

Source-domain paths:

- None found.

Domain-test paths:

- None found.

Package-marker observations:

| Observation | Result |
|---|---|
| `src/rie/__init__.py` exists | `False` |
| `src/rie/application/__init__.py` exists | `True` |
| `tests/__init__.py` exists | `False` |
| `tests/application/__init__.py` exists | `False` |
| `src/rie/domain` exists | `False` |
| `src/rie/domain/__init__.py` exists | `False` |
| `tests/domain` exists | `False` |
| `tests/domain/__init__.py` exists | `False` |
| Production package marker required by current convention | `True` |
| Test package marker required by current convention | `False` |

## 8. Approved exact implementation file scope

The next implementation gate may create or modify exactly these files:

- `src/rie/domain/__init__.py`
- `src/rie/domain/accepted_evidence.py`
- `tests/domain/test_accepted_evidence.py`

No other repository file is authorized by PR-024A.

Any mismatch between this file list and the next implementation proposal requires STOP and a new review.

## 9. Repository convention observations

### 9.1 Dataclass and contract conventions

- `src/rie/application/asset.py` line 1: `from dataclasses import dataclass`
- `src/rie/application/batch.py` line 1: `from dataclasses import dataclass`
- `src/rie/application/evidence_candidate.py` line 3: `from dataclasses import dataclass`
- `src/rie/application/evidence_candidate.py` line 33: `@dataclass(frozen=True)`
- `src/rie/application/metadata.py` line 1: `from dataclasses import dataclass`
- `src/rie/application/metadata.py` line 4: `@dataclass(frozen=True)`
- `src/rie/core/state.py` line 1: `from dataclasses import dataclass`
- `src/rie/extraction/pdf_page_text_extraction.py` line 1: `from dataclasses import dataclass`
- `src/rie/extraction/pdf_page_text_extraction.py` line 4: `@dataclass(frozen=True)`
- `src/rie/extraction/pdf_text_extraction_artifact_inspector.py` line 1: `from dataclasses import dataclass`
- `src/rie/extraction/pdf_text_extraction_artifact_inspector.py` line 52: `@dataclass(frozen=True)`
- `src/rie/extraction/pdf_text_extraction_report.py` line 1: `from dataclasses import dataclass`
- `src/rie/extraction/pdf_text_extraction_report.py` line 6: `@dataclass(frozen=True)`
- `src/rie/extraction/pdf_text_extraction_report.py` line 13: `@dataclass(frozen=True)`
- `src/rie/extraction/text_asset_extraction.py` line 1: `from dataclasses import dataclass`
- `src/rie/extraction/text_asset_extraction.py` line 5: `@dataclass(frozen=True)`
- `src/rie/extraction/text_asset_extraction_report.py` line 1: `from dataclasses import dataclass`
- `src/rie/extraction/text_asset_extraction_report.py` line 6: `@dataclass(frozen=True)`
- `src/rie/infrastructure/repository_config.py` line 1: `from dataclasses import dataclass`
- `src/rie/ingestion/controlled_pdf_structural_metadata_contract.py` line 5: `from dataclasses import dataclass`
- `src/rie/ingestion/controlled_pdf_structural_metadata_contract.py` line 24: `@dataclass(frozen=True)`
- `src/rie/ingestion/controlled_pdf_structural_metadata_contract.py` line 25: `class ControlledPdfStructuralMetadataContractResult:`
- `src/rie/ingestion/controlled_pdf_structural_metadata_execution_contract.py` line 5: `from dataclasses import dataclass`
- `src/rie/ingestion/controlled_pdf_structural_metadata_execution_contract.py` line 18: `@dataclass(frozen=True)`
- `src/rie/ingestion/controlled_pdf_structural_metadata_execution_contract.py` line 19: `class ControlledPdfStructuralMetadataExecutionContractResult:`
- `src/rie/ingestion/controlled_pdf_structural_metadata_implementation.py` line 5: `from dataclasses import dataclass`
- `src/rie/ingestion/controlled_pdf_structural_metadata_implementation.py` line 37: `@dataclass(frozen=True)`
- `src/rie/ingestion/controlled_pdf_structural_metadata_result_contract.py` line 5: `from dataclasses import dataclass`
- `src/rie/ingestion/controlled_pdf_structural_metadata_result_contract.py` line 94: `@dataclass(frozen=True)`
- `src/rie/ingestion/controlled_pdf_structural_metadata_result_contract.py` line 103: `@dataclass(frozen=True)`
- `src/rie/ingestion/controlled_pdf_structural_metadata_result_contract.py` line 122: `@dataclass(frozen=True)`
- `src/rie/ingestion/controlled_pdf_structural_metadata_result_contract.py` line 123: `class ControlledPdfStructuralMetadataResultContractResult:`
- `src/rie/ingestion/controlled_pdf_text_extraction_contract.py` line 5: `from dataclasses import dataclass`
- `src/rie/ingestion/controlled_pdf_text_extraction_contract.py` line 16: `@dataclass(frozen=True)`
- `src/rie/ingestion/controlled_pdf_text_extraction_contract.py` line 17: `class ControlledPdfTextExtractionContractResult:`
- `src/rie/ingestion/controlled_pdf_text_extraction_execution_contract.py` line 5: `from dataclasses import dataclass`
- `src/rie/ingestion/controlled_pdf_text_extraction_execution_contract.py` line 18: `@dataclass(frozen=True)`
- `src/rie/ingestion/controlled_pdf_text_extraction_execution_contract.py` line 19: `class ControlledPdfTextExtractionExecutionContractResult:`
- `src/rie/ingestion/controlled_pdf_text_extraction_implementation.py` line 5: `from dataclasses import dataclass`
- `src/rie/ingestion/controlled_pdf_text_extraction_implementation.py` line 32: `@dataclass(frozen=True)`
- `src/rie/ingestion/controlled_pdf_text_extraction_result_contract.py` line 5: `from dataclasses import dataclass`
- `src/rie/ingestion/controlled_pdf_text_extraction_result_contract.py` line 48: `@dataclass(frozen=True)`
- `src/rie/ingestion/controlled_pdf_text_extraction_result_contract.py` line 68: `@dataclass(frozen=True)`
- `src/rie/ingestion/controlled_pdf_text_extraction_result_contract.py` line 69: `class ControlledPdfTextExtractionResultContractResult:`
- `src/rie/ingestion/controlled_real_asset_fixture_contract.py` line 5: `from dataclasses import dataclass`
- `src/rie/ingestion/controlled_real_asset_fixture_contract.py` line 18: `@dataclass(frozen=True)`
- `src/rie/ingestion/controlled_real_asset_fixture_contract.py` line 31: `@dataclass(frozen=True)`
- `src/rie/ingestion/controlled_real_asset_fixture_contract.py` line 32: `class ControlledRealAssetFixtureContractResult:`
- `src/rie/ingestion/creative_asset_scan_item.py` line 1: `from dataclasses import dataclass`
- `src/rie/ingestion/creative_asset_scan_item.py` line 7: `@dataclass(frozen=True)`
- `src/rie/ingestion/creative_asset_scan_report.py` line 1: `from dataclasses import dataclass`
- `src/rie/ingestion/creative_asset_scan_report.py` line 8: `@dataclass(frozen=True)`
- `src/rie/ingestion/creative_asset_scan_report_inspector.py` line 1: `from dataclasses import dataclass`
- `src/rie/ingestion/creative_asset_scan_report_inspector.py` line 5: `@dataclass(frozen=True)`
- `src/rie/ingestion/real_asset_dry_run_contract.py` line 1: `from dataclasses import dataclass`
- `src/rie/ingestion/real_asset_dry_run_contract.py` line 7: `@dataclass(frozen=True)`
- `src/rie/ingestion/real_asset_dry_run_contract.py` line 8: `class RealAssetDryRunResult:`
- `src/rie/ingestion/real_asset_metadata_collection_contract.py` line 1: `from dataclasses import dataclass`
- `src/rie/ingestion/real_asset_metadata_collection_contract.py` line 8: `@dataclass(frozen=True)`
- `src/rie/ingestion/real_asset_metadata_collector.py` line 1: `from dataclasses import dataclass`
- `src/rie/ingestion/real_asset_metadata_collector.py` line 11: `@dataclass(frozen=True)`
- `src/rie/ingestion/real_asset_metadata_collector.py` line 17: `@dataclass(frozen=True)`
- `src/rie/ingestion/real_asset_metadata_collector.py` line 18: `class RealAssetMetadataCollectionResult:`
- `src/rie/ingestion/real_asset_metadata_dry_run_boundary.py` line 1: `from dataclasses import dataclass`
- `src/rie/ingestion/real_asset_metadata_dry_run_boundary.py` line 6: `@dataclass(frozen=True)`
- `src/rie/ingestion/real_asset_metadata_dry_run_boundary.py` line 17: `@dataclass(frozen=True)`
- `src/rie/ingestion/real_asset_metadata_dry_run_boundary.py` line 18: `class RealAssetMetadataDryRunBoundaryResult:`
- `src/rie/ingestion/real_asset_sandbox_policy.py` line 1: `from dataclasses import dataclass`
- `src/rie/ingestion/real_asset_sandbox_policy.py` line 5: `@dataclass(frozen=True)`
- `src/rie/ingestion/real_filesystem_metadata_adapter.py` line 1: `from dataclasses import dataclass`
- `src/rie/ingestion/real_filesystem_metadata_adapter.py` line 9: `@dataclass(frozen=True)`
- `src/rie/ingestion/real_filesystem_metadata_adapter.py` line 15: `@dataclass(frozen=True)`
- `src/rie/ingestion/real_filesystem_metadata_adapter.py` line 16: `class RealFilesystemMetadataAdapterResult:`
- `src/rie/ingestion/real_filesystem_metadata_adapter_safety_contract.py` line 1: `from dataclasses import dataclass`
- `src/rie/ingestion/real_filesystem_metadata_adapter_safety_contract.py` line 4: `@dataclass(frozen=True)`
- `src/rie/ingestion/unknown_asset_header_inspector.py` line 1: `from dataclasses import dataclass`
- `src/rie/ingestion/unknown_asset_header_inspector.py` line 6: `@dataclass(frozen=True)`

### 9.2 Focused test conventions

- `tests/application/test_evidence_candidate.py` line 4: `from dataclasses import FrozenInstanceError, fields`
- `tests/application/test_evidence_candidate.py` line 43: `def test_valid_construction_with_all_18_required_fields() -> None:`
- `tests/application/test_evidence_candidate.py` line 46: `assert len(fields(candidate)) == 18`
- `tests/application/test_evidence_candidate.py` line 49: `def test_exact_field_values_are_preserved() -> None:`
- `tests/application/test_evidence_candidate.py` line 52: `assert tuple(getattr(candidate, field.name) for field in fields(candidate)) == (`
- `tests/application/test_evidence_candidate.py` line 74: `def test_frozen_assignment_is_rejected() -> None:`
- `tests/application/test_evidence_candidate.py` line 77: `with pytest.raises(FrozenInstanceError):`
- `tests/application/test_evidence_candidate.py` line 81: `def test_equality_for_identical_values() -> None:`
- `tests/application/test_evidence_candidate.py` line 82: `assert _candidate() == _candidate()`
- `tests/application/test_evidence_candidate.py` line 85: `def test_inequality_when_one_field_changes() -> None:`
- `tests/application/test_evidence_candidate.py` line 89: `def test_mutable_warnings_list_is_rejected() -> None:`
- `tests/application/test_evidence_candidate.py` line 90: `with pytest.raises(ValueError, match="warnings"):`
- `tests/application/test_evidence_candidate.py` line 94: `def test_mutable_errors_list_is_rejected() -> None:`
- `tests/application/test_evidence_candidate.py` line 95: `with pytest.raises(ValueError, match="errors"):`
- `tests/application/test_evidence_candidate.py` line 99: `def test_mutable_locator_list_is_rejected() -> None:`
- `tests/application/test_evidence_candidate.py` line 100: `with pytest.raises(ValueError, match="locator"):`
- `tests/application/test_evidence_candidate.py` line 104: `def test_invalid_locator_entry_shape_is_rejected() -> None:`
- `tests/application/test_evidence_candidate.py` line 108: `with pytest.raises(ValueError, match="locator"):`
- `tests/application/test_evidence_candidate.py` line 112: `def test_duplicate_locator_key_is_rejected() -> None:`
- `tests/application/test_evidence_candidate.py` line 113: `with pytest.raises(ValueError, match="duplicate"):`
- `tests/application/test_evidence_candidate.py` line 119: `def test_unordered_locator_keys_are_rejected() -> None:`
- `tests/application/test_evidence_candidate.py` line 120: `with pytest.raises(ValueError, match="ordered"):`
- `tests/application/test_evidence_candidate.py` line 124: `def test_non_string_locator_key_is_rejected() -> None:`
- `tests/application/test_evidence_candidate.py` line 125: `with pytest.raises(ValueError, match="locator"):`
- `tests/application/test_evidence_candidate.py` line 129: `def test_boolean_locator_value_is_rejected() -> None:`
- `tests/application/test_evidence_candidate.py` line 130: `with pytest.raises(ValueError, match="page_index"):`
- `tests/application/test_evidence_candidate.py` line 134: `def test_non_finite_locator_float_is_rejected() -> None:`
- `tests/application/test_evidence_candidate.py` line 143: `with pytest.raises(ValueError, match="locator"):`
- `tests/application/test_evidence_candidate.py` line 147: `def test_empty_required_strings_are_rejected() -> None:`
- `tests/application/test_evidence_candidate.py` line 167: `with pytest.raises(ValueError, match=field_name):`
- `tests/application/test_evidence_candidate.py` line 171: `def test_whitespace_only_required_strings_are_rejected() -> None:`
- `tests/application/test_evidence_candidate.py` line 191: `with pytest.raises(ValueError, match=field_name):`
- `tests/application/test_evidence_candidate.py` line 195: `def test_leading_or_trailing_whitespace_is_rejected() -> None:`
- `tests/application/test_evidence_candidate.py` line 197: `with pytest.raises(ValueError, match="source_id"):`
- `tests/application/test_evidence_candidate.py` line 201: `def test_control_or_newline_characters_are_rejected() -> None:`
- `tests/application/test_evidence_candidate.py` line 203: `with pytest.raises(ValueError, match="source_id"):`
- `tests/application/test_evidence_candidate.py` line 207: `def test_invalid_execution_timestamp_is_rejected() -> None:`
- `tests/application/test_evidence_candidate.py` line 208: `with pytest.raises(ValueError, match="execution_timestamp"):`
- `tests/application/test_evidence_candidate.py` line 212: `def test_timezone_naive_timestamp_is_rejected() -> None:`
- `tests/application/test_evidence_candidate.py` line 213: `with pytest.raises(ValueError, match="execution_timestamp"):`
- `tests/application/test_evidence_candidate.py` line 217: `def test_valid_uppercase_z_timestamp_is_accepted() -> None:`
- `tests/application/test_evidence_candidate.py` line 220: `assert candidate.execution_timestamp == "2026-07-12T12:34:56Z"`
- `tests/application/test_evidence_candidate.py` line 223: `def test_valid_offset_timestamp_is_accepted() -> None:`
- `tests/application/test_evidence_candidate.py` line 226: `assert _candidate(execution_timestamp=timestamp).execution_timestamp == timestamp`
- `tests/application/test_evidence_candidate.py` line 229: `def test_invalid_json_is_rejected() -> None:`
- `tests/application/test_evidence_candidate.py` line 230: `with pytest.raises(ValueError, match="raw_payload"):`
- `tests/application/test_evidence_candidate.py` line 234: `def test_duplicate_json_keys_are_rejected() -> None:`
- `tests/application/test_evidence_candidate.py` line 235: `with pytest.raises(ValueError, match="duplicate"):`
- `tests/application/test_evidence_candidate.py` line 239: `def test_nan_json_is_rejected() -> None:`
- `tests/application/test_evidence_candidate.py` line 240: `with pytest.raises(ValueError, match="finite"):`
- `tests/application/test_evidence_candidate.py` line 244: `def test_infinity_json_is_rejected() -> None:`
- `tests/application/test_evidence_candidate.py` line 246: `with pytest.raises(ValueError, match="finite"):`
- `tests/application/test_evidence_candidate.py` line 250: `def test_overflow_produced_non_finite_json_number_is_rejected() -> None:`
- `tests/application/test_evidence_candidate.py` line 251: `with pytest.raises(ValueError, match="finite"):`
- `tests/application/test_evidence_candidate.py` line 255: `def test_non_canonical_json_is_rejected() -> None:`
- `tests/application/test_evidence_candidate.py` line 257: `with pytest.raises(ValueError, match="canonical"):`
- `tests/application/test_evidence_candidate.py` line 261: `def test_canonical_json_is_accepted() -> None:`
- `tests/application/test_evidence_candidate.py` line 262: `assert _candidate(raw_payload='{"a":1,"b":2}').raw_payload == '{"a":1,"b":2}'`
- `tests/application/test_evidence_candidate.py` line 265: `def test_raw_payload_is_preserved_exactly() -> None:`
- `tests/application/test_evidence_candidate.py` line 268: `assert candidate.raw_payload == '"ข้อมูล"'`
- `tests/application/test_evidence_candidate.py` line 271: `def test_invalid_checksum_characters_are_rejected() -> None:`
- `tests/application/test_evidence_candidate.py` line 272: `with pytest.raises(ValueError, match="source_checksum"):`
- `tests/application/test_evidence_candidate.py` line 276: `def test_odd_length_checksum_is_rejected() -> None:`
- `tests/application/test_evidence_candidate.py` line 277: `with pytest.raises(ValueError, match="source_checksum"):`
- `tests/application/test_evidence_candidate.py` line 281: `def test_lowercase_hexadecimal_checksum_is_accepted() -> None:`
- `tests/application/test_evidence_candidate.py` line 282: `assert _candidate(source_checksum="abcdef01").source_checksum == "abcdef01"`
- `tests/application/test_evidence_candidate.py` line 285: `def test_source_reference_causes_no_filesystem_access(monkeypatch) -> None:`
- `tests/application/test_evidence_candidate.py` line 293: `assert candidate.source_reference == "missing://synthetic/source"`
- `tests/application/test_evidence_candidate.py` line 296: `def test_dto_does_not_calculate_checksum(monkeypatch) -> None:`
- `tests/application/test_evidence_candidate.py` line 302: `assert _candidate().source_checksum == "a0b1c2d3"`
- `tests/application/test_evidence_candidate.py` line 305: `def test_no_default_current_timestamp_exists() -> None:`
- `tests/application/test_evidence_candidate.py` line 313: `def test_candidate_contains_no_eligibility_fields() -> None:`
- `tests/application/test_evidence_candidate.py` line 321: `def test_candidate_contains_no_evidence_id() -> None:`
- `tests/application/test_evidence_candidate.py` line 328: `def test_candidate_contains_no_knowledge_fields() -> None:`
- `tests/application/test_evidence_candidate.py` line 336: `def test_candidate_creates_no_evidence_or_collection_insertion() -> None:`
- `tests/application/test_evidence_candidate.py` line 345: `def test_candidate_performs_no_persistence_parser_ingestion_or_network_call() -> None:`
- `tests/application/test_evidence_candidate.py` line 361: `def test_diagnostic_order_and_duplicates_are_preserved() -> None:`
- `tests/application/test_evidence_candidate.py` line 365: `assert candidate.warnings == diagnostics`
- `tests/application/test_evidence_candidate.py` line 366: `assert candidate.errors == diagnostics`
- `tests/application/test_evidence_candidate.py` line 369: `def test_empty_diagnostic_tuples_are_accepted() -> None:`
- `tests/application/test_evidence_candidate.py` line 372: `assert candidate.warnings == ()`
- `tests/application/test_evidence_candidate.py` line 373: `assert candidate.errors == ()`
- `tests/application/test_evidence_candidate.py` line 376: `def test_empty_or_whitespace_diagnostic_entries_are_rejected() -> None:`
- `tests/application/test_evidence_candidate.py` line 379: `with pytest.raises(ValueError, match=field_name):`
- `tests/application/test_evidence_candidate.py` line 383: `def test_construction_is_deterministic_and_direct_import_works() -> None:`
- `tests/application/test_evidence_candidate.py` line 387: `assert first == second`
- `tests/application/test_evidence_candidate.py` line 388: `assert hash(first) == hash(second)`
- `tests/application/test_evidence_candidate.py` line 389: `assert EvidenceCandidate.__module__ == "rie.application.evidence_candidate"`
- `tests/core/test_engine.py` line 19: `def test_engine_uses_injected_discovery():`
- `tests/core/test_engine.py` line 27: `def test_engine_uses_discovery_service_by_default():`
- `tests/core/test_pipeline.py` line 23: `def test_pipeline_uses_injected_batch_discovery(tmp_path, monkeypatch):`
- `tests/core/test_pipeline.py` line 36: `assert len(fake_discovery.discovered_roots) == 1`
- `tests/core/test_pipeline.py` line 37: `assert fake_discovery.discovered_roots[0].resolve() == batch_folder`
- `tests/extraction/test_export_pdf_text_evidence.py` line 72: `def test_export_pdf_text_evidence_writes_valid_artifact(`
- `tests/extraction/test_export_pdf_text_evidence.py` line 102: `assert result == 0`
- `tests/extraction/test_export_pdf_text_evidence.py` line 108: `assert set(data) == {"pdf_text_evidences"}`
- `tests/extraction/test_export_pdf_text_evidence.py` line 109: `assert data["pdf_text_evidences"] == [`
- `tests/extraction/test_export_pdf_text_evidence.py` line 123: `def test_export_pdf_text_evidence_preserves_content_variants(`
- `tests/extraction/test_export_pdf_text_evidence.py` line 157: `assert result == 0`
- `tests/extraction/test_export_pdf_text_evidence.py` line 161: `assert data["pdf_text_evidences"][0]["content"] == (`
- `tests/extraction/test_export_pdf_text_evidence.py` line 164: `assert data["pdf_text_evidences"][1]["content"] == ""`
- `tests/extraction/test_export_pdf_text_evidence.py` line 165: `assert data["pdf_text_evidences"][1]["warnings"] == [`
- `tests/extraction/test_export_pdf_text_evidence.py` line 170: `def test_export_pdf_text_evidence_preserves_order_and_evidence_index(`
- `tests/extraction/test_export_pdf_text_evidence.py` line 203: `assert result == 0`
- `tests/extraction/test_export_pdf_text_evidence.py` line 204: `assert [record["source_path"] for record in records] == [`
- `tests/extraction/test_export_pdf_text_evidence.py` line 208: `assert [record["page_number"] for record in records] == [5, 6]`
- `tests/extraction/test_export_pdf_text_evidence.py` line 209: `assert [record["extraction_index"] for record in records] == [10, 11]`
- `tests/extraction/test_export_pdf_text_evidence.py` line 210: `assert [record["evidence_index"] for record in records] == [0, 1]`
- `tests/extraction/test_export_pdf_text_evidence.py` line 213: `def test_export_pdf_text_evidence_skips_invalid_page_records(`
- `tests/extraction/test_export_pdf_text_evidence.py` line 240: `assert result == 0`
- `tests/extraction/test_export_pdf_text_evidence.py` line 244: `assert [record["source_path"] for record in records] == [`
- `tests/extraction/test_export_pdf_text_evidence.py` line 248: `assert [record["evidence_index"] for record in records] == [0, 1]`
- `tests/extraction/test_export_pdf_text_evidence.py` line 251: `def test_export_pdf_text_evidence_allows_empty_output(`
- `tests/extraction/test_export_pdf_text_evidence.py` line 268: `assert result == 0`
- `tests/extraction/test_export_pdf_text_evidence.py` line 269: `assert data == {"pdf_text_evidences": []}`
- `tests/extraction/test_export_pdf_text_evidence.py` line 272: `def test_export_pdf_text_evidence_returns_error_for_missing_input(`
- `tests/extraction/test_export_pdf_text_evidence.py` line 286: `assert result == 1`
- `tests/extraction/test_export_pdf_text_evidence.py` line 290: `def test_export_pdf_text_evidence_returns_error_for_directory_input(`
- `tests/extraction/test_export_pdf_text_evidence.py` line 303: `assert result == 1`
- `tests/extraction/test_export_pdf_text_evidence.py` line 307: `def test_export_pdf_text_evidence_returns_error_for_invalid_json(`
- `tests/extraction/test_export_pdf_text_evidence.py` line 322: `assert result == 1`
- `tests/extraction/test_export_pdf_text_evidence.py` line 326: `def test_export_pdf_text_evidence_returns_error_for_malformed_artifact(`
- `tests/extraction/test_export_pdf_text_evidence.py` line 341: `assert result == 1`
- `tests/extraction/test_export_pdf_text_evidence.py` line 345: `def test_export_pdf_text_evidence_returns_error_for_missing_page_extractions(`
- `tests/extraction/test_export_pdf_text_evidence.py` line 360: `assert result == 1`
- `tests/extraction/test_export_pdf_text_evidence.py` line 364: `def test_export_pdf_text_evidence_returns_error_for_page_extractions_not_list(`
- `tests/extraction/test_export_pdf_text_evidence.py` line 379: `assert result == 1`
- `tests/extraction/test_export_pdf_text_evidence.py` line 383: `def test_export_pdf_text_evidence_returns_error_for_missing_output_parent(`
- `tests/extraction/test_export_pdf_text_evidence.py` line 403: `assert result == 1`
- `tests/extraction/test_export_pdf_text_evidence.py` line 407: `def test_export_pdf_text_evidence_emits_no_forbidden_structured_fields(`
- `tests/extraction/test_export_pdf_text_evidence.py` line 434: `assert result == 0`
- `tests/extraction/test_export_pdf_text_evidence.py` line 437: `assert set(record) == PDF_TEXT_EVIDENCE_FIELDS`
- `tests/extraction/test_export_pdf_text_extractions.py` line 70: `def test_export_pdf_text_extractions_exports_valid_scan_report_with_pdf_asset(`
- `tests/extraction/test_export_pdf_text_extractions.py` line 116: `assert result == 0`
- `tests/extraction/test_export_pdf_text_extractions.py` line 121: `assert data["page_extractions"][0]["content"] == (`
- `tests/extraction/test_export_pdf_text_extractions.py` line 126: `def test_export_pdf_text_extractions_creates_output_file(`
- `tests/extraction/test_export_pdf_text_extractions.py` line 149: `assert result == 0`
- `tests/extraction/test_export_pdf_text_extractions.py` line 153: `def test_export_pdf_text_extractions_output_contains_exact_top_level_keys(`
- `tests/extraction/test_export_pdf_text_extractions.py` line 178: `assert result == 0`
- `tests/extraction/test_export_pdf_text_extractions.py` line 179: `assert set(data) == {`
- `tests/extraction/test_export_pdf_text_extractions.py` line 189: `def test_export_pdf_text_extractions_preserves_root(`
- `tests/extraction/test_export_pdf_text_extractions.py` line 215: `assert result == 0`
- `tests/extraction/test_export_pdf_text_extractions.py` line 216: `assert data["root"] == root`
- `tests/extraction/test_export_pdf_text_extractions.py` line 219: `def test_export_pdf_text_extractions_uses_empty_root_when_missing(`
- `tests/extraction/test_export_pdf_text_extractions.py` line 243: `assert result == 0`
- `tests/extraction/test_export_pdf_text_extractions.py` line 244: `assert captured_inputs[0]["root"] == ""`
- `tests/extraction/test_export_pdf_text_extractions.py` line 245: `assert data["root"] == ""`
- `tests/extraction/test_export_pdf_text_extractions.py` line 248: `def test_export_pdf_text_extractions_ignores_non_pdf_assets(`
- `tests/extraction/test_export_pdf_text_extractions.py` line 289: `assert result == 0`
- `tests/extraction/test_export_pdf_text_extractions.py` line 290: `assert captured_inputs[0]["items"] == [`
- `tests/extraction/test_export_pdf_text_extractions.py` line 299: `def test_export_pdf_text_extractions_with_no_pdf_assets_succeeds_and_exports_empty_report(`
- `tests/extraction/test_export_pdf_text_extractions.py` line 330: `assert result == 0`
- `tests/extraction/test_export_pdf_text_extractions.py` line 332: `assert data == {`
- `tests/extraction/test_export_pdf_text_extractions.py` line 342: `def test_export_pdf_text_extractions_preserves_page_level_fields(`
- `tests/extraction/test_export_pdf_text_extractions.py` line 397: `assert result == 0`
- `tests/extraction/test_export_pdf_text_extractions.py` line 398: `assert data["page_extractions"] == [`
- `tests/extraction/test_export_pdf_text_extractions.py` line 420: `def test_export_pdf_text_extractions_preserves_exact_content(`
- `tests/extraction/test_export_pdf_text_extractions.py` line 468: `assert result == 0`
- `tests/extraction/test_export_pdf_text_extractions.py` line 469: `assert data["page_extractions"][0]["content"] == content`
- `tests/extraction/test_export_pdf_text_extractions.py` line 472: `def test_export_pdf_text_extractions_preserves_non_ascii_content(`
- `tests/extraction/test_export_pdf_text_extractions.py` line 521: `assert result == 0`
- `tests/extraction/test_export_pdf_text_extractions.py` line 524: `assert data["page_extractions"][0]["content"] == content`
- `tests/extraction/test_export_pdf_text_extractions.py` line 527: `def test_export_pdf_text_extractions_preserves_newline_content(`
- `tests/extraction/test_export_pdf_text_extractions.py` line 575: `assert result == 0`
- `tests/extraction/test_export_pdf_text_extractions.py` line 576: `assert data["page_extractions"][0]["content"] == content`
- `tests/extraction/test_export_pdf_text_extractions.py` line 579: `def test_export_pdf_text_extractions_preserves_empty_content_and_warnings(`
- `tests/extraction/test_export_pdf_text_extractions.py` line 627: `assert result == 0`
- `tests/extraction/test_export_pdf_text_extractions.py` line 628: `assert data["page_extractions"][0]["content"] == ""`
- `tests/extraction/test_export_pdf_text_extractions.py` line 629: `assert data["page_extractions"][0]["warnings"] == warnings`
- `tests/extraction/test_export_pdf_text_extractions.py` line 632: `def test_export_pdf_text_extractions_failed_pdf_asset_becomes_asset_error_and_returns_zero(`
- `tests/extraction/test_export_pdf_text_extractions.py` line 676: `assert result == 0`
- `tests/extraction/test_export_pdf_text_extractions.py` line 678: `assert data["asset_errors"] == [`
- `tests/extraction/test_export_pdf_text_extractions.py` line 687: `def test_export_pdf_text_extractions_returns_error_for_missing_input_file(`
- `tests/extraction/test_export_pdf_text_extractions.py` line 701: `assert result == 1`
- `tests/extraction/test_export_pdf_text_extractions.py` line 705: `def test_export_pdf_text_extractions_returns_error_for_directory_input(`
- `tests/extraction/test_export_pdf_text_extractions.py` line 718: `assert result == 1`
- `tests/extraction/test_export_pdf_text_extractions.py` line 722: `def test_export_pdf_text_extractions_returns_error_for_invalid_json(`
- `tests/extraction/test_export_pdf_text_extractions.py` line 737: `assert result == 1`
- `tests/extraction/test_export_pdf_text_extractions.py` line 741: `def test_export_pdf_text_extractions_returns_error_for_malformed_top_level_artifact(`
- `tests/extraction/test_export_pdf_text_extractions.py` line 756: `assert result == 1`
- `tests/extraction/test_export_pdf_text_extractions.py` line 760: `def test_export_pdf_text_extractions_returns_error_for_items_not_list(`
- `tests/extraction/test_export_pdf_text_extractions.py` line 781: `assert result == 1`
- `tests/extraction/test_export_pdf_text_extractions.py` line 785: `def test_export_pdf_text_extractions_output_does_not_include_forbidden_structured_fields(`
- `tests/extraction/test_export_pdf_text_extractions.py` line 842: `assert result == 0`
- `tests/extraction/test_export_text_extraction_evidence.py` line 30: `def test_from_dict_deserializes_text_asset_extraction_report(tmp_path):`
- `tests/extraction/test_export_text_extraction_evidence.py` line 56: `assert report.root == str(tmp_path)`
- `tests/extraction/test_export_text_extraction_evidence.py` line 57: `assert report.total_text_assets == 2`
- `tests/extraction/test_export_text_extraction_evidence.py` line 58: `assert report.failed == 1`
- `tests/extraction/test_export_text_extraction_evidence.py` line 59: `assert report.extractions[0].path == successful_path`
- `tests/extraction/test_export_text_extraction_evidence.py` line 60: `assert report.extractions[0].size == 25`
- `tests/extraction/test_export_text_extraction_evidence.py` line 61: `assert report.extractions[0].content == "Prompt content"`
- `tests/extraction/test_export_text_extraction_evidence.py` line 63: `assert report.extractions[1].path == failed_path`
- `tests/extraction/test_export_text_extraction_evidence.py` line 64: `assert report.extractions[1].error == "missing file"`
- `tests/extraction/test_export_text_extraction_evidence.py` line 67: `def test_load_json_reads_text_asset_extraction_report(tmp_path):`
- `tests/extraction/test_export_text_extraction_evidence.py` line 85: `assert report.root == str(tmp_path)`
- `tests/extraction/test_export_text_extraction_evidence.py` line 86: `assert report.total_text_assets == 1`
- `tests/extraction/test_export_text_extraction_evidence.py` line 87: `assert report.failed == 0`
- `tests/extraction/test_export_text_extraction_evidence.py` line 88: `assert report.extractions[0].path == text_path`
- `tests/extraction/test_export_text_extraction_evidence.py` line 89: `assert report.extractions[0].content == "Generate a helmet concept."`
- `tests/extraction/test_export_text_extraction_evidence.py` line 92: `def test_export_text_extraction_evidence_writes_successful_extractions(`
- `tests/extraction/test_export_text_extraction_evidence.py` line 128: `assert result == 0`
- `tests/extraction/test_export_text_extraction_evidence.py` line 135: `assert data == {`
- `tests/extraction/test_export_text_extraction_evidence.py` line 151: `def test_export_text_extraction_evidence_skips_failed_extractions(`
- `tests/extraction/test_export_text_extraction_evidence.py` line 187: `assert result == 0`
- `tests/extraction/test_export_text_extraction_evidence.py` line 190: `assert data["evidences"] == [`
- `tests/extraction/test_export_text_extraction_evidence.py` line 199: `def test_export_text_extraction_evidence_preserves_non_ascii_content(`
- `tests/extraction/test_export_text_extraction_evidence.py` line 230: `assert result == 0`
- `tests/extraction/test_export_text_extraction_evidence.py` line 233: `assert data["evidences"][0]["content"] == content`
- `tests/extraction/test_export_text_extraction_evidence.py` line 236: `def test_export_text_extraction_evidence_returns_error_for_missing_report(`
- `tests/extraction/test_export_text_extraction_evidence.py` line 250: `assert result == 1`
- `tests/extraction/test_export_text_extraction_evidence.py` line 254: `def test_export_text_extraction_evidence_returns_error_for_directory(`
- `tests/extraction/test_export_text_extraction_evidence.py` line 267: `assert result == 1`
- `tests/extraction/test_export_text_extraction_evidence.py` line 271: `def test_export_text_extraction_evidence_returns_error_for_invalid_json(`
- `tests/extraction/test_export_text_extraction_evidence.py` line 286: `assert result == 1`
- `tests/extraction/test_export_text_extraction_evidence.py` line 290: `def test_export_text_extraction_evidence_returns_error_for_malformed_report(`
- `tests/extraction/test_export_text_extraction_evidence.py` line 313: `assert result == 1`
- `tests/extraction/test_export_text_extraction_evidence.py` line 317: `def test_export_text_extraction_evidence_returns_error_for_missing_output_parent(`
- `tests/extraction/test_export_text_extraction_evidence.py` line 344: `assert result == 1`
- `tests/extraction/test_extract_text_assets.py` line 21: `def test_extract_text_assets_prints_summary_for_valid_report(tmp_path, capsys):`
- `tests/extraction/test_extract_text_assets.py` line 41: `assert result == 0`
- `tests/extraction/test_extract_text_assets.py` line 49: `def test_extract_text_assets_writes_json_with_output(tmp_path, capsys):`
- `tests/extraction/test_extract_text_assets.py` line 76: `assert result == 0`
- `tests/extraction/test_extract_text_assets.py` line 78: `assert data["root"] == str(tmp_path)`
- `tests/extraction/test_extract_text_assets.py` line 79: `assert data["total_text_assets"] == 1`
- `tests/extraction/test_extract_text_assets.py` line 80: `assert data["failed"] == 0`
- `tests/extraction/test_extract_text_assets.py` line 81: `assert data["extractions"][0]["content"] == "Rancang helm Café Racer."`
- `tests/extraction/test_extract_text_assets.py` line 84: `def test_extract_text_assets_returns_error_for_missing_report(tmp_path, capsys):`
- `tests/extraction/test_extract_text_assets.py` line 90: `assert result == 1`
- `tests/extraction/test_extract_text_assets.py` line 94: `def test_extract_text_assets_returns_error_for_directory(tmp_path, capsys):`
- `tests/extraction/test_extract_text_assets.py` line 98: `assert result == 1`
- `tests/extraction/test_extract_text_assets.py` line 102: `def test_extract_text_assets_returns_error_for_invalid_json(tmp_path, capsys):`
- `tests/extraction/test_extract_text_assets.py` line 109: `assert result == 1`
- `tests/extraction/test_extract_text_assets.py` line 113: `def test_extract_text_assets_returns_error_for_missing_output_parent(`
- `tests/extraction/test_extract_text_assets.py` line 141: `assert result == 1`
- `tests/extraction/test_extract_text_assets.py` line 145: `def test_extract_text_assets_returns_error_for_write_failure(`
- `tests/extraction/test_extract_text_assets.py` line 182: `assert result == 1`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 45: `def test_inspect_pdf_text_evidence_valid_artifact_returns_zero(`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 55: `assert result == 0`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 58: `def test_inspect_pdf_text_evidence_prints_total_pdf_text_evidences(`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 68: `assert result == 0`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 72: `def test_inspect_pdf_text_evidence_prints_total_content_characters(`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 82: `assert result == 0`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 86: `def test_inspect_pdf_text_evidence_prints_empty_content_evidence_count(`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 96: `assert result == 0`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 100: `def test_inspect_pdf_text_evidence_prints_warning_count(`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 110: `assert result == 0`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 114: `def test_inspect_pdf_text_evidence_prints_invalid_record_count(`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 131: `assert result == 0`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 135: `def test_inspect_pdf_text_evidence_prints_forbidden_field_count(`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 152: `assert result == 0`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 156: `def test_inspect_pdf_text_evidence_readable_artifact_with_invalid_records_returns_zero(`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 174: `assert result == 0`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 178: `def test_inspect_pdf_text_evidence_returns_error_for_missing_input_file(`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 187: `assert result == 1`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 191: `def test_inspect_pdf_text_evidence_returns_error_for_directory_input(`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 198: `assert result == 1`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 202: `def test_inspect_pdf_text_evidence_returns_error_for_invalid_json(`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 212: `assert result == 1`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 216: `def test_inspect_pdf_text_evidence_returns_error_for_top_level_list(`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 226: `assert result == 1`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 230: `def test_inspect_pdf_text_evidence_returns_error_for_missing_pdf_text_evidences(`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 240: `assert result == 1`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 244: `def test_inspect_pdf_text_evidence_returns_error_for_extra_top_level_key(`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 260: `assert result == 1`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 264: `def test_inspect_pdf_text_evidence_returns_error_for_pdf_text_evidences_not_list(`
- `tests/extraction/test_inspect_pdf_text_evidence.py` line 274: `assert result == 1`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 52: `def test_inspect_pdf_text_extractions_valid_artifact_returns_zero(`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 62: `assert result == 0`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 65: `def test_inspect_pdf_text_extractions_prints_total_pdf_assets(`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 78: `assert result == 0`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 83: `def test_inspect_pdf_text_extractions_prints_total_page_extractions(`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 96: `assert result == 0`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 100: `def test_inspect_pdf_text_extractions_prints_failed_pdf_assets(`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 113: `assert result == 0`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 117: `def test_inspect_pdf_text_extractions_prints_empty_content_page_count(`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 130: `assert result == 0`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 134: `def test_inspect_pdf_text_extractions_prints_page_warning_count(`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 156: `assert result == 0`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 160: `def test_inspect_pdf_text_extractions_prints_asset_error_count(`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 176: `assert result == 0`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 180: `def test_inspect_pdf_text_extractions_prints_invalid_page_record_count(`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 195: `assert result == 0`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 199: `def test_inspect_pdf_text_extractions_prints_invalid_asset_error_count(`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 215: `assert result == 0`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 219: `def test_inspect_pdf_text_extractions_prints_forbidden_field_count(`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 240: `assert result == 0`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 244: `def test_inspect_pdf_text_extractions_readable_artifact_with_invalid_records_returns_zero(`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 267: `assert result == 0`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 273: `def test_inspect_pdf_text_extractions_missing_input_file_returns_one(`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 282: `assert result == 1`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 286: `def test_inspect_pdf_text_extractions_directory_input_returns_one(`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 293: `assert result == 1`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 297: `def test_inspect_pdf_text_extractions_invalid_json_returns_one(`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 307: `assert result == 1`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 311: `def test_inspect_pdf_text_extractions_top_level_list_returns_one(`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 321: `assert result == 1`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 325: `def test_inspect_pdf_text_extractions_missing_required_top_level_key_returns_one(`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 337: `assert result == 1`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 341: `def test_inspect_pdf_text_extractions_extra_top_level_key_returns_one(`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 354: `assert result == 1`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 358: `def test_inspect_pdf_text_extractions_page_extractions_not_list_returns_one(`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 371: `assert result == 1`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 375: `def test_inspect_pdf_text_extractions_asset_errors_not_list_returns_one(`
- `tests/extraction/test_inspect_pdf_text_extractions.py` line 388: `assert result == 1`
- `tests/extraction/test_inspect_text_extraction_evidence.py` line 13: `def test_inspect_text_extraction_evidence_prints_summary(tmp_path, capsys):`
- `tests/extraction/test_inspect_text_extraction_evidence.py` line 36: `assert result == 0`
- `tests/extraction/test_inspect_text_extraction_evidence.py` line 45: `def test_inspect_text_extraction_evidence_returns_error_for_missing_file(`
- `tests/extraction/test_inspect_text_extraction_evidence.py` line 54: `assert result == 1`
- `tests/extraction/test_inspect_text_extraction_evidence.py` line 58: `def test_inspect_text_extraction_evidence_returns_error_for_directory(`
- `tests/extraction/test_inspect_text_extraction_evidence.py` line 65: `assert result == 1`
- `tests/extraction/test_inspect_text_extraction_evidence.py` line 69: `def test_inspect_text_extraction_evidence_returns_error_for_invalid_json(`
- `tests/extraction/test_inspect_text_extraction_evidence.py` line 79: `assert result == 1`
- `tests/extraction/test_inspect_text_extraction_evidence.py` line 83: `def test_inspect_text_extraction_evidence_returns_error_for_malformed_artifact(`
- `tests/extraction/test_inspect_text_extraction_evidence.py` line 98: `assert result == 1`
- `tests/extraction/test_inspect_text_extraction_evidence.py` line 102: `def test_inspect_text_extraction_evidence_returns_zero_for_invalid_records_after_readable_artifact(`
- `tests/extraction/test_inspect_text_extraction_evidence.py` line 125: `assert result == 0`
- `tests/extraction/test_pdf_page_text_extraction.py` line 4: `def test_pdf_page_text_extraction_stores_exact_values():`
- `tests/extraction/test_pdf_page_text_extraction.py` line 15: `assert extraction.source_path == "D:\\SPEC\\helmet.pdf"`
- `tests/extraction/test_pdf_page_text_extraction.py` line 16: `assert extraction.size_bytes == 123`
- `tests/extraction/test_pdf_page_text_extraction.py` line 17: `assert extraction.page_number == 2`
- `tests/extraction/test_pdf_page_text_extraction.py` line 18: `assert extraction.extraction_index == 1`
- `tests/extraction/test_pdf_page_text_extraction.py` line 19: `assert extraction.extraction_method == "embedded_text"`
- `tests/extraction/test_pdf_page_text_extraction.py` line 20: `assert extraction.content == "Line 1\nLine 2"`
- `tests/extraction/test_pdf_page_text_extraction.py` line 21: `assert extraction.warnings == ["No embedded text found."]`
- `tests/extraction/test_pdf_text_evidence_smoke_flow.py` line 40: `def test_pdf_text_evidence_artifact_smoke_flow_exports_then_inspects(`
- `tests/extraction/test_pdf_text_evidence_smoke_flow.py` line 121: `assert export_result == 0`
- `tests/extraction/test_pdf_text_evidence_smoke_flow.py` line 123: `assert set(artifact) == {"pdf_text_evidences"}`
- `tests/extraction/test_pdf_text_evidence_smoke_flow.py` line 124: `assert len(records) == 3`
- `tests/extraction/test_pdf_text_evidence_smoke_flow.py` line 130: `assert records == [`
- `tests/extraction/test_pdf_text_evidence_smoke_flow.py` line 166: `assert set(record) == PDF_TEXT_EVIDENCE_FIELDS`
- `tests/extraction/test_pdf_text_evidence_smoke_flow.py` line 180: `assert inspect_result == 0`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 49: `def test_counts_total_pdf_assets():`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 54: `assert inspection.total_pdf_assets == 3`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 57: `def test_counts_total_page_extractions():`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 62: `assert inspection.total_page_extractions == 2`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 65: `def test_counts_failed_pdf_assets():`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 70: `assert inspection.failed_pdf_assets == 1`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 73: `def test_counts_empty_content_pages():`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 84: `assert inspection.empty_content_page_count == 1`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 87: `def test_counts_page_warnings():`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 101: `assert inspection.page_warning_count == 2`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 104: `def test_counts_asset_errors():`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 115: `assert inspection.asset_error_count == 2`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 118: `def test_counts_invalid_page_extraction_records():`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 129: `assert inspection.invalid_page_extraction_record_count == 2`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 132: `def test_counts_invalid_asset_error_records():`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 143: `assert inspection.invalid_asset_error_record_count == 2`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 146: `def test_counts_forbidden_fields():`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 158: `assert inspection.forbidden_field_count == 2`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 159: `assert inspection.invalid_page_extraction_record_count == 1`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 160: `assert inspection.invalid_asset_error_record_count == 1`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 163: `def test_accepts_exact_valid_top_level_fields_only():`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 166: `assert inspection.invalid_page_extraction_record_count == 0`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 167: `assert inspection.invalid_asset_error_record_count == 0`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 168: `assert inspection.forbidden_field_count == 0`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 171: `def test_rejects_extra_top_level_fields():`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 174: `with pytest.raises(ValueError, match="exactly"):`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 178: `def test_rejects_bool_for_top_level_integer_fields():`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 186: `with pytest.raises(ValueError, match="integer"):`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 190: `def test_rejects_bool_for_page_integer_fields():`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 204: `assert inspection.invalid_page_extraction_record_count == 1`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 207: `def test_rejects_bool_for_asset_error_integer_fields():`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 217: `assert inspection.invalid_asset_error_record_count == 1`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 220: `def test_rejects_missing_required_page_fields():`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 228: `assert inspection.invalid_page_extraction_record_count == 1`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 231: `def test_rejects_extra_non_forbidden_page_fields_as_invalid():`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 240: `assert inspection.invalid_page_extraction_record_count == 1`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 241: `assert inspection.forbidden_field_count == 0`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 244: `def test_rejects_invalid_warnings_list():`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 253: `assert inspection.invalid_page_extraction_record_count == 1`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 254: `assert inspection.page_warning_count == 0`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 257: `def test_rejects_warnings_list_with_non_string_item():`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 266: `assert inspection.invalid_page_extraction_record_count == 1`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 267: `assert inspection.page_warning_count == 2`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 270: `def test_rejects_missing_required_asset_error_fields():`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 281: `assert inspection.invalid_asset_error_record_count == 1`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 284: `def test_rejects_extra_non_forbidden_asset_error_fields_as_invalid():`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 294: `assert inspection.invalid_asset_error_record_count == 1`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 295: `assert inspection.forbidden_field_count == 0`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 298: `def test_counts_forbidden_fields_separately():`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 311: `assert inspection.forbidden_field_count == 2`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 312: `assert inspection.invalid_page_extraction_record_count == 1`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 313: `assert inspection.invalid_asset_error_record_count == 1`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 316: `def test_preserves_inspection_only_behavior_no_mutation():`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 331: `assert artifact == original`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 334: `def test_rejects_missing_required_top_level_key():`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 338: `with pytest.raises(ValueError, match="exactly"):`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 342: `def test_rejects_page_extractions_not_list():`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 345: `with pytest.raises(ValueError, match="page_extractions"):`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 349: `def test_rejects_asset_errors_not_list():`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 352: `with pytest.raises(ValueError, match="asset_errors"):`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 356: `def test_rejects_non_dict_top_level_artifact():`
- `tests/extraction/test_pdf_text_extraction_artifact_inspector.py` line 357: `with pytest.raises(ValueError, match="object"):`
- `tests/extraction/test_pdf_text_extraction_report.py` line 8: `def test_pdf_text_extraction_report_calculates_total_pdf_assets():`
- `tests/extraction/test_pdf_text_extraction_report.py` line 40: `assert report.total_pdf_assets == 2`
- `tests/extraction/test_pdf_text_extraction_report.py` line 43: `def test_pdf_text_extraction_report_calculates_total_page_extractions():`
- `tests/extraction/test_pdf_text_extraction_report.py` line 60: `assert report.total_page_extractions == 1`
- `tests/extraction/test_pdf_text_extraction_report.py` line 63: `def test_pdf_text_extraction_report_calculates_failed_pdf_assets():`
- `tests/extraction/test_pdf_text_extraction_report.py` line 76: `assert report.failed_pdf_assets == 1`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 47: `def test_serializer_produces_expected_top_level_keys():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 50: `assert set(result) == {`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 60: `def test_serializer_serializes_empty_report():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 63: `assert result == {`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 73: `def test_serializer_serializes_one_page_extraction_correctly():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 90: `assert result == {`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 110: `def test_serializer_serializes_multiple_page_extractions_in_order():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 136: `assert result["page_extractions"] == [`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 158: `def test_serializer_preserves_exact_content():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 176: `assert result["page_extractions"][0]["content"] == content`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 179: `def test_serializer_preserves_non_ascii_content():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 199: `assert json.loads(result)["page_extractions"][0]["content"] == content`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 202: `def test_serializer_preserves_newline_content():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 220: `assert json.loads(result)["page_extractions"][0]["content"] == content`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 223: `def test_serializer_preserves_empty_content():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 240: `assert result["page_extractions"][0]["content"] == ""`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 243: `def test_serializer_preserves_warnings():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 264: `assert result["page_extractions"][0]["warnings"] == warnings`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 267: `def test_serializer_preserves_asset_errors():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 280: `assert result["asset_errors"] == [`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 289: `def test_serializer_preserves_total_pdf_assets():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 313: `assert result["total_pdf_assets"] == 2`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 316: `def test_serializer_preserves_total_page_extractions():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 342: `assert result["total_page_extractions"] == 2`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 345: `def test_serializer_preserves_failed_pdf_assets():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 358: `assert result["failed_pdf_assets"] == 1`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 361: `def test_serializer_does_not_include_forbidden_fields():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 393: `assert set(page_extraction) == {`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 402: `assert set(asset_error) == {`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 409: `def test_to_json_output_is_deterministic():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 427: `assert first == second`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 430: `def test_to_json_output_can_be_parsed_back_with_json_loads():`
- `tests/extraction/test_pdf_text_extraction_report_serializer.py` line 448: `assert data["page_extractions"][0]["source_path"] == "spec.pdf"`
- `tests/extraction/test_pdf_text_extraction_smoke_flow.py` line 59: `def test_pdf_text_extraction_artifact_smoke_flow_exports_then_inspects(`
- `tests/extraction/test_pdf_text_extraction_smoke_flow.py` line 160: `assert export_result == 0`
- `tests/extraction/test_pdf_text_extraction_smoke_flow.py` line 162: `assert captured_inputs == [`
- `tests/extraction/test_pdf_text_extraction_smoke_flow.py` line 180: `assert set(artifact) == TOP_LEVEL_FIELDS`
- `tests/extraction/test_pdf_text_extraction_smoke_flow.py` line 181: `assert artifact["root"] == str(tmp_path)`
- `tests/extraction/test_pdf_text_extraction_smoke_flow.py` line 182: `assert artifact["total_pdf_assets"] == 2`
- `tests/extraction/test_pdf_text_extraction_smoke_flow.py` line 183: `assert artifact["total_page_extractions"] == 3`
- `tests/extraction/test_pdf_text_extraction_smoke_flow.py` line 184: `assert artifact["failed_pdf_assets"] == 1`
- `tests/extraction/test_pdf_text_extraction_smoke_flow.py` line 185: `assert artifact["page_extractions"] == [`
- `tests/extraction/test_pdf_text_extraction_smoke_flow.py` line 214: `assert artifact["asset_errors"] == [`
- `tests/extraction/test_pdf_text_extraction_smoke_flow.py` line 223: `assert set(page_extraction) == PAGE_EXTRACTION_FIELDS`
- `tests/extraction/test_pdf_text_extraction_smoke_flow.py` line 227: `assert set(asset_error) == ASSET_ERROR_FIELDS`
- `tests/extraction/test_pdf_text_extraction_smoke_flow.py` line 235: `assert inspect_result == 0`
- `tests/extraction/test_pdf_text_extractor.py` line 59: `def test_extractor_creates_page_level_extraction_records(tmp_path):`
- `tests/extraction/test_pdf_text_extractor.py` line 85: `assert report.root == str(tmp_path)`
- `tests/extraction/test_pdf_text_extractor.py` line 86: `assert report.total_pdf_assets == 1`
- `tests/extraction/test_pdf_text_extractor.py` line 87: `assert report.total_page_extractions == 2`
- `tests/extraction/test_pdf_text_extractor.py` line 88: `assert report.failed_pdf_assets == 0`
- `tests/extraction/test_pdf_text_extractor.py` line 98: `def test_extractor_uses_one_based_page_numbers(tmp_path):`
- `tests/extraction/test_pdf_text_extractor.py` line 125: `def test_extraction_index_is_zero_based(tmp_path):`
- `tests/extraction/test_pdf_text_extractor.py` line 152: `def test_extraction_index_preserves_page_extraction_order(tmp_path):`
- `tests/extraction/test_pdf_text_extractor.py` line 198: `def test_extraction_method_is_embedded_text(tmp_path):`
- `tests/extraction/test_pdf_text_extractor.py` line 218: `assert report.page_extractions[0].extraction_method == "embedded_text"`
- `tests/extraction/test_pdf_text_extractor.py` line 221: `def test_empty_page_content_is_allowed(tmp_path):`
- `tests/extraction/test_pdf_text_extractor.py` line 241: `assert report.page_extractions[0].content == ""`
- `tests/extraction/test_pdf_text_extractor.py` line 242: `assert report.page_extractions[0].warnings == [`
- `tests/extraction/test_pdf_text_extractor.py` line 247: `def test_unreadable_pdf_asset_creates_asset_error_and_does_not_crash(`
- `tests/extraction/test_pdf_text_extractor.py` line 267: `assert report.page_extractions == []`
- `tests/extraction/test_pdf_text_extractor.py` line 268: `assert report.failed_pdf_assets == 1`
- `tests/extraction/test_pdf_text_extractor.py` line 269: `assert report.asset_errors[0].source_path == str(pdf_path)`
- `tests/extraction/test_pdf_text_extractor.py` line 270: `assert report.asset_errors[0].size_bytes == 100`
- `tests/extraction/test_pdf_text_extractor.py` line 271: `assert report.asset_errors[0].error == "cannot read pdf"`
- `tests/extraction/test_pdf_text_extractor.py` line 274: `def test_extractor_accepts_source_path_and_size_bytes_records(tmp_path):`
- `tests/extraction/test_pdf_text_extractor.py` line 294: `assert report.page_extractions[0].source_path == str(pdf_path)`
- `tests/extraction/test_pdf_text_extractor.py` line 295: `assert report.page_extractions[0].size_bytes == 100`
- `tests/extraction/test_pdf_text_extractor.py` line 298: `def test_extractor_does_not_add_forbidden_product_or_prompt_fields(`
- `tests/extraction/test_text_asset_extraction_report_serializer.py` line 9: `def test_to_dict_serializes_text_asset_extraction_report(tmp_path):`
- `tests/extraction/test_text_asset_extraction_report_serializer.py` line 30: `assert result == {`
- `tests/extraction/test_text_asset_extraction_report_serializer.py` line 51: `def test_write_json_writes_utf8_json_and_preserves_non_ascii_content(tmp_path):`
- `tests/extraction/test_text_asset_extraction_report_serializer.py` line 71: `assert data["root"] == str(tmp_path)`
- `tests/extraction/test_text_asset_extraction_report_serializer.py` line 72: `assert data["total_text_assets"] == 1`
- `tests/extraction/test_text_asset_extraction_report_serializer.py` line 73: `assert data["failed"] == 0`
- `tests/extraction/test_text_asset_extraction_report_serializer.py` line 74: `assert data["extractions"][0]["content"] == "Helm Café Racer"`
- `tests/extraction/test_text_asset_extractor.py` line 4: `def test_extracts_only_utf8_text_assets_and_preserves_content(tmp_path):`
- `tests/extraction/test_text_asset_extractor.py` line 41: `assert report.root == str(tmp_path)`
- `tests/extraction/test_text_asset_extractor.py` line 42: `assert report.total_text_assets == 1`
- `tests/extraction/test_text_asset_extractor.py` line 43: `assert report.failed == 0`
- `tests/extraction/test_text_asset_extractor.py` line 44: `assert len(report.extractions) == 1`
- `tests/extraction/test_text_asset_extractor.py` line 47: `assert extraction.path == text_file`
- `tests/extraction/test_text_asset_extractor.py` line 48: `assert extraction.size == 32`
- `tests/extraction/test_text_asset_extractor.py` line 49: `assert extraction.content == content`
- `tests/extraction/test_text_asset_extractor.py` line 53: `def test_missing_utf8_text_file_becomes_failed_extraction(tmp_path):`
- `tests/extraction/test_text_asset_extractor.py` line 69: `assert report.total_text_assets == 1`
- `tests/extraction/test_text_asset_extractor.py` line 70: `assert report.failed == 1`
- `tests/extraction/test_text_asset_extractor.py` line 71: `assert report.extractions[0].path == missing_file`
- `tests/extraction/test_text_asset_extractor.py` line 72: `assert report.extractions[0].size == 12`
- `tests/extraction/test_text_asset_extractor.py` line 73: `assert report.extractions[0].content == ""`
- `tests/extraction/test_text_asset_extractor.py` line 77: `def test_invalid_utf8_text_file_becomes_failed_extraction(tmp_path):`
- `tests/extraction/test_text_asset_extractor.py` line 94: `assert report.total_text_assets == 1`
- `tests/extraction/test_text_asset_extractor.py` line 95: `assert report.failed == 1`
- `tests/extraction/test_text_asset_extractor.py` line 96: `assert report.extractions[0].path == invalid_file`
- `tests/extraction/test_text_asset_extractor.py` line 97: `assert report.extractions[0].content == ""`
- `tests/extraction/test_text_extraction_evidence_smoke_flow.py` line 7: `def test_text_extraction_evidence_artifact_smoke_flow_exports_then_inspects(`
- `tests/extraction/test_text_extraction_evidence_smoke_flow.py` line 67: `assert export_result == 0`
- `tests/extraction/test_text_extraction_evidence_smoke_flow.py` line 70: `assert len(records) == 3`
- `tests/extraction/test_text_extraction_evidence_smoke_flow.py` line 71: `assert [record["source_path"] for record in records] == [`
- `tests/extraction/test_text_extraction_evidence_smoke_flow.py` line 80: `assert records[1]["content"] == non_ascii_content`
- `tests/extraction/test_text_extraction_evidence_smoke_flow.py` line 81: `assert records[2]["content"] == ""`
- `tests/extraction/test_text_extraction_evidence_smoke_flow.py` line 84: `assert set(record) == {`
- `tests/extraction/test_text_extraction_evidence_smoke_flow.py` line 110: `assert inspect_result == 0`
- `tests/infrastructure/test_repository_explorer_batch_discovery.py` line 27: `def test_repository_explorer_batch_discovery_maps_exploration_to_batch(tmp_path):`
- `tests/infrastructure/test_repository_explorer_batch_discovery.py` line 73: `assert fake_explorer.explored_roots == [root]`
- `tests/infrastructure/test_repository_explorer_batch_discovery.py` line 75: `assert batch.name == root.name`
- `tests/infrastructure/test_repository_explorer_batch_discovery.py` line 76: `assert batch.root == root`
- `tests/infrastructure/test_repository_explorer_batch_discovery.py` line 77: `assert len(batch.assets) == 1`
- `tests/infrastructure/test_repository_explorer_batch_discovery.py` line 80: `assert asset.path.resolve() == image_file`
- `tests/infrastructure/test_repository_explorer_batch_discovery.py` line 81: `assert asset.filename == "photo.jpg"`
- `tests/infrastructure/test_repository_explorer_batch_discovery.py` line 82: `assert asset.metadata.extension == ".jpg"`
- `tests/infrastructure/test_repository_explorer_batch_discovery.py` line 83: `assert asset.metadata.size == len(image_content)`
- `tests/infrastructure/test_repository_explorer_batch_discovery.py` line 84: `assert asset.metadata.category == "Image"`
- `tests/ingestion/test_controlled_metadata_only_dry_run_smoke_flow.py` line 118: `def test_controlled_smoke_flow_collects_only_immediate_tmp_path_metadata_items(`
- `tests/ingestion/test_controlled_metadata_only_dry_run_smoke_flow.py` line 138: `assert result["collector_result"].item_count == 3`
- `tests/ingestion/test_controlled_metadata_only_dry_run_smoke_flow.py` line 143: `assert relative_paths == {"photo.png", "spec.pdf", "nested"}`
- `tests/ingestion/test_controlled_metadata_only_dry_run_smoke_flow.py` line 162: `def test_controlled_smoke_flow_does_not_recurse_into_nested_directory(`
- `tests/ingestion/test_controlled_metadata_only_dry_run_smoke_flow.py` line 175: `assert result["collector_result"].item_count == 1`
- `tests/ingestion/test_controlled_metadata_only_dry_run_smoke_flow.py` line 178: `def test_controlled_smoke_flow_blocks_before_adapter_when_safety_is_unsafe(`
- `tests/ingestion/test_controlled_metadata_only_dry_run_smoke_flow.py` line 198: `def test_controlled_smoke_flow_blocks_before_adapter_when_collection_is_unsafe(`
- `tests/ingestion/test_controlled_metadata_only_dry_run_smoke_flow.py` line 218: `def test_controlled_smoke_flow_exposes_no_content_derived_fields(tmp_path):`
- `tests/ingestion/test_controlled_metadata_only_dry_run_smoke_flow.py` line 238: `assert result["collector_result"].item_count == 1`
- `tests/ingestion/test_controlled_metadata_only_dry_run_smoke_flow.py` line 241: `def test_controlled_smoke_flow_does_not_create_artifact_types(tmp_path):`
- `tests/ingestion/test_controlled_metadata_only_dry_run_smoke_flow.py` line 251: `def test_smoke_flow_tests_use_tmp_path_only(tmp_path):`
- `tests/ingestion/test_controlled_metadata_only_dry_run_smoke_flow.py` line 254: `assert result["adapter_result"].root == str(tmp_path)`
- `tests/ingestion/test_controlled_metadata_only_dry_run_smoke_flow.py` line 258: `def test_smoke_flow_modules_do_not_expose_forbidden_dependencies():`
- `tests/ingestion/test_controlled_pdf_structural_metadata_contract.py` line 33: `def test_allows_approved_structural_metadata_contract() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_contract.py` line 41: `assert result.reason == "pdf structural metadata contract allowed"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_contract.py` line 42: `assert result.fixture_id == "fixture-1"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_contract.py` line 43: `assert result.fixture_type == "product_spec_pdf"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_contract.py` line 44: `assert result.inspection_mode == STRUCTURAL_METADATA_ONLY_MODE`
- `tests/ingestion/test_controlled_pdf_structural_metadata_contract.py` line 45: `assert result.permitted_fields == PERMITTED_STRUCTURAL_FIELDS`
- `tests/ingestion/test_controlled_pdf_structural_metadata_contract.py` line 49: `def test_blocks_missing_fixture_id() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_contract.py` line 56: `assert result.reason == "fixture_id is required"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_contract.py` line 59: `def test_blocks_unknown_fixture_id() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_contract.py` line 66: `assert result.reason == "fixture_id not found"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_contract.py` line 69: `def test_blocks_non_pdf_fixture_type() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_contract.py` line 78: `assert result.reason == "fixture_type must be product_spec_pdf"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_contract.py` line 81: `def test_blocks_unsupported_inspection_mode() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_contract.py` line 89: `assert result.reason == (`
- `tests/ingestion/test_controlled_pdf_structural_metadata_contract.py` line 94: `def test_blocks_unapproved_permitted_fields() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_contract.py` line 102: `assert result.reason == (`
- `tests/ingestion/test_controlled_pdf_structural_metadata_contract.py` line 107: `def test_blocks_evidence_creation() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_contract.py` line 115: `assert result.reason == (`
- `tests/ingestion/test_controlled_pdf_structural_metadata_contract.py` line 120: `def test_blocks_disallowed_upstream_contract() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_contract.py` line 130: `assert result.reason == "fixture contract is not allowed"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_execution_contract.py` line 38: `def test_allows_approved_execution_contract() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_execution_contract.py` line 47: `assert result.reason == (`
- `tests/ingestion/test_controlled_pdf_structural_metadata_execution_contract.py` line 51: `assert result.max_inspected_pages == MAX_INSPECTED_PAGES_LIMIT`
- `tests/ingestion/test_controlled_pdf_structural_metadata_execution_contract.py` line 57: `def test_blocks_missing_execution_approval() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_execution_contract.py` line 64: `assert result.reason == "execution approval is required"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_execution_contract.py` line 67: `def test_blocks_zero_page_limit() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_execution_contract.py` line 75: `assert result.reason == (`
- `tests/ingestion/test_controlled_pdf_structural_metadata_execution_contract.py` line 80: `def test_blocks_page_limit_above_contract_limit() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_execution_contract.py` line 88: `assert result.reason == (`
- `tests/ingestion/test_controlled_pdf_structural_metadata_execution_contract.py` line 93: `def test_blocks_content_extraction() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_execution_contract.py` line 102: `assert result.reason == (`
- `tests/ingestion/test_controlled_pdf_structural_metadata_execution_contract.py` line 107: `def test_blocks_output_file_creation() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_execution_contract.py` line 116: `assert result.reason == (`
- `tests/ingestion/test_controlled_pdf_structural_metadata_execution_contract.py` line 121: `def test_blocks_evidence_creation() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_execution_contract.py` line 130: `assert result.reason == (`
- `tests/ingestion/test_controlled_pdf_structural_metadata_execution_contract.py` line 135: `def test_blocks_disallowed_upstream_contract() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_execution_contract.py` line 151: `assert result.reason == (`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 229: `def test_requires_explicit_implementation_approval(`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 246: `assert result.inspection_status == "blocked"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 247: `assert result.inspection_error == REQUEST_REQUIRED_ERROR`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 251: `def test_invalid_execution_authority_blocks_before_reader(`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 274: `assert result.inspection_status == "blocked"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 275: `assert result.inspection_error == SAFETY_CHECK_ERROR`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 278: `def test_parser_unavailable_result(monkeypatch) -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 290: `assert result.inspection_status == "parser_unavailable"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 291: `assert result.inspection_error == PARSER_UNAVAILABLE_ERROR`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 292: `assert result.page_details == ()`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 296: `def test_encrypted_result_does_not_access_pages(`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 305: `assert calls == [FIXTURE_PATH]`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 307: `assert result.inspection_status == "encrypted"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 309: `assert result.inspection_error == ENCRYPTED_ERROR`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 310: `assert result.page_count == 0`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 311: `assert result.page_details == ()`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 314: `def test_zero_page_document_is_inspected(monkeypatch) -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 320: `assert calls == [FIXTURE_PATH]`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 321: `assert fake_pages.accessed_indices == []`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 323: `assert result.inspection_status == "inspected"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 324: `assert result.page_count == 0`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 325: `assert result.inspected_page_count == 0`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 326: `assert result.page_details == ()`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 330: `def test_normal_document_is_inspected(monkeypatch) -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 339: `assert calls == [FIXTURE_PATH]`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 340: `assert fake_pages.accessed_indices == [0, 1]`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 342: `assert result.inspection_status == "inspected"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 343: `assert result.page_count == 2`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 344: `assert result.inspected_page_count == 2`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 346: `assert result.page_details[0].width_points == 612.0`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 347: `assert result.page_details[1].rotation_degrees == 90`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 350: `def test_document_above_page_limit_is_bounded(`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 365: `assert result.inspection_status == "bounded"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 366: `assert result.page_count == 5`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 367: `assert result.inspected_page_count == MAX_PAGES`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 369: `assert fake_pages.accessed_indices == [0, 1, 2]`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 372: `def test_one_page_failure_creates_partial_result(`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 384: `assert result.inspection_status == "partial"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 385: `assert result.inspection_error == PARTIAL_INSPECTION_ERROR`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 386: `assert result.page_details[0].inspection_status == "inspected"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 387: `assert result.page_details[1].inspection_status == "page_error"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 388: `assert result.page_details[1].width_points == 0`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 389: `assert result.page_details[1].height_points == 0`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 392: `def test_all_bounded_pages_failing_maps_to_parser_error(`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 404: `assert result.inspection_status == "parser_error"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 405: `assert result.inspection_error == PARSER_ERROR`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 406: `assert result.page_count == 0`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 407: `assert result.inspected_page_count == 0`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 408: `assert result.page_details == ()`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 411: `def test_reader_construction_oserror_maps_to_unreadable(`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 428: `assert result.inspection_status == "unreadable"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 429: `assert result.inspection_error == UNREADABLE_ERROR`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 433: `def test_reader_construction_generic_error_maps_to_parser_error(`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 450: `assert result.inspection_status == "parser_error"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 451: `assert result.inspection_error == PARSER_ERROR`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 455: `def test_page_count_error_maps_to_parser_error(`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 470: `assert result.inspection_status == "parser_error"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 471: `assert result.inspection_error == PARSER_ERROR`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 472: `assert result.page_details == ()`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 484: `def test_rotation_is_normalized(`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 495: `assert result.inspection_status == "inspected"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 502: `def test_invalid_rotation_creates_page_error(`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 513: `assert result.inspection_status == "partial"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 514: `assert result.page_details[1].inspection_status == "page_error"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 517: `def test_invalid_width_creates_page_error(`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 528: `assert result.inspection_status == "partial"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 529: `assert result.page_details[1].inspection_status == "page_error"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 532: `def test_invalid_height_creates_page_error(`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 543: `assert result.inspection_status == "partial"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 544: `assert result.page_details[1].inspection_status == "page_error"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 547: `def test_non_finite_dimension_creates_page_error(`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 558: `assert result.inspection_status == "partial"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 559: `assert result.page_details[1].inspection_status == "page_error"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 562: `def test_bounded_access_never_exceeds_maximum(`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 570: `assert result.inspection_status == "bounded"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 571: `assert fake_pages.accessed_indices == [0, 1, 2]`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 575: `def test_document_metadata_is_never_accessed(`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 584: `assert result.inspection_status == "inspected"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 587: `def test_page_text_extraction_is_never_called(`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 596: `assert result.inspection_status == "inspected"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 599: `def test_result_always_disables_evidence(`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 611: `def test_invalid_request_type_is_blocked(`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 628: `assert result.inspection_status == "blocked"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_implementation.py` line 629: `assert result.inspection_error == SAFETY_CHECK_ERROR`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 101: `def test_allows_zero_page_inspected_result() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 112: `assert result.inspection_status == "inspected"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 113: `assert result.page_count == 0`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 114: `assert result.page_details == ()`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 118: `def test_allows_inspected_result() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 125: `assert result.reason == (`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 128: `assert result.inspected_page_count == 2`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 129: `assert len(result.page_details) == 2`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 133: `def test_allows_bounded_result() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 146: `assert result.inspection_status == "bounded"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 150: `def test_allows_partial_result() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 170: `assert result.inspection_status == "partial"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 171: `assert result.inspection_error == PARTIAL_INSPECTION_ERROR`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 174: `def test_allows_encrypted_result() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 189: `assert result.page_count == 0`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 192: `def test_blocks_missing_execution_contract_result() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 199: `assert result.reason == "execution contract result is required"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 202: `def test_blocks_disallowed_execution_contract() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 211: `assert result.reason == "execution contract is not allowed"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 214: `def test_blocks_fixture_identity_mismatch() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 221: `assert result.reason == "fixture_id mismatch"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 224: `def test_blocks_maximum_page_mismatch() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 231: `assert result.reason == "max_inspected_pages mismatch"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 234: `def test_blocks_negative_page_count() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 245: `assert result.reason == "page_count must not be negative"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 248: `def test_blocks_page_detail_count_mismatch() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 255: `assert result.reason == (`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 260: `def test_blocks_non_contiguous_page_indices() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 269: `assert result.reason == (`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 274: `def test_blocks_zero_dimension_for_inspected_page() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 285: `assert result.reason == (`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 290: `def test_blocks_nan_dimension() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 301: `assert result.reason == "page width must be a finite numeric value"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 304: `def test_blocks_invalid_rotation() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 315: `assert result.reason == "unsupported page rotation"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 318: `def test_blocks_incorrect_truncation_flag() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 325: `assert result.reason == (`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 330: `def test_blocks_partial_result_without_mixed_page_statuses() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 340: `assert result.reason == (`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 345: `def test_blocks_fatal_result_with_page_details() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 357: `assert result.reason == "fatal status requires zero page_count"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 360: `def test_blocks_oversized_inspection_error() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 375: `assert result.reason == (`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 380: `def test_blocks_evidence_authority() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 387: `assert result.reason == (`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 392: `def test_blocks_mutable_page_details_collection() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 401: `assert result.reason == "page_details must be a tuple"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 404: `def test_blocks_boolean_page_count() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 411: `assert result.reason == "page_count must be an integer"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 414: `def test_blocks_encrypted_true_for_inspected_status() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_result_contract.py` line 421: `assert result.reason == (`
- `tests/ingestion/test_controlled_pdf_structural_metadata_synthetic_smoke_flow.py` line 46: `def test_structural_metadata_contract_chain_allows_bounded_execution() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_synthetic_smoke_flow.py` line 50: `assert fixture_result.fixture_count == 1`
- `tests/ingestion/test_controlled_pdf_structural_metadata_synthetic_smoke_flow.py` line 59: `assert metadata_result.fixture_id == FIXTURE_ID`
- `tests/ingestion/test_controlled_pdf_structural_metadata_synthetic_smoke_flow.py` line 60: `assert metadata_result.fixture_path == FIXTURE_PATH`
- `tests/ingestion/test_controlled_pdf_structural_metadata_synthetic_smoke_flow.py` line 61: `assert metadata_result.fixture_type == "product_spec_pdf"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_synthetic_smoke_flow.py` line 62: `assert metadata_result.inspection_mode == STRUCTURAL_METADATA_ONLY_MODE`
- `tests/ingestion/test_controlled_pdf_structural_metadata_synthetic_smoke_flow.py` line 63: `assert metadata_result.permitted_fields == (`
- `tests/ingestion/test_controlled_pdf_structural_metadata_synthetic_smoke_flow.py` line 70: `assert metadata_result.permitted_fields == PERMITTED_STRUCTURAL_FIELDS`
- `tests/ingestion/test_controlled_pdf_structural_metadata_synthetic_smoke_flow.py` line 83: `assert execution_result.fixture_id == FIXTURE_ID`
- `tests/ingestion/test_controlled_pdf_structural_metadata_synthetic_smoke_flow.py` line 84: `assert execution_result.fixture_path == FIXTURE_PATH`
- `tests/ingestion/test_controlled_pdf_structural_metadata_synthetic_smoke_flow.py` line 85: `assert execution_result.fixture_type == "product_spec_pdf"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_synthetic_smoke_flow.py` line 86: `assert execution_result.inspection_mode == STRUCTURAL_METADATA_ONLY_MODE`
- `tests/ingestion/test_controlled_pdf_structural_metadata_synthetic_smoke_flow.py` line 87: `assert execution_result.permitted_fields == PERMITTED_STRUCTURAL_FIELDS`
- `tests/ingestion/test_controlled_pdf_structural_metadata_synthetic_smoke_flow.py` line 89: `assert execution_result.max_inspected_pages == MAX_INSPECTED_PAGES`
- `tests/ingestion/test_controlled_pdf_structural_metadata_synthetic_smoke_flow.py` line 95: `def test_fixture_metadata_authority_does_not_authorize_execution() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_synthetic_smoke_flow.py` line 109: `assert execution_result.reason == "execution approval is required"`
- `tests/ingestion/test_controlled_pdf_structural_metadata_synthetic_smoke_flow.py` line 114: `def test_execution_contract_blocks_content_extraction() -> None:`
- `tests/ingestion/test_controlled_pdf_structural_metadata_synthetic_smoke_flow.py` line 129: `assert execution_result.reason == (`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 1: `from dataclasses import FrozenInstanceError`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 47: `def test_allows_product_spec_pdf_fixture_in_text_only_mode() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 56: `assert result.reason == "pdf text extraction contract allowed"`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 57: `assert result.fixture_id == "fixture-product-spec"`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 58: `assert result.fixture_type == "product_spec_pdf"`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 59: `assert result.extraction_mode == "text_only"`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 61: `assert result.notes == ""`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 64: `def test_preserves_fixture_path_exactly() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 76: `assert result.fixture_path == fixture_path`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 77: `assert result.notes == "reviewed only"`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 80: `def test_result_evidence_allowed_is_false() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 89: `def test_rejects_non_fixture_contract_result() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 96: `assert result.reason == "fixture contract result is required"`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 99: `def test_rejects_disallowed_fixture_contract_result() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 106: `assert result.reason == "fixture contract is not allowed"`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 109: `def test_rejects_empty_fixture_id() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 116: `assert result.reason == "fixture_id is required"`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 119: `def test_rejects_missing_fixture_id() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 126: `assert result.reason == "fixture_id not found"`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 129: `def test_rejects_duplicate_fixture_id() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 142: `assert result.reason == "duplicate fixture_id"`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 149: `def test_rejects_product_photo_fixtures(fixture_type: str) -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 159: `assert result.reason == "fixture_type must be product_spec_pdf"`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 160: `assert result.fixture_type == fixture_type`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 163: `def test_rejects_fixture_with_metadata_disabled() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 173: `assert result.reason == "metadata access must be allowed"`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 176: `def test_rejects_fixture_with_pdf_text_extraction_flag_enabled() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 192: `def test_rejects_fixture_with_evidence_flag_enabled() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 202: `assert result.reason == "fixture evidence flag must remain disabled"`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 205: `def test_rejects_unsupported_extraction_mode() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 213: `assert result.reason == "unsupported extraction_mode"`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 216: `def test_rejects_allow_pdf_text_extraction_true() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 230: `def test_rejects_allow_evidence_creation_true() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 238: `assert result.reason == "evidence creation is not allowed by this contract"`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 241: `def test_rejects_notes_none() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 249: `assert result.reason == "notes is required"`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 250: `assert result.notes == ""`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 253: `def test_fixture_type_is_not_inferred_from_fixture_path() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 266: `assert result.fixture_path == "fixtures/product-photo.jpg"`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 267: `assert result.fixture_type == "product_spec_pdf"`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 270: `def test_dataclass_result_is_immutable() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 276: `with pytest.raises(FrozenInstanceError):`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 280: `def test_result_dataclass_can_be_constructed_directly() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 296: `def test_contract_module_has_no_filesystem_pdf_or_downstream_dependencies() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 1: `from dataclasses import FrozenInstanceError`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 52: `def test_allows_valid_upstream_contract_with_bounded_execution_limits() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 56: `assert result.reason == "pdf text extraction execution contract allowed"`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 57: `assert result.fixture_id == "fixture-product-spec"`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 58: `assert result.fixture_type == "product_spec_pdf"`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 59: `assert result.extraction_mode == "text_only"`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 61: `assert result.max_extracted_characters == 20000`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 62: `assert result.max_preview_characters == 1000`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 65: `assert result.notes == "execution gate only"`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 68: `def test_preserves_fixture_path_exactly() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 75: `assert result.fixture_path == fixture_path`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 78: `def test_result_evidence_allowed_is_false() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 84: `def test_result_allow_full_text_storage_is_false() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 90: `def test_rejects_non_pdf_text_contract_result() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 94: `assert result.reason == "pdf text extraction contract result is required"`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 97: `def test_rejects_disallowed_upstream_contract_result() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 106: `assert result.reason == "pdf text extraction contract is not allowed"`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 109: `def test_rejects_empty_fixture_id() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 115: `assert result.reason == "fixture_id is required"`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 118: `def test_rejects_empty_fixture_path() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 124: `assert result.reason == "fixture_path is required"`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 131: `def test_rejects_product_photo_fixture_types(fixture_type: str) -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 137: `assert result.reason == "fixture_type must be product_spec_pdf"`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 138: `assert result.fixture_type == fixture_type`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 141: `def test_rejects_unsupported_extraction_mode() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 147: `assert result.reason == "extraction_mode must be text_only"`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 150: `def test_rejects_upstream_evidence_allowed_true() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 156: `assert result.reason == "upstream evidence flag must remain disabled"`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 159: `def test_rejects_allow_execution_false() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 163: `assert result.reason == "execution approval is required"`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 167: `def test_rejects_max_extracted_characters_less_than_or_equal_to_zero(`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 179: `def test_rejects_max_extracted_characters_greater_than_limit() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 190: `def test_rejects_max_preview_characters_less_than_or_equal_to_zero(`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 196: `assert result.reason == "max_preview_characters must be greater than zero"`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 199: `def test_rejects_max_preview_characters_greater_than_limit() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 209: `def test_rejects_max_preview_characters_greater_than_extracted_limit() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 222: `def test_rejects_allow_full_text_storage_true() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 226: `assert result.reason == "full text storage is not allowed by this contract"`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 230: `def test_rejects_allow_evidence_creation_true() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 234: `assert result.reason == "evidence creation is not allowed by this contract"`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 237: `def test_rejects_notes_none() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 241: `assert result.reason == "notes is required"`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 242: `assert result.notes == ""`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 245: `def test_fixture_type_is_not_inferred_from_fixture_path() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 254: `assert result.fixture_path == "fixtures/product-photo.jpg"`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 255: `assert result.fixture_type == "product_spec_pdf"`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 258: `def test_dataclass_result_is_immutable() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 261: `with pytest.raises(FrozenInstanceError):`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 265: `def test_result_dataclass_can_be_constructed_directly() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_execution_contract.py` line 285: `def test_contract_module_has_no_filesystem_pdf_or_downstream_dependencies() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 118: `def test_returns_unsupported_pdf_through_result_contract_when_parser_is_absent(`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 129: `assert result.extraction_status == "unsupported_pdf"`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 130: `assert result.extraction_error == "pdf parser dependency is unavailable"`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 133: `def test_uses_existing_parser_dependency_for_synthetic_pdf_when_available(`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 142: `assert result.extraction_status == "unsupported_pdf"`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 146: `assert result.reason == "pdf text extraction result contract allowed"`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 149: `def test_does_not_expose_extracted_text_on_final_result(tmp_path: Path) -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 157: `def test_result_evidence_allowed_is_false(tmp_path: Path) -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 165: `def test_preserves_fixture_fields(tmp_path: Path) -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 170: `assert result.fixture_id == "fixture-product-spec"`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 171: `assert result.source_label == "synthetic sandbox copy"`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 172: `assert result.fixture_path == str(pdf_path)`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 173: `assert result.fixture_type == "product_spec_pdf"`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 174: `assert result.extraction_mode == "text_only"`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 175: `assert result.notes == "implementation skeleton"`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 223: `def test_does_not_read_file_when_gate_or_identity_check_fails(`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 251: `assert result.reason == expected_reason`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 254: `def test_unreadable_file_becomes_deterministic_result_contract_output(`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 269: `assert result.extraction_status == "unreadable"`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 270: `assert result.extraction_error == "pdf file is unreadable"`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 271: `assert result.text_length == 0`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 272: `assert result.text_preview == ""`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 275: `def test_parser_error_becomes_deterministic_result_contract_output(`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 290: `assert result.extraction_status == "parser_error"`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 291: `assert result.extraction_error == "pdf parser error"`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 292: `assert result.text_length == 0`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 293: `assert result.text_preview == ""`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 296: `def test_final_output_is_always_result_contract_result(tmp_path: Path) -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 304: `def test_contract_module_has_no_forbidden_downstream_dependencies() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_implementation.py` line 321: `def test_contract_module_has_no_folder_scanning_fragments() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 1: `from dataclasses import FrozenInstanceError`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 79: `def test_allows_extracted_status_with_positive_text_length_and_bounded_preview() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 83: `assert result.reason == "pdf text extraction result contract allowed"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 84: `assert result.fixture_id == "fixture-product-spec"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 85: `assert result.source_label == "synthetic sandbox copy"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 86: `assert result.fixture_type == "product_spec_pdf"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 87: `assert result.extraction_mode == "text_only"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 88: `assert result.extraction_status == "extracted"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 89: `assert result.text_length == 42`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 90: `assert result.text_preview == "Synthetic product spec preview."`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 92: `assert result.max_extracted_characters == 20000`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 93: `assert result.max_preview_characters == 1000`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 95: `assert result.extraction_error == ""`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 97: `assert result.notes == ""`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 100: `def test_allows_empty_status() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 110: `assert result.extraction_status == "empty"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 111: `assert result.text_length == 0`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 112: `assert result.text_preview == ""`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 116: `def test_allows_truncated_status_with_max_text_length_and_truncated_true() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 126: `assert result.extraction_status == "truncated"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 127: `assert result.text_length == 20000`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 131: `def test_allows_parser_error_status_with_extraction_error() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 142: `assert result.extraction_status == "parser_error"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 143: `assert result.extraction_error == "parser failed"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 146: `def test_preserves_fixture_path_exactly() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 154: `assert result.fixture_path == fixture_path`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 157: `def test_result_does_not_expose_extracted_text_attribute() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 163: `def test_result_evidence_allowed_is_false() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 169: `def test_rejects_non_execution_contract_result() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 173: `assert result.reason == "execution contract result is required"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 176: `def test_rejects_disallowed_execution_contract_result() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 185: `assert result.reason == "execution contract is not allowed"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 188: `def test_rejects_execution_allowed_false() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 194: `assert result.reason == "execution approval is required"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 197: `def test_rejects_upstream_evidence_allowed_true() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 203: `assert result.reason == "upstream evidence flag must remain disabled"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 206: `def test_rejects_upstream_allow_full_text_storage_true() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 212: `assert result.reason == "full text storage must remain disabled"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 215: `def test_rejects_non_result_input() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 219: `assert result.reason == "result input is required"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 222: `def test_rejects_fixture_id_mismatch() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 226: `assert result.reason == "fixture_id mismatch"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 229: `def test_rejects_fixture_path_mismatch() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 233: `assert result.reason == "fixture_path mismatch"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 236: `def test_rejects_fixture_type_mismatch() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 240: `assert result.reason == "fixture_type mismatch"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 243: `def test_rejects_extraction_mode_mismatch() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 247: `assert result.reason == "extraction_mode mismatch"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 250: `def test_rejects_fixture_type_not_product_spec_pdf() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 257: `assert result.reason == "fixture_type must be product_spec_pdf"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 260: `def test_rejects_extraction_mode_not_text_only() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 267: `assert result.reason == "extraction_mode must be text_only"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 270: `def test_rejects_empty_fixture_id() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 277: `assert result.reason == "fixture_id is required"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 280: `def test_rejects_empty_source_label() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 284: `assert result.reason == "source_label is required"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 287: `def test_rejects_empty_fixture_path() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 294: `assert result.reason == "fixture_path is required"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 297: `def test_rejects_unsupported_extraction_status() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 301: `assert result.reason == "unsupported extraction_status"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 304: `def test_rejects_negative_text_length() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 308: `assert result.reason == "text_length must not be negative"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 311: `def test_rejects_text_length_above_execution_limit() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 315: `assert result.reason == "text_length exceeds extraction limit"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 318: `def test_rejects_max_extracted_characters_mismatch() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 322: `assert result.reason == "max_extracted_characters mismatch"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 325: `def test_rejects_max_preview_characters_mismatch() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 329: `assert result.reason == "max_preview_characters mismatch"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 332: `def test_rejects_max_preview_characters_less_than_or_equal_to_zero() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 339: `assert result.reason == "max_preview_characters must be greater than zero"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 342: `def test_rejects_max_preview_characters_greater_than_1000() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 349: `assert result.reason == "max_preview_characters exceeds result contract limit"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 352: `def test_rejects_preview_length_over_limit() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 362: `assert result.reason == "text_preview exceeds preview limit"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 365: `def test_rejects_non_empty_extracted_text() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 369: `assert result.reason == "extracted_text storage is not allowed by this contract"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 372: `def test_rejects_extracted_text_included_true() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 376: `assert result.reason == "extracted_text_included must remain false"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 379: `def test_rejects_evidence_allowed_true() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 383: `assert result.reason == "evidence creation is not allowed by this contract"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 386: `def test_rejects_notes_none() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 390: `assert result.reason == "notes is required"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 393: `def test_rejects_extraction_error_none() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 397: `assert result.reason == "extraction_error is required"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 400: `def test_rejects_successful_status_with_non_empty_extraction_error() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 404: `assert result.reason == "successful status must not have extraction_error"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 407: `def test_rejects_error_status_with_empty_extraction_error() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 417: `assert result.reason == "error status requires extraction_error"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 420: `def test_rejects_extracted_status_with_zero_text_length() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 424: `assert result.reason == "extracted status requires positive text_length"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 427: `def test_rejects_extracted_status_with_truncated_true() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 431: `assert result.reason == "extracted status must not be truncated"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 434: `def test_rejects_empty_status_with_non_zero_text_length() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 444: `assert result.reason == "empty status requires zero text_length"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 447: `def test_rejects_empty_status_with_non_empty_preview() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 457: `assert result.reason == "empty status requires empty text_preview"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 460: `def test_rejects_empty_status_with_truncated_true() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 471: `assert result.reason == "empty status must not be truncated"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 474: `def test_rejects_truncated_status_with_text_length_below_max() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 484: `assert result.reason == "truncated status requires max text_length"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 487: `def test_rejects_truncated_status_with_truncated_false() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 497: `assert result.reason == "truncated status requires truncated true"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 500: `def test_rejects_not_run_status_with_non_zero_text_length() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 510: `assert result.reason == "not_run status requires zero text_length"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 513: `def test_rejects_not_run_status_with_non_empty_preview() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 523: `assert result.reason == "not_run status requires empty text_preview"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 526: `def test_rejects_not_run_status_with_truncated_true() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 537: `assert result.reason == "not_run status must not be truncated"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 540: `def test_rejects_error_status_with_non_zero_text_length() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 551: `assert result.reason == "error status requires zero text_length"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 554: `def test_rejects_error_status_with_non_empty_preview() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 565: `assert result.reason == "error status requires empty text_preview"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 568: `def test_rejects_error_status_with_truncated_true() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 580: `assert result.reason == "error status must not be truncated"`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 583: `def test_dataclass_results_are_immutable() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 587: `with pytest.raises(FrozenInstanceError):`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 590: `with pytest.raises(FrozenInstanceError):`
- `tests/ingestion/test_controlled_pdf_text_extraction_result_contract.py` line 594: `def test_contract_module_has_no_filesystem_pdf_or_downstream_dependencies() -> None:`
- `tests/ingestion/test_controlled_pdf_text_extraction_synthetic_parser_execution.py` line 36: `def test_controlled_synthetic_pdf_parser_execution_reaches_empty_result(`
- `tests/ingestion/test_controlled_pdf_text_extraction_synthetic_parser_execution.py` line 93: `assert parser_paths == [str(pdf_path)]`
- `tests/ingestion/test_controlled_pdf_text_extraction_synthetic_parser_execution.py` line 96: `assert result.extraction_status == "empty"`
- `tests/ingestion/test_controlled_pdf_text_extraction_synthetic_parser_execution.py` line 98: `assert result.fixture_path == str(pdf_path)`
- `tests/ingestion/test_controlled_pdf_text_extraction_synthetic_parser_execution.py` line 99: `assert result.fixture_type == "product_spec_pdf"`
- `tests/ingestion/test_controlled_pdf_text_extraction_synthetic_parser_execution.py` line 100: `assert result.extraction_mode == "text_only"`
- `tests/ingestion/test_controlled_pdf_text_extraction_synthetic_parser_execution.py` line 101: `assert result.text_length == 0`
- `tests/ingestion/test_controlled_pdf_text_extraction_synthetic_parser_execution.py` line 102: `assert result.text_preview == ""`
- `tests/ingestion/test_controlled_pdf_text_extraction_synthetic_parser_execution.py` line 103: `assert result.extraction_error == ""`
- `tests/ingestion/test_controlled_pdf_text_extraction_synthetic_smoke_flow.py` line 117: `def test_synthetic_pdf_text_extraction_smoke_flow_reaches_result_contract(`
- `tests/ingestion/test_controlled_pdf_text_extraction_synthetic_smoke_flow.py` line 138: `assert result.fixture_id == "fixture-product-spec"`
- `tests/ingestion/test_controlled_pdf_text_extraction_synthetic_smoke_flow.py` line 139: `assert result.source_label == "synthetic smoke fixture"`
- `tests/ingestion/test_controlled_pdf_text_extraction_synthetic_smoke_flow.py` line 140: `assert result.fixture_path == str(pdf_path)`
- `tests/ingestion/test_controlled_pdf_text_extraction_synthetic_smoke_flow.py` line 141: `assert result.fixture_type == "product_spec_pdf"`
- `tests/ingestion/test_controlled_pdf_text_extraction_synthetic_smoke_flow.py` line 142: `assert result.extraction_mode == "text_only"`
- `tests/ingestion/test_controlled_pdf_text_extraction_synthetic_smoke_flow.py` line 148: `assert result.extraction_status == "unsupported_pdf"`
- `tests/ingestion/test_controlled_pdf_text_extraction_synthetic_smoke_flow.py` line 149: `assert result.extraction_error == "pdf parser dependency is unavailable"`
- `tests/ingestion/test_controlled_pdf_text_extraction_synthetic_smoke_flow.py` line 152: `def test_smoke_flow_does_not_reach_file_read_when_execution_contract_blocks(`
- `tests/ingestion/test_controlled_pdf_text_extraction_synthetic_smoke_flow.py` line 174: `assert execution_result.reason == "execution approval is required"`
- `tests/ingestion/test_controlled_pdf_text_extraction_synthetic_smoke_flow.py` line 177: `assert result.reason == "execution contract is not allowed"`
- `tests/ingestion/test_controlled_pdf_text_extraction_synthetic_smoke_flow.py` line 180: `def test_smoke_flow_does_not_create_evidence_or_downstream_artifacts(`
- `tests/ingestion/test_controlled_pdf_text_extraction_synthetic_smoke_flow.py` line 217: `def test_smoke_flow_source_has_no_forbidden_discovery_or_downstream_fragments(`
- `tests/ingestion/test_controlled_pdf_text_extraction_text_bearing_synthetic_pdf.py` line 61: `def test_controlled_text_bearing_synthetic_pdf_returns_extracted_result(`
- `tests/ingestion/test_controlled_pdf_text_extraction_text_bearing_synthetic_pdf.py` line 118: `assert parser_paths == [str(pdf_path)]`
- `tests/ingestion/test_controlled_pdf_text_extraction_text_bearing_synthetic_pdf.py` line 121: `assert result.extraction_status == "extracted"`
- `tests/ingestion/test_controlled_pdf_text_extraction_text_bearing_synthetic_pdf.py` line 123: `assert result.fixture_path == str(pdf_path)`
- `tests/ingestion/test_controlled_pdf_text_extraction_text_bearing_synthetic_pdf.py` line 124: `assert result.fixture_type == "product_spec_pdf"`
- `tests/ingestion/test_controlled_pdf_text_extraction_text_bearing_synthetic_pdf.py` line 125: `assert result.extraction_mode == "text_only"`
- `tests/ingestion/test_controlled_pdf_text_extraction_text_bearing_synthetic_pdf.py` line 127: `assert result.text_length == len(result.text_preview)`
- `tests/ingestion/test_controlled_pdf_text_extraction_text_bearing_synthetic_pdf.py` line 128: `assert result.text_preview == SYNTHETIC_TEXT`
- `tests/ingestion/test_controlled_pdf_text_extraction_text_bearing_synthetic_pdf.py` line 130: `assert result.extraction_error == ""`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 1: `from dataclasses import FrozenInstanceError`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 41: `def test_allows_empty_fixture_set_with_default_max_items() -> None:`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 45: `assert result.reason == "fixture contract allowed"`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 46: `assert result.fixture_count == 0`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 47: `assert result.fixtures == ()`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 50: `def test_allows_one_product_spec_pdf_metadata_only_fixture() -> None:`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 56: `assert result.reason == "fixture contract allowed"`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 57: `assert result.fixture_count == 1`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 58: `assert result.fixtures == (fixture,)`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 61: `def test_allows_up_to_four_metadata_only_fixtures() -> None:`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 67: `assert result.reason == "fixture contract allowed"`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 68: `assert result.fixture_count == 4`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 69: `assert result.fixtures == fixtures`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 72: `def test_rejects_max_items_less_than_or_equal_to_zero() -> None:`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 76: `assert result.reason == "max_items must be greater than zero"`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 79: `def test_rejects_max_items_greater_than_four() -> None:`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 83: `assert result.reason == "max_items exceeds fixture contract limit"`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 86: `def test_rejects_fixture_count_greater_than_max_items() -> None:`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 92: `assert result.reason == "fixture count exceeds max_items"`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 93: `assert result.fixture_count == 2`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 94: `assert result.fixtures == fixtures`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 97: `def test_rejects_fixture_count_greater_than_four() -> None:`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 103: `assert result.reason == "fixture count exceeds fixture contract limit"`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 104: `assert result.fixture_count == 5`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 105: `assert result.fixtures == fixtures`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 108: `def test_rejects_non_fixture_item() -> None:`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 112: `assert result.reason == "fixture must be ControlledRealAssetFixtureItem"`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 123: `def test_rejects_empty_required_strings(field_name: str, reason: str) -> None:`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 129: `assert result.reason == reason`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 132: `def test_rejects_unsupported_fixture_type() -> None:`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 138: `assert result.reason == "unsupported fixture_type"`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 141: `def test_rejects_notes_none() -> None:`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 147: `assert result.reason == "notes is required"`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 150: `def test_rejects_allowed_for_metadata_false() -> None:`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 156: `assert result.reason == "metadata access must be allowed"`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 159: `def test_rejects_allowed_for_pdf_text_extraction_true() -> None:`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 165: `assert result.reason == "pdf text extraction is not allowed by this contract"`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 168: `def test_rejects_allowed_for_image_metadata_true() -> None:`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 174: `assert result.reason == "image metadata is not allowed by this contract"`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 177: `def test_rejects_allowed_for_evidence_true() -> None:`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 183: `assert result.reason == "evidence creation is not allowed by this contract"`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 186: `def test_rejects_duplicate_fixture_id() -> None:`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 193: `assert result.reason == "duplicate fixture_id"`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 196: `def test_rejects_duplicate_fixture_path() -> None:`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 203: `assert result.reason == "duplicate fixture_path"`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 206: `def test_fixture_path_string_is_preserved_exactly_and_not_normalized() -> None:`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 213: `assert result.fixtures[0].fixture_path == fixture_path`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 216: `def test_fixture_type_is_not_inferred_from_fixture_path() -> None:`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 225: `assert result.fixtures[0].fixture_type == "product_spec_pdf"`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 228: `def test_result_fixtures_are_tuple() -> None:`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 234: `def test_fixture_item_is_immutable() -> None:`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 237: `with pytest.raises(FrozenInstanceError):`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 241: `def test_contract_module_has_no_filesystem_or_scanner_dependencies() -> None:`
- `tests/ingestion/test_controlled_real_asset_metadata_smoke_flow.py` line 165: `def test_controlled_real_asset_metadata_smoke_flow_uses_explicit_tmp_path_fixture(`
- `tests/ingestion/test_controlled_real_asset_metadata_smoke_flow.py` line 182: `assert result["fixture_contract"].fixture_count == 3`
- `tests/ingestion/test_controlled_real_asset_metadata_smoke_flow.py` line 190: `assert result["collector_result"].item_count == 3`
- `tests/ingestion/test_controlled_real_asset_metadata_smoke_flow.py` line 197: `assert relative_paths == {`
- `tests/ingestion/test_controlled_real_asset_metadata_smoke_flow.py` line 202: `assert suffixes == {".pdf", ".jpg", ".png"}`
- `tests/ingestion/test_controlled_real_asset_metadata_smoke_flow.py` line 213: `def test_current_pr016_contract_blocks_filesystem_metadata_flag(tmp_path):`
- `tests/ingestion/test_controlled_real_asset_metadata_smoke_flow.py` line 238: `def test_fixture_contract_rejects_pdf_text_extraction_before_metadata_flow(`
- `tests/ingestion/test_controlled_real_asset_metadata_smoke_flow.py` line 270: `def test_fixture_contract_rejects_evidence_before_metadata_flow(tmp_path):`
- `tests/ingestion/test_controlled_real_asset_metadata_smoke_flow.py` line 300: `def test_controlled_real_asset_metadata_smoke_flow_does_not_include_nested_files(`
- `tests/ingestion/test_controlled_real_asset_metadata_smoke_flow.py` line 326: `assert result["collector_result"].item_count == 4`
- `tests/ingestion/test_controlled_real_asset_metadata_smoke_flow.py` line 333: `def test_collected_items_expose_no_content_derived_fields(tmp_path):`
- `tests/ingestion/test_controlled_real_asset_metadata_smoke_flow.py` line 364: `def test_smoke_flow_test_file_uses_no_batch_scanner_or_type_detector() -> None:`
- `tests/ingestion/test_creative_asset_batch_scanner.py` line 6: `def test_scans_direct_files_and_reports_detected_asset_types(tmp_path):`
- `tests/ingestion/test_creative_asset_batch_scanner.py` line 34: `assert report.root == folder`
- `tests/ingestion/test_creative_asset_batch_scanner.py` line 35: `assert report.total_files == 6`
- `tests/ingestion/test_creative_asset_batch_scanner.py` line 36: `assert report.count_by_type(CreativeAssetType.PNG) == 1`
- `tests/ingestion/test_creative_asset_batch_scanner.py` line 37: `assert report.count_by_type(CreativeAssetType.JPEG) == 1`
- `tests/ingestion/test_creative_asset_batch_scanner.py` line 38: `assert report.count_by_type(CreativeAssetType.PDF) == 1`
- `tests/ingestion/test_creative_asset_batch_scanner.py` line 39: `assert report.count_by_type(CreativeAssetType.UTF8_TEXT) == 1`
- `tests/ingestion/test_creative_asset_batch_scanner.py` line 40: `assert report.count_by_type(CreativeAssetType.UNKNOWN) == 2`
- `tests/ingestion/test_creative_asset_batch_scanner.py` line 46: `assert png_item.size == png.stat().st_size`
- `tests/ingestion/test_creative_asset_batch_scanner.py` line 53: `assert misleading_item.asset_type == CreativeAssetType.UNKNOWN`
- `tests/ingestion/test_creative_asset_batch_scanner.py` line 56: `def test_captures_file_scan_failure(monkeypatch, tmp_path):`
- `tests/ingestion/test_creative_asset_batch_scanner.py` line 73: `assert report.total_files == 1`
- `tests/ingestion/test_creative_asset_batch_scanner.py` line 74: `assert report.items[0].path == file`
- `tests/ingestion/test_creative_asset_batch_scanner.py` line 75: `assert report.items[0].asset_type == CreativeAssetType.UNKNOWN`
- `tests/ingestion/test_creative_asset_batch_scanner.py` line 76: `assert report.items[0].size == file.stat().st_size`
- `tests/ingestion/test_creative_asset_batch_scanner.py` line 77: `assert report.items[0].error == "cannot read file"`
- `tests/ingestion/test_creative_asset_scan_report_inspector.py` line 4: `def test_inspect_report_computes_inspection_insights():`
- `tests/ingestion/test_creative_asset_scan_report_inspector.py` line 55: `assert inspection.root == "D:\\DAT"`
- `tests/ingestion/test_creative_asset_scan_report_inspector.py` line 56: `assert inspection.total_files == 5`
- `tests/ingestion/test_creative_asset_scan_report_inspector.py` line 57: `assert inspection.counts == data["counts"]`
- `tests/ingestion/test_creative_asset_scan_report_inspector.py` line 58: `assert inspection.total_size_by_type == {`
- `tests/ingestion/test_creative_asset_scan_report_inspector.py` line 72: `assert inspection.utf8_text_files == [data["items"][3]]`
- `tests/ingestion/test_creative_asset_scan_report_inspector.py` line 73: `assert inspection.pdf_files == [data["items"][2]]`
- `tests/ingestion/test_creative_asset_scan_report_inspector.py` line 74: `assert inspection.unknown_files == [data["items"][4]]`
- `tests/ingestion/test_creative_asset_scan_report_inspector.py` line 75: `assert inspection.failed_files == [data["items"][4]]`
- `tests/ingestion/test_creative_asset_scan_report_serializer.py` line 10: `def test_to_dict_serializes_scan_report(tmp_path):`
- `tests/ingestion/test_creative_asset_scan_report_serializer.py` line 33: `assert result["root"] == str(tmp_path)`
- `tests/ingestion/test_creative_asset_scan_report_serializer.py` line 34: `assert result["total_files"] == 2`
- `tests/ingestion/test_creative_asset_scan_report_serializer.py` line 35: `assert result["counts"] == {`
- `tests/ingestion/test_creative_asset_scan_report_serializer.py` line 46: `assert result["failed"] == 1`
- `tests/ingestion/test_creative_asset_scan_report_serializer.py` line 47: `assert result["items"] == [`
- `tests/ingestion/test_creative_asset_scan_report_serializer.py` line 63: `def test_write_json_writes_valid_json(tmp_path):`
- `tests/ingestion/test_creative_asset_scan_report_serializer.py` line 79: `assert data["root"] == str(tmp_path)`
- `tests/ingestion/test_creative_asset_scan_report_serializer.py` line 80: `assert data["total_files"] == 1`
- `tests/ingestion/test_creative_asset_scan_report_serializer.py` line 81: `assert data["counts"]["PDF"] == 1`
- `tests/ingestion/test_creative_asset_scan_report_serializer.py` line 82: `assert data["items"][0]["asset_type"] == "PDF"`
- `tests/ingestion/test_creative_asset_type_detector.py` line 5: `def test_detects_png_from_magic_bytes_with_dat_extension(tmp_path):`
- `tests/ingestion/test_creative_asset_type_detector.py` line 11: `assert result == CreativeAssetType.PNG`
- `tests/ingestion/test_creative_asset_type_detector.py` line 14: `def test_detects_jpeg_from_magic_bytes_with_dat_extension(tmp_path):`
- `tests/ingestion/test_creative_asset_type_detector.py` line 20: `assert result == CreativeAssetType.JPEG`
- `tests/ingestion/test_creative_asset_type_detector.py` line 23: `def test_detects_pdf_from_magic_bytes_with_dat_extension(tmp_path):`
- `tests/ingestion/test_creative_asset_type_detector.py` line 29: `assert result == CreativeAssetType.PDF`
- `tests/ingestion/test_creative_asset_type_detector.py` line 32: `def test_detects_webp_from_magic_bytes_with_dat_extension(tmp_path):`
- `tests/ingestion/test_creative_asset_type_detector.py` line 38: `assert result == CreativeAssetType.WEBP`
- `tests/ingestion/test_creative_asset_type_detector.py` line 41: `def test_detects_little_endian_tiff_from_magic_bytes_with_dat_extension(tmp_path):`
- `tests/ingestion/test_creative_asset_type_detector.py` line 47: `assert result == CreativeAssetType.TIFF`
- `tests/ingestion/test_creative_asset_type_detector.py` line 50: `def test_detects_big_endian_tiff_from_magic_bytes_with_dat_extension(tmp_path):`
- `tests/ingestion/test_creative_asset_type_detector.py` line 56: `assert result == CreativeAssetType.TIFF`
- `tests/ingestion/test_creative_asset_type_detector.py` line 59: `def test_detects_mp4_mp42_from_magic_bytes_with_dat_extension(tmp_path):`
- `tests/ingestion/test_creative_asset_type_detector.py` line 65: `assert result == CreativeAssetType.MP4`
- `tests/ingestion/test_creative_asset_type_detector.py` line 68: `def test_detects_mp4_isom_from_magic_bytes_with_dat_extension(tmp_path):`
- `tests/ingestion/test_creative_asset_type_detector.py` line 74: `assert result == CreativeAssetType.MP4`
- `tests/ingestion/test_creative_asset_type_detector.py` line 77: `def test_detects_zip_container_from_magic_bytes_with_dat_extension(tmp_path):`
- `tests/ingestion/test_creative_asset_type_detector.py` line 83: `assert result == CreativeAssetType.ZIP_CONTAINER`
- `tests/ingestion/test_creative_asset_type_detector.py` line 86: `def test_detects_utf8_text_with_dat_extension(tmp_path):`
- `tests/ingestion/test_creative_asset_type_detector.py` line 92: `assert result == CreativeAssetType.UTF8_TEXT`
- `tests/ingestion/test_creative_asset_type_detector.py` line 95: `def test_detects_unknown_for_invalid_binary_content(tmp_path):`
- `tests/ingestion/test_creative_asset_type_detector.py` line 101: `assert result == CreativeAssetType.UNKNOWN`
- `tests/ingestion/test_creative_asset_type_detector.py` line 104: `def test_ignores_extension_when_content_is_unknown(tmp_path):`
- `tests/ingestion/test_creative_asset_type_detector.py` line 110: `assert result == CreativeAssetType.UNKNOWN`
- `tests/ingestion/test_inspect_scan_report.py` line 51: `def test_inspect_scan_report_prints_key_sections(tmp_path, capsys):`
- `tests/ingestion/test_inspect_scan_report.py` line 58: `assert result == 0`
- `tests/ingestion/test_inspect_scan_report.py` line 76: `def test_inspect_scan_report_returns_error_for_missing_report(tmp_path, capsys):`
- `tests/ingestion/test_inspect_scan_report.py` line 82: `assert result == 1`
- `tests/ingestion/test_inspect_scan_report.py` line 86: `def test_inspect_scan_report_returns_error_for_directory(tmp_path, capsys):`
- `tests/ingestion/test_inspect_scan_report.py` line 90: `assert result == 1`
- `tests/ingestion/test_inspect_scan_report.py` line 94: `def test_inspect_scan_report_returns_error_for_invalid_json(tmp_path, capsys):`
- `tests/ingestion/test_inspect_scan_report.py` line 101: `assert result == 1`
- `tests/ingestion/test_inspect_scan_report.py` line 105: `def test_inspect_scan_report_top_limits_largest_files(tmp_path, capsys):`
- `tests/ingestion/test_inspect_scan_report.py` line 116: `assert result == 0`
- `tests/ingestion/test_inspect_unknown_assets.py` line 17: `def test_inspect_unknown_assets_prints_header_details(tmp_path, capsys):`
- `tests/ingestion/test_inspect_unknown_assets.py` line 36: `assert result == 0`
- `tests/ingestion/test_inspect_unknown_assets.py` line 45: `def test_inspect_unknown_assets_bytes_changes_header_length(tmp_path, capsys):`
- `tests/ingestion/test_inspect_unknown_assets.py` line 68: `assert result == 0`
- `tests/ingestion/test_inspect_unknown_assets.py` line 73: `def test_inspect_unknown_assets_limit_limits_printed_items(tmp_path, capsys):`
- `tests/ingestion/test_inspect_unknown_assets.py` line 104: `assert result == 0`
- `tests/ingestion/test_inspect_unknown_assets.py` line 110: `def test_inspect_unknown_assets_returns_error_for_missing_report(`
- `tests/ingestion/test_inspect_unknown_assets.py` line 119: `assert result == 1`
- `tests/ingestion/test_inspect_unknown_assets.py` line 123: `def test_inspect_unknown_assets_returns_error_for_directory(tmp_path, capsys):`
- `tests/ingestion/test_inspect_unknown_assets.py` line 127: `assert result == 1`
- `tests/ingestion/test_inspect_unknown_assets.py` line 131: `def test_inspect_unknown_assets_returns_error_for_invalid_json(tmp_path, capsys):`
- `tests/ingestion/test_inspect_unknown_assets.py` line 138: `assert result == 1`
- `tests/ingestion/test_real_asset_dry_run_contract.py` line 31: `def test_rejects_blocked_sandbox_policy_decision():`
- `tests/ingestion/test_real_asset_dry_run_contract.py` line 40: `assert decision.sandbox_reason == sandbox_decision.reason`
- `tests/ingestion/test_real_asset_dry_run_contract.py` line 43: `def test_rejects_header_only_mode():`
- `tests/ingestion/test_real_asset_dry_run_contract.py` line 51: `def test_rejects_extraction_preview_mode():`
- `tests/ingestion/test_real_asset_dry_run_contract.py` line 59: `def test_rejects_unknown_mode():`
- `tests/ingestion/test_real_asset_dry_run_contract.py` line 66: `def test_rejects_planned_scan():`
- `tests/ingestion/test_real_asset_dry_run_contract.py` line 74: `def test_rejects_planned_real_asset_reads():`
- `tests/ingestion/test_real_asset_dry_run_contract.py` line 82: `def test_rejects_planned_mutation():`
- `tests/ingestion/test_real_asset_dry_run_contract.py` line 90: `def test_allows_safe_metadata_only_contract_when_policy_passed():`
- `tests/ingestion/test_real_asset_dry_run_contract.py` line 95: `assert decision.item_count == 0`
- `tests/ingestion/test_real_asset_dry_run_contract.py` line 98: `def test_preserves_all_sandbox_decision_values():`
- `tests/ingestion/test_real_asset_dry_run_contract.py` line 109: `assert decision.sandbox_allowed == sandbox_decision.allowed`
- `tests/ingestion/test_real_asset_dry_run_contract.py` line 110: `assert decision.sandbox_reason == sandbox_decision.reason`
- `tests/ingestion/test_real_asset_dry_run_contract.py` line 111: `assert decision.root == sandbox_decision.root`
- `tests/ingestion/test_real_asset_dry_run_contract.py` line 112: `assert decision.recursive == sandbox_decision.recursive`
- `tests/ingestion/test_real_asset_dry_run_contract.py` line 113: `assert decision.read_only == sandbox_decision.read_only`
- `tests/ingestion/test_real_asset_dry_run_contract.py` line 114: `assert decision.allow_real_asset_reads == (`
- `tests/ingestion/test_real_asset_dry_run_contract.py` line 117: `assert decision.allow_mutation == sandbox_decision.allow_mutation`
- `tests/ingestion/test_real_asset_dry_run_contract.py` line 120: `def test_preserves_all_dry_run_contract_input_values():`
- `tests/ingestion/test_real_asset_dry_run_contract.py` line 128: `assert decision.mode == "header_only"`
- `tests/ingestion/test_real_asset_dry_run_contract.py` line 134: `def test_reports_item_count_zero():`
- `tests/ingestion/test_real_asset_dry_run_contract.py` line 138: `assert rejected.item_count == 0`
- `tests/ingestion/test_real_asset_dry_run_contract.py` line 139: `assert allowed.item_count == 0`
- `tests/ingestion/test_real_asset_metadata_collection_contract.py` line 40: `def test_rejects_blocked_boundary_result():`
- `tests/ingestion/test_real_asset_metadata_collection_contract.py` line 52: `assert decision.boundary_reason == boundary_result.reason`
- `tests/ingestion/test_real_asset_metadata_collection_contract.py` line 55: `def test_rejects_non_metadata_only_mode():`
- `tests/ingestion/test_real_asset_metadata_collection_contract.py` line 65: `def test_rejects_filesystem_metadata_flag():`
- `tests/ingestion/test_real_asset_metadata_collection_contract.py` line 73: `def test_rejects_recursive_collection_flag():`
- `tests/ingestion/test_real_asset_metadata_collection_contract.py` line 81: `def test_rejects_content_reads_flag():`
- `tests/ingestion/test_real_asset_metadata_collection_contract.py` line 89: `def test_rejects_mutation_flag():`
- `tests/ingestion/test_real_asset_metadata_collection_contract.py` line 97: `def test_allows_safe_disabled_skeleton_config():`
- `tests/ingestion/test_real_asset_metadata_collection_contract.py` line 105: `def test_preserves_boundary_result_values():`
- `tests/ingestion/test_real_asset_metadata_collection_contract.py` line 114: `assert decision.boundary_allowed == boundary_result.allowed`
- `tests/ingestion/test_real_asset_metadata_collection_contract.py` line 115: `assert decision.boundary_reason == boundary_result.reason`
- `tests/ingestion/test_real_asset_metadata_collection_contract.py` line 116: `assert decision.mode == boundary_result.mode`
- `tests/ingestion/test_real_asset_metadata_collection_contract.py` line 119: `def test_preserves_contract_input_flags():`
- `tests/ingestion/test_real_asset_metadata_collection_contract.py` line 133: `def test_exposes_no_filesystem_execution_or_content_derived_fields():`
- `tests/ingestion/test_real_asset_metadata_collector.py` line 65: `def test_rejects_blocked_collection_decision():`
- `tests/ingestion/test_real_asset_metadata_collector.py` line 77: `assert result.decision_reason == decision.reason`
- `tests/ingestion/test_real_asset_metadata_collector.py` line 80: `def test_returns_empty_items_when_decision_is_blocked():`
- `tests/ingestion/test_real_asset_metadata_collector.py` line 86: `assert result.item_count == 0`
- `tests/ingestion/test_real_asset_metadata_collector.py` line 87: `assert result.items == ()`
- `tests/ingestion/test_real_asset_metadata_collector.py` line 90: `def test_allows_supplied_synthetic_metadata_items_when_decision_is_allowed():`
- `tests/ingestion/test_real_asset_metadata_collector.py` line 97: `assert result.items == (item,)`
- `tests/ingestion/test_real_asset_metadata_collector.py` line 100: `def test_preserves_supplied_items_exactly():`
- `tests/ingestion/test_real_asset_metadata_collector.py` line 111: `def test_preserves_item_count_from_supplied_items():`
- `tests/ingestion/test_real_asset_metadata_collector.py` line 120: `assert result.item_count == 3`
- `tests/ingestion/test_real_asset_metadata_collector.py` line 123: `def test_preserves_decision_allowed_and_reason():`
- `tests/ingestion/test_real_asset_metadata_collector.py` line 131: `assert result.decision_allowed == decision.allowed`
- `tests/ingestion/test_real_asset_metadata_collector.py` line 132: `assert result.decision_reason == decision.reason`
- `tests/ingestion/test_real_asset_metadata_collector.py` line 135: `def test_accepts_empty_supplied_items_when_decision_is_allowed():`
- `tests/ingestion/test_real_asset_metadata_collector.py` line 139: `assert result.item_count == 0`
- `tests/ingestion/test_real_asset_metadata_collector.py` line 140: `assert result.items == ()`
- `tests/ingestion/test_real_asset_metadata_collector.py` line 143: `def test_exposes_no_filesystem_execution_or_content_derived_fields():`
- `tests/ingestion/test_real_asset_metadata_collector.py` line 172: `def test_module_does_not_expose_path_based_behavior():`
- `tests/ingestion/test_real_asset_metadata_collector.py` line 178: `def test_collector_has_no_forbidden_dependency_exports():`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 59: `def test_rejects_blocked_real_asset_dry_run_result():`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 71: `assert decision.dry_run_reason == dry_run_result.reason`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 74: `def test_rejects_non_metadata_only_mode():`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 84: `def test_rejects_negative_size():`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 92: `def test_rejects_empty_path():`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 100: `def test_rejects_empty_relative_path():`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 108: `def test_allows_empty_supplied_item_list():`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 113: `assert decision.item_count == 0`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 114: `assert decision.items == ()`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 117: `def test_allows_supplied_synthetic_metadata_items():`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 123: `assert decision.item_count == 1`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 124: `assert decision.items == (item,)`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 127: `def test_preserves_dry_run_result_values():`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 136: `assert decision.dry_run_allowed == dry_run_result.allowed`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 137: `assert decision.dry_run_reason == dry_run_result.reason`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 138: `assert decision.mode == dry_run_result.mode`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 141: `def test_preserves_item_values_exactly():`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 154: `assert decision.items == (item,)`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 155: `assert decision.items[0].path == "synthetic/assets/spec-sheet.pdf"`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 156: `assert decision.items[0].relative_path == "spec-sheet.pdf"`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 159: `assert decision.items[0].size == 0`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 160: `assert decision.items[0].suffix == ".pdf"`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 161: `assert decision.items[0].error == "Synthetic metadata failure."`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 164: `def test_derives_item_count_only_from_supplied_items():`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 176: `assert decision.item_count == 2`
- `tests/ingestion/test_real_asset_metadata_dry_run_boundary.py` line 179: `def test_exposes_no_content_derived_fields():`
- `tests/ingestion/test_real_asset_sandbox_policy.py` line 18: `def test_rejects_missing_root():`
- `tests/ingestion/test_real_asset_sandbox_policy.py` line 26: `def test_rejects_non_read_only_mode():`
- `tests/ingestion/test_real_asset_sandbox_policy.py` line 33: `def test_rejects_mutation():`
- `tests/ingestion/test_real_asset_sandbox_policy.py` line 41: `def test_rejects_real_asset_reads():`
- `tests/ingestion/test_real_asset_sandbox_policy.py` line 49: `def test_rejects_recursive_mode():`
- `tests/ingestion/test_real_asset_sandbox_policy.py` line 57: `def test_allows_explicit_safe_non_recursive_read_only_sandbox_config():`
- `tests/ingestion/test_real_asset_sandbox_policy.py` line 64: `def test_decision_preserves_all_input_values():`
- `tests/ingestion/test_real_asset_sandbox_policy.py` line 75: `assert decision.root == root`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 29: `def test_rejects_non_positive_max_items(tmp_path):`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 33: `assert result.item_count == 0`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 34: `assert result.items == ()`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 39: `def test_rejects_missing_explicit_root(tmp_path):`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 45: `assert result.item_count == 0`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 46: `assert result.items == ()`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 50: `def test_rejects_root_that_is_a_file(tmp_path):`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 57: `assert result.item_count == 0`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 58: `assert result.items == ()`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 62: `def test_collects_metadata_for_immediate_child_file_in_tmp_path(tmp_path):`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 69: `assert result.item_count == 1`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 70: `assert result.items[0] == RealAssetMetadataDryRunItem(`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 81: `def test_collects_metadata_for_immediate_child_directory_in_tmp_path(tmp_path):`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 88: `assert result.item_count == 1`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 89: `assert result.items[0].path == str(child)`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 90: `assert result.items[0].relative_path == "nested"`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 93: `assert result.items[0].size == 0`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 94: `assert result.items[0].suffix == ""`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 98: `def test_does_not_recurse_into_nested_directories(tmp_path):`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 109: `assert result.item_count == 1`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 112: `def test_applies_max_items_limit(tmp_path):`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 120: `assert result.item_count == 2`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 121: `assert len(result.items) == 2`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 124: `def test_returns_real_asset_metadata_dry_run_item_values(tmp_path):`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 132: `def test_preserves_suffix_and_relative_path(tmp_path):`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 137: `assert result.items[0].relative_path == "manual.pdf"`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 138: `assert result.items[0].suffix == ".pdf"`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 141: `def test_does_not_read_file_contents(monkeypatch, tmp_path):`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 154: `assert result.item_count == 1`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 157: `def test_exposes_no_content_derived_fields():`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 178: `def test_module_does_not_expose_scanner_detector_or_artifact_dependencies():`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 191: `def test_collects_child_metadata_error_without_raising(monkeypatch, tmp_path):`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 206: `assert result.item_count == 1`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 207: `assert result.items[0].path == str(child)`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 208: `assert result.items[0].size == 0`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 213: `def test_tests_use_tmp_path_only_for_adapter_roots(tmp_path):`
- `tests/ingestion/test_real_filesystem_metadata_adapter.py` line 216: `assert result.root == str(tmp_path)`
- `tests/ingestion/test_real_filesystem_metadata_adapter_safety_contract.py` line 25: `def test_rejects_non_positive_max_items():`
- `tests/ingestion/test_real_filesystem_metadata_adapter_safety_contract.py` line 33: `def test_rejects_max_items_greater_than_100():`
- `tests/ingestion/test_real_filesystem_metadata_adapter_safety_contract.py` line 41: `def test_rejects_recursive_flag():`
- `tests/ingestion/test_real_filesystem_metadata_adapter_safety_contract.py` line 49: `def test_rejects_content_reads_flag():`
- `tests/ingestion/test_real_filesystem_metadata_adapter_safety_contract.py` line 57: `def test_rejects_mutation_flag():`
- `tests/ingestion/test_real_filesystem_metadata_adapter_safety_contract.py` line 65: `def test_rejects_symlink_flag():`
- `tests/ingestion/test_real_filesystem_metadata_adapter_safety_contract.py` line 73: `def test_rejects_missing_stable_ordering_requirement():`
- `tests/ingestion/test_real_filesystem_metadata_adapter_safety_contract.py` line 81: `def test_allows_safe_defaults():`
- `tests/ingestion/test_real_filesystem_metadata_adapter_safety_contract.py` line 88: `def test_preserves_all_input_values_in_decision():`
- `tests/ingestion/test_real_filesystem_metadata_adapter_safety_contract.py` line 98: `assert decision.max_items == 101`
- `tests/ingestion/test_real_filesystem_metadata_adapter_safety_contract.py` line 106: `def test_exposes_no_filesystem_execution_or_content_derived_fields():`
- `tests/ingestion/test_real_filesystem_metadata_adapter_safety_contract.py` line 132: `def test_module_does_not_expose_forbidden_dependencies():`
- `tests/ingestion/test_scan_assets.py` line 6: `def test_scan_assets_prints_summary_for_valid_folder(tmp_path, capsys):`
- `tests/ingestion/test_scan_assets.py` line 16: `assert result == 0`
- `tests/ingestion/test_scan_assets.py` line 26: `def test_scan_assets_writes_json_report_with_output(tmp_path, capsys):`
- `tests/ingestion/test_scan_assets.py` line 42: `assert result == 0`
- `tests/ingestion/test_scan_assets.py` line 45: `assert data["root"] == str(folder)`
- `tests/ingestion/test_scan_assets.py` line 46: `assert data["total_files"] == 2`
- `tests/ingestion/test_scan_assets.py` line 47: `assert data["counts"]["PNG"] == 1`
- `tests/ingestion/test_scan_assets.py` line 48: `assert data["counts"]["UTF8_TEXT"] == 1`
- `tests/ingestion/test_scan_assets.py` line 49: `assert data["failed"] == 0`
- `tests/ingestion/test_scan_assets.py` line 50: `assert len(data["items"]) == 2`
- `tests/ingestion/test_scan_assets.py` line 53: `def test_scan_assets_returns_error_for_missing_folder(tmp_path, capsys):`
- `tests/ingestion/test_scan_assets.py` line 59: `assert result == 1`
- `tests/ingestion/test_scan_assets.py` line 63: `def test_scan_assets_returns_error_for_file_path(tmp_path, capsys):`
- `tests/ingestion/test_scan_assets.py` line 70: `assert result == 1`
- `tests/ingestion/test_scan_assets.py` line 74: `def test_scan_assets_returns_error_for_missing_output_parent(tmp_path, capsys):`
- `tests/ingestion/test_scan_assets.py` line 87: `assert result == 1`
- `tests/ingestion/test_scan_assets.py` line 91: `def test_scan_assets_returns_error_for_json_write_failure(`
- `tests/ingestion/test_scan_assets.py` line 116: `assert result == 1`
- `tests/ingestion/test_scan_assets.py` line 120: `def test_scan_assets_is_non_recursive_by_default(tmp_path, capsys):`
- `tests/ingestion/test_scan_assets.py` line 130: `assert result == 0`
- `tests/ingestion/test_scan_assets.py` line 136: `def test_scan_assets_recursive_includes_nested_files(tmp_path, capsys):`
- `tests/ingestion/test_scan_assets.py` line 149: `assert result == 0`
- `tests/ingestion/test_unknown_asset_header_inspector.py` line 5: `def test_inspect_unknown_assets_reads_header_bytes_and_formats_header(tmp_path):`
- `tests/ingestion/test_unknown_asset_header_inspector.py` line 30: `assert len(inspections) == 1`
- `tests/ingestion/test_unknown_asset_header_inspector.py` line 31: `assert inspections[0].path == str(file)`
- `tests/ingestion/test_unknown_asset_header_inspector.py` line 32: `assert inspections[0].size == file.stat().st_size`
- `tests/ingestion/test_unknown_asset_header_inspector.py` line 33: `assert inspections[0].header_hex == "52 49 46 46 78 78 78 78 57 45 42 50"`
- `tests/ingestion/test_unknown_asset_header_inspector.py` line 34: `assert inspections[0].header_ascii == "RIFFxxxxWEBP"`
- `tests/ingestion/test_unknown_asset_header_inspector.py` line 35: `assert inspections[0].candidate == "WEBP"`
- `tests/ingestion/test_unknown_asset_header_inspector.py` line 39: `def test_inspect_unknown_assets_respects_limit(tmp_path):`
- `tests/ingestion/test_unknown_asset_header_inspector.py` line 66: `assert len(inspections) == 1`
- `tests/ingestion/test_unknown_asset_header_inspector.py` line 67: `assert inspections[0].path == str(first)`
- `tests/ingestion/test_unknown_asset_header_inspector.py` line 70: `def test_inspect_unknown_assets_captures_missing_file_error(tmp_path):`
- `tests/ingestion/test_unknown_asset_header_inspector.py` line 85: `assert inspections[0].path == str(missing)`
- `tests/ingestion/test_unknown_asset_header_inspector.py` line 86: `assert inspections[0].size == 99`
- `tests/ingestion/test_unknown_asset_header_inspector.py` line 87: `assert inspections[0].header_hex == ""`
- `tests/ingestion/test_unknown_asset_header_inspector.py` line 88: `assert inspections[0].header_ascii == ""`
- `tests/ingestion/test_unknown_asset_header_inspector.py` line 89: `assert inspections[0].candidate == "UNKNOWN"`
- `tests/ingestion/test_unknown_asset_header_inspector.py` line 93: `def test_guess_candidate_detects_small_candidate_set():`
- `tests/ingestion/test_unknown_asset_header_inspector.py` line 94: `assert guess_candidate(b"RIFFxxxxWEBPmore") == "WEBP"`
- `tests/ingestion/test_unknown_asset_header_inspector.py` line 95: `assert guess_candidate(b"RIFFxxxxAVI more") == "RIFF_CONTAINER"`
- `tests/ingestion/test_unknown_asset_header_inspector.py` line 96: `assert guess_candidate(b"PK\x03\x04content") == "ZIP_CONTAINER"`
- `tests/ingestion/test_unknown_asset_header_inspector.py` line 97: `assert guess_candidate(b"\x1f\x8bcontent") == "GZIP"`
- `tests/ingestion/test_unknown_asset_header_inspector.py` line 98: `assert guess_candidate(b"GIF89acontent") == "GIF"`
- `tests/ingestion/test_unknown_asset_header_inspector.py` line 99: `assert guess_candidate(b" \n {\"key\": true}") == "JSON_TEXT"`
- `tests/ingestion/test_unknown_asset_header_inspector.py` line 100: `assert guess_candidate(b"\x00\x01\x02") == "UNKNOWN"`
- `tests/knowledge/test_export_text_knowledge.py` line 16: `def test_export_text_knowledge_writes_valid_knowledge_items(`
- `tests/knowledge/test_export_text_knowledge.py` line 49: `assert result == 0`
- `tests/knowledge/test_export_text_knowledge.py` line 55: `assert data == {`
- `tests/knowledge/test_export_text_knowledge.py` line 73: `def test_export_text_knowledge_preserves_order_and_evidence_index(`
- `tests/knowledge/test_export_text_knowledge.py` line 106: `assert result == 0`
- `tests/knowledge/test_export_text_knowledge.py` line 107: `assert data["knowledge_items"] == [`
- `tests/knowledge/test_export_text_knowledge.py` line 123: `def test_export_text_knowledge_skips_invalid_evidence_records(`
- `tests/knowledge/test_export_text_knowledge.py` line 163: `assert result == 0`
- `tests/knowledge/test_export_text_knowledge.py` line 167: `assert data["knowledge_items"] == [`
- `tests/knowledge/test_export_text_knowledge.py` line 181: `assert set(data["knowledge_items"][0]) == {`
- `tests/knowledge/test_export_text_knowledge.py` line 189: `def test_export_text_knowledge_preserves_non_ascii_content(`
- `tests/knowledge/test_export_text_knowledge.py` line 219: `assert result == 0`
- `tests/knowledge/test_export_text_knowledge.py` line 222: `assert data["knowledge_items"][0]["content"] == content`
- `tests/knowledge/test_export_text_knowledge.py` line 225: `def test_export_text_knowledge_preserves_newline_content(`
- `tests/knowledge/test_export_text_knowledge.py` line 254: `assert result == 0`
- `tests/knowledge/test_export_text_knowledge.py` line 255: `assert data["knowledge_items"][0]["content"] == content`
- `tests/knowledge/test_export_text_knowledge.py` line 258: `def test_export_text_knowledge_returns_error_for_missing_artifact(`
- `tests/knowledge/test_export_text_knowledge.py` line 272: `assert result == 1`
- `tests/knowledge/test_export_text_knowledge.py` line 276: `def test_export_text_knowledge_returns_error_for_directory(`
- `tests/knowledge/test_export_text_knowledge.py` line 289: `assert result == 1`
- `tests/knowledge/test_export_text_knowledge.py` line 293: `def test_export_text_knowledge_returns_error_for_invalid_json(`
- `tests/knowledge/test_export_text_knowledge.py` line 308: `assert result == 1`
- `tests/knowledge/test_export_text_knowledge.py` line 312: `def test_export_text_knowledge_returns_error_for_malformed_artifact(`
- `tests/knowledge/test_export_text_knowledge.py` line 332: `assert result == 1`
- `tests/knowledge/test_export_text_knowledge.py` line 336: `def test_export_text_knowledge_returns_error_for_missing_output_parent(`
- `tests/knowledge/test_export_text_knowledge.py` line 356: `assert result == 1`
- `tests/knowledge/test_inspect_text_knowledge.py` line 13: `def test_inspect_text_knowledge_prints_summary(tmp_path, capsys):`
- `tests/knowledge/test_inspect_text_knowledge.py` line 38: `assert result == 0`
- `tests/knowledge/test_inspect_text_knowledge.py` line 47: `def test_inspect_text_knowledge_returns_error_for_missing_file(`
- `tests/knowledge/test_inspect_text_knowledge.py` line 56: `assert result == 1`
- `tests/knowledge/test_inspect_text_knowledge.py` line 60: `def test_inspect_text_knowledge_returns_error_for_directory(`
- `tests/knowledge/test_inspect_text_knowledge.py` line 67: `assert result == 1`
- `tests/knowledge/test_inspect_text_knowledge.py` line 71: `def test_inspect_text_knowledge_returns_error_for_invalid_json(`
- `tests/knowledge/test_inspect_text_knowledge.py` line 81: `assert result == 1`
- `tests/knowledge/test_inspect_text_knowledge.py` line 85: `def test_inspect_text_knowledge_returns_error_for_malformed_artifact(`
- `tests/knowledge/test_inspect_text_knowledge.py` line 100: `assert result == 1`
- `tests/knowledge/test_inspect_text_knowledge.py` line 104: `def test_inspect_text_knowledge_returns_zero_for_invalid_records_after_readable_artifact(`
- `tests/knowledge/test_inspect_text_knowledge.py` line 128: `assert result == 0`
- `tests/knowledge/test_text_knowledge_smoke_flow.py` line 7: `def test_text_knowledge_artifact_smoke_flow_exports_then_inspects(`
- `tests/knowledge/test_text_knowledge_smoke_flow.py` line 58: `assert export_result == 0`
- `tests/knowledge/test_text_knowledge_smoke_flow.py` line 62: `assert len(records) == 3`
- `tests/knowledge/test_text_knowledge_smoke_flow.py` line 63: `assert [record["source_path"] for record in records] == [`
- `tests/knowledge/test_text_knowledge_smoke_flow.py` line 68: `assert [record["evidence_index"] for record in records] == [`
- `tests/knowledge/test_text_knowledge_smoke_flow.py` line 79: `assert records[1]["content"] == non_ascii_newline_content`
- `tests/knowledge/test_text_knowledge_smoke_flow.py` line 80: `assert records[2]["content"] == ""`
- `tests/knowledge/test_text_knowledge_smoke_flow.py` line 98: `assert set(record) == {`
- `tests/knowledge/test_text_knowledge_smoke_flow.py` line 114: `assert inspect_result == 0`
- `tests/prompt/test_export_text_prompt_candidates.py` line 40: `def test_export_text_prompt_candidates_exports_valid_text_knowledge_json(`
- `tests/prompt/test_export_text_prompt_candidates.py` line 75: `assert result == 0`
- `tests/prompt/test_export_text_prompt_candidates.py` line 82: `assert data == {`
- `tests/prompt/test_export_text_prompt_candidates.py` line 102: `def test_export_text_prompt_candidates_preserves_exact_content(`
- `tests/prompt/test_export_text_prompt_candidates.py` line 132: `assert result == 0`
- `tests/prompt/test_export_text_prompt_candidates.py` line 133: `assert data["prompt_candidates"][0]["content"] == content`
- `tests/prompt/test_export_text_prompt_candidates.py` line 136: `def test_export_text_prompt_candidates_preserves_non_ascii_content(`
- `tests/prompt/test_export_text_prompt_candidates.py` line 167: `assert result == 0`
- `tests/prompt/test_export_text_prompt_candidates.py` line 170: `assert data["prompt_candidates"][0]["content"] == content`
- `tests/prompt/test_export_text_prompt_candidates.py` line 173: `def test_export_text_prompt_candidates_preserves_newline_content(`
- `tests/prompt/test_export_text_prompt_candidates.py` line 203: `assert result == 0`
- `tests/prompt/test_export_text_prompt_candidates.py` line 204: `assert data["prompt_candidates"][0]["content"] == content`
- `tests/prompt/test_export_text_prompt_candidates.py` line 207: `def test_export_text_prompt_candidates_preserves_empty_content(`
- `tests/prompt/test_export_text_prompt_candidates.py` line 236: `assert result == 0`
- `tests/prompt/test_export_text_prompt_candidates.py` line 237: `assert data["prompt_candidates"][0]["content"] == ""`
- `tests/prompt/test_export_text_prompt_candidates.py` line 240: `def test_export_text_prompt_candidates_skips_invalid_records_and_preserves_knowledge_index(`
- `tests/prompt/test_export_text_prompt_candidates.py` line 283: `assert result == 0`
- `tests/prompt/test_export_text_prompt_candidates.py` line 287: `assert data["prompt_candidates"] == [`
- `tests/prompt/test_export_text_prompt_candidates.py` line 305: `def test_export_text_prompt_candidates_rejects_bool_size_bytes(`
- `tests/prompt/test_export_text_prompt_candidates.py` line 340: `assert result == 0`
- `tests/prompt/test_export_text_prompt_candidates.py` line 341: `assert data["prompt_candidates"] == [`
- `tests/prompt/test_export_text_prompt_candidates.py` line 352: `def test_export_text_prompt_candidates_rejects_bool_evidence_index(`
- `tests/prompt/test_export_text_prompt_candidates.py` line 387: `assert result == 0`
- `tests/prompt/test_export_text_prompt_candidates.py` line 388: `assert data["prompt_candidates"] == [`
- `tests/prompt/test_export_text_prompt_candidates.py` line 399: `def test_export_text_prompt_candidates_returns_error_for_missing_input(`
- `tests/prompt/test_export_text_prompt_candidates.py` line 413: `assert result == 1`
- `tests/prompt/test_export_text_prompt_candidates.py` line 417: `def test_export_text_prompt_candidates_returns_error_for_directory_input(`
- `tests/prompt/test_export_text_prompt_candidates.py` line 430: `assert result == 1`
- `tests/prompt/test_export_text_prompt_candidates.py` line 434: `def test_export_text_prompt_candidates_returns_error_for_invalid_json(`
- `tests/prompt/test_export_text_prompt_candidates.py` line 449: `assert result == 1`
- `tests/prompt/test_export_text_prompt_candidates.py` line 453: `def test_export_text_prompt_candidates_returns_error_for_malformed_top_level_artifact(`
- `tests/prompt/test_export_text_prompt_candidates.py` line 471: `assert result == 1`
- `tests/prompt/test_export_text_prompt_candidates.py` line 475: `def test_export_text_prompt_candidates_returns_error_for_knowledge_items_not_list(`
- `tests/prompt/test_export_text_prompt_candidates.py` line 495: `assert result == 1`
- `tests/prompt/test_export_text_prompt_candidates.py` line 499: `def test_export_text_prompt_candidates_output_excludes_forbidden_fields(`
- `tests/prompt/test_export_text_prompt_candidates.py` line 529: `assert result == 0`
- `tests/prompt/test_export_text_prompt_candidates.py` line 530: `assert set(candidate) == {`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 13: `def test_inspect_text_prompt_candidates_valid_artifact_returns_zero(`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 36: `assert result == 0`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 39: `def test_inspect_text_prompt_candidates_prints_total_prompt_candidates(`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 69: `assert result == 0`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 74: `def test_inspect_text_prompt_candidates_prints_total_content_characters(`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 104: `assert result == 0`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 108: `def test_inspect_text_prompt_candidates_prints_empty_content_count(`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 131: `assert result == 0`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 135: `def test_inspect_text_prompt_candidates_prints_invalid_record_count(`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 157: `assert result == 0`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 161: `def test_inspect_text_prompt_candidates_prints_forbidden_field_count(`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 185: `assert result == 0`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 189: `def test_inspect_text_prompt_candidates_readable_artifact_with_invalid_records_returns_zero(`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 214: `assert result == 0`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 220: `def test_inspect_text_prompt_candidates_missing_input_file_returns_one(`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 229: `assert result == 1`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 233: `def test_inspect_text_prompt_candidates_directory_input_returns_one(`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 240: `assert result == 1`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 244: `def test_inspect_text_prompt_candidates_invalid_json_returns_one(`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 254: `assert result == 1`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 258: `def test_inspect_text_prompt_candidates_top_level_list_returns_one(`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 268: `assert result == 1`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 272: `def test_inspect_text_prompt_candidates_missing_prompt_candidates_returns_one(`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 282: `assert result == 1`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 286: `def test_inspect_text_prompt_candidates_prompt_candidates_not_list_returns_one(`
- `tests/prompt/test_inspect_text_prompt_candidates.py` line 296: `assert result == 1`
- `tests/prompt/test_text_prompt_candidate_smoke_flow.py` line 31: `def test_text_prompt_candidate_artifact_smoke_flow_exports_then_inspects(`
- `tests/prompt/test_text_prompt_candidate_smoke_flow.py` line 93: `assert export_result == 0`
- `tests/prompt/test_text_prompt_candidate_smoke_flow.py` line 98: `assert prompt_candidate_artifact == {`
- `tests/prompt/test_text_prompt_candidate_smoke_flow.py` line 125: `assert set(candidate) == {`
- `tests/prompt/test_text_prompt_candidate_smoke_flow.py` line 137: `assert inspect_result == 0`
- `tests/repository_analyzer.py` line 6: `def test_should_analyze_repository():`
- `tests/test_asset_analyzer.py` line 10: `def test_should_return_medium_analysis_for_5mb_asset():`
- `tests/test_asset_analyzer.py` line 23: `assert analysis.size_class == SizeClass.MEDIUM`
- `tests/test_composition.py` line 8: `def test_create_repository_explorer_engine_wires_repository_explorer_discovery():`
- `tests/test_evidence_builder.py` line 10: `def test_should_build_evidence_from_asset():`
- `tests/test_evidence_builder.py` line 27: `assert evidence.asset_path == Path("photo.jpg")`
- `tests/test_evidence_builder.py` line 28: `assert evidence.filename == "photo.jpg"`
- `tests/test_evidence_builder.py` line 29: `assert evidence.metadata == asset.metadata`
- `tests/test_evidence_builder.py` line 30: `assert evidence.analysis.size_class == SizeClass.MEDIUM`
- `tests/test_evidence_collector.py` line 10: `def test_should_collect_evidences():`
- `tests/test_evidence_collector.py` line 47: `assert len(collection.evidences) == 3`
- `tests/test_evidence_collector.py` line 48: `assert collection.evidences[0].analysis.size_class == SizeClass.SMALL`
- `tests/test_evidence_collector.py` line 49: `assert collection.evidences[1].analysis.size_class == SizeClass.MEDIUM`
- `tests/test_evidence_collector.py` line 50: `assert collection.evidences[2].analysis.size_class == SizeClass.LARGE`
- `tests/test_export_official_knowledge_cli.py` line 37: `def test_export_official_knowledge_writes_valid_artifact(tmp_path, capsys):`
- `tests/test_export_official_knowledge_cli.py` line 68: `assert result == 0`
- `tests/test_export_official_knowledge_cli.py` line 74: `assert set(data) == {"official_knowledge_items"}`
- `tests/test_export_official_knowledge_cli.py` line 75: `assert data["official_knowledge_items"] == [`
- `tests/test_export_official_knowledge_cli.py` line 107: `def test_export_official_knowledge_preserves_order_and_indexes(`
- `tests/test_export_official_knowledge_cli.py` line 133: `assert result == 0`
- `tests/test_export_official_knowledge_cli.py` line 148: `def test_export_official_knowledge_missing_optional_fields_become_null(`
- `tests/test_export_official_knowledge_cli.py` line 178: `assert result == 0`
- `tests/test_export_official_knowledge_cli.py` line 188: `def test_export_official_knowledge_preserves_non_ascii_and_newline_content(`
- `tests/test_export_official_knowledge_cli.py` line 210: `assert result == 0`
- `tests/test_export_official_knowledge_cli.py` line 213: `assert record["content"] == content`
- `tests/test_export_official_knowledge_cli.py` line 216: `def test_export_official_knowledge_returns_error_for_missing_input(`
- `tests/test_export_official_knowledge_cli.py` line 230: `assert result == 1`
- `tests/test_export_official_knowledge_cli.py` line 235: `def test_export_official_knowledge_returns_error_for_invalid_json(`
- `tests/test_export_official_knowledge_cli.py` line 250: `assert result == 1`
- `tests/test_export_official_knowledge_cli.py` line 255: `def test_export_official_knowledge_returns_error_for_invalid_source_shape(`
- `tests/test_export_official_knowledge_cli.py` line 270: `assert result == 1`
- `tests/test_export_official_knowledge_cli.py` line 275: `def test_export_official_knowledge_returns_error_for_forbidden_field(`
- `tests/test_export_official_knowledge_cli.py` line 293: `assert result == 1`
- `tests/test_export_official_knowledge_cli.py` line 298: `def test_export_official_knowledge_returns_error_for_missing_output_parent(`
- `tests/test_export_official_knowledge_cli.py` line 313: `assert result == 1`
- `tests/test_inspect_evidence_eligibility_cli.py` line 61: `def test_valid_synthetic_registry_returns_zero(tmp_path, capsys):`
- `tests/test_inspect_evidence_eligibility_cli.py` line 68: `assert result == 0`
- `tests/test_inspect_evidence_eligibility_cli.py` line 71: `def test_output_includes_total_sources(tmp_path, capsys):`
- `tests/test_inspect_evidence_eligibility_cli.py` line 78: `assert result == 0`
- `tests/test_inspect_evidence_eligibility_cli.py` line 83: `def test_output_includes_allowed_count(tmp_path, capsys):`
- `tests/test_inspect_evidence_eligibility_cli.py` line 90: `assert result == 0`
- `tests/test_inspect_evidence_eligibility_cli.py` line 95: `def test_output_includes_requires_review_count(tmp_path, capsys):`
- `tests/test_inspect_evidence_eligibility_cli.py` line 102: `assert result == 0`
- `tests/test_inspect_evidence_eligibility_cli.py` line 106: `def test_output_includes_blocked_count(tmp_path, capsys):`
- `tests/test_inspect_evidence_eligibility_cli.py` line 113: `assert result == 0`
- `tests/test_inspect_evidence_eligibility_cli.py` line 117: `def test_output_includes_evidence_eligibility_counts(tmp_path, capsys):`
- `tests/test_inspect_evidence_eligibility_cli.py` line 124: `assert result == 0`
- `tests/test_inspect_evidence_eligibility_cli.py` line 132: `def test_output_does_not_include_source_path(tmp_path, capsys):`
- `tests/test_inspect_evidence_eligibility_cli.py` line 143: `assert result == 0`
- `tests/test_inspect_evidence_eligibility_cli.py` line 148: `def test_missing_argument_exits_non_zero_through_argparse():`
- `tests/test_inspect_evidence_eligibility_cli.py` line 149: `with pytest.raises(SystemExit) as exc_info:`
- `tests/test_inspect_evidence_eligibility_cli.py` line 155: `def test_missing_registry_file_returns_one(tmp_path, capsys):`
- `tests/test_inspect_evidence_eligibility_cli.py` line 161: `assert result == 1`
- `tests/test_inspect_evidence_eligibility_cli.py` line 165: `def test_invalid_json_returns_one(tmp_path, capsys):`
- `tests/test_inspect_evidence_eligibility_cli.py` line 172: `assert result == 1`
- `tests/test_inspect_evidence_eligibility_cli.py` line 176: `def test_invalid_registry_shape_returns_one(tmp_path, capsys):`
- `tests/test_inspect_evidence_eligibility_cli.py` line 183: `assert result == 1`
- `tests/test_inspect_evidence_eligibility_cli.py` line 187: `def test_nonexistent_source_path_inside_registry_still_succeeds(`
- `tests/test_inspect_evidence_eligibility_cli.py` line 202: `assert result == 0`
- `tests/test_inspect_evidence_eligibility_cli.py` line 206: `def test_tests_use_synthetic_registry_data_only(tmp_path):`
- `tests/test_inspect_official_knowledge_cli.py` line 38: `def test_inspect_official_knowledge_valid_artifact_returns_zero(`
- `tests/test_inspect_official_knowledge_cli.py` line 48: `assert result == 0`
- `tests/test_inspect_official_knowledge_cli.py` line 58: `def test_inspect_official_knowledge_empty_items_is_valid(`
- `tests/test_inspect_official_knowledge_cli.py` line 68: `assert result == 0`
- `tests/test_inspect_official_knowledge_cli.py` line 73: `def test_inspect_official_knowledge_missing_governance_is_counted_but_valid(`
- `tests/test_inspect_official_knowledge_cli.py` line 93: `assert result == 0`
- `tests/test_inspect_official_knowledge_cli.py` line 99: `def test_inspect_official_knowledge_missing_required_traceability_is_invalid(`
- `tests/test_inspect_official_knowledge_cli.py` line 112: `assert result == 1`
- `tests/test_inspect_official_knowledge_cli.py` line 117: `def test_inspect_official_knowledge_forbidden_field_is_invalid(`
- `tests/test_inspect_official_knowledge_cli.py` line 130: `assert result == 1`
- `tests/test_inspect_official_knowledge_cli.py` line 135: `def test_inspect_official_knowledge_index_mismatch_is_invalid(`
- `tests/test_inspect_official_knowledge_cli.py` line 148: `assert result == 1`
- `tests/test_inspect_official_knowledge_cli.py` line 153: `def test_inspect_official_knowledge_returns_error_for_missing_file(`
- `tests/test_inspect_official_knowledge_cli.py` line 162: `assert result == 1`
- `tests/test_inspect_official_knowledge_cli.py` line 166: `def test_inspect_official_knowledge_returns_error_for_invalid_json(`
- `tests/test_inspect_official_knowledge_cli.py` line 176: `assert result == 1`
- `tests/test_inspect_official_knowledge_cli.py` line 180: `def test_inspect_official_knowledge_returns_error_for_directory(`
- `tests/test_inspect_official_knowledge_cli.py` line 187: `assert result == 1`
- `tests/test_inspect_official_source_registry_cli.py` line 37: `def test_valid_synthetic_registry_returns_zero(tmp_path, capsys):`
- `tests/test_inspect_official_source_registry_cli.py` line 44: `assert result == 0`
- `tests/test_inspect_official_source_registry_cli.py` line 47: `def test_valid_synthetic_registry_prints_total_official_sources(`
- `tests/test_inspect_official_source_registry_cli.py` line 60: `assert result == 0`
- `tests/test_inspect_official_source_registry_cli.py` line 65: `def test_valid_synthetic_registry_prints_aggregate_enum_counts(`
- `tests/test_inspect_official_source_registry_cli.py` line 95: `assert result == 0`
- `tests/test_inspect_official_source_registry_cli.py` line 113: `def test_output_does_not_include_source_path(tmp_path, capsys):`
- `tests/test_inspect_official_source_registry_cli.py` line 121: `assert result == 0`
- `tests/test_inspect_official_source_registry_cli.py` line 126: `def test_missing_argument_exits_non_zero_through_argparse():`
- `tests/test_inspect_official_source_registry_cli.py` line 127: `with pytest.raises(SystemExit) as exc_info:`
- `tests/test_inspect_official_source_registry_cli.py` line 133: `def test_missing_registry_file_returns_one(tmp_path, capsys):`
- `tests/test_inspect_official_source_registry_cli.py` line 139: `assert result == 1`
- `tests/test_inspect_official_source_registry_cli.py` line 143: `def test_invalid_json_returns_one(tmp_path, capsys):`
- `tests/test_inspect_official_source_registry_cli.py` line 150: `assert result == 1`
- `tests/test_inspect_official_source_registry_cli.py` line 154: `def test_invalid_registry_shape_returns_one(tmp_path, capsys):`
- `tests/test_inspect_official_source_registry_cli.py` line 161: `assert result == 1`
- `tests/test_inspect_official_source_registry_cli.py` line 165: `def test_nonexistent_source_path_inside_registry_still_succeeds(`
- `tests/test_inspect_official_source_registry_cli.py` line 180: `assert result == 0`
- `tests/test_inspect_official_source_registry_cli.py` line 184: `def test_no_real_rsv_locked_content_is_used(tmp_path):`
- `tests/test_official_knowledge_artifact_inspector.py` line 55: `def test_inspects_valid_artifact():`
- `tests/test_official_knowledge_artifact_inspector.py` line 65: `assert inspection.total_official_knowledge_items == 2`
- `tests/test_official_knowledge_artifact_inspector.py` line 66: `assert inspection.missing_required_traceability_count == 0`
- `tests/test_official_knowledge_artifact_inspector.py` line 67: `assert inspection.missing_governance_count == 0`
- `tests/test_official_knowledge_artifact_inspector.py` line 68: `assert inspection.forbidden_field_count == 0`
- `tests/test_official_knowledge_artifact_inspector.py` line 69: `assert inspection.index_mismatch_count == 0`
- `tests/test_official_knowledge_artifact_inspector.py` line 73: `def test_empty_official_knowledge_items_list_is_valid():`
- `tests/test_official_knowledge_artifact_inspector.py` line 80: `assert inspection.total_official_knowledge_items == 0`
- `tests/test_official_knowledge_artifact_inspector.py` line 84: `def test_missing_official_knowledge_items_key_is_invalid():`
- `tests/test_official_knowledge_artifact_inspector.py` line 87: `assert inspection.total_official_knowledge_items == 0`
- `tests/test_official_knowledge_artifact_inspector.py` line 91: `def test_official_knowledge_items_not_list_is_invalid():`
- `tests/test_official_knowledge_artifact_inspector.py` line 98: `assert inspection.total_official_knowledge_items == 0`
- `tests/test_official_knowledge_artifact_inspector.py` line 102: `def test_missing_or_empty_required_traceability_fields_are_counted():`
- `tests/test_official_knowledge_artifact_inspector.py` line 121: `assert inspection.total_official_knowledge_items == 5`
- `tests/test_official_knowledge_artifact_inspector.py` line 122: `assert inspection.missing_required_traceability_count == 5`
- `tests/test_official_knowledge_artifact_inspector.py` line 123: `assert inspection.index_mismatch_count == 0`
- `tests/test_official_knowledge_artifact_inspector.py` line 127: `def test_missing_governance_is_counted_but_does_not_make_artifact_invalid():`
- `tests/test_official_knowledge_artifact_inspector.py` line 140: `assert inspection.total_official_knowledge_items == 2`
- `tests/test_official_knowledge_artifact_inspector.py` line 141: `assert inspection.missing_governance_count == 2`
- `tests/test_official_knowledge_artifact_inspector.py` line 142: `assert inspection.missing_required_traceability_count == 0`
- `tests/test_official_knowledge_artifact_inspector.py` line 143: `assert inspection.forbidden_field_count == 0`
- `tests/test_official_knowledge_artifact_inspector.py` line 144: `assert inspection.index_mismatch_count == 0`
- `tests/test_official_knowledge_artifact_inspector.py` line 148: `def test_forbidden_fields_are_counted_and_make_artifact_invalid():`
- `tests/test_official_knowledge_artifact_inspector.py` line 161: `assert inspection.forbidden_field_count == 3`
- `tests/test_official_knowledge_artifact_inspector.py` line 165: `def test_official_knowledge_index_mismatch_is_counted_and_invalid():`
- `tests/test_official_knowledge_artifact_inspector.py` line 176: `assert inspection.index_mismatch_count == 1`
- `tests/test_official_knowledge_artifact_inspector.py` line 180: `def test_non_dict_item_is_invalid_and_counted_as_missing_traceability():`
- `tests/test_official_knowledge_artifact_inspector.py` line 186: `assert inspection.total_official_knowledge_items == 2`
- `tests/test_official_knowledge_artifact_inspector.py` line 187: `assert inspection.missing_required_traceability_count == 1`
- `tests/test_official_knowledge_artifact_inspector.py` line 191: `def test_inspector_does_not_mutate_artifact():`
- `tests/test_official_knowledge_artifact_inspector.py` line 197: `assert artifact == original_artifact`
- `tests/test_official_knowledge_cli_smoke_flow.py` line 49: `def test_official_knowledge_cli_smoke_flow_exports_then_inspects(`
- `tests/test_official_knowledge_cli_smoke_flow.py` line 114: `assert export_result == 0`
- `tests/test_official_knowledge_cli_smoke_flow.py` line 120: `assert set(artifact) == {"official_knowledge_items"}`
- `tests/test_official_knowledge_cli_smoke_flow.py` line 121: `assert len(records) == 2`
- `tests/test_official_knowledge_cli_smoke_flow.py` line 134: `assert records[0]["knowledge_id"] == "EX-001"`
- `tests/test_official_knowledge_cli_smoke_flow.py` line 135: `assert records[0]["source_path"] == (`
- `tests/test_official_knowledge_cli_smoke_flow.py` line 138: `assert records[0]["source_document"] == (`
- `tests/test_official_knowledge_cli_smoke_flow.py` line 141: `assert records[0]["source_section"] == "Example Section"`
- `tests/test_official_knowledge_cli_smoke_flow.py` line 142: `assert records[0]["source_page"] == 1`
- `tests/test_official_knowledge_cli_smoke_flow.py` line 143: `assert records[0]["content"] == "Example official knowledge content."`
- `tests/test_official_knowledge_cli_smoke_flow.py` line 144: `assert records[0]["status"] == "LOCKED"`
- `tests/test_official_knowledge_cli_smoke_flow.py` line 145: `assert records[0]["governance_level"] == (`
- `tests/test_official_knowledge_cli_smoke_flow.py` line 161: `assert set(record) == OFFICIAL_KNOWLEDGE_FIELDS`
- `tests/test_official_knowledge_cli_smoke_flow.py` line 167: `assert inspect_result == 0`
- `tests/test_official_knowledge_collection_serializer.py` line 42: `def test_serializes_one_official_knowledge_item_to_expected_dict_shape():`
- `tests/test_official_knowledge_collection_serializer.py` line 47: `assert serialized == {`
- `tests/test_official_knowledge_collection_serializer.py` line 67: `def test_serializes_optional_none_fields_as_none():`
- `tests/test_official_knowledge_collection_serializer.py` line 97: `def test_serializes_multiple_items_preserving_order_and_indexes():`
- `tests/test_official_knowledge_collection_serializer.py` line 124: `def test_serializes_empty_collection():`
- `tests/test_official_knowledge_collection_serializer.py` line 129: `assert OfficialKnowledgeCollectionSerializer.to_dict(collection) == {`
- `tests/test_official_knowledge_collection_serializer.py` line 134: `def test_serializer_output_includes_no_forbidden_fields():`
- `tests/test_official_knowledge_collection_serializer.py` line 171: `def test_to_json_preserves_none_as_json_null_and_non_ascii_content():`
- `tests/test_official_knowledge_collection_serializer.py` line 187: `assert json.loads(serialized_json) == (`
- `tests/test_official_knowledge_collector.py` line 40: `def test_collects_one_source_item_into_one_official_knowledge_item():`
- `tests/test_official_knowledge_collector.py` line 46: `assert len(collection.official_knowledge_items) == 1`
- `tests/test_official_knowledge_collector.py` line 53: `def test_preserves_all_source_fields_exactly():`
- `tests/test_official_knowledge_collector.py` line 71: `assert item.knowledge_id == source_item.knowledge_id`
- `tests/test_official_knowledge_collector.py` line 72: `assert item.source_path == source_item.source_path`
- `tests/test_official_knowledge_collector.py` line 73: `assert item.source_document == source_item.source_document`
- `tests/test_official_knowledge_collector.py` line 74: `assert item.source_section == source_item.source_section`
- `tests/test_official_knowledge_collector.py` line 75: `assert item.source_page == source_item.source_page`
- `tests/test_official_knowledge_collector.py` line 76: `assert item.title == source_item.title`
- `tests/test_official_knowledge_collector.py` line 77: `assert item.content == source_item.content`
- `tests/test_official_knowledge_collector.py` line 78: `assert item.status == source_item.status`
- `tests/test_official_knowledge_collector.py` line 79: `assert item.governance_level == source_item.governance_level`
- `tests/test_official_knowledge_collector.py` line 80: `assert item.pdf_evidence_index == source_item.pdf_evidence_index`
- `tests/test_official_knowledge_collector.py` line 81: `assert item.extraction_index == source_item.extraction_index`
- `tests/test_official_knowledge_collector.py` line 84: `def test_official_knowledge_index_starts_at_zero():`
- `tests/test_official_knowledge_collector.py` line 87: `assert collection.official_knowledge_items[0].official_knowledge_index == 0`
- `tests/test_official_knowledge_collector.py` line 90: `def test_multiple_source_items_preserve_order_and_receive_indexes():`
- `tests/test_official_knowledge_collector.py` line 113: `def test_knowledge_id_remains_none_when_source_knowledge_id_is_none():`
- `tests/test_official_knowledge_collector.py` line 121: `def test_collector_does_not_skip_duplicate_content():`
- `tests/test_official_knowledge_collector.py` line 129: `assert len(collection.official_knowledge_items) == 2`
- `tests/test_official_knowledge_collector.py` line 130: `assert collection.official_knowledge_items[0].content == (`
- `tests/test_official_knowledge_collector.py` line 139: `def test_empty_source_list_returns_empty_collection():`
- `tests/test_official_knowledge_collector.py` line 143: `assert collection.official_knowledge_items == []`
- `tests/test_official_knowledge_collector.py` line 146: `def test_official_knowledge_item_and_collection_expose_no_forbidden_fields():`
- `tests/test_official_knowledge_collector.py` line 150: `assert [field.name for field in fields(item)] == [`
- `tests/test_official_knowledge_collector.py` line 164: `assert [field.name for field in fields(collection)] == [`
- `tests/test_official_knowledge_smoke_flow.py` line 15: `def test_official_knowledge_end_to_end_smoke_flow():`
- `tests/test_official_knowledge_smoke_flow.py` line 55: `assert source_items == original_source_items`
- `tests/test_official_knowledge_smoke_flow.py` line 77: `assert official_knowledge_items[0]["source_path"] == (`
- `tests/test_official_knowledge_smoke_flow.py` line 80: `assert official_knowledge_items[0]["source_document"] == (`
- `tests/test_official_knowledge_smoke_flow.py` line 83: `assert official_knowledge_items[0]["source_section"] == (`
- `tests/test_official_knowledge_smoke_flow.py` line 86: `assert official_knowledge_items[0]["source_page"] == 1`
- `tests/test_official_knowledge_smoke_flow.py` line 87: `assert official_knowledge_items[0]["content"] == (`
- `tests/test_official_knowledge_smoke_flow.py` line 91: `assert official_knowledge_items[0]["status"] == "LOCKED"`
- `tests/test_official_knowledge_smoke_flow.py` line 92: `assert official_knowledge_items[0]["governance_level"] == (`
- `tests/test_official_knowledge_smoke_flow.py` line 98: `assert inspection.total_official_knowledge_items == 2`
- `tests/test_official_knowledge_smoke_flow.py` line 99: `assert inspection.missing_required_traceability_count == 0`
- `tests/test_official_knowledge_smoke_flow.py` line 100: `assert inspection.missing_governance_count == 1`
- `tests/test_official_knowledge_smoke_flow.py` line 101: `assert inspection.forbidden_field_count == 0`
- `tests/test_official_knowledge_smoke_flow.py` line 102: `assert inspection.index_mismatch_count == 0`
- `tests/test_official_knowledge_source_input_loader.py` line 37: `def test_loads_one_valid_official_knowledge_source_item():`
- `tests/test_official_knowledge_source_input_loader.py` line 42: `assert len(items) == 1`
- `tests/test_official_knowledge_source_input_loader.py` line 44: `assert items[0].knowledge_id == "BK-001"`
- `tests/test_official_knowledge_source_input_loader.py` line 45: `assert items[0].source_path == (`
- `tests/test_official_knowledge_source_input_loader.py` line 48: `assert items[0].source_document == "Example Official Knowledge Base"`
- `tests/test_official_knowledge_source_input_loader.py` line 49: `assert items[0].source_section == "Example Section"`
- `tests/test_official_knowledge_source_input_loader.py` line 50: `assert items[0].source_page == 1`
- `tests/test_official_knowledge_source_input_loader.py` line 51: `assert items[0].title == "Example Locked Knowledge"`
- `tests/test_official_knowledge_source_input_loader.py` line 52: `assert items[0].content == "Example official knowledge content."`
- `tests/test_official_knowledge_source_input_loader.py` line 53: `assert items[0].status == "LOCKED"`
- `tests/test_official_knowledge_source_input_loader.py` line 54: `assert items[0].governance_level == "OFFICIAL SOURCE OF TRUTH"`
- `tests/test_official_knowledge_source_input_loader.py` line 55: `assert items[0].pdf_evidence_index == 0`
- `tests/test_official_knowledge_source_input_loader.py` line 56: `assert items[0].extraction_index == 0`
- `tests/test_official_knowledge_source_input_loader.py` line 59: `def test_multiple_valid_items_preserve_order():`
- `tests/test_official_knowledge_source_input_loader.py` line 86: `def test_empty_official_knowledge_source_items_list_returns_empty_list():`
- `tests/test_official_knowledge_source_input_loader.py` line 92: `def test_omitted_optional_fields_become_none():`
- `tests/test_official_knowledge_source_input_loader.py` line 118: `def test_provided_none_optional_fields_remain_none():`
- `tests/test_official_knowledge_source_input_loader.py` line 142: `def test_missing_required_fields_fail_clearly():`
- `tests/test_official_knowledge_source_input_loader.py` line 152: `with pytest.raises(ValueError, match=field_name):`
- `tests/test_official_knowledge_source_input_loader.py` line 158: `def test_empty_required_string_fields_fail_clearly():`
- `tests/test_official_knowledge_source_input_loader.py` line 167: `with pytest.raises(ValueError, match=field_name):`
- `tests/test_official_knowledge_source_input_loader.py` line 173: `def test_top_level_input_that_is_not_a_dict_fails():`
- `tests/test_official_knowledge_source_input_loader.py` line 174: `with pytest.raises(ValueError, match="object"):`
- `tests/test_official_knowledge_source_input_loader.py` line 178: `def test_missing_official_knowledge_source_items_key_fails():`
- `tests/test_official_knowledge_source_input_loader.py` line 179: `with pytest.raises(ValueError, match="official_knowledge_source_items"):`
- `tests/test_official_knowledge_source_input_loader.py` line 183: `def test_unknown_top_level_key_fails():`
- `tests/test_official_knowledge_source_input_loader.py` line 184: `with pytest.raises(ValueError, match="official_knowledge_source_items"):`
- `tests/test_official_knowledge_source_input_loader.py` line 193: `def test_official_knowledge_source_items_that_is_not_a_list_fails():`
- `tests/test_official_knowledge_source_input_loader.py` line 194: `with pytest.raises(ValueError, match="list"):`
- `tests/test_official_knowledge_source_input_loader.py` line 202: `def test_non_dict_item_fails():`
- `tests/test_official_knowledge_source_input_loader.py` line 203: `with pytest.raises(ValueError, match="object"):`
- `tests/test_official_knowledge_source_input_loader.py` line 209: `def test_unknown_item_field_fails():`
- `tests/test_official_knowledge_source_input_loader.py` line 210: `with pytest.raises(ValueError, match="unknown field"):`
- `tests/test_official_knowledge_source_input_loader.py` line 216: `def test_forbidden_item_field_fails():`
- `tests/test_official_knowledge_source_input_loader.py` line 217: `with pytest.raises(ValueError, match="forbidden field"):`
- `tests/test_official_knowledge_source_input_loader.py` line 223: `def test_bool_values_for_integer_fields_fail():`
- `tests/test_official_knowledge_source_input_loader.py` line 229: `with pytest.raises(ValueError, match=field_name):`
- `tests/test_official_knowledge_source_input_loader.py` line 235: `def test_non_int_non_none_values_for_integer_fields_fail():`
- `tests/test_official_knowledge_source_input_loader.py` line 241: `with pytest.raises(ValueError, match=field_name):`
- `tests/test_official_knowledge_source_input_loader.py` line 247: `def test_non_ascii_and_newline_content_are_preserved():`
- `tests/test_official_knowledge_source_input_loader.py` line 254: `assert items[0].content == content`
- `tests/test_official_knowledge_source_input_loader.py` line 257: `def test_loader_does_not_mutate_input():`
- `tests/test_official_knowledge_source_input_loader.py` line 263: `assert source_input == original_source_input`
- `tests/test_official_knowledge_source_item.py` line 10: `def test_creates_valid_curated_official_knowledge_source_item():`
- `tests/test_official_knowledge_source_item.py` line 25: `assert item.knowledge_id == "BK-001"`
- `tests/test_official_knowledge_source_item.py` line 26: `assert item.source_path == "official/example.pdf"`
- `tests/test_official_knowledge_source_item.py` line 27: `assert item.source_document == "Example Official Knowledge Base"`
- `tests/test_official_knowledge_source_item.py` line 28: `assert item.source_section == "Example Section"`
- `tests/test_official_knowledge_source_item.py` line 29: `assert item.source_page == 1`
- `tests/test_official_knowledge_source_item.py` line 30: `assert item.title == "Example Locked Knowledge"`
- `tests/test_official_knowledge_source_item.py` line 31: `assert item.content == "Example official knowledge content."`
- `tests/test_official_knowledge_source_item.py` line 32: `assert item.status == "LOCKED"`
- `tests/test_official_knowledge_source_item.py` line 33: `assert item.governance_level == "OFFICIAL SOURCE OF TRUTH"`
- `tests/test_official_knowledge_source_item.py` line 34: `assert item.pdf_evidence_index == 0`
- `tests/test_official_knowledge_source_item.py` line 35: `assert item.extraction_index == 0`
- `tests/test_official_knowledge_source_item.py` line 38: `def test_knowledge_id_can_be_none():`
- `tests/test_official_knowledge_source_item.py` line 56: `def test_optional_traceability_fields_can_be_none():`
- `tests/test_official_knowledge_source_item.py` line 79: `def test_required_string_fields_cannot_be_empty():`
- `tests/test_official_knowledge_source_item.py` line 103: `with pytest.raises(ValueError, match=field_name):`
- `tests/test_official_knowledge_source_item.py` line 107: `def test_official_knowledge_source_item_exposes_no_forbidden_fields():`
- `tests/test_official_knowledge_source_item.py` line 122: `assert [field.name for field in fields(item)] == [`
- `tests/test_official_source.py` line 42: `def test_creates_valid_official_source():`
- `tests/test_official_source.py` line 45: `assert source.source_id == "SRC-001"`
- `tests/test_official_source.py` line 46: `assert source.source_path == "docs/example_official_source.pdf"`
- `tests/test_official_source.py` line 47: `assert source.source_type == SourceType.PDF`
- `tests/test_official_source.py` line 48: `assert source.document_classification == (`
- `tests/test_official_source.py` line 51: `assert source.authority_status == AuthorityStatus.OFFICIAL`
- `tests/test_official_source.py` line 52: `assert source.lifecycle_status == LifecycleStatus.LOCKED`
- `tests/test_official_source.py` line 53: `assert source.evidence_eligibility == (`
- `tests/test_official_source.py` line 56: `assert source.version == "v1.0"`
- `tests/test_official_source.py` line 57: `assert source.review_notes == "Reviewed as generic test data."`
- `tests/test_official_source.py` line 60: `def test_official_source_enums_expose_expected_values():`
- `tests/test_official_source.py` line 61: `assert SourceType.PDF.value == "pdf"`
- `tests/test_official_source.py` line 62: `assert SourceType.UNKNOWN.value == "unknown"`
- `tests/test_official_source.py` line 63: `assert DocumentClassification.PROJECT_RULEBOOK.value == (`
- `tests/test_official_source.py` line 66: `assert AuthorityStatus.SOURCE_OF_TRUTH_CANDIDATE.value == (`
- `tests/test_official_source.py` line 69: `assert LifecycleStatus.SUPERSEDED.value == "superseded"`
- `tests/test_official_source.py` line 70: `assert EvidenceEligibility.NOT_ELIGIBLE.value == "not_eligible"`
- `tests/test_official_source.py` line 73: `def test_source_id_and_source_path_must_be_non_empty_strings():`
- `tests/test_official_source.py` line 78: `with pytest.raises(ValueError, match=field_name):`
- `tests/test_official_source.py` line 82: `def test_source_path_does_not_need_to_exist():`
- `tests/test_official_source.py` line 87: `assert source.source_path == "docs/not-a-real-locked-source.pdf"`
- `tests/test_official_source.py` line 90: `def test_status_and_classification_fields_must_be_enum_instances():`
- `tests/test_official_source.py` line 100: `with pytest.raises(ValueError, match=field_name):`
- `tests/test_official_source.py` line 104: `def test_optional_metadata_can_be_none():`
- `tests/test_official_source.py` line 114: `def test_optional_metadata_must_be_strings_when_provided():`
- `tests/test_official_source.py` line 119: `with pytest.raises(ValueError, match=field_name):`
- `tests/test_official_source.py` line 123: `def test_official_source_exposes_no_downstream_workflow_fields():`
- `tests/test_official_source.py` line 126: `assert [field.name for field in fields(source)] == [`
- `tests/test_official_source_evidence_eligibility_gate.py` line 45: `def test_allowed_decision_passes():`
- `tests/test_official_source_evidence_eligibility_gate.py` line 53: `def test_requires_review_decision_blocks():`
- `tests/test_official_source_evidence_eligibility_gate.py` line 62: `def test_not_allowed_decision_blocks():`
- `tests/test_official_source_evidence_eligibility_gate.py` line 70: `def test_blocked_non_review_decision_preserves_non_review_blocked_shape():`
- `tests/test_official_source_evidence_eligibility_gate.py` line 79: `def test_gate_result_preserves_source_id():`
- `tests/test_official_source_evidence_eligibility_gate.py` line 84: `assert result.source_id == "SRC-SYN-GATE-999"`
- `tests/test_official_source_evidence_eligibility_gate.py` line 87: `def test_gate_result_preserves_requires_review():`
- `tests/test_official_source_evidence_eligibility_gate.py` line 95: `def test_gate_result_has_non_empty_reason():`
- `tests/test_official_source_evidence_eligibility_gate.py` line 100: `assert result.reason == "Synthetic gate reason."`
- `tests/test_official_source_evidence_eligibility_gate.py` line 103: `def test_gate_accepts_decision_not_official_source():`
- `tests/test_official_source_evidence_eligibility_gate.py` line 104: `with pytest.raises(TypeError, match="EvidenceEligibilityDecision"):`
- `tests/test_official_source_evidence_eligibility_gate.py` line 108: `def test_gate_result_exposes_no_source_path_field():`
- `tests/test_official_source_evidence_eligibility_gate.py` line 114: `def test_gate_result_exposes_no_downstream_workflow_fields():`
- `tests/test_official_source_evidence_eligibility_gate.py` line 136: `def test_tests_use_synthetic_data_only():`
- `tests/test_official_source_evidence_eligibility_policy.py` line 32: `def test_eligible_returns_allowed_without_review():`
- `tests/test_official_source_evidence_eligibility_policy.py` line 42: `def test_eligible_with_review_returns_blocked_with_review_required():`
- `tests/test_official_source_evidence_eligibility_policy.py` line 54: `def test_not_eligible_returns_blocked_without_review_required():`
- `tests/test_official_source_evidence_eligibility_policy.py` line 64: `def test_unknown_returns_blocked_without_review_required():`
- `tests/test_official_source_evidence_eligibility_policy.py` line 74: `def test_decision_preserves_source_id():`
- `tests/test_official_source_evidence_eligibility_policy.py` line 77: `assert decision.source_id == "SRC-SYN-999"`
- `tests/test_official_source_evidence_eligibility_policy.py` line 80: `def test_decision_preserves_evidence_eligibility():`
- `tests/test_official_source_evidence_eligibility_policy.py` line 85: `assert decision.evidence_eligibility == (`
- `tests/test_official_source_evidence_eligibility_policy.py` line 90: `def test_lifecycle_status_does_not_change_decision():`
- `tests/test_official_source_evidence_eligibility_policy.py` line 98: `assert active.allowed == superseded.allowed`
- `tests/test_official_source_evidence_eligibility_policy.py` line 99: `assert active.requires_review == superseded.requires_review`
- `tests/test_official_source_evidence_eligibility_policy.py` line 102: `def test_authority_status_does_not_change_decision():`
- `tests/test_official_source_evidence_eligibility_policy.py` line 110: `assert official.allowed == draft.allowed`
- `tests/test_official_source_evidence_eligibility_policy.py` line 111: `assert official.requires_review == draft.requires_review`
- `tests/test_official_source_evidence_eligibility_policy.py` line 114: `def test_source_type_does_not_change_decision():`
- `tests/test_official_source_evidence_eligibility_policy.py` line 122: `assert pdf.allowed == markdown.allowed`
- `tests/test_official_source_evidence_eligibility_policy.py` line 123: `assert pdf.requires_review == markdown.requires_review`
- `tests/test_official_source_evidence_eligibility_policy.py` line 126: `def test_nonexistent_source_path_is_not_checked(tmp_path):`
- `tests/test_official_source_evidence_eligibility_policy.py` line 136: `def test_tests_use_synthetic_official_source_only():`
- `tests/test_official_source_evidence_workflow_gate.py` line 44: `def test_allowed_gate_result_allows_workflow():`
- `tests/test_official_source_evidence_workflow_gate.py` line 52: `def test_requires_review_gate_result_blocks_workflow():`
- `tests/test_official_source_evidence_workflow_gate.py` line 61: `def test_blocked_gate_result_blocks_workflow():`
- `tests/test_official_source_evidence_workflow_gate.py` line 69: `def test_preserves_source_id():`
- `tests/test_official_source_evidence_workflow_gate.py` line 74: `assert result.source_id == "SRC-SYN-WORKFLOW-999"`
- `tests/test_official_source_evidence_workflow_gate.py` line 77: `def test_preserves_requires_review():`
- `tests/test_official_source_evidence_workflow_gate.py` line 85: `def test_preserves_reason():`
- `tests/test_official_source_evidence_workflow_gate.py` line 90: `assert result.reason == "Synthetic workflow gate reason."`
- `tests/test_official_source_evidence_workflow_gate.py` line 93: `def test_rejects_official_source_input():`
- `tests/test_official_source_evidence_workflow_gate.py` line 94: `with pytest.raises(TypeError, match="EvidenceEligibilityGateResult"):`
- `tests/test_official_source_evidence_workflow_gate.py` line 98: `def test_rejects_raw_source_path_string_input():`
- `tests/test_official_source_evidence_workflow_gate.py` line 99: `with pytest.raises(TypeError, match="EvidenceEligibilityGateResult"):`
- `tests/test_official_source_evidence_workflow_gate.py` line 103: `def test_result_exposes_no_downstream_or_asset_fields():`
- `tests/test_official_source_evidence_workflow_gate.py` line 128: `def test_tests_use_synthetic_data_only():`
- `tests/test_official_source_evidence_workflow_gate.py` line 138: `def test_no_filesystem_reads_are_required(monkeypatch):`
- `tests/test_official_source_evidence_workflow_preflight.py` line 20: `def test_allowed_workflow_gate_result_allows_preflight() -> None:`
- `tests/test_official_source_evidence_workflow_preflight.py` line 30: `assert result == EvidenceWorkflowPreflightResult(`
- `tests/test_official_source_evidence_workflow_preflight.py` line 38: `def test_requires_review_blocks_preflight() -> None:`
- `tests/test_official_source_evidence_workflow_preflight.py` line 50: `assert result.reason == "Evidence workflow requires review."`
- `tests/test_official_source_evidence_workflow_preflight.py` line 53: `def test_blocked_workflow_gate_result_blocks_preflight() -> None:`
- `tests/test_official_source_evidence_workflow_preflight.py` line 65: `assert result.reason == "Evidence workflow is blocked."`
- `tests/test_official_source_evidence_workflow_preflight.py` line 68: `def test_preserves_source_id() -> None:`
- `tests/test_official_source_evidence_workflow_preflight.py` line 78: `assert result.source_id == "source-xyz"`
- `tests/test_official_source_evidence_workflow_preflight.py` line 81: `def test_preserves_requires_review() -> None:`
- `tests/test_official_source_evidence_workflow_preflight.py` line 94: `def test_preserves_reason() -> None:`
- `tests/test_official_source_evidence_workflow_preflight.py` line 104: `assert result.reason == "custom reason"`
- `tests/test_official_source_evidence_workflow_preflight.py` line 107: `def test_rejects_official_source_input() -> None:`
- `tests/test_official_source_evidence_workflow_preflight.py` line 120: `with pytest.raises(TypeError):`
- `tests/test_official_source_evidence_workflow_preflight.py` line 124: `def test_rejects_raw_source_path_string_input() -> None:`
- `tests/test_official_source_evidence_workflow_preflight.py` line 125: `with pytest.raises(TypeError):`
- `tests/test_official_source_evidence_workflow_preflight.py` line 129: `def test_rejects_extraction_report_like_input() -> None:`
- `tests/test_official_source_evidence_workflow_preflight.py` line 130: `with pytest.raises(TypeError):`
- `tests/test_official_source_evidence_workflow_preflight.py` line 134: `def test_result_exposes_no_forbidden_fields() -> None:`
- `tests/test_official_source_evidence_workflow_preflight.py` line 161: `def test_preflight_requires_no_filesystem_reads(monkeypatch: pytest.MonkeyPatch) -> None:`
- `tests/test_official_source_registry_loader.py` line 46: `def test_valid_mapping_returns_ordered_official_source_objects():`
- `tests/test_official_source_registry_loader.py` line 54: `assert len(sources) == 2`
- `tests/test_official_source_registry_loader.py` line 56: `assert [source.source_id for source in sources] == [`
- `tests/test_official_source_registry_loader.py` line 60: `assert sources[0].source_path == "docs/source-001.pdf"`
- `tests/test_official_source_registry_loader.py` line 61: `assert sources[0].source_type == SourceType.PDF`
- `tests/test_official_source_registry_loader.py` line 62: `assert sources[0].document_classification == (`
- `tests/test_official_source_registry_loader.py` line 65: `assert sources[0].authority_status == (`
- `tests/test_official_source_registry_loader.py` line 68: `assert sources[0].lifecycle_status == LifecycleStatus.LOCKED`
- `tests/test_official_source_registry_loader.py` line 69: `assert sources[0].evidence_eligibility == (`
- `tests/test_official_source_registry_loader.py` line 72: `assert sources[0].version == "v1.0"`
- `tests/test_official_source_registry_loader.py` line 73: `assert sources[0].review_notes == "Synthetic example only."`
- `tests/test_official_source_registry_loader.py` line 76: `def test_empty_official_sources_returns_empty_list():`
- `tests/test_official_source_registry_loader.py` line 82: `def test_non_mapping_top_level_input_fails():`
- `tests/test_official_source_registry_loader.py` line 83: `with pytest.raises(TypeError, match="mapping"):`
- `tests/test_official_source_registry_loader.py` line 87: `def test_missing_top_level_official_sources_fails():`
- `tests/test_official_source_registry_loader.py` line 88: `with pytest.raises(ValueError, match="official_sources"):`
- `tests/test_official_source_registry_loader.py` line 92: `def test_unknown_top_level_key_fails():`
- `tests/test_official_source_registry_loader.py` line 93: `with pytest.raises(ValueError, match="official_sources"):`
- `tests/test_official_source_registry_loader.py` line 102: `def test_official_sources_that_is_not_list_fails():`
- `tests/test_official_source_registry_loader.py` line 103: `with pytest.raises(TypeError, match="list"):`
- `tests/test_official_source_registry_loader.py` line 111: `def test_non_mapping_item_fails():`
- `tests/test_official_source_registry_loader.py` line 112: `with pytest.raises(TypeError, match="object"):`
- `tests/test_official_source_registry_loader.py` line 118: `def test_missing_required_fields_fail():`
- `tests/test_official_source_registry_loader.py` line 131: `with pytest.raises(ValueError, match=field_name):`
- `tests/test_official_source_registry_loader.py` line 137: `def test_blank_source_id_fails():`
- `tests/test_official_source_registry_loader.py` line 138: `with pytest.raises(ValueError, match="source_id"):`
- `tests/test_official_source_registry_loader.py` line 144: `def test_blank_source_path_fails():`
- `tests/test_official_source_registry_loader.py` line 145: `with pytest.raises(ValueError, match="source_path"):`
- `tests/test_official_source_registry_loader.py` line 151: `def test_duplicate_source_id_fails():`
- `tests/test_official_source_registry_loader.py` line 152: `with pytest.raises(ValueError, match="duplicate source_id"):`
- `tests/test_official_source_registry_loader.py` line 161: `def test_invalid_enum_string_fails():`
- `tests/test_official_source_registry_loader.py` line 171: `with pytest.raises(ValueError, match=field_name):`
- `tests/test_official_source_registry_loader.py` line 177: `def test_explicit_unknown_enum_values_pass():`
- `tests/test_official_source_registry_loader.py` line 190: `assert sources[0].source_type == SourceType.UNKNOWN`
- `tests/test_official_source_registry_loader.py` line 191: `assert sources[0].document_classification == (`
- `tests/test_official_source_registry_loader.py` line 194: `assert sources[0].authority_status == AuthorityStatus.UNKNOWN`
- `tests/test_official_source_registry_loader.py` line 195: `assert sources[0].lifecycle_status == LifecycleStatus.UNKNOWN`
- `tests/test_official_source_registry_loader.py` line 196: `assert sources[0].evidence_eligibility == EvidenceEligibility.UNKNOWN`
- `tests/test_official_source_registry_loader.py` line 199: `def test_unknown_item_field_fails():`
- `tests/test_official_source_registry_loader.py` line 200: `with pytest.raises(ValueError, match="unknown field"):`
- `tests/test_official_source_registry_loader.py` line 206: `def test_source_local_id_fails_until_supported():`
- `tests/test_official_source_registry_loader.py` line 207: `with pytest.raises(ValueError, match="source_local_id"):`
- `tests/test_official_source_registry_loader.py` line 213: `def test_forbidden_downstream_fields_fail():`
- `tests/test_official_source_registry_loader.py` line 230: `with pytest.raises(ValueError, match="forbidden field"):`
- `tests/test_official_source_registry_loader.py` line 236: `def test_nonexistent_source_path_passes_as_string_reference():`
- `tests/test_official_source_registry_loader.py` line 243: `assert sources[0].source_path == "docs/not-a-real-synthetic-source.pdf"`
- `tests/test_official_source_registry_loader.py` line 246: `def test_deprecated_and_superseded_lifecycle_entries_remain_returned():`
- `tests/test_official_source_registry_loader.py` line 254: `assert [source.lifecycle_status for source in sources] == [`
- `tests/test_official_source_registry_loader.py` line 260: `def test_input_order_is_preserved():`
- `tests/test_official_source_registry_loader.py` line 269: `assert [source.source_id for source in sources] == [`
- `tests/test_official_source_registry_loader.py` line 276: `def test_input_is_not_mutated():`
- `tests/test_official_source_registry_loader.py` line 282: `assert registry == original_registry`
- `tests/test_official_source_registry_loader.py` line 285: `def test_valid_synthetic_json_file_loads_official_source_objects(tmp_path):`
- `tests/test_official_source_registry_loader.py` line 303: `assert [source.source_id for source in sources] == [`
- `tests/test_official_source_registry_loader.py` line 307: `assert sources[0].source_type == SourceType.PDF`
- `tests/test_official_source_registry_loader.py` line 308: `assert sources[0].document_classification == (`
- `tests/test_official_source_registry_loader.py` line 313: `def test_json_file_path_may_be_provided_as_string(tmp_path):`
- `tests/test_official_source_registry_loader.py` line 321: `assert sources[0].source_id == "SRC-001"`
- `tests/test_official_source_registry_loader.py` line 324: `def test_missing_registry_json_file_raises_file_not_found_error(tmp_path):`
- `tests/test_official_source_registry_loader.py` line 327: `with pytest.raises(FileNotFoundError):`
- `tests/test_official_source_registry_loader.py` line 331: `def test_invalid_registry_json_file_raises_value_error(tmp_path):`
- `tests/test_official_source_registry_loader.py` line 335: `with pytest.raises(ValueError, match="Official Source registry JSON"):`
- `tests/test_official_source_registry_loader.py` line 339: `def test_top_level_list_json_fails_through_mapping_validation(tmp_path):`
- `tests/test_official_source_registry_loader.py` line 343: `with pytest.raises(TypeError, match="mapping"):`
- `tests/test_official_source_registry_loader.py` line 347: `def test_json_file_loader_does_not_check_source_path_existence(tmp_path):`
- `tests/test_official_source_registry_loader.py` line 358: `assert sources[0].source_path == "docs/not-a-real-synthetic-source.pdf"`
- `tests/test_official_source_registry_loader.py` line 361: `def test_json_file_loader_has_no_default_config_path():`
- `tests/test_official_source_registry_loader.py` line 362: `with pytest.raises(TypeError):`
- `tests/test_official_source_registry_loader.py` line 366: `def test_test_data_is_synthetic():`
- `tests/test_official_source_registry_loader.py` line 370: `assert item["review_notes"] == "Synthetic example only."`
- `tests/test_pdf_text_extraction_evidence.py` line 28: `def test_pdf_text_extraction_evidence_stores_exact_copied_values():`
- `tests/test_pdf_text_extraction_evidence.py` line 40: `assert evidence.source_path == "spec.pdf"`
- `tests/test_pdf_text_extraction_evidence.py` line 41: `assert evidence.content == "Raw page text"`
- `tests/test_pdf_text_extraction_evidence.py` line 42: `assert evidence.size_bytes == 123`
- `tests/test_pdf_text_extraction_evidence.py` line 43: `assert evidence.page_number == 2`
- `tests/test_pdf_text_extraction_evidence.py` line 44: `assert evidence.extraction_index == 4`
- `tests/test_pdf_text_extraction_evidence.py` line 45: `assert evidence.extraction_method == "embedded_text"`
- `tests/test_pdf_text_extraction_evidence.py` line 46: `assert evidence.warnings == ["No embedded text found."]`
- `tests/test_pdf_text_extraction_evidence.py` line 47: `assert evidence.evidence_index == 0`
- `tests/test_pdf_text_extraction_evidence.py` line 50: `def test_pdf_text_extraction_evidence_exposes_only_boundary_fields():`
- `tests/test_pdf_text_extraction_evidence.py` line 62: `assert [field.name for field in fields(evidence)] == [`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 35: `def test_counts_total_pdf_text_evidences():`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 45: `assert inspection.total_pdf_text_evidences == 2`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 48: `def test_counts_total_content_characters():`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 59: `assert inspection.total_content_characters == len("FirstSecond")`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 62: `def test_counts_empty_content_evidence():`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 72: `assert inspection.empty_content_evidence_count == 1`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 75: `def test_counts_warning_count():`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 90: `assert inspection.warning_count == 2`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 93: `def test_counts_invalid_records():`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 103: `assert inspection.invalid_record_count == 2`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 106: `def test_counts_forbidden_fields():`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 116: `assert inspection.forbidden_field_count == 2`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 117: `assert inspection.invalid_record_count == 2`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 120: `def test_accepts_exact_valid_top_level_fields_only():`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 123: `assert inspection.invalid_record_count == 0`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 124: `assert inspection.forbidden_field_count == 0`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 127: `def test_rejects_extra_top_level_key():`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 128: `with pytest.raises(ValueError, match="exactly"):`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 132: `def test_rejects_missing_pdf_text_evidences_key():`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 133: `with pytest.raises(ValueError, match="exactly"):`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 146: `def test_rejects_bool_integer_fields(field):`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 155: `assert inspection.invalid_record_count == 1`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 158: `def test_rejects_missing_required_evidence_fields():`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 166: `assert inspection.invalid_record_count == 1`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 169: `def test_rejects_extra_non_forbidden_evidence_fields_as_invalid():`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 178: `assert inspection.invalid_record_count == 1`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 179: `assert inspection.forbidden_field_count == 0`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 182: `def test_rejects_invalid_warnings_list():`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 191: `assert inspection.invalid_record_count == 1`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 192: `assert inspection.warning_count == 0`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 195: `def test_rejects_warnings_list_with_non_string_item():`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 204: `assert inspection.invalid_record_count == 1`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 205: `assert inspection.warning_count == 2`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 208: `def test_counts_forbidden_fields_separately():`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 218: `assert inspection.forbidden_field_count == 2`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 219: `assert inspection.invalid_record_count == 2`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 222: `def test_preserves_inspection_only_behavior_no_mutation():`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 235: `assert artifact == original`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 238: `def test_rejects_pdf_text_evidences_not_list():`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 239: `with pytest.raises(ValueError, match="pdf_text_evidences"):`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 243: `def test_rejects_non_dict_top_level_artifact():`
- `tests/test_pdf_text_extraction_evidence_artifact_inspector.py` line 244: `with pytest.raises(ValueError, match="object"):`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 22: `def test_builder_preserves_pdf_page_extraction_values():`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 36: `assert evidence.source_path == "helmet-spec.pdf"`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 37: `assert evidence.size_bytes == 4096`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 38: `assert evidence.page_number == 3`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 39: `assert evidence.extraction_index == 7`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 40: `assert evidence.extraction_method == "embedded_text"`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 41: `assert evidence.content == "Shell construction"`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 42: `assert evidence.warnings == ["No embedded text found."]`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 43: `assert evidence.evidence_index == 2`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 46: `def test_builder_preserves_content_exactly():`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 54: `assert evidence.content == content`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 57: `def test_builder_preserves_non_ascii_content():`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 65: `assert evidence.content == content`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 68: `def test_builder_preserves_newline_content():`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 76: `assert evidence.content == content`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 79: `def test_builder_preserves_empty_content():`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 85: `assert evidence.content == ""`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 88: `def test_builder_preserves_warnings():`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 99: `assert evidence.warnings == warnings`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 102: `def test_builder_rejects_missing_required_fields():`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 106: `with pytest.raises(ValueError, match="exactly"):`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 110: `def test_builder_rejects_extra_fields():`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 111: `with pytest.raises(ValueError, match="exactly"):`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 126: `def test_builder_rejects_wrong_field_types(field, value):`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 127: `with pytest.raises(ValueError):`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 142: `def test_builder_rejects_bool_integer_fields(field):`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 143: `with pytest.raises(ValueError, match="integer"):`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 150: `def test_builder_rejects_bool_evidence_index():`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 151: `with pytest.raises(ValueError, match="Evidence index"):`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 158: `def test_builder_rejects_invalid_warnings_list():`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 159: `with pytest.raises(ValueError, match="warnings"):`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 166: `def test_builder_rejects_warnings_list_with_non_string_item():`
- `tests/test_pdf_text_extraction_evidence_builder.py` line 167: `with pytest.raises(ValueError, match="warnings"):`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 49: `def test_serializer_produces_top_level_pdf_text_evidences_key():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 54: `assert set(data) == {"pdf_text_evidences"}`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 57: `def test_serializer_serializes_empty_collection():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 62: `assert data == {"pdf_text_evidences": []}`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 65: `def test_serializer_serializes_one_evidence_correctly():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 83: `assert data == {`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 99: `def test_serializer_serializes_multiple_evidences_in_order():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 118: `def test_serializer_preserves_exact_content():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 129: `assert data["pdf_text_evidences"][0]["content"] == content`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 132: `def test_serializer_preserves_non_ascii_content():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 145: `assert json.loads(json_output)["pdf_text_evidences"][0]["content"] == (`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 150: `def test_serializer_preserves_newline_content():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 161: `assert data["pdf_text_evidences"][0]["content"] == content`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 164: `def test_serializer_preserves_empty_content():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 173: `assert data["pdf_text_evidences"][0]["content"] == ""`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 176: `def test_serializer_preserves_warnings():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 190: `assert data["pdf_text_evidences"][0]["warnings"] == warnings`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 193: `def test_serializer_preserves_source_path():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 202: `assert data["pdf_text_evidences"][0]["source_path"] == "manual.pdf"`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 205: `def test_serializer_preserves_size_bytes():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 214: `assert data["pdf_text_evidences"][0]["size_bytes"] == 2048`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 217: `def test_serializer_preserves_page_number():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 226: `assert data["pdf_text_evidences"][0]["page_number"] == 4`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 229: `def test_serializer_preserves_extraction_index():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 238: `assert data["pdf_text_evidences"][0]["extraction_index"] == 8`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 241: `def test_serializer_preserves_extraction_method():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 250: `assert data["pdf_text_evidences"][0]["extraction_method"] == (`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 255: `def test_serializer_preserves_evidence_index():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 264: `assert data["pdf_text_evidences"][0]["evidence_index"] == 5`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 267: `def test_serializer_does_not_include_forbidden_fields():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 286: `def test_to_json_output_is_deterministic():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 301: `assert first_output == second_output`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 304: `def test_to_json_output_can_be_parsed_back_with_json_loads():`
- `tests/test_pdf_text_extraction_evidence_collection_serializer.py` line 315: `assert json.loads(json_output) == (`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 60: `def test_collector_consumes_page_extractions_from_pdf_text_artifact():`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 69: `assert len(collection.evidences) == 2`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 70: `assert collection.evidences[0].source_path == "first.pdf"`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 71: `assert collection.evidences[0].content == "First"`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 72: `assert collection.evidences[1].source_path == "second.pdf"`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 73: `assert collection.evidences[1].content == "Second"`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 76: `def test_collector_skips_invalid_page_extraction_records():`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 85: `assert len(collection.evidences) == 1`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 86: `assert collection.evidences[0].source_path == "valid.pdf"`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 89: `def test_collector_preserves_evidence_index_positions_for_valid_output_order():`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 104: `def test_collector_does_not_confuse_page_number_with_evidence_index():`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 111: `assert collection.evidences[0].page_number == 8`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 112: `assert collection.evidences[0].evidence_index == 0`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 115: `def test_collector_does_not_confuse_extraction_index_with_evidence_index():`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 122: `assert collection.evidences[0].extraction_index == 12`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 123: `assert collection.evidences[0].evidence_index == 0`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 134: `def test_collector_rejects_bool_for_integer_fields(field):`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 141: `assert collection.evidences == []`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 144: `def test_collector_rejects_invalid_warnings_list():`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 151: `assert collection.evidences == []`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 154: `def test_collector_rejects_warnings_list_with_non_string_item():`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 161: `assert collection.evidences == []`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 164: `def test_collector_ignores_asset_errors_and_does_not_create_evidence():`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 179: `assert collection.evidences == []`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 182: `def test_collector_keeps_empty_content_as_valid_evidence():`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 192: `assert len(collection.evidences) == 1`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 193: `assert collection.evidences[0].content == ""`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 194: `assert collection.evidences[0].warnings == ["No embedded text found."]`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 197: `def test_collector_returns_empty_collection_for_empty_page_extractions():`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 202: `assert collection.evidences == []`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 205: `def test_collector_rejects_non_dict_artifact():`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 206: `with pytest.raises(ValueError, match="object"):`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 210: `def test_collector_rejects_non_list_page_extractions():`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 211: `with pytest.raises(ValueError, match="page_extractions"):`
- `tests/test_pdf_text_extraction_evidence_collector.py` line 217: `def test_collector_does_not_add_forbidden_product_or_prompt_fields():`
- `tests/test_repository_explorer_entrypoint.py` line 13: `def test_repository_explorer_main_runs_composed_engine(monkeypatch):`
- `tests/test_size_classifier.py` line 5: `def test_should_return_small_for_zero_byte():`
- `tests/test_size_classifier.py` line 10: `assert result == SizeClass.SMALL`
- `tests/test_size_classifier.py` line 13: `def test_should_return_small_for_file_under_1mb():`
- `tests/test_size_classifier.py` line 18: `assert result == SizeClass.SMALL`
- `tests/test_size_classifier.py` line 21: `def test_should_return_medium_for_exactly_1mb():`
- `tests/test_size_classifier.py` line 26: `assert result == SizeClass.MEDIUM`
- `tests/test_size_classifier.py` line 29: `def test_should_return_medium_for_file_between_1mb_and_10mb():`
- `tests/test_size_classifier.py` line 34: `assert result == SizeClass.MEDIUM`
- `tests/test_size_classifier.py` line 37: `def test_should_return_medium_for_exactly_10mb():`
- `tests/test_size_classifier.py` line 42: `assert result == SizeClass.MEDIUM`
- `tests/test_size_classifier.py` line 45: `def test_should_return_large_for_file_over_10mb():`
- `tests/test_size_classifier.py` line 50: `assert result == SizeClass.LARGE`
- `tests/test_statistics_collector.py` line 11: `def test_should_collect_repository_statistics():`
- `tests/test_statistics_collector.py` line 58: `assert statistics.total_assets == 4`
- `tests/test_statistics_collector.py` line 59: `assert statistics.small_assets == 2`
- `tests/test_statistics_collector.py` line 60: `assert statistics.medium_assets == 1`
- `tests/test_statistics_collector.py` line 61: `assert statistics.large_assets == 1`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 8: `def test_inspects_valid_text_extraction_evidence_artifact():`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 26: `assert inspection.total_evidences == 2`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 27: `assert inspection.total_content_characters == 12`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 28: `assert inspection.empty_content_count == 0`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 29: `assert inspection.invalid_record_count == 0`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 30: `assert inspection.forbidden_field_count == 0`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 33: `def test_counts_empty_content_records():`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 51: `assert inspection.total_evidences == 2`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 52: `assert inspection.total_content_characters == 3`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 53: `assert inspection.empty_content_count == 1`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 54: `assert inspection.invalid_record_count == 0`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 57: `def test_counts_invalid_records_for_missing_required_fields():`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 73: `assert inspection.total_evidences == 2`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 74: `assert inspection.invalid_record_count == 2`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 77: `def test_counts_invalid_records_for_wrong_field_types():`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 100: `assert inspection.total_evidences == 3`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 101: `assert inspection.invalid_record_count == 3`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 104: `def test_counts_forbidden_fields():`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 125: `assert inspection.total_evidences == 2`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 126: `assert inspection.invalid_record_count == 2`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 127: `assert inspection.forbidden_field_count == 3`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 130: `def test_rejects_missing_evidences():`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 131: `with pytest.raises(ValueError, match="evidences"):`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 135: `def test_rejects_non_list_evidences():`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 136: `with pytest.raises(ValueError, match="list"):`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 140: `def test_rejects_non_dict_top_level_artifact():`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 141: `with pytest.raises(ValueError, match="object"):`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 145: `def test_rejects_bool_size_bytes():`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 158: `assert inspection.total_evidences == 1`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 159: `assert inspection.invalid_record_count == 1`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 162: `def test_counts_non_dict_evidence_entries_as_invalid():`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 177: `assert inspection.total_evidences == 3`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 178: `assert inspection.total_content_characters == 6`
- `tests/test_text_extraction_evidence_artifact_inspector.py` line 179: `assert inspection.invalid_record_count == 2`
- `tests/test_text_extraction_evidence_builder.py` line 11: `def test_builds_text_extraction_evidence_from_successful_extraction(tmp_path):`
- `tests/test_text_extraction_evidence_builder.py` line 21: `assert evidence.source_path == str(path)`
- `tests/test_text_extraction_evidence_builder.py` line 22: `assert evidence.content == "Generate a helmet concept."`
- `tests/test_text_extraction_evidence_builder.py` line 23: `assert evidence.size_bytes == 42`
- `tests/test_text_extraction_evidence_builder.py` line 26: `def test_preserves_extracted_content_exactly_including_non_ascii_text(tmp_path):`
- `tests/test_text_extraction_evidence_builder.py` line 37: `assert evidence.content == content`
- `tests/test_text_extraction_evidence_builder.py` line 40: `def test_text_extraction_evidence_does_not_expose_analysis_or_size_class(`
- `tests/test_text_extraction_evidence_builder.py` line 51: `assert [field.name for field in fields(evidence)] == [`
- `tests/test_text_extraction_evidence_builder.py` line 60: `def test_builder_rejects_failed_text_extraction(tmp_path):`
- `tests/test_text_extraction_evidence_builder.py` line 68: `with pytest.raises(ValueError):`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 12: `def test_serializes_empty_text_extraction_evidence_collection():`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 17: `assert json.loads(result) == {`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 22: `def test_serializes_one_text_extraction_evidence():`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 35: `assert json.loads(result) == {`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 46: `def test_serializes_multiple_evidences_deterministically():`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 65: `assert first == second`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 66: `assert json.loads(first)["evidences"] == [`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 80: `def test_preserves_non_ascii_content_with_ensure_ascii_false():`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 94: `assert json.loads(result)["evidences"][0]["content"] == (`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 99: `def test_serialized_output_contains_only_evidence_fields():`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 113: `assert set(data) == {"evidences"}`
- `tests/test_text_extraction_evidence_collection_serializer.py` line 114: `assert set(data["evidences"][0]) == {`
- `tests/test_text_extraction_evidence_collector.py` line 11: `def test_collects_evidence_from_successful_text_extractions(tmp_path):`
- `tests/test_text_extraction_evidence_collector.py` line 34: `assert len(collection.evidences) == 2`
- `tests/test_text_extraction_evidence_collector.py` line 35: `assert collection.evidences[0].source_path == str(first_path)`
- `tests/test_text_extraction_evidence_collector.py` line 36: `assert collection.evidences[0].content == "First prompt"`
- `tests/test_text_extraction_evidence_collector.py` line 37: `assert collection.evidences[0].size_bytes == 10`
- `tests/test_text_extraction_evidence_collector.py` line 38: `assert collection.evidences[1].source_path == str(second_path)`
- `tests/test_text_extraction_evidence_collector.py` line 39: `assert collection.evidences[1].content == "Second prompt"`
- `tests/test_text_extraction_evidence_collector.py` line 40: `assert collection.evidences[1].size_bytes == 20`
- `tests/test_text_extraction_evidence_collector.py` line 43: `def test_skips_failed_text_extractions(tmp_path):`
- `tests/test_text_extraction_evidence_collector.py` line 66: `assert len(collection.evidences) == 1`
- `tests/test_text_extraction_evidence_collector.py` line 67: `assert collection.evidences[0].source_path == str(successful_path)`
- `tests/test_text_knowledge_artifact_inspector.py` line 6: `def test_inspects_valid_text_knowledge_artifact():`
- `tests/test_text_knowledge_artifact_inspector.py` line 26: `assert inspection.total_knowledge_items == 2`
- `tests/test_text_knowledge_artifact_inspector.py` line 27: `assert inspection.total_content_characters == 12`
- `tests/test_text_knowledge_artifact_inspector.py` line 28: `assert inspection.empty_content_count == 0`
- `tests/test_text_knowledge_artifact_inspector.py` line 29: `assert inspection.invalid_record_count == 0`
- `tests/test_text_knowledge_artifact_inspector.py` line 30: `assert inspection.forbidden_field_count == 0`
- `tests/test_text_knowledge_artifact_inspector.py` line 33: `def test_counts_empty_content_items():`
- `tests/test_text_knowledge_artifact_inspector.py` line 53: `assert inspection.total_knowledge_items == 2`
- `tests/test_text_knowledge_artifact_inspector.py` line 54: `assert inspection.total_content_characters == 3`
- `tests/test_text_knowledge_artifact_inspector.py` line 55: `assert inspection.empty_content_count == 1`
- `tests/test_text_knowledge_artifact_inspector.py` line 56: `assert inspection.invalid_record_count == 0`
- `tests/test_text_knowledge_artifact_inspector.py` line 59: `def test_counts_invalid_records_for_missing_required_fields():`
- `tests/test_text_knowledge_artifact_inspector.py` line 77: `assert inspection.total_knowledge_items == 2`
- `tests/test_text_knowledge_artifact_inspector.py` line 78: `assert inspection.invalid_record_count == 2`
- `tests/test_text_knowledge_artifact_inspector.py` line 81: `def test_counts_invalid_records_for_wrong_field_types():`
- `tests/test_text_knowledge_artifact_inspector.py` line 113: `assert inspection.total_knowledge_items == 4`
- `tests/test_text_knowledge_artifact_inspector.py` line 114: `assert inspection.invalid_record_count == 4`
- `tests/test_text_knowledge_artifact_inspector.py` line 117: `def test_rejects_bool_size_bytes():`
- `tests/test_text_knowledge_artifact_inspector.py` line 131: `assert inspection.total_knowledge_items == 1`
- `tests/test_text_knowledge_artifact_inspector.py` line 132: `assert inspection.invalid_record_count == 1`
- `tests/test_text_knowledge_artifact_inspector.py` line 135: `def test_rejects_bool_evidence_index():`
- `tests/test_text_knowledge_artifact_inspector.py` line 149: `assert inspection.total_knowledge_items == 1`
- `tests/test_text_knowledge_artifact_inspector.py` line 150: `assert inspection.invalid_record_count == 1`
- `tests/test_text_knowledge_artifact_inspector.py` line 153: `def test_counts_forbidden_fields():`
- `tests/test_text_knowledge_artifact_inspector.py` line 176: `assert inspection.total_knowledge_items == 2`
- `tests/test_text_knowledge_artifact_inspector.py` line 177: `assert inspection.invalid_record_count == 2`
- `tests/test_text_knowledge_artifact_inspector.py` line 178: `assert inspection.forbidden_field_count == 3`
- `tests/test_text_knowledge_artifact_inspector.py` line 181: `def test_rejects_missing_knowledge_items():`
- `tests/test_text_knowledge_artifact_inspector.py` line 182: `with pytest.raises(ValueError, match="knowledge_items"):`
- `tests/test_text_knowledge_artifact_inspector.py` line 186: `def test_rejects_non_list_knowledge_items():`
- `tests/test_text_knowledge_artifact_inspector.py` line 187: `with pytest.raises(ValueError, match="list"):`
- `tests/test_text_knowledge_artifact_inspector.py` line 191: `def test_rejects_non_dict_top_level_artifact():`
- `tests/test_text_knowledge_artifact_inspector.py` line 192: `with pytest.raises(ValueError, match="object"):`
- `tests/test_text_knowledge_artifact_inspector.py` line 196: `def test_counts_non_dict_knowledge_items_as_invalid():`
- `tests/test_text_knowledge_artifact_inspector.py` line 212: `assert inspection.total_knowledge_items == 3`
- `tests/test_text_knowledge_artifact_inspector.py` line 213: `assert inspection.total_content_characters == 6`
- `tests/test_text_knowledge_artifact_inspector.py` line 214: `assert inspection.invalid_record_count == 2`
- `tests/test_text_knowledge_builder.py` line 9: `def test_builds_text_knowledge_from_valid_evidence_record():`
- `tests/test_text_knowledge_builder.py` line 22: `assert knowledge.source_path == "prompt.dat"`
- `tests/test_text_knowledge_builder.py` line 23: `assert knowledge.content == "Generate a helmet concept."`
- `tests/test_text_knowledge_builder.py` line 24: `assert knowledge.size_bytes == 26`
- `tests/test_text_knowledge_builder.py` line 25: `assert knowledge.evidence_index == 0`
- `tests/test_text_knowledge_builder.py` line 28: `def test_preserves_content_exactly_including_non_ascii_and_newlines():`
- `tests/test_text_knowledge_builder.py` line 41: `assert knowledge.content == content`
- `tests/test_text_knowledge_builder.py` line 44: `def test_preserves_source_path_size_bytes_and_evidence_index():`
- `tests/test_text_knowledge_builder.py` line 56: `assert knowledge.source_path == "D:\\PROJECT\\RIE\\prompt.dat"`
- `tests/test_text_knowledge_builder.py` line 57: `assert knowledge.size_bytes == 6`
- `tests/test_text_knowledge_builder.py` line 58: `assert knowledge.evidence_index == 7`
- `tests/test_text_knowledge_builder.py` line 61: `def test_builder_rejects_missing_required_fields():`
- `tests/test_text_knowledge_builder.py` line 67: `with pytest.raises(ValueError):`
- `tests/test_text_knowledge_builder.py` line 74: `def test_builder_rejects_extra_fields():`
- `tests/test_text_knowledge_builder.py` line 82: `with pytest.raises(ValueError):`
- `tests/test_text_knowledge_builder.py` line 89: `def test_builder_rejects_wrong_field_types():`
- `tests/test_text_knowledge_builder.py` line 109: `with pytest.raises(ValueError):`
- `tests/test_text_knowledge_builder.py` line 116: `def test_builder_rejects_bool_size_bytes():`
- `tests/test_text_knowledge_builder.py` line 123: `with pytest.raises(ValueError):`
- `tests/test_text_knowledge_builder.py` line 130: `def test_text_knowledge_exposes_no_summary_category_embedding_prompt_analysis_or_size_class():`
- `tests/test_text_knowledge_builder.py` line 142: `assert [field.name for field in fields(knowledge)] == [`
- `tests/test_text_knowledge_collection_serializer.py` line 8: `def test_serializes_empty_text_knowledge_collection():`
- `tests/test_text_knowledge_collection_serializer.py` line 13: `assert json.loads(result) == {`
- `tests/test_text_knowledge_collection_serializer.py` line 18: `def test_serializes_one_text_knowledge_item():`
- `tests/test_text_knowledge_collection_serializer.py` line 32: `assert json.loads(result) == {`
- `tests/test_text_knowledge_collection_serializer.py` line 44: `def test_serializes_multiple_text_knowledge_items_deterministically():`
- `tests/test_text_knowledge_collection_serializer.py` line 65: `assert first == second`
- `tests/test_text_knowledge_collection_serializer.py` line 66: `assert json.loads(first)["knowledge_items"] == [`
- `tests/test_text_knowledge_collection_serializer.py` line 82: `def test_preserves_non_ascii_content_with_ensure_ascii_false():`
- `tests/test_text_knowledge_collection_serializer.py` line 99: `assert json.loads(result)["knowledge_items"][0]["content"] == content`
- `tests/test_text_knowledge_collection_serializer.py` line 102: `def test_preserves_newline_content_exactly():`
- `tests/test_text_knowledge_collection_serializer.py` line 117: `assert json.loads(result)["knowledge_items"][0]["content"] == content`
- `tests/test_text_knowledge_collection_serializer.py` line 120: `def test_preserves_evidence_index():`
- `tests/test_text_knowledge_collection_serializer.py` line 134: `assert json.loads(result)["knowledge_items"][0]["evidence_index"] == 7`
- `tests/test_text_knowledge_collection_serializer.py` line 137: `def test_serialized_output_contains_only_knowledge_fields():`
- `tests/test_text_knowledge_collection_serializer.py` line 152: `assert set(data) == {"knowledge_items"}`
- `tests/test_text_knowledge_collection_serializer.py` line 153: `assert set(data["knowledge_items"][0]) == {`
- `tests/test_text_knowledge_collector.py` line 8: `def test_collector_builds_collection_from_evidence_artifact():`
- `tests/test_text_knowledge_collector.py` line 27: `assert len(collection.knowledge_items) == 2`
- `tests/test_text_knowledge_collector.py` line 28: `assert collection.knowledge_items[0].source_path == "first.dat"`
- `tests/test_text_knowledge_collector.py` line 29: `assert collection.knowledge_items[0].content == "First prompt"`
- `tests/test_text_knowledge_collector.py` line 30: `assert collection.knowledge_items[0].size_bytes == 12`
- `tests/test_text_knowledge_collector.py` line 31: `assert collection.knowledge_items[0].evidence_index == 0`
- `tests/test_text_knowledge_collector.py` line 32: `assert collection.knowledge_items[1].source_path == "second.dat"`
- `tests/test_text_knowledge_collector.py` line 33: `assert collection.knowledge_items[1].evidence_index == 1`
- `tests/test_text_knowledge_collector.py` line 36: `def test_collector_preserves_evidence_order():`
- `tests/test_text_knowledge_collector.py` line 63: `def test_collector_skips_invalid_evidence_records():`
- `tests/test_text_knowledge_collector.py` line 88: `assert len(collection.knowledge_items) == 2`
- `tests/test_text_knowledge_collector.py` line 89: `assert collection.knowledge_items[0].source_path == "valid-first.dat"`
- `tests/test_text_knowledge_collector.py` line 90: `assert collection.knowledge_items[0].evidence_index == 0`
- `tests/test_text_knowledge_collector.py` line 91: `assert collection.knowledge_items[1].source_path == "valid-second.dat"`
- `tests/test_text_knowledge_collector.py` line 92: `assert collection.knowledge_items[1].evidence_index == 3`
- `tests/test_text_knowledge_collector.py` line 95: `def test_empty_evidence_artifact_creates_empty_knowledge_collection():`
- `tests/test_text_knowledge_collector.py` line 99: `assert collection.knowledge_items == []`
- `tests/test_text_knowledge_collector.py` line 102: `def test_text_knowledge_collection_is_distinct_from_evidence_collection():`
- `tests/test_text_prompt_candidate.py` line 6: `def test_text_prompt_candidate_stores_exact_copied_values():`
- `tests/test_text_prompt_candidate.py` line 15: `assert candidate.source_path == "prompt.dat"`
- `tests/test_text_prompt_candidate.py` line 16: `assert candidate.content == "Generate a helmet concept."`
- `tests/test_text_prompt_candidate.py` line 17: `assert candidate.size_bytes == 26`
- `tests/test_text_prompt_candidate.py` line 18: `assert candidate.evidence_index == 2`
- `tests/test_text_prompt_candidate.py` line 19: `assert candidate.knowledge_index == 5`
- `tests/test_text_prompt_candidate.py` line 22: `def test_text_prompt_candidate_exposes_only_boundary_fields():`
- `tests/test_text_prompt_candidate.py` line 31: `assert [field.name for field in fields(candidate)] == [`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 8: `def test_counts_total_prompt_candidates():`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 30: `assert inspection.total_prompt_candidates == 2`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 31: `assert inspection.invalid_record_count == 0`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 34: `def test_counts_total_content_characters():`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 57: `assert inspection.total_content_characters == 12`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 60: `def test_counts_empty_content_candidates():`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 82: `assert inspection.empty_content_candidate_count == 1`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 83: `assert inspection.total_content_characters == 3`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 86: `def test_counts_invalid_records():`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 108: `assert inspection.invalid_record_count == 3`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 111: `def test_counts_forbidden_fields():`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 136: `assert inspection.invalid_record_count == 2`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 137: `assert inspection.forbidden_field_count == 3`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 140: `def test_accepts_exact_valid_fields_only():`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 155: `assert inspection.invalid_record_count == 0`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 156: `assert inspection.forbidden_field_count == 0`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 159: `def test_rejects_bool_for_size_bytes():`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 174: `assert inspection.invalid_record_count == 1`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 177: `def test_rejects_bool_for_evidence_index():`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 192: `assert inspection.invalid_record_count == 1`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 195: `def test_rejects_bool_for_knowledge_index():`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 210: `assert inspection.invalid_record_count == 1`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 213: `def test_rejects_missing_required_fields():`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 227: `assert inspection.invalid_record_count == 1`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 230: `def test_rejects_extra_non_forbidden_fields_as_invalid():`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 246: `assert inspection.invalid_record_count == 1`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 247: `assert inspection.forbidden_field_count == 0`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 250: `def test_counts_forbidden_fields_separately():`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 266: `assert inspection.invalid_record_count == 1`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 267: `assert inspection.forbidden_field_count == 1`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 270: `def test_preserves_inspection_only_behavior_no_mutation():`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 294: `assert artifact == original`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 297: `def test_rejects_missing_prompt_candidates():`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 298: `with pytest.raises(ValueError, match="prompt_candidates"):`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 302: `def test_rejects_non_list_prompt_candidates():`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 303: `with pytest.raises(ValueError, match="list"):`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 307: `def test_rejects_non_dict_top_level_artifact():`
- `tests/test_text_prompt_candidate_artifact_inspector.py` line 308: `with pytest.raises(ValueError, match="object"):`
- `tests/test_text_prompt_candidate_builder.py` line 7: `def test_builder_preserves_content_exactly():`
- `tests/test_text_prompt_candidate_builder.py` line 21: `assert candidate.content == "Generate a helmet concept."`
- `tests/test_text_prompt_candidate_builder.py` line 24: `def test_builder_preserves_non_ascii_content():`
- `tests/test_text_prompt_candidate_builder.py` line 38: `assert candidate.content == content`
- `tests/test_text_prompt_candidate_builder.py` line 41: `def test_builder_preserves_newline_content():`
- `tests/test_text_prompt_candidate_builder.py` line 55: `assert candidate.content == content`
- `tests/test_text_prompt_candidate_builder.py` line 58: `def test_builder_preserves_empty_content():`
- `tests/test_text_prompt_candidate_builder.py` line 71: `assert candidate.content == ""`
- `tests/test_text_prompt_candidate_builder.py` line 74: `def test_builder_copies_source_path_size_bytes_and_evidence_index():`
- `tests/test_text_prompt_candidate_builder.py` line 87: `assert candidate.source_path == "D:\\PROJECT\\RIE\\prompt.dat"`
- `tests/test_text_prompt_candidate_builder.py` line 88: `assert candidate.size_bytes == 6`
- `tests/test_text_prompt_candidate_builder.py` line 89: `assert candidate.evidence_index == 7`
- `tests/test_text_prompt_candidate_builder.py` line 92: `def test_builder_adds_knowledge_index():`
- `tests/test_text_prompt_candidate_builder.py` line 105: `assert candidate.knowledge_index == 5`
- `tests/test_text_prompt_candidate_builder.py` line 108: `def test_builder_rejects_invalid_text_knowledge_records():`
- `tests/test_text_prompt_candidate_builder.py` line 150: `with pytest.raises(ValueError):`
- `tests/test_text_prompt_candidate_builder.py` line 157: `def test_builder_rejects_bool_integer_fields():`
- `tests/test_text_prompt_candidate_builder.py` line 174: `with pytest.raises(ValueError):`
- `tests/test_text_prompt_candidate_builder.py` line 181: `def test_builder_rejects_bool_knowledge_index():`
- `tests/test_text_prompt_candidate_builder.py` line 189: `with pytest.raises(ValueError):`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 12: `def test_serializer_produces_top_level_prompt_candidates_key():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 17: `assert result == {`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 22: `def test_serializer_serializes_one_candidate_correctly():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 37: `assert result == {`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 50: `def test_serializer_serializes_multiple_candidates_in_order():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 72: `assert result["prompt_candidates"] == [`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 90: `def test_serializer_preserves_exact_content():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 111: `def test_serializer_preserves_non_ascii_content():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 129: `assert json.loads(result)["prompt_candidates"][0]["content"] == content`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 132: `def test_serializer_preserves_newline_content():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 148: `assert json.loads(result)["prompt_candidates"][0]["content"] == content`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 151: `def test_serializer_preserves_empty_content():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 166: `assert result["prompt_candidates"][0]["content"] == ""`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 169: `def test_serializer_preserves_evidence_index():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 184: `assert result["prompt_candidates"][0]["evidence_index"] == 7`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 187: `def test_serializer_preserves_knowledge_index():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 202: `assert result["prompt_candidates"][0]["knowledge_index"] == 9`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 205: `def test_serializer_does_not_include_forbidden_fields():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 221: `assert set(candidate) == {`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 255: `def test_to_json_output_is_deterministic():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 271: `assert first == second`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 274: `def test_to_json_output_can_be_parsed_back_with_json_loads():`
- `tests/test_text_prompt_candidate_collection_serializer.py` line 290: `assert data["prompt_candidates"][0]["source_path"] == "prompt.dat"`
- `tests/test_text_prompt_candidate_collector.py` line 9: `def test_collector_builds_collection_from_text_knowledge_artifact():`
- `tests/test_text_prompt_candidate_collector.py` line 30: `assert len(collection.prompt_candidates) == 2`
- `tests/test_text_prompt_candidate_collector.py` line 31: `assert collection.prompt_candidates[0].source_path == "first.dat"`
- `tests/test_text_prompt_candidate_collector.py` line 32: `assert collection.prompt_candidates[0].content == "First prompt"`
- `tests/test_text_prompt_candidate_collector.py` line 33: `assert collection.prompt_candidates[0].size_bytes == 12`
- `tests/test_text_prompt_candidate_collector.py` line 34: `assert collection.prompt_candidates[0].evidence_index == 0`
- `tests/test_text_prompt_candidate_collector.py` line 35: `assert collection.prompt_candidates[0].knowledge_index == 0`
- `tests/test_text_prompt_candidate_collector.py` line 36: `assert collection.prompt_candidates[1].source_path == "second.dat"`
- `tests/test_text_prompt_candidate_collector.py` line 37: `assert collection.prompt_candidates[1].knowledge_index == 1`
- `tests/test_text_prompt_candidate_collector.py` line 40: `def test_collector_skips_invalid_text_knowledge_records():`
- `tests/test_text_prompt_candidate_collector.py` line 68: `assert len(collection.prompt_candidates) == 2`
- `tests/test_text_prompt_candidate_collector.py` line 69: `assert collection.prompt_candidates[0].source_path == "valid-first.dat"`
- `tests/test_text_prompt_candidate_collector.py` line 70: `assert collection.prompt_candidates[1].source_path == "valid-second.dat"`
- `tests/test_text_prompt_candidate_collector.py` line 73: `def test_collector_preserves_original_knowledge_index_positions():`
- `tests/test_text_prompt_candidate_collector.py` line 109: `def test_collector_rejects_bool_for_integer_fields():`
- `tests/test_text_prompt_candidate_collector.py` line 135: `assert len(collection.prompt_candidates) == 1`
- `tests/test_text_prompt_candidate_collector.py` line 136: `assert collection.prompt_candidates[0].source_path == "valid.dat"`
- `tests/test_text_prompt_candidate_collector.py` line 139: `def test_empty_text_knowledge_artifact_creates_empty_prompt_candidate_collection():`
- `tests/test_text_prompt_candidate_collector.py` line 143: `assert collection.prompt_candidates == []`
- `tests/test_text_prompt_candidate_collector.py` line 146: `def test_collector_does_not_add_prompt_generation_or_interpretive_fields():`

### 9.3 Existing accepted-Evidence implementation symbols

- No matching tracked lines found.

No accepted-Evidence prerequisite implementation symbol exists at the Phase 24 entry checkpoint.

## 10. PR-023C contract observations

- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 1: `# PR-023C — Accepted Evidence Contract and Materialization Boundary Review`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 8: `\| Branch \| `phase-023-knowledge-governance-review` \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 18: `PR-023C defines the authoritative accepted-Evidence contract boundary and the materialization boundary without creating code.`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 22: `- application-layer `EvidenceCandidate`;`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 26: `- materialization result;`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 28: `- Knowledge construction.`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 39: `- File: `docs/architecture/pr-023b-accepted-evidence-materialization-identity-and-repository-prerequisite-review.md``
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 56: `### 4.1 Application EvidenceCandidate`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 59: `- `src/rie/application/evidence_candidate.py` line 34: `class EvidenceCandidate:``
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 184: `- Name: `AcceptedEvidence``
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 187: `- Mutability: immutable`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 188: `- Construction: only through an explicit application-layer materialization service`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 190: `- Knowledge coupling: prohibited`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 194: ``EvidenceCandidate` remains in the application layer and is not moved into the domain.`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 196: `## 6. AcceptedEvidence top-level contract`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 200: `\| Field \| Type \| Required \| Meaning \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 204: `\| `candidate_reference` \| `EvidenceCandidateReference` \| Yes \| Immutable link to the originating candidate snapshot \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 207: `\| `factual_payload` \| `EvidencePayload` \| Yes \| Immutable factual payload, schema, digest, and locator \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 210: `\| `materialization_record` \| `EvidenceMaterializationRecord` \| Yes \| Auditable construction record \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 211: `\| `diagnostics` \| `tuple[EvidenceDiagnostic, ...]` \| Yes \| Immutable warnings and informational diagnostics; may be empty \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 213: `No optional top-level fields and no default values are approved.`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 215: `## 7. EvidenceCandidateReference contract`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 217: `\| Field \| Type \| Required \| Rule \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 226: `This is a reference contract, not a second mutable copy of `EvidenceCandidate`.`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 232: `\| Field \| Type \| Required \| Rule \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 243: `Path existence is not validated by this immutable contract.`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 249: `\| Field \| Type \| Required \| Rule \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 260: `\| Field \| Type \| Required \| Rule \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 264: `\| `payload` \| immutable scalar, tuple, or immutable mapping representation \| Yes \| Factual value only; no business interpretation \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 270: `- Knowledge summaries;`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 282: `\| Field \| Type \| Required \| Rule \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 285: `\| `locator_value` \| immutable scalar or tuple \| Yes \| Exact reproducible location \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 294: `\| Field \| Type \| Required \| Rule \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 298: `\| `lineage` \| `tuple[str, ...]` \| Yes \| Ordered immutable lineage identifiers; may not be empty \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 306: `\| Field \| Type \| Required \| Rule \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 308: `\| `decision` \| literal `eligible` \| Yes \| Any other decision blocks materialization \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 320: `## 14. EvidenceMaterializationRecord contract`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 322: `\| Field \| Type \| Required \| Rule \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 334: `Materialization does not generate identity silently. It receives a validated identity result from the later approved identity boundary.`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 338: `\| Field \| Type \| Required \| Rule \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 348: `## 16. Validation boundary`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 350: `The immutable contract validates only structural invariants:`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 352: `- all required fields exist;`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 359: `- payload and locator are immutable representations;`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 363: `The immutable contract must not:`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 373: `- infer Knowledge;`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 381: `## 17. Materialization input boundary`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 385: `1. one immutable `EvidenceCandidate`;`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 388: `4. one explicit materialization context containing reviewer/service identity and audit timestamp.`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 390: `It may produce one `EvidenceMaterializationResult`.`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 398: `- Knowledge builder;`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 405: `## 18. EvidenceMaterializationResult contract`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 407: `\| Field \| Type \| Required \| Rule \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 410: `\| `accepted_evidence` \| `AcceptedEvidence` or null \| Yes \| Present only when materialized \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 412: `\| `diagnostics` \| `tuple[EvidenceDiagnostic, ...]` \| Yes \| Complete immutable diagnostics \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 416: `- `materialized` requires one `AcceptedEvidence` and no error diagnostics;`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 419: `- the result does not construct Knowledge.`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 421: `## 19. Materialization preconditions`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 423: `Materialization succeeds only when all conditions hold:`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 426: `2. candidate snapshot is immutable and complete;`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 438: `14. materialization context is explicit;`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 439: `15. no repository, parser, filesystem, network, AI, Knowledge, or Prompt dependency is present.`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 441: `## 20. Materialization rejection codes`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 463: `- `materialization_context_incomplete``
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 491: `- materialization timestamp;`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 496: `- Knowledge or Prompt content.`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 508: `\| `src/rie/application/evidence_candidate.py` \| Retained as immutable application input DTO \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 515: `\| Existing Knowledge modules \| Outside materialization boundary \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 516: `\| Existing Prompt modules \| Outside materialization boundary \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 524: `\| `EvidenceCandidate` \| Application layer \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 527: `\| `AcceptedEvidence` \| RIE domain \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 528: `\| Materialization orchestration \| Application service \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 532: `\| Knowledge construction \| Later phase after Evidence prerequisites \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 533: `\| Prompt Candidate \| Downstream of validated Knowledge only \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 539: `**Rejected.** The observed shape is too small and does not carry the required governance, provenance, eligibility, and identity boundaries.`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 545: `### Option C — Extend `EvidenceCandidate` until it becomes accepted Evidence`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 551: `**Rejected.** Persistence must not own eligibility, identity, or materialization semantics.`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 553: `### Option E — Approve a new immutable `AcceptedEvidence` contract and separate materialization result`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 561: `The accepted-Evidence contract and materialization boundary are approved at documentation level.`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 595: `\| Structural validation boundary \| PASSED \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 596: `\| Materialization input/result boundary \| PASSED \|`
- `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md` line 625: `\| Knowledge or Prompt Candidate created \| False \|`

These observations are excerpts only. The full PR-023C document remains authoritative.

The implementation must not reinterpret, simplify, add defaults to, or silently omit required contract fields.

## 11. Approved first implementation scope

The next gate is limited to:

1. the immutable `AcceptedEvidence` domain contract;
2. only nested immutable value contracts strictly required to instantiate `AcceptedEvidence` exactly as defined by PR-023C;
3. explicit required constructor fields;
4. explicit contract/schema/version fields required by PR-023C;
5. structural validation that can be evaluated from constructor inputs alone;
6. focused unit tests for immutability, required fields, constructor behavior, equality, explicit versions, and approved cross-field consistency;
7. package marker files only when listed in the approved exact file scope.

## 12. Required implementation properties

The implementation must:

- use immutable Python contracts;
- use `@dataclass(frozen=True)` where consistent with the repository contract style;
- expose no mutable collection value;
- use immutable tuples or immutable nested contracts where collections are required;
- provide no default value for a field that PR-023C defines as required;
- perform no I/O;
- read no environment variables;
- use no clock, random value, UUID, hash service, database, parser, network, AI, or repository adapter;
- create no Evidence identity;
- perform no materialization;
- perform no eligibility decision;
- create no accepted Evidence from an `EvidenceCandidate` automatically;
- import no Knowledge or Prompt type;
- preserve historical Evidence modules unchanged.

## 13. Structural validation boundary

Allowed validation is limited to deterministic local contract checks such as:

- required string values are non-empty when PR-023C requires non-empty values;
- version values are explicit;
- immutable collections contain the approved immutable value type;
- duplicated canonical keys inside one aggregate are rejected when prohibited by PR-023C;
- cross-field invariants explicitly stated in PR-023C are enforced.

Not allowed:

- source existence checks;
- file digest calculation;
- identity calculation;
- eligibility lookup;
- repository lookup;
- semantic duplicate analysis;
- conflict resolution;
- authority scoring;
- lifecycle mutation;
- Knowledge inference.

## 14. Focused test boundary

The next implementation gate may add focused tests only for the approved files.

Required categories:

1. frozen-instance mutation rejection;
2. all required fields accepted when valid;
3. omitted required fields fail through constructor semantics;
4. explicit version fields preserved;
5. equality is value-based;
6. immutable collections cannot be mutated through the aggregate;
7. approved structural validation rejects invalid local values;
8. no defaults silently fill required fields;
9. no side effects occur during construction.

Tests must not use PDF/image assets, OCR, parser execution, network, database, filesystem fixture trees, or AI.

Full regression is not part of the first implementation gate unless separately authorized after focused implementation review.

## 15. Explicit exclusions

PR-024B must not implement:

- `EvidenceIdentityResult`;
- canonical serialization;
- SHA-256 identity policy;
- `EvidenceMaterializationResult`;
- materializer service;
- `EvidenceRepository`;
- write/lookup requests or results;
- persistence adapter;
- serializer migration;
- EvidenceRelationship;
- Knowledge or KnowledgeCandidate;
- KnowledgeRepository;
- Prompt Candidate or Final Prompt;
- CLI, API, dashboard, ingestion, PDF/image/OCR processing;
- migration or deletion of historical Evidence classes.

## 16. Dependency direction

Allowed:

`	ext
standard library
    -> immutable accepted-Evidence value contracts
    -> AcceptedEvidence
`

Prohibited:

`	ext
AcceptedEvidence
    -> application services
    -> infrastructure
    -> parser/ingestion
    -> repository adapter
    -> Knowledge
    -> Prompt
`

`EvidenceCandidate` may later be an input to an approved materialization service, but it is not a dependency of the immutable accepted-Evidence domain contract.

## 17. Compatibility freeze

During PR-024B:

- `src/rie/application/evidence_candidate.py` remains unchanged;
- `tests/application/test_evidence_candidate.py` remains unchanged;
- historical `src/evidence` modules remain unchanged;
- collection and extraction behavior remain unchanged;
- existing Knowledge modules remain unchanged;
- existing Prompt modules remain unchanged;
- `pyproject.toml` and dependency files remain unchanged;
- no broad import rewrite is allowed;
- no rename or deletion is allowed.

## 18. Review and commit discipline for PR-024B

The implementation gate must:

1. verify the exact PR-024A commit checkpoint;
2. create only the approved files;
3. execute focused tests exactly once unless a separately reviewed failure requires a new gate;
4. record the exact test command and result;
5. perform no automatic retry;
6. stop before stage/commit/push;
7. upload the complete external output for independent assessment;
8. stage/commit/push only after explicit approval.

## 19. Options reviewed

### Option A — Implement the full accepted-Evidence stack in one PR

**Rejected.** It combines domain contract, identity, materialization, repository, persistence, and governance.

### Option B — Place `AcceptedEvidence` in the application package beside `EvidenceCandidate`

**Rejected.** Accepted Evidence is a domain fact contract, while `EvidenceCandidate` is an application DTO.

### Option C — Reuse or rename a historical generic `Evidence` class

**Rejected.** Existing Evidence meanings are compatibility surfaces and require separate migration review.

### Option D — Implement only the immutable accepted-Evidence contract and focused tests

**Selected.** This is the smallest reviewable runtime slice.

### Option E — Start Knowledge governance now

**Rejected.** Durable accepted Evidence, identity, materialization, and repository behavior are not implemented.

## 20. Final decision

# PHASE 24 BOOTSTRAP BOUNDARY APPROVED; ACCEPTED EVIDENCE IMMUTABLE DOMAIN CONTRACT IMPLEMENTATION AUTHORIZED AS THE NEXT CONTROLLED GATE

Phase 24 bootstrap is valid.

The next controlled gate may implement only the exact immutable accepted-Evidence domain contract and focused tests within the approved file scope.

## 21. Exact next gate

**PR-024B - AcceptedEvidence Immutable Domain Contract Implementation**

Type: **Implementation**

No identity, materialization, repository, persistence, Knowledge, Prompt, asset, or migration implementation is authorized.

## 22. Acceptance assessment

| Acceptance area | Result |
|---|---|
| Phase 24 branch entry | PASSED |
| Phase 24 local/tracking/remote synchronization | PASSED |
| Main and Phase 23 checkpoint preservation | PASSED |
| Phase 23 annotated tag preservation | PASSED |
| Phase 22 branch/tag preservation | PASSED |
| Governing document hash verification | PASSED |
| Read-only repository structure inspection | PASSED |
| Existing implementation-symbol absence | PASSED |
| Exact implementation file scope | PASSED |
| Immutable contract boundary | PASSED |
| Structural validation boundary | PASSED |
| Focused test boundary | PASSED |
| Compatibility freeze | PASSED |
| Five architecture options | PASSED |
| Exactly one final decision | PASSED — `PHASE 24 BOOTSTRAP BOUNDARY APPROVED; ACCEPTED EVIDENCE IMMUTABLE DOMAIN CONTRACT IMPLEMENTATION AUTHORIZED AS THE NEXT CONTROLLED GATE` |
| Exactly one next gate | PASSED |
| Code/test/asset boundary | PASSED |

## 23. Action truth table

| Action | Performed |
|---|---|
| Read-only Phase 24 entry verification | True |
| Phase 23/22 reference verification | True |
| Architecture document hash verification | True |
| Read-only source/test convention inspection | True |
| One repository review document created | True |
| One external output created | True |
| Production code modified | False |
| Test code modified | False |
| Tests executed | False |
| Project Python interpreter executed | False |
| Dependency/configuration changed | False |
| PDF/image/OCR/parser/ingestion executed | False |
| Real asset processed | False |
| AcceptedEvidence implemented | False |
| Identity implemented | False |
| Materializer implemented | False |
| EvidenceRepository implemented | False |
| Persistence implemented | False |
| Knowledge or Prompt implemented | False |
| Repository file staged | False |
| Commit created | False |
| Push performed | False |
| Merge/tag/branch action performed | False |
| Branch deleted | False |
| Automatic retry performed | False |

## 24. Gate conclusion

PR-024A concludes **PHASE 24 BOOTSTRAP BOUNDARY APPROVED; ACCEPTED EVIDENCE IMMUTABLE DOMAIN CONTRACT IMPLEMENTATION AUTHORIZED AS THE NEXT CONTROLLED GATE**.

Only `PR-024B - AcceptedEvidence Immutable Domain Contract Implementation` is authorized after PR-024A commit/push verification.
