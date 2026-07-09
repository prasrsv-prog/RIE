import argparse
from collections import Counter

from official_source.official_source import OfficialSource
from official_source.official_source_registry_loader import (
    OfficialSourceRegistryLoader,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect an Official Source Registry.",
    )
    parser.add_argument("registry_json_path")

    args = parser.parse_args(argv)

    try:
        sources = OfficialSourceRegistryLoader.load_from_json_file(
            args.registry_json_path,
        )
    except (FileNotFoundError, OSError, TypeError, ValueError) as exc:
        print(f"Failed to inspect Official Source Registry: {exc}")
        return 1

    print_inspection(sources)
    return 0


def print_inspection(sources: list[OfficialSource]) -> None:
    print("Official Source Registry Inspection")
    print(f"total_official_sources: {len(sources)}")
    _print_count_section(
        "source_type",
        Counter(source.source_type.value for source in sources),
    )
    _print_count_section(
        "document_classification",
        Counter(source.document_classification.value for source in sources),
    )
    _print_count_section(
        "authority_status",
        Counter(source.authority_status.value for source in sources),
    )
    _print_count_section(
        "lifecycle_status",
        Counter(source.lifecycle_status.value for source in sources),
    )
    _print_count_section(
        "evidence_eligibility",
        Counter(source.evidence_eligibility.value for source in sources),
    )


def _print_count_section(label: str, counts: Counter[str]) -> None:
    print(f"{label}:")

    for value in sorted(counts):
        print(f"  {value}: {counts[value]}")


if __name__ == "__main__":
    raise SystemExit(main())
