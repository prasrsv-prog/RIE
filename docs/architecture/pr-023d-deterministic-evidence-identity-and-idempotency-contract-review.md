# PR-023D — Deterministic Evidence Identity and Idempotency Contract Review

## 1. Gate identity

| Item | Value |
|---|---|
| Repository | `D:\PROJECT\RIE` |
| Branch | `phase-023-knowledge-governance-review` |
| Reviewed HEAD | `3b176d1f0f096603547905e0ea8b666d67250508` |
| Gate type | Documentation-only |
| Inherited PR-023C decision | `ACCEPTED EVIDENCE CONTRACT BOUNDARY APPROVED; IMPLEMENTATION DEFERRED` |
| Final PR-023D decision | **DETERMINISTIC EVIDENCE IDENTITY AND IDEMPOTENCY CONTRACT APPROVED; REPOSITORY IMPLEMENTATION DEFERRED** |
| Recommended next gate | **PR-023E - Evidence Repository Interface and Persistence Boundary Review** |
| Recommended next gate type | **Documentation-only** |

## 2. Purpose

PR-023D defines deterministic factual Evidence identity, governance acceptance identity, replay classification, duplicate handling, collision handling, idempotent behavior, conflict/supersession boundaries, and repository key requirements without creating code or persistence.

The review preserves the separation between:

- `EvidenceCandidate`;
- eligibility result;
- deterministic identity result;
- `AcceptedEvidence`;
- materialization result;
- repository interface;
- persistence adapter;
- Knowledge.

## 3. Checkpoint and preservation

PR-023C was verified as an exact one-file documentation commit:

- Commit: `3b176d1f0f096603547905e0ea8b666d67250508`
- Parent: `6cc26a79476251cb579e25f2227ef9c660d5abc0`
- Subject: `docs: define accepted evidence contract boundary`
- File: `docs/architecture/pr-023c-accepted-evidence-contract-and-materialization-boundary-review.md`
- File SHA-256: `6459c0309242ed1d08b0cd4d6bb5ba1dd70ca356199b5c7ee0f02c3348b5457c`

The Phase 23 branch is synchronized with its remote at divergence `0 0`.

Phase 22 remains preserved:

- Branch: `phase-022-evidence-candidate-boundary-review`
- Branch target: `e41269e764979f94f23f93692136c63cc603f2e2`
- Official tag: `v0.22.0-rcis-evidence-candidate-boundary-phase`
- Tag object: `1a7488e7cc2830aea2506182e6a6aba797cbebcf`
- Peeled target: `e41269e764979f94f23f93692136c63cc603f2e2`

The controlled PDF sandbox and `D:\PROJECT\pytest-temp` were verified empty. Real and synthetic PDF targets were absent. The known read-only `.pytest_cache` warning was not repaired or deleted.

## 4. Read-only repository observations

### 4.1 Identity-related matches

- `tests/application/test_evidence_candidate.py` line 2: `import hashlib`
- `tests/application/test_evidence_candidate.py` line 22: `"source_checksum_algorithm": "sha256",`
- `tests/application/test_evidence_candidate.py` line 55: `"sha256",`
- `tests/application/test_evidence_candidate.py` line 300: `monkeypatch.setattr(hashlib, "sha256", fail_checksum)`
- `tests/application/test_evidence_candidate.py` line 324: `assert "evidence_id" not in names`
- `tests/application/test_evidence_candidate.py` line 325: `assert "candidate_id" not in names`
- `tests/test_official_source_evidence_workflow_gate.py` line 111: `"evidence_id",`
- `tests/test_official_source_evidence_workflow_preflight.py` line 147: `assert "evidence_id" not in exposed_fields`

### 4.2 Duplicate, replay, collision, conflict, and supersession matches

