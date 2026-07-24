# PR-058B - Fresh-Environment Installation and Configuration Contract Review

## Status

PROPOSED

## Identity

- Phase: 57
- PR boundary: PR-058B
- Phase branch: `phase-057-operational-activation-readiness`
- Required branch commit: `53ae8b486da7dc8add93b07b648bbb30e359aced`
- Required commit parent: `eeb1e2108b4dada892f360edba1450ba01d25b92`
- Required commit subject: `docs: define Phase 57 operational activation boundary`
- Phase 56 release mode: `SOURCE_AND_GOVERNANCE_WITHOUT_BINARY_ATTACHMENT`

## Decision

Phase 57 will use a source-tree module execution boundary for its controlled operational activation.

The authorized later execution shape is:

1. use the exact reviewed Phase 57 branch state;
2. create a repository-local `.venv`;
3. use an explicitly selected local CPython interpreter satisfying Python 3.12 or later;
4. install only the exact runtime dependency recorded in `requirements-lock.txt`;
5. do not install the RIE project as a wheel or editable package;
6. invoke the public module entry point through `.venv\Scripts\python.exe -m rie`;
7. use an explicit configuration JSON;
8. use only committed sample materials after a separate execution authorization.

PR-058B performs no environment creation, dependency installation, package build, project installation, CLI execution, sample workflow execution, or real-asset use.

## Reviewed installation inputs

### `pyproject.toml`

Required raw-byte identity:

- SHA-256: `d5d8f2280f60343f30d476ed87972f10af73813a8d3206a8f7920a8f9ac0102c`
- bytes: `564`
- LF: `36`
- CR: `0`
- BOM: absent
- ASCII-only: true
- exactly one final LF: true

Relevant contract:

- project name: `rie`;
- project version: `0.1.0`;
- required Python: `>=3.12`;
- declared runtime dependency: `pypdf`;
- console script: `rie = rie.operator.operator_cli:main`;
- build backend: `setuptools.build_meta`;
- build requirements: `setuptools>=68` and `wheel`.

### `requirements-lock.txt`

Required raw-byte identity:

- SHA-256: `9d411c7864dd14f54ae9c2aa0f1806c9c7a94d352d7c0c9b450cfecf01bbb8bc`
- bytes: `14`
- LF: `1`
- exact content: `pypdf==6.14.2`.

### Operator installation documentation

`docs/operator/installation-and-configuration.md`:

- SHA-256: `ec24325b685b99c384914476aeabf42b496a55175d864f2ad04e68a19bf3c88e`;
- bytes: `717`;
- LF: `20`.

It defines Python 3.12 or later, the `rie` operator command, and the exact configuration fields.

### Fresh-environment acceptance documentation

`docs/operator/fresh-environment-acceptance.md`:

- SHA-256: `1af9ff1134e7f6a296fad465af7449d85b28fc5981f04a116f65c9c7d901fa07`;
- bytes: `701`;
- LF: `15`.

It records the historical accepted wheel-based fresh-environment method. That historical method remains evidence, but the current source-and-governance release does not include a wheel attachment or installation claim.

## Installation mode decision

Selected Phase 57 activation mode:

`REPOSITORY_LOCAL_VENV_WITH_LOCKED_RUNTIME_DEPENDENCY_AND_SOURCE_MODULE_EXECUTION`

This mode is selected because:

- the release intentionally has no binary attachment;
- the release does not make a binary installation claim;
- the runtime dependency is pinned exactly;
- `python -m rie` is a committed public entry point;
- source module execution avoids silently rebuilding or substituting an unavailable release wheel;
- no project build dependency needs to be resolved during operational activation.

This decision does not invalidate historical wheel acceptance evidence. It defines the controlled operational path for the current source-only release mode.

## Interpreter boundary

A later execution authorization must:

- locate an already installed local CPython interpreter;
- require version `3.12` or later;
- record the complete `sys.version`;
- record the executable path;
- record the interpreter architecture;
- reject unsupported implementations or versions;
- not download or install Python automatically;
- not modify system-wide Python registration;
- not require administrator privileges;
- not change the selected interpreter after evidence begins.

PR-058B does not claim that every future Python version has been acceptance-tested. The exact interpreter selected for execution must be captured in the execution report.

## Virtual-environment boundary

The authorized environment path for later execution is:

`D:\PROJECT\RIE\.venv`

A later execution must:

