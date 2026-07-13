# PR-025C — KnowledgeCandidate Construction Result and Full Regression Review

## 1. Review identity and repository checkpoint

| Item | Verified value |
|---|---|
| Review | PR-025C |
| Final execution gate | PR-025C R4 — Controlled Stale Basetemp Cleanup and Full Regression Review |
| Repository | `D:\PROJECT\RIE` |
| Branch | `phase-025-knowledge-construction` |
| HEAD | `2d94cf2ba22d3bf3eeca368d316da6bb2a52c470` |
| Parent | `da5f8e86da1a70c0d7221030ee86d0a1bc1e6a5c` |
| Commit subject | `feat: add minimal knowledge candidate construction` |
| Local phase ref | `2d94cf2ba22d3bf3eeca368d316da6bb2a52c470` |
| Remote phase ref | `2d94cf2ba22d3bf3eeca368d316da6bb2a52c470` |
| Divergence | `0 0` |

The implementation commit is synchronized with `origin/phase-025-knowledge-construction`. The repository was clean with no staged files before R4. The only repository change made by this review is this new, untracked document.

## 2. Exact PR-025B implementation commit scope

Commit `2d94cf2ba22d3bf3eeca368d316da6bb2a52c470` adds exactly:

- `src/rie/domain/knowledge_candidate.py`;
- `src/rie/application/knowledge_constructor.py`;
- `tests/domain/test_knowledge_candidate.py`;
- `tests/application/test_knowledge_constructor.py`.

No documentation, configuration, dependency, interface, infrastructure, database, asset, CLI, Prompt Candidate, or legacy Knowledge file was changed by the implementation commit.

## 3. Immutable KnowledgeCandidate result

The domain implementation provides frozen immutable contracts for:

- `KnowledgeDiagnostic`;
- `KnowledgeEvidenceSupport`;
- `KnowledgeCandidateIdentityInput`;
- `KnowledgeCandidate`.

Validation fails closed for invalid identifier formats, non-tuple collections, duplicate or unordered references, empty required values, wrong exact member types, empty or duplicate support, and unsupported governance states. A constructed candidate remains fixed at:

```text
authority_status = unassessed
lifecycle_status = candidate
review_status = pending_review
conflict_status = not_assessed
conflict_ids = ()
```

`KnowledgeCandidate` is a reviewable construction result. It is not reviewed Knowledge, accepted Knowledge, a business decision, or a Prompt Candidate.

## 4. Deterministic `kc1_` identity result

The implementation defines the approved identity policy:

```text
policy_id = rcis-knowledge-candidate-identity
policy_version = 1.0.0
canonicalization_contract = knowledge-candidate-json-v1
digest_algorithm = sha256
id_prefix = kc1_
```

Identity uses UTF-8 canonical JSON, Unicode NFC normalization in the identity projection, sorted object keys, compact separators, deterministic tuple/list projection, and ordered support references. Candidate IDs have the exact form `kc1_<64 lowercase SHA-256 hex characters>`.

The identity projection includes only the approved contract, statement, rule, support, and initial governance fields. Diagnostics, source paths, timestamps, list position, Python object identity, and future review metadata remain excluded. The visible candidate statement is preserved exactly and is not visibly normalized.

## 5. Exact AcceptedEvidence and AcceptanceRecord boundary

`KnowledgeConstructionRequest` requires:

- an exact `rie.domain.accepted_evidence.AcceptedEvidence` object;
- a non-empty tuple of exact `rie.domain.acceptance_record.AcceptanceRecord` objects;
- an explicit construction-rule ID and version.

The constructor rejects raw dictionaries, paths, extraction output, `EvidenceCandidate`, legacy Evidence, legacy Knowledge, and duck-typed substitutes. It performs no repository lookup and accepts no unresolved repository identifier in place of the exact upstream objects.

Every supplied acceptance record must reference the same Evidence ID. The materialization acceptance record must be present, and its actor, reason, review record, materializer identity/version, and accepted/materialized time must match the accepted-Evidence materialization record.

## 6. Verbatim-text construction and explicit rejection behavior

The application implementation supports exactly one rule:

```text
rule_id = rcis-accepted-text-verbatim
rule_version = 1.0.0
```

Construction succeeds only for eligible accepted Evidence with payload type `text`, schema `1.0.0`, and exactly one immutable mapping entry named `text` containing a non-empty string. The statement is copied exactly without trimming, case folding, summarization, semantic correction, or inference.

`KnowledgeConstructionResult` is explicit:

- `constructed` contains exactly one `KnowledgeCandidate` and no rejection reason;
- `rejected` contains no candidate, a deterministic reason-code tuple, and immutable diagnostics.

Unsupported rules, mismatched acceptance records, unsupported payloads, missing text, non-string text, and empty text fail without candidate construction or automatic correction.

## 7. Complete provenance result

`KnowledgeEvidenceSupport` preserves:

- accepted Evidence ID;
- ordered unique acceptance-record IDs;
- ordered unique acceptance review-record IDs;
- source ID and source-content digest;
- source authority and lifecycle snapshots;
- payload digest;
- locator type, immutable locator value, and locator schema version.

