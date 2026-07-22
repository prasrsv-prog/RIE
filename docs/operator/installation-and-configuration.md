# Installation and configuration

RIE Core v1 supports Python 3.12 or later. Install the accepted wheel in a
fresh environment using the dependency versions recorded in
`requirements-lock.txt`.

The installed console command is `rie`. Verify installation with:

`rie --version`

Every non-help command requires `--config <path>`. The configuration JSON
contains exactly:

- `schema_version`: `rie_operator_configuration_v1`
- `workspace_path`: explicit operator workspace
- `audit_path`: explicit JSONL audit path

Relative paths resolve from the configuration file directory. Configuration
identity and digest are included in audit records. Credentials and secrets
are not configuration fields and are not recorded.
