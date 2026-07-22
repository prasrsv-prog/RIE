# Sample workflow

Use `samples/rie-core-v1/official-source-registry.json` and the adjacent
`sample-source.pdf`.

Execute registry validation, source inspection, PDF ingestion, Evidence
build, Knowledge build, Prompt Candidate build, audit inspection, and
export. Use explicit output paths inside the configured workspace.

Repeat the same ingestion command. The expected status is
`REUSED_EXISTING`, and all governed artifact digests remain unchanged.
Inspect the Prompt Candidate export before any downstream use. This
workflow never executes a prompt or invokes a model.