- `src/official_source/official_source.py` line 41: `SUPERSEDED = "superseded"`
- `src/official_source/official_source_registry_loader.py` line 97: `raise ValueError(f"duplicate source_id: {source.source_id}.")`
- `src/rie/application/evidence_candidate.py` line 181: `"raw_payload must not contain duplicate JSON object keys"`
- `src/rie/application/evidence_candidate.py` line 244: `raise ValueError(f"locator contains duplicate key: {key}")`
- `src/rie/ingestion/controlled_pdf_structural_metadata_contract.py` line 94: `reason="duplicate fixture_id",`
- `src/rie/ingestion/controlled_pdf_text_extraction_contract.py` line 81: `reason="duplicate fixture_id",`
- `src/rie/ingestion/controlled_real_asset_fixture_contract.py` line 166: `reason="duplicate fixture_id",`
- `src/rie/ingestion/controlled_real_asset_fixture_contract.py` line 174: `reason="duplicate fixture_path",`
- `tests/application/test_evidence_candidate.py` line 113: `with pytest.raises(ValueError, match="duplicate"):`
- `tests/application/test_evidence_candidate.py` line 235: `with pytest.raises(ValueError, match="duplicate"):`
- `tests/ingestion/test_controlled_pdf_text_extraction_contract.py` line 142: `assert result.reason == "duplicate fixture_id"`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 187: `first = _fixture(fixture_id="duplicate", fixture_path="fixtures/one.pdf")`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 188: `second = _fixture(fixture_id="duplicate", fixture_path="fixtures/two.pdf")`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 193: `assert result.reason == "duplicate fixture_id"`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 197: `first = _fixture(fixture_id="one", fixture_path="fixtures/duplicate.pdf")`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 198: `second = _fixture(fixture_id="two", fixture_path="fixtures/duplicate.pdf")`
- `tests/ingestion/test_controlled_real_asset_fixture_contract.py` line 203: `assert result.reason == "duplicate fixture_path"`
- `tests/test_inspect_official_source_registry_cli.py` line 86: `lifecycle_status="superseded",`
- `tests/test_inspect_official_source_registry_cli.py` line 107: `assert "superseded: 1" in output`
- `tests/test_official_source.py` line 69: `assert LifecycleStatus.SUPERSEDED.value == "superseded"`
- `tests/test_official_source_evidence_eligibility_policy.py` line 94: `superseded = _evaluate(`
- `tests/test_official_source_evidence_eligibility_policy.py` line 95: `_source(lifecycle_status=LifecycleStatus.SUPERSEDED),`
- `tests/test_official_source_evidence_eligibility_policy.py` line 98: `assert active.allowed == superseded.allowed`
- `tests/test_official_source_evidence_eligibility_policy.py` line 99: `assert active.requires_review == superseded.requires_review`
- `tests/test_official_source_registry_loader.py` line 152: `with pytest.raises(ValueError, match="duplicate source_id"):`
- `tests/test_official_source_registry_loader.py` line 250: `_item(source_id="SRC-002", lifecycle_status="superseded"),`
- `tests/test_official_source_registry_loader.py` line 256: `LifecycleStatus.SUPERSEDED,`

### 4.3 Builder and candidate construction observations

- `src/evidence/evidence_builder.py` line 11: `def build(`
- `src/evidence/evidence_builder.py` line 17: `return Evidence(`
- `src/evidence/pdf_text_extraction_evidence_builder.py` line 7: `"source_path",`
- `src/evidence/pdf_text_extraction_evidence_builder.py` line 20: `def build(`
- `src/evidence/pdf_text_extraction_evidence_builder.py` line 30: `"source_path, size_bytes, page_number, extraction_index, "`
- `src/evidence/pdf_text_extraction_evidence_builder.py` line 34: `source_path = page_extraction_record["source_path"]`
- `src/evidence/pdf_text_extraction_evidence_builder.py` line 42: `if not isinstance(source_path, str):`
- `src/evidence/pdf_text_extraction_evidence_builder.py` line 44: `"PDF page extraction record source_path must be a string."`
- `src/evidence/pdf_text_extraction_evidence_builder.py` line 87: `return PdfTextExtractionEvidence(`
- `src/evidence/pdf_text_extraction_evidence_builder.py` line 88: `source_path=source_path,`
- `src/evidence/pdf_text_extraction_evidence_builder.py` line 99: `def _is_int_not_bool(value: Any) -> bool:`
- `src/evidence/pdf_text_extraction_evidence_builder.py` line 100: `return isinstance(value, int) and not isinstance(value, bool)`
- `src/evidence/text_extraction_evidence_builder.py` line 9: `def build(`
- `src/evidence/text_extraction_evidence_builder.py` line 17: `return TextExtractionEvidence(`
- `src/evidence/text_extraction_evidence_builder.py` line 18: `source_path=str(extraction.path),`
- `src/rie/application/evidence_candidate.py` line 54: `def __post_init__(self) -> None:`
- `src/rie/application/evidence_candidate.py` line 112: `def _validate_required_string(field_name: str, value: object) -> None:`
- `src/rie/application/evidence_candidate.py` line 128: `def _contains_control_character(value: str) -> bool:`
- `src/rie/application/evidence_candidate.py` line 129: `return any(`
- `src/rie/application/evidence_candidate.py` line 135: `def _validate_token(`
- `src/rie/application/evidence_candidate.py` line 144: `def _validate_checksum(value: str) -> None:`
- `src/rie/application/evidence_candidate.py` line 154: `def _validate_execution_timestamp(value: str) -> None:`
- `src/rie/application/evidence_candidate.py` line 173: `def _reject_duplicate_object_pairs(`
- `src/rie/application/evidence_candidate.py` line 185: `return result`
- `src/rie/application/evidence_candidate.py` line 188: `def _reject_non_finite_constant(value: str) -> None:`
- `src/rie/application/evidence_candidate.py` line 194: `def _validate_canonical_json(value: str) -> None:`
- `src/rie/application/evidence_candidate.py` line 219: `def _validate_locator(`
- `src/rie/application/evidence_candidate.py` line 308: `def _validate_diagnostics(`

