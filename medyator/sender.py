from abc import ABC, abstractmethod
from typing import TypeVar

from .contracts import Query, Command

TResponse = TypeVar("TResponse")


class Sender(ABC):
    @abstractmethod
    def send_query(self, request: Query[TResponse]) -> TResponse:
        raise NotImplementedError

    @abstractmethod
    def send_command(self, request: Command) -> None:
        raise NotImplementedError
