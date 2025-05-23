from abc import ABC, abstractmethod
from typing import Awaitable, TypeVar, Union, overload

from .contracts import AsyncCommand, AsyncQuery, Command, Query

TResponse = TypeVar("TResponse")


class Sender(ABC):
    @overload
    @abstractmethod
    async def send(self, request: Command) -> Awaitable[None]: ...

    @overload
    @abstractmethod
    async def send(self, request: Query[TResponse]) -> Awaitable[TResponse]: ...

    @overload
    @abstractmethod
    async def send(self, request: AsyncCommand) -> Awaitable[None]: ...

    @overload
    @abstractmethod
    async def send(self, request: AsyncQuery[TResponse]) -> Awaitable[TResponse]: ...

    @abstractmethod
    async def send(
        self, request: Union[Command, Query[TResponse], AsyncCommand, AsyncQuery[TResponse]]
    ) -> Union[Awaitable[None], Awaitable[TResponse]]:
        raise NotImplementedError
