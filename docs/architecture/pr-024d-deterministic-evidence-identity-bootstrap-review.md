# PR-024D — Deterministic Evidence Identity Bootstrap Review

## 1. Gate identity

| Item | Value |
|---|---|
| Repository | `D:\PROJECT\RIE` |
| Branch | `phase-024-accepted-evidence-implementation` |
| Reviewed HEAD | `d8522eabff3b700a757d81605daa44a65316b798` |
| Gate type | Documentation-only |
| Final decision | **DETERMINISTIC EVIDENCE IDENTITY BOOTSTRAP BOUNDARY APPROVED; TWO-FILE IDENTITY IMPLEMENTATION AUTHORIZED AS THE NEXT CONTROLLED GATE** |
| Next gate | **PR-024E - Deterministic Evidence Identity Contract and Policy Implementation** |
| Next gate type | **Implementation** |

## 2. Purpose

PR-024D establishes the smallest deterministic Evidence identity implementation boundary after the immutable `AcceptedEvidence` contract was committed and pushed.

It does not implement identity, rerun focused tests, run full regression, or modify existing code.

## 3. Verified Phase 24 checkpoint

Verified:

- local/tracking/remote Phase 24 HEAD: `d8522eabff3b700a757d81605daa44a65316b798`;
- divergence: `0 0`;
- latest parent: `e08f87054f280ad29e588f8f0e55220afc556448`;
- latest subject: `feat: add accepted evidence immutable domain contract`;
- latest commit scope: exactly four approved PR-024B/PR-024C files;
- Phase 24 is exactly two commits ahead of main;
- Phase 24 total diff is exactly five added files;
- no merge commits;
- clean working tree before document creation.

## 4. AcceptedEvidence implementation checkpoint

Preserved implementation files:

| File | SHA-256 |
|---|---|
| `src/rie/domain/__init__.py` | `19367c9343a82e2ce80681b03d70afbc8bb3fa2ea7d50a86f483079846cc2f02` |
| `src/rie/domain/accepted_evidence.py` | `13ab1389879581a7c169f4b134e7ab065f0b56d5c497412993909e3535370f00` |
| `tests/domain/test_accepted_evidence.py` | `fe7750e195be73d35131fc6786406a7ded7dc986f306acea3231de471f979de7` |
| `docs/architecture/pr-024c-accepted-evidence-immutable-domain-contract-implementation-result-review.md` | `5c6f1de1d31b1187c62135396d473f5ef60d6ca691b5fbd89c878119e424fff8` |

The accepted-Evidence implementation remains immutable and unchanged.

Captured focused result remains:

- one execution;
- zero automatic retries;
- 60 passed;
- full regression deferred.

PR-024D does not rerun those tests.

## 5. Governing identity contract

The governing identity review remains:

- `docs/architecture/pr-023d-deterministic-evidence-identity-and-idempotency-contract-review.md`;
- SHA-256: `8ed9ad0023759047b6ca5372fe763ce6b8dc608a1ea1139f1145492cd05f8dbb`.

The immutable accepted-Evidence contract supplies all required factual identity values.

## 6. Exact factual identity inputs

The next implementation must use exactly these fourteen factual inputs:

- `accepted_evidence_contract_version`
- `source_identifier`
- `source_content_digest`
- `producer_name`
- `producer_version`
- `producer_kind`
- `producer_contract_version`
- `payload_type`
- `payload_schema_version`
- `payload_digest`
- `canonical_locator_type`
- `canonical_locator_value`
- `locator_schema_version`
- `producer_output_digest`

No additional factual input may be introduced without a new architecture review.

## 7. Explicit identity exclusions

The following are excluded from factual Evidence identity:

- `source_path`
- `document_classification`
- `authority_status`
- `lifecycle_status`
- `evidence_eligibility`
- `collection_id`
- `lineage`
- `observed_at`
- `eligibility_result`
- `materialization_record`
- `diagnostics`
- `timestamps`
- `random values`
- `Knowledge`
- `Prompt Candidate`

Governance acceptance identity remains distinct from factual Evidence identity.

## 8. Approved implementation file scope

The next implementation gate may create exactly:

1. `src/rie/domain/evidence_identity.py`;
2. `tests/domain/test_evidence_identity.py`.

No existing file modification is authorized.

In particular, `src/rie/domain/__init__.py` must remain unchanged during PR-024E.

## 9. Required implementation contracts

PR-024E may implement:

- immutable `EvidenceIdentityInput` containing exactly fourteen fields;
- immutable `EvidenceIdentityResult`;
- immutable versioned identity policy constants or contract;
- deterministic extraction of identity input from `AcceptedEvidence`;
- deterministic canonical UTF-8 JSON serialization;
- NFC normalization of textual identity values;
- fixed key order;
- no insignificant whitespace;
- lowercase SHA-256 hexadecimal digest;
- `evidence_id` format `ev1_<64hex>`;
- explicit identity policy ID and version in the result.

## 10. Canonicalization boundary

Canonicalization must:

- be deterministic;
- use standard-library functionality only;
- serialize exactly the fourteen approved inputs;
- preserve explicit locator structure;
- reject unsupported mutable or non-canonical values;
- reject non-finite floats;
- avoid null insertion for absent values;
- avoid path normalization;
- avoid timestamps;
- avoid random values;
- avoid locale-dependent behavior.

