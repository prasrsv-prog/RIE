from dataclasses import FrozenInstanceError, MISSING, fields
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

import pytest

SOURCE_PATH = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "rie"
    / "domain"
    / "governed_creative_workflow_result.py"
)
SPEC = spec_from_file_location(
    "target_governed_creative_workflow_result",
    SOURCE_PATH,
)
assert SPEC is not None
assert SPEC.loader is not None
MODULE = module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

GovernedCreativeWorkflowResult = MODULE.GovernedCreativeWorkflowResult

PROJECT = "project:alpha"
CAMPAIGN = (PROJECT, "campaign:one")
BRIEF = "brief:approved:001"
INSTRUCTION = ("instruction:approved:001", "APPROVED_INSTRUCTION")
EVENT_ID = "a" * 64
EVENT_REFERENCE = (PROJECT, CAMPAIGN[1], EVENT_ID)
HANDOFF_REFERENCE = (PROJECT, CAMPAIGN[1], "handoff:001")
CANDIDATE_REFERENCE = (PROJECT, CAMPAIGN[1], "candidate:001")
OPERATOR_DECISION_REFERENCE = (
    PROJECT,
    CAMPAIGN[1],
    "operator-decision:accepted:001",
)
GOVERNED_ASSET_REFERENCE = (
    PROJECT,
    CAMPAIGN[1],
    "governed-asset:accepted:001",
)
CONTRACT = ("GATE_18_CREATIVE_WORKFLOW", "1.0")


def make_result(**overrides):
    values = {
        "workflow_request_reference": "workflow-request:001",
        "idempotency_key": "idempotency:001",
        "project_context_reference": PROJECT,
        "campaign_context_reference": CAMPAIGN,
        "creative_brief_reference": BRIEF,
        "instruction_reference": INSTRUCTION,
        "final_workflow_state": "COMPLETED",
        "last_accepted_event_reference": EVENT_REFERENCE,
        "manual_external_tool_handoff_reference": HANDOFF_REFERENCE,
        "creative_result_candidate_reference": CANDIDATE_REFERENCE,
        "accepted_operator_decision_reference": OPERATOR_DECISION_REFERENCE,
        "accepted_governed_asset_reference": GOVERNED_ASSET_REFERENCE,
        "reason_codes": ("COMPLETED", "WORKFLOW_CONTEXT_PRESERVED"),
        "diagnostics": (
            ("ASSET_REFERENCE", "accepted"),
            ("OPERATOR_DECISION", "accepted"),
        ),
        "workflow_contract_reference": CONTRACT,
        "production_release_claimed": False,
    }
    values.update(overrides)
    return GovernedCreativeWorkflowResult(**values)


def test_exact_sixteen_fields_and_no_defaults():
    assert [item.name for item in fields(GovernedCreativeWorkflowResult)] == [
        "workflow_request_reference",
        "idempotency_key",
        "project_context_reference",
        "campaign_context_reference",
        "creative_brief_reference",
        "instruction_reference",
        "final_workflow_state",
        "last_accepted_event_reference",
        "manual_external_tool_handoff_reference",
        "creative_result_candidate_reference",
        "accepted_operator_decision_reference",
        "accepted_governed_asset_reference",
        "reason_codes",
        "diagnostics",
        "workflow_contract_reference",
        "production_release_claimed",
    ]
    assert all(
        item.default is MISSING
        and item.default_factory is MISSING
        for item in fields(GovernedCreativeWorkflowResult)
    )


def test_result_is_immutable():
    result = make_result()
    with pytest.raises(FrozenInstanceError):
        result.final_workflow_state = "SAFE_STOP"


@pytest.mark.parametrize(
    "state",
    ["COMPLETED", "REJECTED", "SAFE_STOP"],
)
def test_exact_final_workflow_states_are_supported(state):
    overrides = {"final_workflow_state": state}
    if state != "COMPLETED":
        overrides.update(
            accepted_operator_decision_reference=None,
            accepted_governed_asset_reference=None,
        )
    result = make_result(**overrides)
    assert result.final_workflow_state == state


@pytest.mark.parametrize(
    "state",
    [
        "REQUESTED",
        "INPUTS_VALIDATED",
        "INSTRUCTION_READY",
        "CANDIDATE_ADMITTED",
        "OPERATOR_DECISION_RECORDED",
        "GOVERNED_ASSET_REFERENCE_RECORDED",
        "UNKNOWN",
    ],
)
def test_non_final_workflow_states_are_rejected(state):
    with pytest.raises(ValueError, match="final_workflow_state"):
        make_result(final_workflow_state=state)


@pytest.mark.parametrize(
    "authority",
    ["PROMPT_CANDIDATE", "APPROVED_INSTRUCTION"],
)
def test_both_instruction_authority_states_are_supported(authority):
    result = make_result(
        instruction_reference=("instruction:001", authority)
    )
    assert result.instruction_reference[1] == authority