These observations do not establish an authoritative identity or idempotency contract. Existing hashes, digests, timestamps, equality behavior, UUID references, duplicate checks, or builders may belong to other layers or historical code.

## 5. Identity categories

The architecture defines three separate identities:

| Identity | Meaning | Mutability |
|---|---|---|
| `evidence_id` | Stable identity of accepted factual Evidence | Immutable |
| `acceptance_record_id` | Stable identity of the governance acceptance event | Immutable |
| repository record key | Storage lookup key derived from approved identities and repository contract | Deferred to PR-023E |

These identities must never be collapsed.

A change in governance review must not automatically change `evidence_id` when the factual Evidence inputs remain identical.

A change in factual content, producer contract, locator, or source content digest must produce a different `evidence_id`.

## 6. Deterministic identity result contract

The future identity service returns an immutable `EvidenceIdentityResult` with exactly these fields:

| Field | Type | Required | Rule |
|---|---|---:|---|
| `status` | `generated` or `rejected` | Yes | Explicit outcome |
| `evidence_id` | `str` or null | Yes | Present only for `generated` |
| `canonical_identity_bytes_digest` | `str` or null | Yes | Digest of canonical identity bytes |
| `identity_policy_id` | `str` | Yes | Stable policy identifier |
| `identity_policy_version` | `str` | Yes | Explicit version |
| `algorithm` | `str` | Yes | Exact digest algorithm identifier |
| `algorithm_version` | `str` | Yes | Exact algorithm/canonicalization version |
| `reason_codes` | `tuple[str, ...]` | Yes | Explicit success or rejection reasons |
| `diagnostics` | immutable diagnostic tuple | Yes | Complete diagnostics |

The result performs no repository lookup or write.

## 7. Canonical factual identity inputs

`evidence_id` is derived from exactly these semantic inputs from the PR-023C contract:

1. accepted-Evidence contract version;
2. source identifier;
3. source content digest;
4. producer name;
5. producer version;
6. producer kind;
7. producer contract version;
8. payload type;
9. payload schema version;
10. payload digest;
11. canonical locator type;
12. canonical locator value;
13. locator schema version;
14. producer output digest.

No other semantic fields participate.

## 8. Explicitly excluded factual identity inputs

The following must not participate in `evidence_id`:

- source path by itself;
- candidate snapshot digest by itself;
- observed/materialized/evaluated timestamps;
- authority status;
- lifecycle status;
- source eligibility declaration;
- eligibility decision timestamp;
- acceptance actor;
- acceptance reason;
- review record identity;
- policy human-readable message;
- diagnostic wording or ordering;
- repository location;
- insertion sequence;
- database row identifier;
- branch, commit, or filesystem metadata;
- Knowledge text;
- Prompt Candidate content;
- random values.

Exclusion prevents audit metadata and persistence details from changing factual identity.

