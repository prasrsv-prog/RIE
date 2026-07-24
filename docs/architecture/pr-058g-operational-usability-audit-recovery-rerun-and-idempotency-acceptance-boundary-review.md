# PR-058G - Operational Usability, Audit, Recovery, Rerun, and Idempotency Acceptance Boundary Review

## Status

PROPOSED

## Identity

- Phase: 57
- PR boundary: PR-058G
- Phase branch: `phase-057-operational-activation-readiness`
- Required branch commit: `0c1c65324a7dc06123a18613d63b0a5cb594401f`
- Main checkpoint: `eeb1e2108b4dada892f360edba1450ba01d25b92`
- Accepted execution evidence review: PR-058F

## Decision

The Phase 57 synthetic operational workflow is accepted within the bounded usability, audit, recovery, rerun, and idempotency scope established below.

This acceptance does not expand authorization to real RSV assets, production activation, prompt or model execution, dependency reinstall, environment cleanup, source mutation, release mutation, or tag mutation.

## Usability acceptance

The controlled workflow is usable from a fresh external Python environment through source-module execution.

The accepted operator path uses:

- system CPython 3.12.10, 64-bit;
- external fresh environment `D:\PROJECT\RIE-PHASE57-FRESH-VENV`;
- exact runtime dependency `pypdf==6.14.2`;
- temporary `PYTHONPATH=D:\PROJECT\RIE\src`;
- controlled operator configuration under `D:\PROJECT\RIE-PHASE57-CONTROLLED-EXECUTION`;
- committed synthetic registry and PDF materialized as byte-exact raw Git blob mirrors.

The accepted sequence completed all eleven governed operations:

1. registry validation;
2. source inspection;
3. initial PDF ingestion;
4. Evidence build;
5. Evidence inspection;
6. Knowledge build;
7. Knowledge inspection;
8. Prompt Candidate build;
9. Prompt Candidate audit inspection;
10. Prompt Candidate export;
11. exact PDF ingestion rerun.

All initial operations returned `SUCCEEDED`. The exact ingestion rerun returned `REUSED_EXISTING`.

## Audit acceptance

The operator audit evidence is accepted with:

- SHA-256 `64d9715a86e675e72f2e999c727ceac4dadf6752a6811e8aa5ead4a8f29564bf`;
- 14899 bytes;
- 11 JSONL records;
- 11 unique audit IDs;
- persisted audit evidence for every governed operation.

The Prompt Candidate build audit ID is:

`43c429c55fcfbbbbe9d1f2d26cb727ea763550040dbfc1c955b9fe43e0796010`

The audit inspection operation resolved that identifier and its recorded `prompt-candidate build` command successfully.

## Recovery acceptance

The recovery boundary is accepted because each failure stopped without unsafe fallback and preserved its evidence:

1. the initial execution stopped before environment creation when the Windows working-tree PDF representation differed from the committed raw Git blob;
2. correction-1 established that the mismatch was CRLF representation only and not content mutation;
3. correction-2 created the fresh environment, then stopped before pip because of an empty-prefix-argument binding defect;
4. correction-3 invoked pip exactly once, installed `pypdf==6.14.2`, then stopped because an empty byte array could not bind to the hashing parameter;
5. correction-4 reused the preserved valid environment, invoked pip zero additional times, and completed the workflow.

No failed execution evidence was replaced. No reset, clean, automatic retry, old `.venv` fallback, or uncontrolled environment recreation occurred.

Recovery acceptance is limited to the demonstrated preserved-state continuation path. It does not claim generalized crash recovery for every failure mode.

## Rerun acceptance

The exact PDF ingestion rerun used the same:

- registry;
- source ID;
- configuration;
- controlled input PDF;
- destination artifact path.

The rerun returned `REUSED_EXISTING`.

Only one exact rerun was performed. Broader repeated-run behavior remains outside this acceptance.

## Idempotency acceptance

The reviewed ingestion artifact remained:

- SHA-256 `6ba9e7f0581f7c851054bf16d82a70ed1d023dc885239339b5a6c1d941f5dd07`;
- 864 bytes.

The artifact was unchanged after the exact rerun.

This establishes idempotency only for the accepted synthetic PDF ingestion identity and exact rerun inputs. It does not establish idempotency for modified source bytes, modified registry records, changed configuration, concurrent execution, partial audit corruption, or real assets.

