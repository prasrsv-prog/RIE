# PR-012 Official Source Registry / Document Classification Architecture Review

## Status

PR-012 is a review-only architecture step.

No production implementation is approved in PR-012. This document does not create
domain models, registry data files, CLI commands, tests, evidence extraction,
knowledge conversion, or source document mutations.

## Context

RIE has completed the Official Knowledge Foundation and the Official Knowledge
CLI Foundation.

The current safe Official Knowledge flow is:

```text
curated official knowledge source JSON
  |
  v
python -m rie.knowledge.export_official_knowledge <input_json> --output <output_json>
  |
  v
official knowledge artifact JSON
  |
  v
python -m rie.knowledge.inspect_official_knowledge <artifact_json>
  |
  v
valid inspection result
```

The next required layer is a controlled Official Source Registry / document
classification boundary before source documents are allowed to participate in
evidence or Official Knowledge workflows.

## Problem Statement

RIE needs a safe way to answer these questions before using a source document:

- What is this source?
- Is this source recognized?
- What document category is it?
- What authority level does it have?
- What lifecycle state does it have?
- Is it eligible to become an evidence source?

Without this boundary, downstream workflows risk treating a file extension,
filename, folder location, or lifecycle word as proof of authority.

## Scope

PR-012 reviews the architecture for:

- Official Source Registry architecture
- document classification boundary
- authority status boundary
- lifecycle status boundary
- evidence eligibility boundary
- manual-first source declaration
- traceability requirements
- risks and open questions

## Non-Scope

PR-012 explicitly excludes:

- Product Knowledge
- Prompt Candidate
- Final Prompt
- PDF-to-Official-Knowledge automatic conversion
- AI-based classification
- AI inference
- evidence extraction implementation
- registry implementation
- CLI implementation
- tests

## Core Principle

Official Source Registry is a governance layer, not an extraction layer.

It may determine whether a source is eligible for downstream workflows, but it
must not extract evidence, create knowledge, generate prompts, or mutate source
documents.

## Conceptual Flow

```text
Document / File
  |
  v
Official Source Registry
  |
  v
Document Classification
  |
  v
Evidence Eligibility
  |
  v
Evidence Workflow
  |
  v
Official Knowledge Workflow
```

This flow is conceptual only. PR-012 does not implement any of these stages.

## Proposed Domain Concepts

These concepts are proposed for review only. They are not implementation
contracts in PR-012.

### OfficialSource

An `OfficialSource` would represent a governed source declaration.

Conceptual fields:

- `source_id`
- `source_path`
- `source_type`
- `document_classification`
- `authority_status`
- `lifecycle_status`
- `evidence_eligibility`
- `version`
- review metadata / notes

### SourceType

`SourceType` describes the technical or container form of the source. It does
not establish authority.

Example values:

- `PDF`
- `MARKDOWN`
- `DOCX`
- `IMAGE`
- `SPREADSHEET`
- `DIRECTORY`
- `UNKNOWN`

### DocumentClassification

`DocumentClassification` describes the kind of document being registered. It is
separate from both file type and authority.

Example values:

- `OFFICIAL_KNOWLEDGE_BASE`
- `CREATIVE_LOGIC_SPECIFICATION`
- `BRAND_KNOWLEDGE_SPECIFICATION`
- `MASTER_ASSET_LIBRARY`
- `PROJECT_RULEBOOK`
- `ARCHITECTURE_BASELINE`
- `CONTINUITY_PACK`
- `PROJECT_VISION_KIT`
- `WORKING_NOTE`
- `UNKNOWN`

### AuthorityStatus

`AuthorityStatus` describes whether the source is authoritative for downstream
use.

Example values:

- `OFFICIAL`
- `SOURCE_OF_TRUTH_CANDIDATE`
- `REFERENCE`
- `DRAFT`
- `UNKNOWN`

### LifecycleStatus

`LifecycleStatus` describes the source document lifecycle. It must not be
treated as authority by itself.

Example values:

- `ACTIVE`
- `LOCKED`
- `FINAL`
- `DEPRECATED`
- `SUPERSEDED`
- `UNKNOWN`

### EvidenceEligibility

`EvidenceEligibility` describes whether a source may feed an evidence workflow.