## 9. Canonical serialization

Canonical identity serialization uses a versioned, deterministic UTF-8 JSON object with these rules:

1. top-level keys are fixed and appear in the contract-defined order;
2. nested locator keys are fixed and ordered;
3. strings are Unicode-normalized using NFC;
4. strings are preserved semantically and are not lowercased unless the field contract explicitly requires a lowercase controlled token;
5. no insignificant whitespace is emitted;
6. JSON separators are comma and colon only;
7. numbers, if ever permitted in locator values, use canonical decimal representation without exponent normalization drift;
8. tuples serialize as ordered arrays;
9. mappings are forbidden unless their key order is defined by the contract;
10. null is forbidden in identity inputs;
11. timestamps are excluded;
12. path separators are not normalized because source path is excluded;
13. canonicalization version is explicit.

Canonical JSON field order:

1. `accepted_evidence_contract_version`
2. `source_id`
3. `source_content_digest`
4. `producer_name`
5. `producer_version`
6. `producer_kind`
7. `producer_contract_version`
8. `payload_type`
9. `payload_schema_version`
10. `payload_digest`
11. `locator_type`
12. `locator_value`
13. `locator_schema_version`
14. `producer_output_digest`

## 10. Digest algorithm and evidence_id format

Approved factual identity algorithm:

- Algorithm: `SHA-256`
- Input: canonical UTF-8 JSON bytes
- Hex encoding: lowercase hexadecimal
- Digest length: 64 hexadecimal characters
- Policy identifier: `rcis.accepted-evidence-identity`
- Policy version: `1.0`
- Canonicalization version: `json-nfc-ordered-v1`

Approved `evidence_id` format:

`	ext
ev1_<64-lowercase-hex-sha256>
`

Example shape only:

`	ext
ev1_0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
`

No UUID, timestamp, counter, path slug, random suffix, or database-generated identifier is allowed.

## 11. Governance acceptance_record_id

`acceptance_record_id` identifies the acceptance event, not the factual Evidence.

Canonical inputs:

1. `evidence_id`;
2. eligibility policy identifier;
3. eligibility policy version;
4. candidate snapshot digest;
5. review record identifier;
6. accepted-by identifier;
7. materializer identifier;
8. materializer version;
9. materialization timestamp in canonical RFC 3339 UTC form.

Algorithm:

- SHA-256 over versioned canonical UTF-8 JSON;
- lowercase hexadecimal;
- policy identifier `rcis.evidence-acceptance-record-identity`;
- policy version `1.0`.

Format:

`	ext
ar1_<64-lowercase-hex-sha256>
`

Different valid acceptance events for the same factual `evidence_id` may have different `acceptance_record_id` values.

## 12. Identity validation

The identity service rejects generation when:

- any required input is absent;
- an input is null;
- a controlled token is unsupported;
- a digest is not lowercase 64-character hexadecimal;
- locator canonicalization is unsupported;
- mapping order is ambiguous;
- Unicode normalization fails;
- canonical serialization version is unsupported;
- digest algorithm/version is unsupported;
- canonical bytes cannot be reproduced exactly;
- supplied candidate/materialization references disagree.

The identity service does not repair, infer, fetch, parse, or generate missing factual inputs.

## 13. Replay and duplicate classification

A future repository boundary must classify each write request before persistence.

| Classification | Condition | Repository meaning |
|---|---|---|
| `exact_replay` | Same `evidence_id` and byte-for-byte equivalent canonical accepted-Evidence content | Idempotent no-op |
| `governance_replay` | Same `acceptance_record_id` and equivalent acceptance record | Idempotent no-op |
| `same_fact_new_acceptance` | Same `evidence_id` with a new valid `acceptance_record_id` | Preserve new governance event without duplicating factual Evidence |
| `identity_collision` | Same `evidence_id` but different canonical factual identity bytes or factual content | Reject and raise explicit collision error |
| `acceptance_collision` | Same `acceptance_record_id` but different canonical acceptance bytes | Reject and raise explicit collision error |
| `semantic_duplicate` | Different `evidence_id` but a reviewer suspects equivalent meaning | Do not merge automatically; record review candidate |
| `conflicting_evidence` | Different `evidence_id` supports incompatible factual claims | Preserve both; create explicit conflict relationship later |
| `superseding_evidence` | New factual Evidence explicitly supersedes prior Evidence | Preserve both identities and explicit supersession relation |
| `new_evidence` | No equivalent factual identity exists | Eligible for repository insertion after PR-023E |

