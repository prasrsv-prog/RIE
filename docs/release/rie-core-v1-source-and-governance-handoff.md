# RIE Core v1 - Source and Governance Handoff

## Handoff status

- Handoff type: `PRE_RELEASE_CANDIDATE`
- Product label: `RIE Core v1`
- Release title: `RIE Core v1 - Governed PDF Operator Workflow`
- Release mode: `SOURCE_AND_GOVERNANCE_WITHOUT_BINARY_ATTACHMENT`
- Binary wheel attached: `False`
- Dependency wheel attached: `False`
- Installation claim included: `False`
- Release authorized: `False`
- Real RSV asset use authorized: `False`

## Current candidate checkpoint

- Repository: `D:\PROJECT\RIE`
- Candidate phase branch: `phase-056-end-to-end-cli-audit-packaging-release`
- Current candidate phase commit: `90e769029bf55482edb3169ae3ec9895b79126f8`
- Current local `main`: `b348506541584d3b420a59af167a957834744801`
- Candidate annotated tag: `v0.56.0-rcis-end-to-end-cli-audit-packaging-release-phase`

The current candidate phase commit is not yet the final release commit.

The final release commit, final `main` commit, annotated tag object, and peeled tag target must be filled only by a later authorized release operation.

## Included handoff scope

This handoff candidate covers:

- repository source state after final authorization;
- committed architecture and governance records;
- committed governed PDF operator-workflow documentation;
- source-and-governance release notes;
- repository identity verification commands;
- support boundary;
- rollback and withdrawal boundary;
- real-asset pilot separation.

This handoff candidate does not include installation instructions or runtime execution instructions.

## Excluded artifacts

The following are not release attachments:

- `rie-0.1.0-py3-none-any.whl`;
- `pypdf-6.14.2-py3-none-any.whl`;
- any source distribution archive;
- any rebuilt, rematerialized, copied, or substituted wheel;
- any virtual environment;
- any wheelhouse or cache;
- any acceptance sandbox;
- any real RSV PDF, JPEG, PNG, extracted knowledge, prompt candidate, or pilot output.

The release attachment inventory is empty.

## Historical artifact evidence

The accepted historical RIE wheel identity is:

- filename: `rie-0.1.0-py3-none-any.whl`;
- SHA-256: `7a276511d4bbc4cbdbcba32d459ae8f7cb106f1423832be65945d2f5a8226362`;
- bytes: `301685`.

The accepted historical pypdf wheel identity is:

- filename: `pypdf-6.14.2-py3-none-any.whl`;
- SHA-256: `3f07891af76dc002657e04993ab9b4de81de29f9013b9761d0b7968bff12e946`;
- bytes: `349514`.

These identities are provenance references only.

They do not represent current binary custody, release attachment availability, or an installation promise.

## Operator verification boundary

After a separately authorized merge and tag operation, the operator must verify repository identities only.

The final handoff must provide exact resolved values for:

- final release commit;
- live remote `main` commit;
- annotated tag object;
- peeled tag target;
- release-note Git blob identity;
- handoff Git blob identity;
- clean repository status;
- empty binary attachment inventory.

The verification must not execute package installation or process real assets.

## Repository verification command template

The following command categories are permitted only after final values are resolved:

```powershell
git -C D:\PROJECT\RIE rev-parse refs/heads/main
git -C D:\PROJECT\RIE ls-remote origin refs/heads/main
git -C D:\PROJECT\RIE rev-parse <FINAL_TAG_NAME>
git -C D:\PROJECT\RIE rev-parse <FINAL_TAG_NAME>^{}
git -C D:\PROJECT\RIE status --porcelain=v1 --untracked-files=all
```

The placeholders must not be executed as literal values.

No installation command belongs in this handoff.

## Support boundary

The release supports the governed repository source and documentation boundary for the accepted PDF workflow.

The release does not claim support for:

- binary installation;
- offline installation;
- dependency artifact delivery;
- unsupported Python versions;
- OCR expansion;
- JPEG or PNG extraction;
- automated full-library ingestion;
- local AI generator integration;
- production deployment;
- external publication;
- real RSV asset processing without separate authorization.

## Rollback and withdrawal

Published repository history must not be reset or force-pushed.

A repository correction must use a separately reviewed forward commit or revert commit.

A published annotated tag must not be moved, recreated, or silently repointed.

A release withdrawal must preserve:

- tag identity;
- release notes;
- governance decision records;
- historical artifact references;
- withdrawal reason;
- corrective next step.

Because no binary is attached, binary rollback is outside this release mode.

## Real-asset pilot separation

This handoff does not authorize selecting, copying, hashing, opening, registering, ingesting, or processing a real RSV PDF.

The first real-asset pilot requires a separate committed authorization record after release publication.

JPEG and PNG assets remain excluded.

## Finalization requirements

Before this handoff can become final:

- this handoff candidate and the release notes must be reviewed and committed;
- an updated readiness review must pass for the selected release mode;
- a final Gate 12 release authorization record must be committed and published;
- the final release commit must be identified;
- fast-forward merge must be separately authorized and verified;
- the annotated tag must be separately authorized, created, pushed, and verified;
- the final resolved identities must be recorded.

Until then, this document remains a pre-release handoff candidate.