Example values:

- `ELIGIBLE`
- `ELIGIBLE_WITH_REVIEW`
- `NOT_ELIGIBLE`
- `UNKNOWN`

## Separation Rules

- Source Type does not determine authority.
- PDF does not mean Official Knowledge.
- LOCKED does not automatically mean OFFICIAL.
- FINAL does not automatically mean SOURCE_OF_TRUTH.
- Filename matching is only a hint.
- Registry declaration / human review is authority.

## Manual-First Registry Rule

Initial registry recognition should be explicit and manual.

The first registry boundary should not use automatic AI classification,
filename-only authority, or content-based inference.

Filename matching may be useful later as a convenience hint, but it must never
replace a registry declaration or human review.

## SSOT / LOCKED Preservation

RIE must preserve all locked / SSOT documents.

During PR-012, RIE must not mutate, rewrite, normalize, replace, move, or
otherwise alter locked / SSOT documents. The registry may reference source
documents in the future, but it must not change them.

Reference set / SSOT candidate documents:

- COS-001 - Creative Logic Specification V2.0
- COS-002 - RSV Brand Knowledge Specification V1.0
- RSV Group Master Asset Library V1
- RSV Group Project Rulebook V1
- RSV COS Architecture Baseline v1.0 LOCKED
- RSV Official Knowledge Base v1.0 LOCKED

These documents remain locked / SSOT reference inputs. They are not hardcoded
into PR-012 implementation, tests, or registry data.

## Evidence Boundary

The registry may decide whether a source is eligible to become an evidence
source.

It must not:

- create Evidence objects
- create Knowledge objects
- create Product Knowledge
- create Prompt Candidates
- perform extraction
- call AI
- rewrite source content

Evidence creation remains a separate downstream workflow.

## Official Knowledge Boundary

Official Knowledge remains separate from TextKnowledge, PDF Text Evidence,
Product Knowledge, Prompt Candidate, Final Prompt, and AI inference.

The registry may identify a source as eligible for curated Official Knowledge
preparation, but it must not convert that source into Official Knowledge. The
current Official Knowledge CLI still requires curated source JSON input.

## Recommended Decisions

- Official Source Registry is a governance concept, not extraction.
- Document Classification, Authority Status, Lifecycle Status, and Evidence
  Eligibility are separate.
- Source Type must not determine authority.
- LOCKED and FINAL are lifecycle states, not authority states.
- The first registry model should be explicit and manual.
- Filename matching may be used only as a hint.
- PR-012 is a docs-only review.
- Product Knowledge, Prompt Candidate, and automatic PDF conversion are not
  allowed in PR-012.

## Risks and Mitigations

### Risk: Treating filenames as authority

Mitigation: Treat filename matching as a hint only. Require explicit registry
declaration / human review before a source becomes authoritative.

### Risk: Mixing lifecycle status with authority status

Mitigation: Model lifecycle and authority as separate concepts. LOCKED and FINAL
do not imply OFFICIAL.

### Risk: Introducing Product Knowledge too early

Mitigation: Keep the registry focused on source governance and eligibility.
Defer Product Knowledge to a separate architecture review.

### Risk: Accidentally allowing AI inference

Mitigation: Keep PR-012 manual-first and review-only. Explicitly exclude AI
classification and content-based inference.

### Risk: Treating PDFs as Official Knowledge automatically

Mitigation: Keep `SourceType` separate from `DocumentClassification` and
`AuthorityStatus`. A PDF is only a file/container type.

### Risk: Mutating locked documents

Mitigation: The registry may reference locked / SSOT documents in the future,
but it must not mutate, rewrite, normalize, replace, or move them.

## Open Questions

- Should the first registry be a domain model first or a static config reader?
- Should `source_id` be human-readable, deterministic, or provided manually?
- Should review metadata be required in the first implementation?
- Should deprecated/superseded sources remain readable for historical
  traceability?
- Should registry validation come before CLI inspection?

## Recommended Next Steps After Approval

These are future PR slices only. PR-012 does not implement them.

- PR-012B - Domain model skeleton
- PR-012C - Manual registry config reader
- PR-012D - Registry inspection CLI
- PR-012E - Evidence eligibility integration

