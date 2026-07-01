from .size_class import SizeClass


SMALL_FILE_LIMIT = 1 * 1024 * 1024
MEDIUM_FILE_LIMIT = 10 * 1024 * 1024


class SizeClassifier:
    """
    Classifies a file size into a standard SizeClass.
    """

    @staticmethod
    def classify(size_in_bytes: int) -> SizeClass:
        if size_in_bytes < SMALL_FILE_LIMIT:
            return SizeClass.SMALL

        if size_in_bytes <= MEDIUM_FILE_LIMIT:
            return SizeClass.MEDIUM

        return SizeClass.LARGE