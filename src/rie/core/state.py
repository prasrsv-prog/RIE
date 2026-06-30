from dataclasses import dataclass


@dataclass
class EngineState:

    running: bool = False

    batch_id: str = ""

    processed: int = 0

    failed: int = 0