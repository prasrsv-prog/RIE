# PR-015B — Evidence Workflow Gate Integration Contract Review.md

## Status

Architecture Review Only

## Context

Current safe checkpoint:

```text
v0.15.0-rcis-evidence-workflow-gate-boundary
3366ff0 merge: pr-015a evidence workflow gate boundary
```

The project currently has the following governance path:

```text
OfficialSource
    ↓
EvidenceEligibilityPolicy
    ↓
EvidenceEligibilityDecision
    ↓
EvidenceEligibilityGate
    ↓
EvidenceEligibilityGateResult
    ↓
EvidenceWorkflowGate
    ↓
EvidenceWorkflowGateResult
```

PR-015A introduced `EvidenceWorkflowGate` as a governance boundary. It does not yet integrate with evidence collectors, evidence builders, extraction CLIs, real assets, PDF parsing, image parsing, knowledge creation, product knowledge, prompt candidates, or AI.

PR-015B reviews the safest contract for future integration between the evidence workflow and the workflow gate.

## Review Objective

Define how the evidence workflow may safely use `EvidenceWorkflowGate` without crossing into unsafe behavior.

This review does not implement integration.

## Current Evidence Workflow

The current evidence workflow has two primary evidence collection paths.

### Text Extraction Evidence

```text
TextAssetExtractionReport
    ↓
TextExtractionEvidenceCollector.collect(report)
    ↓
TextExtractionEvidenceBuilder.build(extraction)
    ↓
TextExtractionEvidenceCollection
```

Relevant files:

```text
src/collection/text_extraction_evidence_collector.py
src/evidence/text_extraction_evidence_builder.py
src/rie/extraction/export_text_extraction_evidence.py
```

### PDF Text Extraction Evidence

```text
PDF text extraction artifact
    ↓
PdfTextExtractionEvidenceCollector.collect(artifact)
    ↓
PdfTextExtractionEvidenceBuilder.build(page_extraction_record, evidence_index)
    ↓
PdfTextExtractionEvidenceCollection
```

Relevant files:

```text
src/collection/pdf_text_extraction_evidence_collector.py
src/evidence/pdf_text_extraction_evidence_builder.py
src/rie/extraction/export_pdf_text_evidence.py
```

## Key Finding

The safest integration point is before `collector.collect(...)`.

The evidence builders are not the correct place for governance checks. Builders should remain focused on creating evidence objects from already-accepted records.

The collectors are closer to the workflow boundary, but changing collectors directly would require changing their existing call sites and test expectations.

Therefore, the safest future integration contract is a preflight boundary that runs before evidence collection.

## Integration Contract Decision

Future evidence workflow integration should follow this shape:

```text
EvidenceWorkflowGateResult
    ↓
Evidence workflow preflight
    ↓
allowed: collector.collect(...)
blocked: return blocked workflow result without collecting evidence
```

The preflight layer may decide whether evidence collection is allowed, but it must not create evidence itself.

## Approved Integration Rule

Future integration must happen before:

```text
TextExtractionEvidenceCollector.collect(report)
PdfTextExtractionEvidenceCollector.collect(artifact)
```

The gate must not be inserted inside:

```text
TextExtractionEvidenceBuilder.build(...)
PdfTextExtractionEvidenceBuilder.build(...)
```

## Responsibilities

### EvidenceWorkflowGate

Responsible for:

```text
- accepting EvidenceEligibilityGateResult
- producing EvidenceWorkflowGateResult
- preserving source_id
- preserving requires_review
- preserving reason
- deciding whether the evidence workflow is allowed
```

Not responsible for:

```text
- reading files
- reading source_path
- parsing PDFs
- parsing images
- loading registries
- creating evidence
- creating knowledge
- creating product knowledge
- creating prompt candidates
- calling AI
```

### Future Evidence Workflow Preflight

Responsible for:

```text
- accepting EvidenceWorkflowGateResult
- allowing or blocking evidence collection
- returning a workflow-level decision
```

Not responsible for:

```text
- modifying source files
- mutating assets
- parsing source documents
- inferring product knowledge
- creating prompt candidates
- calling AI
```

### Evidence Collectors

Current responsibility remains:

```text
- collect valid extraction records into evidence collections
```

Collectors should not yet be modified in PR-015B.

Future collector integration may be considered only after a preflight contract exists.

### Evidence Builders

Builders must remain pure evidence constructors.

They should not know about:

```text
- OfficialSource
- EvidenceEligibilityDecision
- EvidenceEligibilityGateResult
- EvidenceWorkflowGateResult
- registry files
- authority status
- lifecycle status
- source document eligibility
```

## Blocked Behavior

If `EvidenceWorkflowGateResult.workflow_allowed` is false, future integration must block evidence collection.

Normal blocked decisions should return a blocked result, not raise exceptions.

Examples of blocked cases:

```text
- requires_review is true
- allowed is false
- evidence eligibility is unknown
- evidence eligibility is not eligible
```

## Allowed Behavior

If `EvidenceWorkflowGateResult.workflow_allowed` is true and `requires_review` is false, future integration may allow evidence collection to proceed.

However, allowing evidence collection does not mean:

```text
- creating Official Knowledge
- creating Product Knowledge
- creating Prompt Candidate
- accepting source_path as truth
- reading real assets without sandbox rules
```

## Real Asset Boundary

PR-015B does not approve real asset testing.

Real asset testing is deferred to the Jalur B sequence:

```text
PR-016 — Real Asset Sandbox / Dry-Run Foundation
PR-017 — Controlled Real Asset Evidence Smoke Test
```

After Jalur B is complete, controlled tests may use:

```text
- one product specification PDF
- one to three product photos
- sandbox copy only
- read-only mode
```

Real asset tests must not use the original production asset library directly.

## Forbidden Scope for PR-015B

PR-015B must not:

```text
- modify src/evidence/*
- modify src/collection/*
- modify src/rie/extraction/*
- modify src/knowledge/*
- modify configs
- modify examples
- modify locked / SSOT documents
- read source documents
- read real asset files
- parse PDFs
- parse images
- create Evidence
- create Official Knowledge
- create Product Knowledge
- create Prompt Candidate
- create Final Prompt
- call AI
- mutate files
- move files
- rename files
- delete files
- add dashboard or API work
- add default registry loading
```

## Proposed PR-015C Direction

PR-015C may implement a small preflight skeleton.

Possible future scope:

```text
src/official_source/official_source_evidence_workflow_preflight.py
tests/test_official_source_evidence_workflow_preflight.py
```

Possible concepts:

```text
EvidenceWorkflowPreflightResult
EvidenceWorkflowPreflight
```

The preflight should accept `EvidenceWorkflowGateResult` only.

It should not accept:

```text
- OfficialSource
- source_path
- asset path
- PDF artifact
- image artifact
- extraction report
- evidence collection
```

PR-015C should still avoid modifying evidence collectors and extraction CLIs unless a separate review explicitly approves that integration.

## Decision

PR-015B confirms the integration contract:

```text
EvidenceWorkflowGate must protect the evidence workflow before collector.collect(...).
```

No implementation is approved in PR-015B.

The recommended next step is:

```text
PR-015C — Evidence Workflow Preflight Skeleton
```

PR-015C should remain under `src/official_source` and should not touch evidence collectors, evidence builders, extraction CLIs, real assets, PDFs, images, knowledge, prompt, product knowledge, AI, dashboard, or API work.
