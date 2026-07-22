# Fresh-environment acceptance

The acceptance test copies the source tree to a controlled temporary
location, builds one wheel without dependency resolution, creates a fresh
Python environment, installs the wheel, and invokes only the installed
`rie` command.

Acceptance proves version and help output, all ten commands, registry
validation, the complete PDF-to-Prompt Candidate workflow, human and JSON
semantic equivalence, audit linkage, safe rerun, deterministic rejection,
recovery guidance, export digest integrity, and absence of duplicate
governed state.

The acceptance test does not create or publish a release tag. Release
authorization remains a later independently accepted checkpoint.
