# PR-018A - PDF Parser Environment Review

Status: Docs-only parser environment review.

Current checkpoint:

- v0.17.13-rcis-controlled-pdf-text-extraction-phase-closure
- afad20a docs: close controlled pdf text extraction phase

## Purpose

PR-018A reviews the parser environment before actual successful PDF text
extraction is enabled.

PR-018A does not install dependencies, modify pyproject.toml, modify lock
files, modify production code, modify tests, parse PDFs, or touch real RSV
assets. It does not create Evidence, Knowledge, or Prompt Candidate artifacts,
and it does not authorize AI inference.

This review documents the current environment only. It does not resolve or
mutate the environment.

## Context

PR-017 completed the controlled PDF text extraction gates, added a bounded
implementation skeleton, and added a synthetic smoke flow. The synthetic flow
confirmed deterministic unsupported_pdf fallback behavior when pypdf is
unavailable.

PR-017 did not approve real RSV asset processing or Evidence creation. Its
closure did not authorize successful parser execution against real or
production assets.

## Parser Environment Findings

The authorized environment checks reported:

- Active Python executable:
  `D:\PROJECT\RIE\.venv\Scripts\python.exe`
- pyproject.toml declares pypdf: yes
- Declaration location: dependency list entry `"pypdf"`
- pypdf import succeeded: no
- Import failure category: `ModuleNotFoundError`
- Import failure detail: `No module named 'pypdf'`
- Actual successful synthetic PDF extraction currently enabled: no
- Current implementation behavior: deterministic unsupported_pdf fallback

The declared project dependency and the installed active virtual environment
are therefore not currently aligned for pypdf. A declaration in
pyproject.toml does not by itself prove that the dependency is importable from
the active interpreter.

No PDF was parsed and no PDF text was extracted during this review.

## Dependency Boundary

- dependency synchronization is outside PR-018A
- installing pypdf is outside PR-018A
- modifying pyproject.toml is outside PR-018A
- modifying lock files is outside PR-018A
- changing the active virtual environment is outside PR-018A
- resolving the environment requires a separate explicitly approved step

PR-018A does not run pip install, uv sync, poetry install, or any equivalent
dependency mutation command.

## Risk Assessment

Enabling parser execution without an explicit environment review creates the
following risks:

- false assumption that the parser is installed because it is declared
- accidental dependency or virtual environment mutation
- inconsistent behavior across developer environments
- tests passing only through the unsupported parser fallback
- unclear distinction between a declared dependency and an installed,
  importable dependency

The current test state proves deterministic fallback behavior. It does not
prove successful pypdf parsing in the active virtual environment.

## Recommended Next Options

### Option 1: PR-018B - Dependency Synchronization Plan

- create a docs-only plan for synchronizing the active virtual environment
  with declared dependencies
- identify the approved dependency management path
- define verification and rollback expectations
- do not install or synchronize dependencies yet

### Option 2: PR-018B - Controlled Synthetic PDF Parser Execution

- proceed only after dependency state is explicitly reviewed and approved
- use a synthetic tmp_path PDF only
- do not touch real RSV assets
- do not create Evidence
- require output to pass ControlledPdfTextExtractionResultContract

## Preferred Recommendation

Proceed with PR-018B - Dependency Synchronization Plan first. pypdf is declared
but not importable, so the dependency state should be reviewed and an explicit
synchronization decision should be approved before controlled parser execution
is attempted.

## Review Acceptance

- Only this docs file is added.
- No production code is changed.
- No tests are changed.
- No pyproject.toml or lock files are changed.
- No dependencies are installed or changed.
- No PDFs or real RSV assets are accessed.
- No commit is created by PR-018A preparation.