## 14. Idempotent no-op contract

An idempotent no-op:

- performs no mutation to the stored factual record;
- does not overwrite timestamps or diagnostics;
- does not change insertion order;
- does not create a duplicate row/object;
- returns the existing identity and a status of `unchanged`;
- records no hidden retry;
- may return an explicit replay diagnostic;
- must be deterministic for the same repository state and input.

The repository must not silently convert collisions or semantic duplicates into no-ops.

## 15. Collision handling

Identity collision handling is fail-closed.

Required behavior:

1. reject the write;
2. preserve the existing record unchanged;
3. return explicit collision classification;
4. provide both canonical byte digests;
5. provide identity policy/version;
6. emit no overwrite;
7. emit no retry;
8. require manual architecture/review follow-up;
9. do not construct Knowledge;
10. do not alter conflict or supersession relations automatically.

No salt, suffix, rehash, random UUID, or fallback algorithm may be introduced automatically.

## 16. Semantic duplicate handling

Semantic equivalence is not identity equality.

The system must not:

- use AI or LLM similarity;
- use text normalization to collapse Evidence;
- compare summaries;
- compare only payload strings while ignoring provenance;
- select the newest record;
- merge locators;
- infer source authority;
- suppress duplicates silently.

A semantic duplicate may become a later review candidate only. It remains outside deterministic idempotency.

## 17. Conflict boundary

Conflicting Evidence uses distinct `evidence_id` values because factual inputs differ.

Conflict representation must be explicit and separate from the Evidence object:

- relationship identifier;
- left Evidence identifier;
- right Evidence identifier;
- conflict type;
- reason codes;
- review status;
- reviewer;
- review timestamp;
- contract version.

PR-023D does not create or implement EvidenceRelationship.

No identity service or repository write may select a winner.

## 18. Supersession boundary

Supersession does not mutate or delete prior Evidence.

A future supersession relationship must contain:

- prior `evidence_id`;
- superseding `evidence_id`;
- explicit reason;
- authority/review record;
- effective timestamp;
- relationship version.

The superseding Evidence receives its own deterministic identity.

## 19. Repository key requirements

PR-023D approves requirements, not a repository implementation.

The future repository contract must support:

- primary factual key: `evidence_id`;
- governance event key: `acceptance_record_id`;
- immutable canonical bytes digest for collision verification;
- lookup by factual identity;
- lookup by governance event identity;
- exact replay classification;
- collision rejection;
- preservation of multiple acceptance events for one factual Evidence;
- explicit conflict/supersession relationship references;
- no last-write-wins;
- no hidden retry;
- no automatic deletion or compaction.

The exact interface and persistence ownership are deferred to PR-023E.

## 20. Determinism requirements

Given identical approved semantic inputs and identical identity policy/version, the identity service must always produce:

- identical canonical JSON bytes;
- identical canonical byte digest;
- identical `evidence_id`;
- identical status and reason codes.

Determinism must hold across:

- process restarts;
- operating systems;
- locale settings;
- timezone settings;
- dictionary insertion order;
- repository state;
- file location;
- execution time.

## 21. Versioning and migration

Identity policy/version is immutable after publication.

A future change to canonical fields, normalization, serialization, algorithm, or ID prefix requires a new policy version.

Rules:

- old IDs remain valid and resolvable;
- no silent re-identification;
- migration creates explicit mapping records;
- repository keys are not rewritten in place;
- accepted Evidence preserves the identity policy/version used;
- mixed policy versions may coexist;
- collisions are evaluated within the declared policy/version;
- cross-version equivalence requires explicit review.

## 22. Layer ownership

| Concern | Owner |
|---|---|
| Canonical identity input assembly | Application service after PR-023C validation |
| Canonicalization policy | Dedicated identity policy |
| Digest execution | Dedicated deterministic identity service |
| `EvidenceIdentityResult` | Immutable application/domain contract |
| `evidence_id` storage | AcceptedEvidence domain contract |
| `acceptance_record_id` | Materialization governance contract |
| Replay/collision classification | Future repository interface |
| Persistence | Future infrastructure adapter |
| Semantic duplicate review | Later governance workflow |
| Conflict/supersession relationship | Later EvidenceRelationship boundary |
| Knowledge | Not authorized |