@pytest.mark.parametrize(
    "authority",
    ["APPROVED", "INSTRUCTION", "", "prompt_candidate"],
)
def test_unknown_instruction_authority_is_rejected(authority):
    with pytest.raises(ValueError):
        make_result(instruction_reference=("instruction:001", authority))


def test_completed_requires_operator_decision_reference():
    with pytest.raises(ValueError, match="operator decision"):
        make_result(accepted_operator_decision_reference=None)


def test_completed_requires_governed_asset_reference():
    with pytest.raises(ValueError, match="governed asset"):
        make_result(accepted_governed_asset_reference=None)


@pytest.mark.parametrize("state", ["REJECTED", "SAFE_STOP"])
@pytest.mark.parametrize(
    "field_name,reference",
    [
        (
            "accepted_operator_decision_reference",
            OPERATOR_DECISION_REFERENCE,
        ),
        ("accepted_governed_asset_reference", GOVERNED_ASSET_REFERENCE),
    ],
)
def test_non_completed_results_reject_fabricated_downstream_references(
    state,
    field_name,
    reference,
):
    values = {
        "final_workflow_state": state,
        "accepted_operator_decision_reference": None,
        "accepted_governed_asset_reference": None,
        field_name: reference,
    }
    with pytest.raises(ValueError, match="must not fabricate"):
        make_result(**values)


def test_rejected_may_preserve_candidate_and_handoff_references():
    result = make_result(
        final_workflow_state="REJECTED",
        accepted_operator_decision_reference=None,
        accepted_governed_asset_reference=None,
    )
    assert result.manual_external_tool_handoff_reference == HANDOFF_REFERENCE
    assert result.creative_result_candidate_reference == CANDIDATE_REFERENCE


def test_safe_stop_may_preserve_candidate_without_handoff():
    result = make_result(
        final_workflow_state="SAFE_STOP",
        manual_external_tool_handoff_reference=None,
        accepted_operator_decision_reference=None,
        accepted_governed_asset_reference=None,
    )
    assert result.creative_result_candidate_reference == CANDIDATE_REFERENCE


def test_completed_handoff_requires_candidate_reference():
    with pytest.raises(ValueError, match="handoff result requires candidate"):
        make_result(creative_result_candidate_reference=None)


def test_completed_without_handoff_may_omit_candidate_reference():
    result = make_result(
        manual_external_tool_handoff_reference=None,
        creative_result_candidate_reference=None,
    )
    assert result.creative_result_candidate_reference is None


@pytest.mark.parametrize(
    "field_name",
    [
        "workflow_request_reference",
        "idempotency_key",
        "project_context_reference",
        "creative_brief_reference",
    ],
)
@pytest.mark.parametrize("value", ["", "   ", "caf\u00e9", "bad\nvalue"])
def test_required_text_fields_reject_invalid_text(field_name, value):
    with pytest.raises((TypeError, ValueError)):
        make_result(**{field_name: value})


@pytest.mark.parametrize(
    "field_name",
    [
        "workflow_request_reference",
        "idempotency_key",
        "project_context_reference",
        "creative_brief_reference",
    ],
)
@pytest.mark.parametrize("value", [None, 7, b"bytes", object()])
def test_required_text_fields_reject_non_text(field_name, value):
    with pytest.raises(TypeError):
        make_result(**{field_name: value})


def test_campaign_reference_must_match_project_context():
    with pytest.raises(ValueError, match="project binding"):
        make_result(
            campaign_context_reference=(
                "project:other",
                CAMPAIGN[1],
            )
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "last_accepted_event_reference",
        "manual_external_tool_handoff_reference",
        "creative_result_candidate_reference",
        "accepted_operator_decision_reference",
        "accepted_governed_asset_reference",
    ],
)
def test_bound_references_reject_cross_project_binding(field_name):
    bad = ("project:other", CAMPAIGN[1], "reference:001")
    if field_name == "last_accepted_event_reference":
        bad = ("project:other", CAMPAIGN[1], EVENT_ID)
    with pytest.raises(ValueError, match="project binding"):
        make_result(**{field_name: bad})


@pytest.mark.parametrize(
    "field_name",
    [
        "last_accepted_event_reference",
        "manual_external_tool_handoff_reference",
        "creative_result_candidate_reference",
        "accepted_operator_decision_reference",
        "accepted_governed_asset_reference",
    ],
)
def test_bound_references_reject_cross_campaign_binding(field_name):
    bad = (PROJECT, "campaign:other", "reference:001")
    if field_name == "last_accepted_event_reference":
        bad = (PROJECT, "campaign:other", EVENT_ID)
    with pytest.raises(ValueError, match="campaign binding"):
        make_result(**{field_name: bad})


