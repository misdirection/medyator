from typing import Awaitable, Generic, TypeVar

from .contracts import AsyncCommand, AsyncQuery, Command, Query

TCommand = TypeVar("TCommand", bound=Command)
TQuery = TypeVar("TQuery", bound=Query)
TResponse = TypeVar("TResponse")


class CommandHandler(Generic[TCommand]):
    def __call__(self, request: TCommand) -> None:
        raise NotImplementedError


class QueryHandler(Generic[TQuery, TResponse]):
    def __call__(self, request: TQuery) -> TResponse:
        raise NotImplementedError


class AsyncCommandHandler(Generic[TCommand], CommandHandler[TCommand]):
    async def __call__(self, request: TCommand) -> Awaitable[None]:
        raise NotImplementedError


class AsyncQueryHandler(Generic[TQuery, TResponse], QueryHandler[TQuery, TResponse]):
    async def __call__(self, request: TQuery) -> Awaitable[TResponse]:
        raise NotImplementedError
