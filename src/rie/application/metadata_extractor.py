from rie.application.metadata import Metadata


class MetadataExtractor:

    def extract(
        self,
        extension: str,
        size: int,
    ) -> Metadata:

        category = self.detect_category(extension)

        return Metadata(
            extension=extension,
            size=size,
            category=category,
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