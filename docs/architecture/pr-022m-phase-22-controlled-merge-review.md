# PR-022M — Phase 22 Controlled Merge Review

## Status

PASSED — documentation-only controlled merge review.

## Current checkpoint

- Branch: `phase-022-evidence-candidate-boundary-review`
- Local and remote Phase 22 HEAD: `1fa03ca`
- Phase divergence: `0 0`
- Local main and origin/main: `3642955`
- Main divergence: `0 0`
- Repository before review: clean

## Purpose

This review defines the exact fast-forward integration policy for Phase 22, the required preflight and post-merge verification, branch-preservation rules, stop and recovery boundaries, and the official Phase 22 tag proposal.

PR-022M does not merge, switch branches, push main, create a tag, delete a branch, run tests, invoke the interpreter, or modify source and tests.

## Reviewed Phase 22 chain

| Gate | Commit | Parent | Role |
|---|---:|---:|---|
| PR-022A | `6a3ea85` | `3642955` | Architecture review |
| PR-022B | `0f683a3` | `6a3ea85` | Contract review |
| PR-022C | `cada6a1` | `0f683a3` | Implementation review |
| PR-022D | `a79713a` | `cada6a1` | EvidenceCandidate implementation |
| PR-022E | `00525b9` | `a79713a` | Implementation result review |
| PR-022F | `93966f6` | `00525b9` | Regression execution review |
| PR-022H | `2ae6b5a` | `93966f6` | Failed execution review |
| PR-022I | `bf6f0ef` | `2ae6b5a` | Revised execution review |
| PR-022K | `ac58c2f` | `bf6f0ef` | Revised execution result review |
| PR-022L | `1fa03ca` | `ac58c2f` | Phase closure review |

PR-022G and PR-022J were execution-only gates and intentionally have no repository commit.

## Merge feasibility assessment

At the PR-022L checkpoint:

- main is an ancestor of the Phase 22 branch;
- the Phase 22 branch is exactly ten commits ahead of main;
- there are zero merge commits in `main..phase-022-evidence-candidate-boundary-review`;
- the branch can be integrated using a strict fast-forward;
- no conflict resolution, rebase, squash, cherry-pick, or merge commit is required.

After PR-022M is committed, the future merge candidate is expected to be eleven commits ahead of main. The future execution must use the committed PR-022M hash as the exact phase HEAD.

## Approved integration strategy

The only approved integration operation is:

```powershell
git merge --ff-only phase-022-evidence-candidate-boundary-review
```

Prohibited alternatives:

- non-fast-forward merge;
- merge commit creation;
- squash merge;
- rebase;
- cherry-pick integration;
- force push;
- manual commit rewriting;
- amendment of any Phase 22 commit.

## Future PR-022N preflight

Before switching to main or performing a merge, PR-022N must:

1. Start on `phase-022-evidence-candidate-boundary-review`.
2. Verify the repository is clean.
3. Fetch origin and tags read-only.
4. Verify local and remote phase heads equal the committed PR-022M hash.
5. Verify local main and origin/main still equal `3642955`.
6. Verify both divergences are `0 0`.
7. Verify main remains an ancestor of the phase branch.
8. Verify `main..phase` contains exactly eleven commits.
9. Verify the Phase 22 range still contains zero merge commits.
10. Verify the proposed official tag is absent locally and remotely.
11. Verify all preserved external evidence outputs remain present.
12. Verify the retained parent temp directory exists and is empty.
13. Verify controlled execution children remain absent.
14. Verify the controlled sandbox remains empty.
15. Stop before merge if any precondition differs.

No failed precondition may be repaired inside PR-022N, except a read-only fetch.

## Exact controlled merge sequence

After all preflight checks pass, PR-022N may perform:

```powershell
git switch main
git merge --ff-only phase-022-evidence-candidate-boundary-review
```

Before pushing main, PR-022N must verify:

- local main equals the approved phase HEAD;
- local phase branch still equals that same HEAD;
- origin/main remains at the original pre-merge main checkpoint;
- repository status is clean;
- no merge commit was introduced.

Only after those checks pass may PR-022N execute:

```powershell
git push origin main
git fetch origin
```

Post-push verification must prove:

- local main equals origin/main;
- local main equals the phase branch HEAD;
- origin phase branch remains preserved at the same HEAD;
- main divergence is `0 0`;
- phase divergence is `0 0`;
- repository remains clean.

## Branch-preservation policy

After the controlled merge:

- keep local `phase-022-evidence-candidate-boundary-review`;
- keep remote `origin/phase-022-evidence-candidate-boundary-review`;
- do not delete either branch;
- do not rename the branch;
- do not add new commits to the phase branch during merge execution.

Branch deletion, archival, or reuse requires a separate reviewed decision.

## Official Phase 22 tag proposal

Proposed annotated tag:

`v0.22.0-rcis-evidence-candidate-boundary-phase`

Proposed annotation message:

`RCIS Phase 22 - Evidence Candidate Boundary`

Required future target:

- the verified merged main HEAD;
- the preserved Phase 22 branch HEAD;
- the committed PR-022M checkpoint.

PR-022M does not authorize creating or pushing the tag. PR-022N is merge-only and must not create the tag. Tag creation requires a separate post-merge review after main synchronization is independently verified.

## Stop and recovery boundaries

### Before local merge

Any mismatch causes an immediate stop. Do not switch branches and do not merge.

### During local merge

If `git merge --ff-only` fails:

- do not retry with a different strategy;
- do not resolve conflicts;
- do not create a merge commit;
- do not reset automatically;
- capture the state and stop for a separate recovery review.

### After local merge but before push

If verification fails:

