from abc import ABC, abstractmethod
from typing import TypeVar, Union, overload, Awaitable # Added Awaitable

from .contracts import Command, Query, AsyncCommand, AsyncQuery # Added Async types

TResponse = TypeVar("TResponse")


class Sender(ABC):
    @overload
    @abstractmethod
    async def send(self, request: Command) -> None: ... # Changed to async, returns None directly

    @overload
    @abstractmethod
    async def send(self, request: Query[TResponse]) -> TResponse: ... # Changed to async

    @overload
    @abstractmethod
    async def send(self, request: AsyncCommand) -> None: ... # Added overload for AsyncCommand

    @overload
    @abstractmethod
    async def send(self, request: AsyncQuery[TResponse]) -> TResponse: ... # Added overload for AsyncQuery

    @abstractmethod
    async def send(
        self, request: Union[Command, Query[TResponse], AsyncCommand, AsyncQuery[TResponse]]
    ) -> Union[None, TResponse]: # Return type is direct due to async def
        raise NotImplementedError
