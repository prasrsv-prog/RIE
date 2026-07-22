# Audit and recovery

Every non-help invocation with valid explicit configuration produces one
append-only JSONL audit record. Records include deterministic operation
identity, invocation sequence, prior audit linkage, normalized arguments,
package and contract versions, configuration identity, result, outputs, and
recovery state.

Dry-run returns a non-persistent audit preview.

Recovery instructions are safe to repeat. Never delete governed state
blindly, edit persisted artifacts manually, reset history, force push,
replace an artifact silently, bypass a frozen contract, or retry
automatically. Preserve every failure report and audit record.
