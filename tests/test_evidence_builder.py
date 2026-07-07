from pathlib import Path

from rie.application.asset import Asset

from analysis.size_class import SizeClass
from evidence.evidence_builder import EvidenceBuilder
from rie.application.metadata import Metadata


def test_should_build_evidence_from_asset():

    # Arrange
    asset = Asset(
    path=Path("photo.jpg"),
    filename="photo.jpg",
    metadata=Metadata(
        extension=".jpg",
        size=5 * 1024 * 1024,
        category="image",
    )
)

    # Act
    evidence = EvidenceBuilder.build(asset)

    # Assert
    assert evidence.asset_path == Path("photo.jpg")
    assert evidence.filename == "photo.jpg"
    assert evidence.metadata == asset.metadata
    assert evidence.analysis.size_class == SizeClass.MEDIUM