from abc import ABC, abstractmethod
from typing import TypeVar

from .contracts import Query, Command
TResponse = TypeVar('TResponse')

class Sender(ABC):
    @abstractmethod
    def sendQuery(self, request: Query[TResponse]) -> TResponse:
        pass

    @abstractmethod
    def sendCommand(self, request: Command) -> None:
        pass
