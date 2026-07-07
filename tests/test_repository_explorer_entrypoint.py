from rie import repository_explorer


class FakeEngine:

    def __init__(self) -> None:
        self.run_called = False

    def run(self) -> None:
        self.run_called = True


def test_repository_explorer_main_runs_composed_engine(monkeypatch):
    fake_engine = FakeEngine()

    monkeypatch.setattr(
        repository_explorer,
        "create_repository_explorer_engine",
        lambda: fake_engine,
    )

    repository_explorer.main()

    assert fake_engine.run_called is True