Persistence serialization remains separate from identity canonicalization.

## 11. Result boundary

`EvidenceIdentityResult` must expose only reviewed deterministic outputs such as:

- `evidence_id`;
- digest algorithm;
- digest hex;
- identity policy ID;
- identity policy version;
- canonicalization contract version;
- canonical byte length or digest verification data when explicitly justified.

It must not contain repository state, duplicate classification, acceptance governance, Knowledge, or Prompt information.

## 12. Focused test boundary

PR-024E focused tests must cover:

1. immutable identity input and result contracts;
2. all fourteen required fields;
3. no defaults for required fields;
4. fixed key order;
5. UTF-8 encoding;
6. NFC text normalization;
7. whitespace-independent canonical output;
8. deterministic repeated calculation;
9. exact lowercase SHA-256 digest;
10. exact `ev1_` format;
11. excluded governance fields do not affect factual identity;
12. each factual input changes identity when changed;
13. unsupported mutable values fail closed;
14. non-finite floats fail closed;
15. no clock, UUID, random, repository, filesystem, network, Knowledge, or Prompt dependency.

Tests must execute exactly once in a later implementation gate and must use a controlled temp path only if actually required. Identity unit tests should not require filesystem temp state.

## 13. Explicit exclusions from PR-024E

PR-024E must not implement:

- `acceptance_record_id` or `ar1_` generation;
- replay classification;
- exact/governance replay handling;
- collision repository checks;
- semantic duplicate handling;
- conflict or supersession relationships;
- `EvidenceMaterializationResult`;
- materializer service;
- `EvidenceRepository`;
- persistence adapter;
- Knowledge or Prompt Candidate;
- PDF/image/OCR/parser behavior;
- migration of historical Evidence types.

Acceptance-record identity and repository replay behavior require later separate gates.

## 14. Dependency direction

Allowed:

`	ext
standard library
    -> AcceptedEvidence
    -> EvidenceIdentityInput
    -> canonicalization
    -> EvidenceIdentityResult
`

Prohibited:

`	ext
identity
    -> application services
    -> infrastructure
    -> repository adapter
    -> persistence
    -> Knowledge
    -> Prompt
`

## 15. Compatibility freeze

During PR-024E:

- `src/rie/domain/accepted_evidence.py` remains unchanged;
- `tests/domain/test_accepted_evidence.py` remains unchanged;
- `src/rie/application/evidence_candidate.py` remains unchanged;
- `tests/application/test_evidence_candidate.py` remains unchanged;
- historical Evidence modules remain unchanged;
- Knowledge and Prompt modules remain unchanged;
- dependency/configuration files remain unchanged;
- no broad import rewrite or export aggregation is allowed.

## 16. Full regression decision

Full regression remains deferred.

PR-024E may run only its exact focused identity test file. A later controlled regression gate remains required before Knowledge governance readiness can be reopened.

## 17. Options reviewed

### Option A — Combine factual identity and acceptance-record identity

**Rejected.** They represent distinct factual and governance identities.

### Option B — Add identity behavior directly to `AcceptedEvidence`

**Rejected.** The immutable fact contract must remain free of hashing policy behavior.

### Option C — Implement identity plus materialization

**Rejected.** This combines two separate Phase 24 slices.

### Option D — Implement deterministic factual identity in two new files

**Selected.** This is the smallest reviewable identity slice.

### Option E — Start repository replay classification now

**Rejected.** Repository behavior depends on a verified deterministic identity implementation.

## 18. Final decision

# DETERMINISTIC EVIDENCE IDENTITY BOOTSTRAP BOUNDARY APPROVED; TWO-FILE IDENTITY IMPLEMENTATION AUTHORIZED AS THE NEXT CONTROLLED GATE

The next implementation may create exactly two files for deterministic factual Evidence identity and focused tests.

## 19. Exact next gate

**PR-024E - Deterministic Evidence Identity Contract and Policy Implementation**

Type: **Implementation**

No materialization, acceptance-record identity, replay classification, repository, persistence, Knowledge, or Prompt implementation is authorized.

## 20. Action truth table

| Action | Performed |
|---|---|
| Read-only Phase 24 checkpoint verification | True |
| Latest four-file commit verification | True |
| Five-file total branch scope verification | True |
| AcceptedEvidence hash verification | True |
| PR-023D identity contract verification | True |
| Identity input availability inspection | True |
| Existing identity implementation absence check | True |
| One repository review document created | True |
| One external output created | True |
| Production code modified | False |
| Test code modified | False |
| Tests executed | False |
| Project interpreter executed | False |
| Existing file modified | False |
| Dependency/configuration changed | False |
| Asset/parser execution | False |
| Identity implemented | False |
| Materializer/repository/persistence implemented | False |
| Knowledge or Prompt implemented | False |
| Repository file staged | False |
| Commit created | False |
| Push performed | False |
| Merge/tag/branch action | False |
| Automatic retry | False |

## 21. Gate conclusion

PR-024D concludes **DETERMINISTIC EVIDENCE IDENTITY BOOTSTRAP BOUNDARY APPROVED; TWO-FILE IDENTITY IMPLEMENTATION AUTHORIZED AS THE NEXT CONTROLLED GATE**.

Only `PR-024E - Deterministic Evidence Identity Contract and Policy Implementation` is authorized after PR-024D commit/push verification.
