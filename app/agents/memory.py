from typing import Any


class AgentMemory:
    def __init__(self) -> None:
        self.history: list[dict[str, Any]] = []

    def add(self, item: dict[str, Any]) -> None:
        self.history.append(item)

    def recent(self, count: int = 10) -> list[dict[str, Any]]:
        return self.history[-count:]
