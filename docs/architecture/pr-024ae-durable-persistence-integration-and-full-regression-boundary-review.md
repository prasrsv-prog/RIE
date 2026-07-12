# PR-024AE — Durable Persistence Integration and Full-Regression Boundary Review

## 1. Gate identity

| Item | Value |
|---|---|
| Repository | `D:\PROJECT\RIE` |
| Branch | `phase-024-accepted-evidence-implementation` |
| Reviewed checkpoint | `1f6c9aab0725e1308b96f23cbee9e24cb619bc80` |
| Parent | `328393179c771ba6680bb312092842f1254bfc21` |
| Latest subject | `feat: add sqlite evidence repository adapter` |
| Gate type | Documentation-only integration and regression boundary review |
| Decision | **DURABLE ADAPTER ACCEPTED AS EXPLICIT OPT-IN INFRASTRUCTURE; RUNTIME INTEGRATION DEFERRED; ONE CONTROLLED FULL REGRESSION AUTHORIZED** |

## 2. Current durable persistence checkpoint

The SQLite Evidence Repository adapter is committed and synchronized locally and remotely.

Exact committed implementation scope:

```text
src/rie/infrastructure/sqlite_evidence_repository.py
tests/infrastructure/test_sqlite_evidence_repository.py
docs/architecture/pr-024ac-sqlite-evidence-repository-adapter-implementation-result-review.md
```

Exact fingerprints:

```text
Adapter source:
ec459f0c6bd1dc3e9d09f3cd6597ceef89c5f3b03ed72ad43819561792a60888

Focused test module:
2a57ee3e49205448e10f9ab80ddbddf21d44d911136e8a23b567ec83e96f99f8

Implementation result review:
192c229f7f275264cb15405007f1a169fb491cbb105452213dee499a1054ab5f
```

The corrected focused execution passed `42` cases in one pytest process with zero retry.

## 3. Phase 24 scope interpretation

Phase 24 establishes:

- AcceptedEvidence immutable domain contracts;
- deterministic Evidence identity;
- EvidenceCandidate snapshot digest;
- AcceptedEvidence materialization;
- AcceptanceRecord and deterministic acceptance identity;
- EvidenceRepository interface;
- in-memory reference adapter;
- persistence serialization contract;
- durable SQLite adapter.

Phase 24 does not need to activate durable persistence automatically in an existing application path.

Automatic runtime activation would cross from infrastructure implementation into application composition and deployment policy.

That boundary requires separate evidence and should not be inferred from the adapter's existence.

## 4. Integration decision

The SQLite adapter is approved only as an explicit opt-in infrastructure component.

Approved usage boundary:

```python
SqliteEvidenceRepository(database_path)
```

The caller must explicitly provide the database path.

No existing application flow may silently replace the in-memory adapter.

No existing application flow may silently create a durable database.

No default repository selection is authorized.

No process-wide singleton is authorized.

No service locator is authorized.

No hidden fallback from SQLite to memory is authorized.

No hidden fallback from memory to SQLite is authorized.

## 5. Runtime wiring status

Runtime wiring remains deferred.

This review does not authorize changes to:

- application pipeline construction;
- application engine construction;
- command-line entry points;
- environment-variable parsing;
- project configuration;
- dependency injection containers;
- service registries;
- startup hooks;
- shutdown hooks;
- database lifecycle ownership;
- production database-path conventions.

The current committed adapter remains independently constructible and testable.

## 6. Database-path policy

No production database path is approved in this gate.

The repository must not contain a committed `.db`, `.sqlite`, or `.sqlite3` file.

The repository must not auto-create parent directories.

The adapter must continue rejecting unsupported path forms according to its committed contract.

A future runtime composition review must define:

- path owner;
- path source;
- path validation;
- process ownership;
- backup expectations;
- operational recovery;
- deployment-specific permissions.

None of those concerns are implemented in this gate.

## 7. Migration boundary

Only schema version `1` exists.

No migration framework is authorized.

No schema version `2` is authorized.

No automatic migration is authorized.

No compatibility downgrade is authorized.

An incompatible existing database must continue to fail closed.

## 8. Repository semantics preserved

The durable adapter must continue preserving the approved repository classifications:

```text
new_evidence
same_fact_new_acceptance
exact_replay
governance_replay
identity_collision
acceptance_collision
rejected
```

Durable persistence must not introduce:

- semantic duplicate inference;
- Evidence supersession;
- mutable factual replacement;
- Knowledge creation;
- Evidence-to-Knowledge promotion;
- Prompt Candidate creation;
- Final Prompt creation;
- business decisions.

## 9. Full-regression purpose

A full regression is required before Phase 24 closure.

The regression establishes that all committed Phase 24 contracts and adapters remain compatible with the existing repository test suite.

The regression is not an integration test against a production database.

