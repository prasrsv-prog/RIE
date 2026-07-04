from src.analysis.size_classifier import SizeClassifier

from rie.application.metadata import Metadata


class MetadataExtractor:

    def __init__(self) -> None:
        self.size_classifier = SizeClassifier()

    def extract(
        self,
        extension: str,
        size: int,
    ) -> Metadata:

        category = self.detect_category(extension)

        size_class = self.size_classifier.classify(size)

        return Metadata(
            extension=extension,
            size=size,
            category=category,
            size_label=size_class.name,
        )

    def detect_category(
        self,
        extension: str,
    ) -> str:

        extension = extension.lower()

        mapping = {
            ".jpg": "Image",
            ".jpeg": "Image",
            ".png": "Image",
            ".webp": "Image",

            ".psd": "Photoshop",
            ".ai": "Illustrator",

            ".mp4": "Video",
            ".mov": "Video",

            ".pdf": "Document",
        }

        return mapping.get(extension, "Unknown")