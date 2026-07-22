from rie.operator.operator_recovery import recovery_for


def test_recovery_is_repeatable_and_forbids_unsafe_actions() -> None:
    recovery = recovery_for("STATE_CONFLICT_OR_IDEMPOTENCY_VIOLATION")
    assert recovery["safe_to_repeat"] == "true"
    assert "force push" in recovery["prohibited_actions"]
    assert "blind deletion" in recovery["prohibited_actions"]