## Artifact-chain acceptance

The accepted artifact chain is:

- Evidence:
  - SHA-256 `cc1fc8ad17f9c7d512c8579a308ff4670aebb3cb51afb64671a46777e62c158c`;
  - 806 bytes.
- Knowledge:
  - SHA-256 `cd4bdfb0589f5d885dd22e3655dd5c48a19d09bbadd7d12d620ed3a9d495e835`;
  - 433 bytes.
- Prompt Candidate:
  - SHA-256 `2e69ee3072ca2efdf01615c0efe2ef3fb81a847d038e6ec7d97ae501e41c4f8e`;
  - 470 bytes.
- exported Prompt Candidate:
  - SHA-256 `2e69ee3072ca2efdf01615c0efe2ef3fb81a847d038e6ec7d97ae501e41c4f8e`;
  - 470 bytes.

The exported Prompt Candidate is an exact-byte match to the source Prompt Candidate artifact.

## Repository and publication acceptance

PR-058F is published as:

- commit `0c1c65324a7dc06123a18613d63b0a5cb594401f`;
- parent `2cb27fb3b9c715d1f86491474adc3c840e892e0c`;
- subject `docs: review Phase 57 controlled execution evidence`;
- committed path `docs/architecture/pr-058f-controlled-fresh-environment-and-sample-workflow-execution-evidence-review.md`.

Local, origin-tracking, and live remote Phase 57 refs all match that commit.

The repository was clean with zero staged paths after publication. Main and the Phase 56 tag remained unchanged.

## Preserved environment boundary

The repository-local `.venv` remains:

- present;
- ignored by Git;
- unexecuted;
- uninspected through Python or pip;
- unmodified.

The external fresh environment and controlled execution root remain preserved evidence. PR-058G does not authorize their deletion, mutation, recreation, or execution.

## Residual limitations

The following limitations remain explicit:

- the dependency lock pins `pypdf==6.14.2` but does not pin the downloaded distribution artifact hash;
- the workflow used only the committed synthetic sample;
- no real RSV PDF or asset was selected, read, or inspected;
- no prompt or model execution occurred;
- no full test suite was executed during the controlled workflow;
- the RIE project was not installed as a package;
- no wheel was built;
- recovery acceptance covers only the demonstrated failure sequence;
- rerun and idempotency acceptance cover one exact synthetic ingestion rerun;
- production concurrency, partial-write recovery, audit repair, changed-input reruns, and production deployment remain unaccepted.

## Explicitly unauthorized

PR-058G does not authorize or perform:

- pip invocation;
- dependency installation;
- Python environment execution;
- RIE CLI execution;
- sample workflow rerun;
- cleanup of failed or successful evidence;
- use of the repository-local `.venv`;
- real RSV asset use;
- official-source registry mutation;
- prompt or model execution;
- source-code modification;
- test execution;
- commit or push;
- merge to main;
- hosted-release mutation;
- tag creation, movement, replacement, or deletion;
- reset, clean, amend, rebase, cherry-pick, squash, or force-push.

## Acceptance boundary

PR-058G materialization is accepted only when:

- the PR-058F publication report matches its exact raw-byte and semantic contract;
- PR-058F commit identity, parent, subject, path, and committed document fingerprint match;
- local, origin, and live Phase 57 refs match;
- main and the Phase 56 tag remain unchanged;
- controlled configuration, audit, ingestion, Evidence, Knowledge, Prompt Candidate, and exported Prompt Candidate fingerprints match;
- audit record count and unique audit ID count both equal 11;
- the exact rerun status is `REUSED_EXISTING`;
- the ingestion artifact remains unchanged;
- the exported Prompt Candidate remains an exact-byte match;
- this document is the only new working-tree path;
- staged path count remains zero;
- no environment, execution evidence, source, registry, release, or tag mutation occurs;
- the report contains exactly one `FINAL_RESULT=PASSED`.

## Next operation after independent acceptance

After PR-058G materialization acceptance:

1. manually stage only this document;
2. manually commit with subject:
   `docs: accept Phase 57 operational workflow boundary`;
3. manually push the Phase 57 branch;
4. independently verify publication;
5. prepare PR-058H Phase 57 closure review without production activation or cleanup.
