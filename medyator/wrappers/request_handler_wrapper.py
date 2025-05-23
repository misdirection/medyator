import inspect
from typing import Any, Awaitable, Generic, Protocol, TypeVar, Union, cast

from ..request_handler import (
    AsyncCommandHandler,
    AsyncQueryHandler,
    CommandHandler,
    QueryHandler,
)
from ..contracts.service_provider import ServiceProvider
from ..contracts import AsyncCommand, AsyncQuery, Command, Query

TResponse = TypeVar("TResponse")
# Updated TQuery to bind to a Union of Query[TResponse] and AsyncQuery[TResponse]
TQuery = TypeVar("TQuery", bound=Union[Query[TResponse], AsyncQuery[TResponse]])
# Updated TCommand to bind to a Union of Command and AsyncCommand
TCommand = TypeVar("TCommand", bound=Union[Command, AsyncCommand])


class RequestHandlerBase(Protocol):
    async def __call__(
        self, request: Any, service_provider: ServiceProvider
    ) -> Awaitable[Any]:
        raise NotImplementedError


class QueryHandlerWrapper(RequestHandlerBase, Protocol, Generic[TResponse]):
    async def __call__(
        self,
        request: Union[Query[TResponse], AsyncQuery[TResponse]],
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
            Union[QueryHandler[TQuery, TResponse], AsyncQueryHandler[TQuery, TResponse]],
            service_provider.get(type(request)),
        )
        if inspect.iscoroutinefunction(actual_handler.__call__):
            return await actual_handler(request)
        else:
            # If actual_handler is sync, its result is TResponse.
            # Since this wrapper method is async def, Python wraps it in Awaitable[TResponse].
            return actual_handler(request)


# Making CommandHandlerWrapper consistent by inheriting RequestHandlerBase
class CommandHandlerWrapper(RequestHandlerBase, Protocol): # Added Generic[TCommand] if TCommand is used here, but it's not in the __call__ signature directly
    async def __call__(
        self,
        request: Union[Command, AsyncCommand], # Using Union for broader compatibility at protocol level
        service_provider: ServiceProvider
    ) -> Awaitable[None]:
        raise NotImplementedError


class CommandHandlerWrapperImpl(CommandHandlerWrapper, Generic[TCommand]):
    async def __call__(
        self, request: TCommand, service_provider: ServiceProvider
    ) -> Awaitable[None]:
        actual_handler = cast(
            Union[CommandHandler[TCommand], AsyncCommandHandler[TCommand]],
            service_provider.get(type(request)),
        )
        if inspect.iscoroutinefunction(actual_handler.__call__):
            await actual_handler(request)
        else:
            actual_handler(request)
        return None # Explicit return None, becomes Awaitable[None]