- require that the active repository and Phase 57 commit are exact;
- require that `.venv` is absent before fresh creation;
- stop if `.venv` already exists;
- create it using the selected interpreter and standard `venv`;
- use only executables inside `.venv` after creation;
- not activate or mutate any global environment;
- not copy an environment from another computer;
- not commit or stage `.venv`;
- preserve failure evidence if creation fails;
- not automatically delete or recreate a failed environment.

Deletion or replacement of an existing `.venv` is not authorized by this review.

## Runtime dependency installation boundary

The only authorized runtime dependency input is:

`requirements-lock.txt`

The only authorized package version is:

`pypdf==6.14.2`

A later execution authorization must freeze an exact pip command and must require:

- `.venv\Scripts\python.exe -m pip`;
- no dependency upgrade;
- no use of `pyproject.toml` dependency resolution for installation;
- no editable installation;
- no project wheel installation;
- no source distribution installation;
- no unreviewed requirements file;
- no global package installation;
- no cache substitution claim;
- explicit capture of the installed `pypdf` version;
- explicit capture of `pip freeze`;
- stop on dependency resolution or installation failure;
- no automatic retry.

Network access to the configured Python package index may be separately authorized only for retrieval of the exact pinned dependency. PR-058B does not perform or authorize that network request now.

## Project execution boundary

The RIE project itself will not be installed during Phase 57 activation.

A later execution will invoke:

`D:\PROJECT\RIE\.venv\Scripts\python.exe -m rie`

from the repository root.

This requires the committed source tree and does not create a substituted wheel.

The following remain unauthorized:

- `pip install .`;
- `pip install -e .`;
- local wheel build;
- source distribution build;
- build isolation;
- package upload;
- release asset upload;
- use of the historical wheel as though it were currently available.

## Build-system boundary

`pyproject.toml` specifies `setuptools>=68` and `wheel` without exact versions.

Therefore PR-058B does not authorize a new wheel build. A later wheel build would require a separate review that freezes exact build-tool versions, build isolation, artifact provenance, artifact fingerprint, and custody.

Operational activation does not require that build.

## Configuration contract

Every non-help command requires an explicit configuration path.

The configuration JSON must contain exactly:

- `schema_version`;
- `workspace_path`;
- `audit_path`.

Required schema value:

`rie_operator_configuration_v1`

A later execution authorization must define a fresh controlled configuration and must require:

- an explicit absolute or configuration-relative workspace path;
- an explicit JSONL audit path;
- both paths inside the authorized Phase 57 sandbox;
- no credentials or secrets;
- no path to a real RSV asset;
- no production workspace;
- no production audit log;
- no mutation of committed sample files;
- configuration identity and digest capture.

PR-058B does not create the configuration file.

## Freshness and isolation boundary

A later activation execution must begin from:

- exact Phase 57 branch and commit;
- clean working tree;
- staged path count zero;
- no pre-existing `.venv`;
- no pre-existing authorized output sandbox;
- no remote, tag, or hosted-release mutation.

The execution must not rely on an existing environment, an existing generated artifact, or an unverified package cache as acceptance evidence.

## Failure boundary

If interpreter discovery, environment creation, dependency installation, configuration validation, or CLI startup fails:

1. preserve the report;
2. preserve the environment state;
3. do not retry automatically;
4. do not delete `.venv`;
5. do not install an alternative package version;
6. do not switch interpreter;
7. do not patch source code;
8. do not use global packages;
9. classify the failure in a separate review.

## Explicitly unauthorized now

PR-058B does not authorize or perform:

- virtual-environment creation;
- pip invocation;
- dependency installation;
- project installation;
- wheel build;
- CLI invocation;
- committed sample workflow execution;
- test-suite execution;
- acceptance rerun;
- real RSV PDF selection;
- real RSV asset reading or inspection;
- registry mutation;
- pilot execution;
- source-code modification;
- release mutation;
- tag mutation;
- force-push;
- reset or clean.

## PR-058B acceptance boundary

PR-058B is accepted only when:

- PR-058A commit publication is independently accepted;
- the Phase 57 local, origin, and live remote refs match;
- `main` remains at the Phase 56 release commit;
- all reviewed installation inputs match their exact raw-byte identities;
- this document is the only new working-tree path;
- nothing is staged;
- no environment or package operation is performed;
- no sample or real asset is processed;
- the report ends with exactly one `FINAL_RESULT=PASSED`.

## Next operation after independent acceptance

After PR-058B materialization acceptance:

1. manually stage only this document;
2. manually commit with:
   `docs: define Phase 57 installation and configuration contract`;
3. manually push the Phase 57 branch;
4. independently verify the commit publication;
5. begin PR-058C to authorize exact environment creation, dependency installation, configuration materialization, and committed sample workflow execution.
