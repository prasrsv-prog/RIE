import rie.operator as operator


def test_public_api_is_available() -> None:
    assert operator.ExitCode.SUCCESS == 0
    assert "ingest pdf" in operator.REQUIRED_COMMANDS
    assert callable(operator.load_configuration)
    assert callable(operator.render)
