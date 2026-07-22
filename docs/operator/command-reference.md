# Command reference

Global options:

- `--config <path>`
- `--format human|json`
- `--version`

Required commands:

- `rie registry validate REGISTRY`
- `rie source inspect REGISTRY SOURCE_ID`
- `rie ingest pdf REGISTRY SOURCE_ID --output PATH [--dry-run]`
- `rie evidence build INPUT --output PATH [--dry-run]`
- `rie evidence inspect INPUT`
- `rie knowledge build INPUT --output PATH [--dry-run]`
- `rie knowledge inspect INPUT`
- `rie prompt-candidate build INPUT --output PATH [--dry-run]`
- `rie audit job AUDIT_ID`
- `rie export INPUT --output PATH [--overwrite] [--dry-run]`

Exit codes are stable from 0 through 8. JSON and human formats expose the
same command, status, exit code, issue code, message, identifiers,
provenance, audit, outputs, and recovery semantics. No command performs
automatic retry or hidden source selection.
