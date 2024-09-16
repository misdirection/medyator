from abc import ABC, abstractmethod
from typing import TypeVar, Union, overload

from .contracts import Command, Query

TResponse = TypeVar("TResponse")


class Sender(ABC):
    @overload
    @abstractmethod
    def send(self, request: Command) -> None: ...

    @overload
    @abstractmethod
    def send(self, request: Query[TResponse]) -> TResponse: ...

    @abstractmethod
    def send(self, request: Union[Command, Query[TResponse]]) -> Union[None, TResponse]:
        raise NotImplementedError
