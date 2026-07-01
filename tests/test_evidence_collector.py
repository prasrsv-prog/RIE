from pathlib import Path

from rie.application.asset import Asset
from rie.application.metadata import Metadata

from src.collection.evidence_collector import EvidenceCollector
from src.analysis.size_class import SizeClass


def test_should_collect_evidences():
    
    # Arrange
    assets = [
        Asset(
            path=Path("photo1.jpg"),
            filename="photo1.jpg",
            metadata=Metadata(
                extension=".jpg",
                size=500 * 1024,
                category="image"
            )
        ),
        Asset(
            path=Path("photo2.jpg"),
            filename="photo2.jpg",
            metadata=Metadata(
                extension=".jpg",
                size=5 * 1024 * 1024,
                category="image"
            )
        ),
        Asset(
            path=Path("photo3.jpg"),
            filename="photo3.jpg",
            metadata=Metadata(
                extension=".jpg",
                size=11 * 1024 * 1024,
                category="image"
    )
)
]
    
    # Act
    collection = EvidenceCollector.collect(assets)

    # Assert
    assert len(collection.evidences) == 3
    assert collection.evidences[0].analysis.size_class == SizeClass.SMALL
    assert collection.evidences[1].analysis.size_class == SizeClass.MEDIUM
    assert collection.evidences[2].analysis.size_class == SizeClass.LARGE