The regression must not activate application runtime wiring.

The regression must not create a repository-managed database.

## 10. Authorized full-regression command

The next gate may execute exactly one pytest process using:

```powershell
$env:PYTHONPATH = "src"
$env:RCIS_SQLITE_TEST_ROOT = "D:\PROJECT\pytest-temp"
& "D:\PROJECT\RIE\.venv\Scripts\python.exe" `
  -m pytest `
  -q `
  -p no:cacheprovider `
  --color=no `
  --basetemp "D:\PROJECT\pytest-temp\pr-024af-full-regression" `
  tests
```

No automatic retry is allowed.

No second pytest process is allowed in the same gate.

The exact pass count is observed from the controlled run and is not guessed in advance.

## 11. Full-regression success criteria

The next gate passes only if:

- pytest exit code is `0`;
- all collected tests pass;
- failed count is `0`;
- error count is `0`;
- skipped count is `0`, unless an existing committed test explicitly defines a skip and the gate records it for independent review;
- pytest process count is exactly `1`;
- retry count is `0`;
- `RCIS_SQLITE_TEST_ROOT` is explicitly set to `D:\PROJECT\pytest-temp`;
- source, test, and review hashes remain unchanged;
- HEAD remains unchanged;
- local/tracking/remote Phase 24 heads remain identical;
- divergence remains `0 0`;
- working tree remains clean;
- the controlled pytest temp directory is removed;
- `D:\PROJECT\pytest-temp` is empty;
- no repository database exists;
- controlled sandbox remains empty;
- controlled PDF targets remain absent.

A skip is not automatically accepted.

Any skip requires STOP and independent review.

## 12. Failure handling

Any regression failure must stop the gate.

No automatic rerun is allowed.

No selective rerun is allowed.

No test repair is allowed inside the regression gate.

No source repair is allowed inside the regression gate.

The output must preserve:

- exact command;
- exit code;
- stdout;
- stderr;
- observed summary;
- failure stage;
- process count;
- retry count;
- final repository state when safely readable.

## 13. Test-environment boundary

The regression uses:

```text
PYTHONPATH=src
RCIS_SQLITE_TEST_ROOT=D:\PROJECT\pytest-temp
cache provider disabled
controlled basetemp under D:\PROJECT\pytest-temp
```

The known inaccessible repository `.pytest_cache` path remains untouched.

The gate must not attempt to clean, chmod, delete, or repair `.pytest_cache`.

The gate must not use the repository root as pytest basetemp.

## 14. Database cleanup boundary

The full regression must not create a database under the repository.

Temporary SQLite files created by tests must remain under controlled test temporary directories.

The controlled basetemp must be removed after pytest exits.

Cleanup is not a retry.

Cleanup must not alter committed repository content.

If controlled cleanup fails, the gate stops.

## 15. Git boundary

The full-regression gate is read-only with respect to Git history.

It must not:

- stage;
- commit;
- push;
- fetch;
- merge;
- tag;
- create a branch;
- delete a branch;
- reset;
- rebase;
- amend;
- rewrite history.

## 16. Deferred integration work

Application composition remains deferred beyond the full regression.

A future integration review would need direct evidence of:

- the actual composition root;
- current repository construction sites;
- lifecycle ownership;
- configuration ownership;
- database-path ownership;
- explicit operator choice between memory and SQLite.

No such integration change is assumed here.

## 17. Phase 24 closure dependency

Phase 24 closure remains blocked until:

1. one controlled full regression passes;
2. the full-regression output is independently reviewed;
3. a regression result review is committed;
4. Phase 24 closure review passes;
5. Phase 24 is fast-forward merged to `main`;
6. local `main`, `origin/main`, and remote `main` are identical;
7. the official Phase 24 annotated tag is created and pushed;
8. local and remote tag objects and peeled targets are verified;
9. the working tree is clean;
10. the office-PC continuity handoff is complete.

## 18. Office-PC continuity requirement

Before stopping work on this PC, the final handoff must record:

- repository path;
- final branch;
- final Phase 24 commit;
- final `main` commit;
- official Phase 24 tag;
- local tag object;
- remote tag object;
- peeled tag target;
- regression result;
- divergence;
- working-tree status;
- exact office-PC commands.

Required office-PC commands include:

```powershell
git fetch --prune --tags
git checkout main
git pull --ff-only origin main
```

The office PC must then verify the expected HEAD, tag target, divergence `0 0`, and clean status.

## 19. Decision

# DURABLE ADAPTER ACCEPTED AS EXPLICIT OPT-IN INFRASTRUCTURE; RUNTIME INTEGRATION DEFERRED; ONE CONTROLLED FULL REGRESSION AUTHORIZED

## 20. Exact next gate

**PR-024AF — Phase 24 Controlled Full Regression Execution**