- do not push main;
- do not create a tag;
- do not force-reset automatically;
- preserve the observed state for a separate reviewed recovery gate.

### After main push

If remote verification fails:

- do not force push;
- do not rewrite published history;
- do not delete branches or tags;
- record the inconsistency and stop for a separate recovery review.

## Evidence and boundary preservation

The following remain external and preserved:

- PR-022G failed execution output;
- PR-022H failure-review output;
- PR-022I revised-execution-review output;
- PR-022J successful regression output;
- PR-022K result-review output;
- PR-022L closure-review output.

The merge does not authorize:

- additional test execution;
- source or test modification;
- dependency or configuration modification;
- PDF access or processing;
- parser or ingestion execution;
- Evidence or EvidenceRelationship creation;
- Knowledge or Prompt Candidate creation;
- persistence;
- cleanup of `.pytest_cache`;
- cleanup of the retained parent temp directory.

## Acceptance criteria

1. **SATISFIED** — Current branch is `phase-022-evidence-candidate-boundary-review`.
2. **SATISFIED** — Local Phase 22 HEAD equals `1fa03ca`.
3. **SATISFIED** — Remote Phase 22 HEAD equals `1fa03ca`.
4. **SATISFIED** — Phase branch divergence is `0 0`.
5. **SATISFIED** — Local main equals `3642955`.
6. **SATISFIED** — origin/main equals `3642955`.
7. **SATISFIED** — Main divergence is `0 0`.
8. **SATISFIED** — Repository was clean before PR-022M creation.
9. **SATISFIED** — The Phase 22 closure review output is present and PASSED.
10. **SATISFIED** — The Phase 22 closure decision is preserved.
11. **SATISFIED** — All ten committed Phase 22 gates through PR-022L are present.
12. **SATISFIED** — All expected adjacent parent relationships are exact.
13. **SATISFIED** — PR-022G remains an execution-only gate with no repository commit.
14. **SATISFIED** — PR-022J remains an execution-only gate with no repository commit.
15. **SATISFIED** — EvidenceCandidate source remains committed.
16. **SATISFIED** — EvidenceCandidate tests remain committed.
17. **SATISFIED** — main is an ancestor of the Phase 22 branch.
18. **SATISFIED** — The current phase branch is ten commits ahead of main.
19. **SATISFIED** — There are no merge commits in the current Phase 22 range.
20. **SATISFIED** — Fast-forward merge feasibility is established.
21. **SATISFIED** — Only `git merge --ff-only` is approved.
22. **SATISFIED** — A merge commit is prohibited.
23. **SATISFIED** — Squash merge is prohibited.
24. **SATISFIED** — Rebase is prohibited.
25. **SATISFIED** — Cherry-pick integration is prohibited.
26. **SATISFIED** — Force push is prohibited.
27. **SATISFIED** — The future execution must begin from the committed PR-022M checkpoint.
28. **SATISFIED** — The future phase HEAD must be synchronized with origin.
29. **SATISFIED** — The future main HEAD must be synchronized with origin.
30. **SATISFIED** — The future repository must be clean.
31. **SATISFIED** — Future execution must fetch origin before final preflight.
32. **SATISFIED** — Future execution must verify main is still an ancestor of phase.
33. **SATISFIED** — Future execution must verify no unexpected merge commits.
34. **SATISFIED** — Future execution must verify the proposed tag is absent locally.
35. **SATISFIED** — Future execution must verify the proposed tag is absent remotely.
36. **SATISFIED** — Future execution must switch to main only after all preflight checks pass.
37. **SATISFIED** — Future execution must fast-forward local main to the phase HEAD.
38. **SATISFIED** — Future execution must verify local main equals phase HEAD before push.
39. **SATISFIED** — Future execution must push main without force.
40. **SATISFIED** — Future execution must verify origin/main equals the phase HEAD.
41. **SATISFIED** — The Phase 22 branch must be preserved locally after merge.
42. **SATISFIED** — The Phase 22 branch must be preserved remotely after merge.
43. **SATISFIED** — The Phase 22 branch must not be deleted automatically.
44. **SATISFIED** — The official Phase 22 tag proposal is defined exactly once.
45. **SATISFIED** — The proposed tag is annotated.
46. **SATISFIED** — The proposed tag target is the verified merged main HEAD.
47. **SATISFIED** — Tag creation is not authorized by PR-022M.
48. **SATISFIED** — Tag creation is not authorized by the next merge-execution gate.
49. **SATISFIED** — Tag creation requires a separate post-merge review.
50. **SATISFIED** — Pre-push verification failure requires an immediate stop without push.
51. **SATISFIED** — A failed local merge must not be repaired automatically.
52. **SATISFIED** — A post-push inconsistency must not be corrected with history rewrite.
53. **SATISFIED** — Rollback or recovery requires a separate reviewed gate.
54. **SATISFIED** — PR-022G failed evidence remains preserved.
55. **SATISFIED** — PR-022J successful evidence remains preserved.
56. **SATISFIED** — The retained parent temp directory exists and remains empty.
57. **SATISFIED** — Controlled execution children remain absent.
58. **SATISFIED** — The controlled sandbox remains empty.
59. **SATISFIED** — No PDF, parser, ingestion, Evidence, Knowledge, or persistence action is authorized.
60. **SATISFIED** — Exactly one next controlled merge-execution gate is recommended.

## Controlled merge review decision

**READY FOR PHASE 22 CONTROLLED MERGE EXECUTION**

## Recommended PR-022N

**PR-022N — Phase 22 Controlled Merge Execution**

PR-022N may perform only the reviewed fetch, exact preflight, strict fast-forward merge, main push, and post-push verification. It must not run tests, create a tag, delete branches, modify source or tests, or perform recovery actions.