Acceptance-record input order does not alter canonical identity. Canonical ordering does not mutate the request or its upstream objects. Source authority and lifecycle remain provenance snapshots and are not promoted into KnowledgeCandidate governance.

## 8. Preserved governance and integration boundaries

Committed source inspection and focused/full test evidence confirm:

- no authority promotion;
- no lifecycle or review promotion;
- no conflict detection or resolution;
- no repository lookup or repository wiring;
- no persistence, serialization, database schema, or migration;
- no Prompt Candidate or final prompt creation;
- no AI inference, summarization, embeddings, or semantic correction;
- no legacy Knowledge integration or migration;
- no filesystem or source-asset reads;
- no automatic acceptance, retry, or historical overwrite.

## 9. Inherited focused result

The independently verified focused PR-025B result is:

```text
89 passed
0 failed
0 errors
0 skipped
1 pytest process
0 retries
```

Focused tests were not rerun during PR-025C R4.

## 10. Prior environment-failure sequence

The implementation was not changed in response to any environment failure.

1. Original PR-025C stopped during collection because the exact project virtual environment could not import declared dependency `pypdf`.
2. PR-025C R1 restored only declared dependency `pypdf` version `6.14.2`; its regression then failed because the required external pytest parent did not exist.
3. PR-025C R2 restored the parent and reached the suite; 22 SQLite tests failed because `RCIS_SQLITE_TEST_ROOT` was unset.

PR-025C R3 stopped before pytest because elevated inspection proved the stale R2 basetemp was populated rather than empty. That stop preserved its contents until R4 explicitly authorized controlled deletion.

## 11. R4 controlled stale-basetemp cleanup

Before deletion, R4 verified that `D:\PROJECT\pytest-temp` contained exactly one direct child:

```text
D:\PROJECT\pytest-temp\pr-025c-r2-full-regression
```

The child resolved to the exact canonical path, was inside the intended parent, was a normal directory rather than a symbolic link, junction, or reparse point, and contained 622 descendants: 316 directories and 306 files totaling 76,641 bytes.

R4 recursively deleted only that exact stale R2 basetemp. It did not remove the parent or touch `.pytest_cache` or any unrelated path. The parent was verified empty before the R4 test.

## 12. R4 exact environment and full-regression result

R4 set both variables in the same PowerShell process:

```text
PYTHONPATH=src
RCIS_SQLITE_TEST_ROOT=D:\PROJECT\pytest-temp
```

Exact command:

```powershell
D:\PROJECT\RIE\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --color=no --basetemp D:\PROJECT\pytest-temp\pr-025c-r4-full-regression tests
```

Actual result:

```text
1670 passed in 6.38s
0 failed
0 errors
0 skipped
1 pytest process
0 retries
exit code 0
```

No focused rerun, second pytest process, or automatic correction occurred.

## 13. Final repository and temporary-state hygiene

After the pass, R4 verified that the exact current-run basetemp was the only child of the controlled parent. It was a normal directory, not a link or reparse point, and contained 622 generated descendants. R4 recursively deleted only:

```text
D:\PROJECT\pytest-temp\pr-025c-r4-full-regression
```

Final hygiene result:

- `D:\PROJECT\pytest-temp` exists and is empty;
- no R4 SQLite database remains;
- no repository database or build artifact was created;
- production source and tests are unchanged;
- configuration, dependency declarations, interfaces, and infrastructure are unchanged;
- no existing documentation was modified;
- repository status contains only this new review document;
- no file is staged;
- no commit, push, fetch, merge, tag, reset, rebase, or amend occurred.

## 14. Deferred scope

PR-025C does not authorize or implement:

- reviewed, accepted, locked, rejected, or superseded Knowledge;
- Knowledge authority decisions or lifecycle transitions;
- conflict detection, representation, review, or resolution;
- multi-Evidence Knowledge composition;
- `KnowledgeRepository`, persistence, serialization, or migration;
- runtime repository lookup or CLI integration;
- Prompt Candidate or generator integration;
- AI inference or business/creative decisions;
- legacy Knowledge migration or replacement.

These capabilities require separately reviewed gates after Phase 25 closure.

## 15. Definition of Done

PR-025C is complete because:

- the exact synchronized implementation checkpoint and four-file scope are verified;
- the immutable domain, deterministic identity, application, provenance, and governance boundaries match PR-025A;
- the inherited focused result is `89 passed`;
- the one authorized R4 full regression passed all `1670` tests;
- the full regression used the exact project interpreter and authorized environment;
- no retry or second pytest process occurred;
- controlled stale and current basetemp paths were removed exactly;
- the external pytest parent is empty;
- repository scope is exactly this one new review document;
- no source, test, configuration, dependency, database, asset, interface, or infrastructure file changed;
- no Git write or history operation occurred.

## 16. Final decision

# APPROVED FOR PHASE 25 CLOSURE

The minimal KnowledgeCandidate construction contract is implemented, focused coverage is verified, the full regression passes, provenance and governance boundaries are preserved, and final repository and temporary-state hygiene are clean. Phase 25 is approved for its separately controlled closure workflow.
