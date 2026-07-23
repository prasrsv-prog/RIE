# PR-057G - Operator Handoff and Rollback Requirements Review

## Status

- Review result: `PASSED`
- Gate 11: `CLOSED`
- Gate 12 review boundary: `ACTIVE`
- Operator handoff requirements defined: `True`
- Rollback requirements defined: `True`
- Operator handoff executed by this review: `False`
- Installation authorized by this review: `False`
- Merge authorized by this review: `False`
- Tag creation authorized by this review: `False`
- RIE Core v1 release authorized by this review: `False`
- Real RSV asset use authorized: `False`

## Repository checkpoint

- Repository: `D:\PROJECT\RIE`
- Active branch: `phase-056-end-to-end-cli-audit-packaging-release`
- Reviewed commit: `74490f47dbe25e5cde9de565575bf2972ece49be`
- Parent: `e3b77a047d15b93d4c5c7778d90168b7883f9610`
- Subject: `docs: review RIE Core v1 release artifact provenance`
- Local `main`: `b348506541584d3b420a59af167a957834744801`
- Phase/origin divergence: `0 0`
- Main/phase divergence: `0 11`

## Review purpose

This review defines the minimum operator handoff, verification, failure-preservation, support, and rollback requirements for a later RIE Core v1 release.

It does not install the package, recover or rebuild a wheel, merge to `main`, create a tag, publish a release, execute a controlled PDF pilot, or authorize real RSV asset use.

## Handoff package requirements

A release handoff is incomplete unless it identifies and preserves:

1. product label `RIE Core v1`;
2. Python package `rie` version `0.1.0`;
3. release source commit and published `main` commit;
4. annotated tag name, tag object, and peeled target;
5. release wheel filename `rie-0.1.0-py3-none-any.whl`;
6. wheel SHA-256 `7a276511d4bbc4cbdbcba32d459ae8f7cb106f1423832be65945d2f5a8226362`;
7. wheel byte size `301685`;
8. runtime dependency identity `pypdf 6.14.2`;
9. accepted fresh-environment result;
10. release notes and scope exclusions;
11. operator verification commands;
12. rollback checkpoint and incident-record location.

The exact accepted RIE and pypdf wheel binaries are not currently in verified custody. A binary-install handoff therefore remains incomplete until a separately authorized artifact-availability operation succeeds.

## Operator environment boundary

The accepted environment identity is:

- Python: `3.12.10`
- pytest: `9.1.1`
- pypdf: `6.14.2`
- setuptools: `83.0.0`
- wheel: `0.47.0`

A later handoff may support a broader environment only after separate compatibility evidence is accepted.

The operator must use an isolated environment and must not install into a shared or uncontrolled production interpreter.

## Pre-install verification requirements

Before any installation, the operator must verify:

- the release source and tag identities;
- the exact artifact filename;
- SHA-256 and byte size;
- wheel metadata name and version;
- declared dependency identity;
- absence of an unreviewed replacement artifact;
- a clean and isolated target environment;
- an approved installation instruction.

If any fingerprint differs, installation must stop without substitution.

## Post-install verification requirements

A later release handoff must provide exact commands that prove:

- the installed package imports successfully;
- the installed package version matches `0.1.0`;
- the console entry point exists;
- the installed console workflow reaches the accepted help or verification boundary;
- `pypdf` imports from the isolated target;
- the runtime reports `pypdf 6.14.2`;
- no source checkout path shadows the installed package;
- no real RSV asset was processed during verification.

PR-057G defines these requirements but does not execute them.

## Operator workflow boundary

The released operator workflow remains PDF-only and governed.

The operator may not:

- process JPEG or PNG assets;
- automatically traverse neighboring asset files;
- ingest the full RSV library;
- replace an official source without explicit review;
- bypass official-source registration;
- treat prompt candidates as automatically approved creative output;
- run a real-asset pilot before separate authorization;
- alter evidence or audit outputs after generation.

## Evidence and failure preservation

For every controlled run, the operator must preserve:

- command identity;
- source identity and checksum;
- environment identity;
- output paths;
- generated evidence;
- audit output;
- final result;
- failure stage;
- any accepted warning classification.

On failure, the operator must not automatically retry, reset, clean, amend, force-push, replace the source asset, overwrite evidence, or delete diagnostic material.

## Support boundary

The initial release handoff supports only the accepted governed PDF operator workflow.

Support does not include:

- OCR feature expansion;
- JPEG or PNG extraction;
- visual product interpretation;
- ComfyUI, Stable Diffusion, or Ollama integration;
- autonomous full-library ingestion;
- unreviewed dependency upgrades;
- binary substitution;
- unsupported Python versions;
- uncontrolled network retrieval during an operator run.

## Rollback checkpoints

The required pre-release rollback references are:

- pre-merge `main`: `b348506541584d3b420a59af167a957834744801`;
- current accepted phase checkpoint at this review: `74490f47dbe25e5cde9de565575bf2972ece49be`;
- accepted release wheel identity: SHA-256 `7a276511d4bbc4cbdbcba32d459ae8f7cb106f1423832be65945d2f5a8226362`;
- accepted package version: `0.1.0`.

The final Gate 12 authorization record must replace the phase checkpoint above with the final accepted release commit before merge authorization becomes effective.

## Repository rollback policy

After a published fast-forward merge, repository rollback must use a separately reviewed forward commit or revert commit.

Rollback must not use:

- destructive reset of published history;
- force-push;
- moving or recreating a published tag;
- deletion of accepted evidence;
- silent restoration of an older binary under the same identity.

If a release is withdrawn, its tag and checksum records remain immutable and the withdrawal must be recorded separately.

## Runtime rollback policy

A runtime rollback must:

1. stop new controlled runs;
2. preserve the failed environment and evidence when safe;
3. record the installed package and dependency identities;
4. uninstall or quarantine only under an explicit rollback instruction;
5. restore a previously accepted environment only if its identities are known;
6. rerun verification without real assets;
7. require human acceptance before controlled processing resumes.

No runtime rollback is executed by PR-057G.

## Real-asset separation

Release handoff and real-asset pilot handoff are separate.

A completed RIE Core v1 release does not automatically authorize processing a real RSV PDF.

The first real-asset pilot remains limited to exactly one manually selected official RSV PDF and requires a separate authorization record.

JPEG and PNG assets remain excluded.

## Remaining release blockers

The following remain unresolved:

- exact RIE wheel custody is not verified;
- exact pypdf wheel custody is not verified;
- binary artifact publication is not authorized;
- operator handoff has not been executed;
- controlled one-PDF pilot authorization has not been published;
- final Gate 12 release authorization has not been published;
- merge, tag, and release have not been performed.

## Authorization boundary

This review authorizes only:

`pr_057h_commit_and_publish_operator_handoff_and_rollback_requirements_review`

PR-057H may stage, commit, push, and post-publish verify only this PR-057G review document.

PR-057H must not install, recover or rebuild artifacts, merge, tag, release, execute a pilot, or authorize real RSV asset use.

## Gate status

- Gate 11: closed
- Gate 12 review boundary: active
- Operator handoff requirements: defined
- Rollback requirements: defined
- Operator handoff execution: not performed
- Binary publication authorization: not granted
- Release authorization: not granted
- Merge authorization: not granted
- Tag creation authorization: not granted
- Real RSV asset use: not authorized