@pytest.mark.parametrize(
    "value",
    [
        (PROJECT, CAMPAIGN[1], "not-a-hash"),
        (PROJECT, CAMPAIGN[1], "A" * 64),
        (PROJECT, CAMPAIGN[1], "a" * 63),
        (PROJECT, CAMPAIGN[1], "g" * 64),
    ],
)
def test_last_event_reference_requires_sha256_identity(value):
    with pytest.raises(ValueError, match="lowercase SHA256"):
        make_result(last_accepted_event_reference=value)


@pytest.mark.parametrize(
    "field_name",
    [
        "last_accepted_event_reference",
        "manual_external_tool_handoff_reference",
        "creative_result_candidate_reference",
        "accepted_operator_decision_reference",
        "accepted_governed_asset_reference",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        "reference",
        (),
        ("one",),
        ("one", "two"),
        ("one", "two", "three", "four"),
        ["one", "two", "three"],
    ],
)
def test_bound_references_require_exact_immutable_tuple(
    field_name,
    value,
):
    with pytest.raises((TypeError, ValueError)):
        make_result(**{field_name: value})


@pytest.mark.parametrize(
    "marker",
    [
        "secret",
        "password",
        "api_key",
        "access_token",
        "authorization:",
        "credential",
        "private_key",
        "session_token",
    ],
)
def test_references_reject_secret_material(marker):
    with pytest.raises(ValueError, match="secret material"):
        make_result(
            creative_result_candidate_reference=(
                PROJECT,
                CAMPAIGN[1],
                f"candidate:{marker}:001",
            )
        )


@pytest.mark.parametrize(
    "prefix",
    ["memory:", "mutable:", "object:", "session:", "temp:"],
)
def test_references_reject_mutable_reference(prefix):
    with pytest.raises(ValueError, match="immutable reference"):
        make_result(
            creative_result_candidate_reference=(
                PROJECT,
                CAMPAIGN[1],
                f"{prefix}candidate",
            )
        )


@pytest.mark.parametrize(
    "reason_codes",
    [
        (),
        ("z_code",),
        ("CODE", "CODE"),
        ("SECOND", "FIRST"),
        ["FIRST"],
        ("FIRST", 7),
    ],
)
def test_reason_codes_require_deterministic_ordering(reason_codes):
    with pytest.raises((TypeError, ValueError)):
        make_result(reason_codes=reason_codes)


def test_reason_codes_accept_sorted_unique_codes():
    result = make_result(reason_codes=("ALPHA", "OMEGA"))
    assert result.reason_codes == ("ALPHA", "OMEGA")


@pytest.mark.parametrize(
    "diagnostics",
    [
        [("CODE", "detail")],
        (("CODE",),),
        (("CODE", "detail", "extra"),),
        (("lowercase", "detail"),),
        (("CODE", "detail"), ("CODE", "detail")),
        (("SECOND", "detail"), ("FIRST", "detail")),
        (("CODE", "secret=value"),),
        (("CODE", "memory:object"),),
    ],
)
def test_diagnostics_require_deterministic_safe_entries(diagnostics):
    with pytest.raises((TypeError, ValueError)):
        make_result(diagnostics=diagnostics)


def test_diagnostics_may_be_empty():
    result = make_result(diagnostics=())
    assert result.diagnostics == ()


@pytest.mark.parametrize(
    "value",
    [
        ("only-one",),
        ("one", "two", "three"),
        ["name", "version"],
        ("name", ""),
        ("name", "caf\u00e9"),
    ],
)
def test_workflow_contract_reference_requires_exact_pair(value):
    with pytest.raises((TypeError, ValueError)):
        make_result(workflow_contract_reference=value)


@pytest.mark.parametrize("value", [True, 1, "false", None])
def test_production_release_claim_must_remain_false(value):
    with pytest.raises((TypeError, ValueError)):
        make_result(production_release_claimed=value)


def test_completed_is_not_production_release():
    result = make_result()
    assert result.final_workflow_state == "COMPLETED"
    assert result.production_release_claimed is False


def test_identical_inputs_return_equal_results():
    assert make_result() == make_result()


def test_manual_handoff_reference_is_optional():
    result = make_result(manual_external_tool_handoff_reference=None)
    assert result.manual_external_tool_handoff_reference is None


def test_candidate_reference_is_optional_for_safe_stop():
    result = make_result(
        final_workflow_state="SAFE_STOP",
        creative_result_candidate_reference=None,
        accepted_operator_decision_reference=None,
        accepted_governed_asset_reference=None,
    )
    assert result.creative_result_candidate_reference is None


def test_operator_and_asset_references_preserve_exact_context():
    result = make_result()
    assert result.accepted_operator_decision_reference[:2] == CAMPAIGN
    assert result.accepted_governed_asset_reference[:2] == CAMPAIGN


def test_targeted_file_only_no_runtime_execution(monkeypatch):
    import builtins

    called = False

    def fail_open(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("file IO is not authorized")

    monkeypatch.setattr(builtins, "open", fail_open)
    result = make_result()
    assert result.final_workflow_state == "COMPLETED"
    assert called is False
