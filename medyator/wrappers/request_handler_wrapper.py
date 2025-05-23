import inspect
from typing import Any, Awaitable, Generic, Protocol, TypeVar, cast

from ..request_handler import (
    CommandHandler,
    QueryHandler,
)
from ..contracts.service_provider import ServiceProvider
from ..contracts import Command, Query

TResponse = TypeVar("TResponse")
TQuery = TypeVar("TQuery", bound=Query[TResponse])
TCommand = TypeVar("TCommand", bound=Command)


class RequestHandlerBase(Protocol):
    async def __call__(
        self, request: Any, service_provider: ServiceProvider
    ) -> Awaitable[Any]:
        raise NotImplementedError


class QueryHandlerWrapper(RequestHandlerBase, Protocol, Generic[TResponse]):
    async def __call__(
        self,
        request: Query[TResponse],
        service_provider: ServiceProvider,
    ) -> Awaitable[TResponse]:
        raise NotImplementedError


class QueryHandlerWrapperImpl(
    QueryHandlerWrapper[TResponse], Generic[TQuery, TResponse]
):
    async def __call__(
        self, request: TQuery, service_provider: ServiceProvider
    ) -> Awaitable[TResponse]:
        actual_handler = cast(
            QueryHandler[TQuery, TResponse],
            service_provider.get(request),
        )
        if inspect.iscoroutinefunction(actual_handler.__call__):
            return await actual_handler(request)
        else:
            return actual_handler(request)


class CommandHandlerWrapper(RequestHandlerBase, Protocol):
    async def __call__(
        self,
        request: Command,
        service_provider: ServiceProvider
    ) -> Awaitable[None]:
        raise NotImplementedError


class CommandHandlerWrapperImpl(CommandHandlerWrapper, Generic[TCommand]):
    async def __call__(
        self, request: TCommand, service_provider: ServiceProvider
    ) -> Awaitable[None]:
        actual_handler = cast(
            CommandHandler[TCommand],
            service_provider.get(request),
        )
        if inspect.iscoroutinefunction(actual_handler.__call__):
            await actual_handler(request)
        else:
            actual_handler(request)
        return None
