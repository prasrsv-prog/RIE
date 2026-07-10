"""Value-only contract for controlled real asset fixture declarations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


ALLOWED_FIXTURE_TYPES: tuple[str, ...] = (
    "product_spec_pdf",
    "product_photo_jpeg",
    "product_photo_png",
)

FIXTURE_CONTRACT_LIMIT = 4


@dataclass(frozen=True)
class ControlledRealAssetFixtureItem:
    fixture_id: str
    source_label: str
    fixture_path: str
    fixture_type: str
    allowed_for_metadata: bool
    allowed_for_pdf_text_extraction: bool
    allowed_for_image_metadata: bool
    allowed_for_evidence: bool
    notes: str


@dataclass(frozen=True)
class ControlledRealAssetFixtureContractResult:
    allowed: bool
    reason: str
    fixture_count: int
    fixtures: tuple[ControlledRealAssetFixtureItem, ...]


class ControlledRealAssetFixtureContract:
    @staticmethod
    def evaluate(
        fixtures: Iterable[ControlledRealAssetFixtureItem] = (),
        max_items: int = FIXTURE_CONTRACT_LIMIT,
    ) -> ControlledRealAssetFixtureContractResult:
        fixture_tuple = tuple(fixtures)

        if max_items <= 0:
            return ControlledRealAssetFixtureContractResult(
                allowed=False,
                reason="max_items must be greater than zero",
                fixture_count=len(fixture_tuple),
                fixtures=fixture_tuple,
            )

        if max_items > FIXTURE_CONTRACT_LIMIT:
            return ControlledRealAssetFixtureContractResult(
                allowed=False,
                reason="max_items exceeds fixture contract limit",
                fixture_count=len(fixture_tuple),
                fixtures=fixture_tuple,
            )

        if len(fixture_tuple) > FIXTURE_CONTRACT_LIMIT:
            return ControlledRealAssetFixtureContractResult(
                allowed=False,
                reason="fixture count exceeds fixture contract limit",
                fixture_count=len(fixture_tuple),
                fixtures=fixture_tuple,
            )

        if len(fixture_tuple) > max_items:
            return ControlledRealAssetFixtureContractResult(
                allowed=False,
                reason="fixture count exceeds max_items",
                fixture_count=len(fixture_tuple),
                fixtures=fixture_tuple,
            )

        fixture_ids: set[str] = set()
        fixture_paths: set[str] = set()

        for fixture in fixture_tuple:
            if not isinstance(fixture, ControlledRealAssetFixtureItem):
                return ControlledRealAssetFixtureContractResult(
                    allowed=False,
                    reason="fixture must be ControlledRealAssetFixtureItem",
                    fixture_count=len(fixture_tuple),
                    fixtures=fixture_tuple,
                )

            if not fixture.fixture_id.strip():
                return ControlledRealAssetFixtureContractResult(
                    allowed=False,
                    reason="fixture_id is required",
                    fixture_count=len(fixture_tuple),
                    fixtures=fixture_tuple,
                )

            if not fixture.source_label.strip():
                return ControlledRealAssetFixtureContractResult(
                    allowed=False,
                    reason="source_label is required",
                    fixture_count=len(fixture_tuple),
                    fixtures=fixture_tuple,
                )

            if not fixture.fixture_path.strip():
                return ControlledRealAssetFixtureContractResult(
                    allowed=False,
                    reason="fixture_path is required",
                    fixture_count=len(fixture_tuple),
                    fixtures=fixture_tuple,
                )

            if fixture.fixture_type not in ALLOWED_FIXTURE_TYPES:
                return ControlledRealAssetFixtureContractResult(
                    allowed=False,
                    reason="unsupported fixture_type",
                    fixture_count=len(fixture_tuple),
                    fixtures=fixture_tuple,
                )

            if fixture.notes is None:
                return ControlledRealAssetFixtureContractResult(
                    allowed=False,
                    reason="notes is required",
                    fixture_count=len(fixture_tuple),
                    fixtures=fixture_tuple,
                )

            if not fixture.allowed_for_metadata:
                return ControlledRealAssetFixtureContractResult(
                    allowed=False,
                    reason="metadata access must be allowed",
                    fixture_count=len(fixture_tuple),
                    fixtures=fixture_tuple,
                )

            if fixture.allowed_for_pdf_text_extraction:
                return ControlledRealAssetFixtureContractResult(
                    allowed=False,
                    reason="pdf text extraction is not allowed by this contract",
                    fixture_count=len(fixture_tuple),
                    fixtures=fixture_tuple,
                )

            if fixture.allowed_for_image_metadata:
                return ControlledRealAssetFixtureContractResult(
                    allowed=False,
                    reason="image metadata is not allowed by this contract",
                    fixture_count=len(fixture_tuple),
                    fixtures=fixture_tuple,
                )

            if fixture.allowed_for_evidence:
                return ControlledRealAssetFixtureContractResult(
                    allowed=False,
                    reason="evidence creation is not allowed by this contract",
                    fixture_count=len(fixture_tuple),
                    fixtures=fixture_tuple,
                )

            if fixture.fixture_id in fixture_ids:
                return ControlledRealAssetFixtureContractResult(
                    allowed=False,
                    reason="duplicate fixture_id",
                    fixture_count=len(fixture_tuple),
                    fixtures=fixture_tuple,
                )

            if fixture.fixture_path in fixture_paths:
                return ControlledRealAssetFixtureContractResult(
                    allowed=False,
                    reason="duplicate fixture_path",
                    fixture_count=len(fixture_tuple),
                    fixtures=fixture_tuple,
                )

            fixture_ids.add(fixture.fixture_id)
            fixture_paths.add(fixture.fixture_path)

        return ControlledRealAssetFixtureContractResult(
            allowed=True,
            reason="fixture contract allowed",
            fixture_count=len(fixture_tuple),
            fixtures=fixture_tuple,
        )
