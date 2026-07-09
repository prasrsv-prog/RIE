import argparse
from collections import Counter

from official_source.official_source import EvidenceEligibility
from official_source.official_source_evidence_eligibility_policy import (
    EvidenceEligibilityDecision,
)
from official_source.official_source_evidence_eligibility_policy import (
    OfficialSourceEvidenceEligibilityPolicy,
)
from official_source.official_source_registry_loader import (
    OfficialSourceRegistryLoader,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect Official Source evidence eligibility.",
    )
    parser.add_argument("registry_json_path")

    args = parser.parse_args(argv)

    try:
        sources = OfficialSourceRegistryLoader.load_from_json_file(
            args.registry_json_path,
        )
        decisions = [
            OfficialSourceEvidenceEligibilityPolicy.evaluate(source)
            for source in sources
        ]
    except (FileNotFoundError, OSError, TypeError, ValueError) as exc:
        print(f"Failed to inspect Evidence Eligibility: {exc}")
        return 1

    print_inspection(decisions)
    return 0


def print_inspection(
    decisions: list[EvidenceEligibilityDecision],
) -> None:
    print("Evidence Eligibility Inspection")
    print(f"total_sources: {len(decisions)}")
    print()
    print("decision_summary:")
    print(f"allowed: {_count_allowed(decisions)}")
    print(f"requires_review: {_count_requires_review(decisions)}")
    print(f"blocked: {_count_blocked(decisions)}")
    print()
    print("evidence_eligibility:")

    eligibility_counts = Counter(
        decision.evidence_eligibility
        for decision in decisions
    )

    for evidence_eligibility in EvidenceEligibility:
        print(
            f"{evidence_eligibility.value}: "
            f"{eligibility_counts[evidence_eligibility]}"
        )


def _count_allowed(
    decisions: list[EvidenceEligibilityDecision],
) -> int:
    return sum(decision.allowed for decision in decisions)


def _count_requires_review(
    decisions: list[EvidenceEligibilityDecision],
) -> int:
    return sum(decision.requires_review for decision in decisions)


def _count_blocked(
    decisions: list[EvidenceEligibilityDecision],
) -> int:
    return sum(
        not decision.allowed and not decision.requires_review
        for decision in decisions
    )


if __name__ == "__main__":
    raise SystemExit(main())