## 23. Options reviewed

### Option A — UUID identity

**Rejected.** UUIDs do not prove deterministic factual equivalence.

### Option B — Source path plus timestamp

**Rejected.** Paths and timestamps are unstable and do not represent factual identity.

### Option C — Payload digest only

**Rejected.** Payload-only identity discards source, producer, schema, locator, and provenance boundaries.

### Option D — Dataclass equality as identity

**Rejected.** Equality semantics are not a versioned canonical identity policy.

### Option E — Versioned canonical semantic inputs plus SHA-256

**Selected.** This is deterministic, reproducible, traceable, and independent of persistence.

## 24. Final architecture decision

# DETERMINISTIC EVIDENCE IDENTITY AND IDEMPOTENCY CONTRACT APPROVED; REPOSITORY IMPLEMENTATION DEFERRED

The deterministic factual identity, governance acceptance identity, replay classification, collision handling, semantic duplicate boundary, conflict/supersession boundary, and repository key requirements are approved at documentation level.

Implementation remains deferred until the repository interface and persistence boundary are reviewed.

## 25. Exact next safe gate

**PR-023E - Evidence Repository Interface and Persistence Boundary Review**

Type: **Documentation-only**

The next gate must define, without coding:

1. exact EvidenceRepository interface methods;
2. accepted input/result contracts;
3. factual and governance key ownership;
4. lookup and write semantics;
5. exact replay and collision result mapping;
6. transaction and atomicity expectations;
7. interface versus infrastructure ownership;
8. persistence adapter boundaries;
9. error and no-retry behavior;
10. no Knowledge or Prompt coupling;
11. exactly one final decision and one next review-only gate.

## 26. Acceptance assessment

| Acceptance area | Result |
|---|---|
| PR-023C commit/push checkpoint | PASSED |
| Phase 22 branch/tag preservation | PASSED |
| Sandbox/temp preservation | PASSED |
| Read-only identity inspection | PASSED |
| Identity category separation | PASSED |
| Exact factual identity inputs | PASSED |
| Canonical serialization | PASSED |
| Digest algorithm and ID format | PASSED |
| Governance acceptance identity | PASSED |
| Replay/duplicate classification | PASSED |
| Idempotent no-op semantics | PASSED |
| Collision handling | PASSED |
| Semantic duplicate boundary | PASSED |
| Conflict/supersession boundary | PASSED |
| Repository key requirements | PASSED |
| Determinism/versioning | PASSED |
| Five architecture options | PASSED |
| Exactly one final decision | PASSED — `DETERMINISTIC EVIDENCE IDENTITY AND IDEMPOTENCY CONTRACT APPROVED; REPOSITORY IMPLEMENTATION DEFERRED` |
| Exactly one next review-only gate | PASSED |
| Code/test/asset boundary | PASSED |

## 27. Action truth table

| Action | Performed |
|---|---|
| Read-only checkpoint verification | True |
| Read-only identity/idempotency source inspection | True |
| One repository review document created | True |
| One external output created | True |
| Production code modified | False |
| Test code modified | False |
| Tests executed | False |
| Project Python interpreter executed | False |
| Dependency/venv/pyproject/config changed | False |
| PDF/image/OCR/parser/ingestion executed | False |
| Real asset processed | False |
| Identity implementation created | False |
| Accepted Evidence created | False |
| EvidenceRepository or persistence created | False |
| EvidenceRelationship created | False |
| Knowledge or Prompt Candidate created | False |
| AI/LLM inference executed | False |
| Repository file staged | False |
| Commit created | False |
| Push performed | False |
| Merge/history rewrite performed | False |
| Tag action performed | False |
| Automatic retry performed | False |

## 28. Gate conclusion

PR-023D concludes **DETERMINISTIC EVIDENCE IDENTITY AND IDEMPOTENCY CONTRACT APPROVED; REPOSITORY IMPLEMENTATION DEFERRED**.

Only `PR-023E - Evidence Repository Interface and Persistence Boundary Review` is recommended. No production implementation is authorized.
