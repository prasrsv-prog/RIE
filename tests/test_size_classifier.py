from analysis.size_classifier import SizeClassifier
from analysis.size_class import SizeClass


def test_should_return_small_for_zero_byte():
    size = 0

    result = SizeClassifier.classify(size)

    assert result == SizeClass.SMALL


def test_should_return_small_for_file_under_1mb():
    size = 500 * 1024

    result = SizeClassifier.classify(size)

    assert result == SizeClass.SMALL


def test_should_return_medium_for_exactly_1mb():
    size = 1024 * 1024

    result = SizeClassifier.classify(size)

    assert result == SizeClass.MEDIUM


def test_should_return_medium_for_file_between_1mb_and_10mb():
    size = 5 * 1024 * 1024

    result = SizeClassifier.classify(size)

    assert result == SizeClass.MEDIUM    


def test_should_return_medium_for_exactly_10mb():
    size = 10 * 1024 * 1024

    result = SizeClassifier.classify(size)

    assert result == SizeClass.MEDIUM


def test_should_return_large_for_file_over_10mb():
    size = 11 * 1024 * 1024

    result = SizeClassifier.classify(size)

    assert result == SizeClass.LARGE        