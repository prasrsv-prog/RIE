"""
RCIS Intelligence Engine
Core Engine
"""
from rie.core.pipeline import Pipeline
from rie.core.state import EngineState


class Engine:
    def __init__(self) -> None:

        self.state = EngineState()
        self.pipeline = Pipeline()

        self.name = "RCIS Intelligence Engine"
        self.version = "0.1.0"
        self.status = "Development"

    def run(self) -> None:

        self.state.running = True
        print(f"Running : {self.state.running}")

        print("=" * 50)
        print(self.name)
        print(f"Version : {self.version}")
        print(f"Status  : {self.status}")
        print("=" * 50)

        self.pipeline.execute()

        print(f"Processed : {self.state.processed}")
        print(f"Failed    : {self.state.failed}")
        self.state.running = False
        print(f"Running : {self.state.running}")