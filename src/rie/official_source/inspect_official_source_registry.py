import argparse

from official_source.official_source_registry_validation import (
    OfficialSourceRegistryValidationRequest,
)
from official_source.official_source_registry_validation import (
    OfficialSourceRegistryValidationStatus,
)
from official_source.official_source_registry_validation import (
    render_official_source_registry_validation_report,
)
from official_source.official_source_registry_validation import (
    validate_official_source_registry,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate an Official Source Registry.",
    )
    parser.add_argument("registry_json_path")

    args = parser.parse_args(argv)
    result = validate_official_source_registry(
        OfficialSourceRegistryValidationRequest(
            registry_path=args.registry_json_path,
        )
    )
    print(render_official_source_registry_validation_report(result))

    if result.status is OfficialSourceRegistryValidationStatus.VALID:
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
