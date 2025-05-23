import inspect
from typing import Any, Awaitable, Generic, Protocol, TypeVar, cast # Removed Union as it's no longer needed in this file's type hints after simplification

from ..request_handler import (
    CommandHandler,
    QueryHandler,
) # Removed AsyncCommandHandler, AsyncQueryHandler
from ..contracts.service_provider import ServiceProvider
from ..contracts import Command, Query # Removed AsyncCommand, AsyncQuery

TResponse = TypeVar("TResponse")
# TQuery is a specific type of Query that returns TResponse
TQuery = TypeVar("TQuery", bound=Query[TResponse])
# TCommand is a specific type of Command
TCommand = TypeVar("TCommand", bound=Command)


class RequestHandlerBase(Protocol):
    async def __call__(
        self, request: Any, service_provider: ServiceProvider
    ) -> Awaitable[Any]:
        raise NotImplementedError


class QueryHandlerWrapper(RequestHandlerBase, Protocol, Generic[TResponse]):
    async def __call__(
        self,
        request: Query[TResponse], # Removed Union with AsyncQuery
        service_provider: ServiceProvider,
    ) -> Awaitable[TResponse]:
        raise NotImplementedError


class QueryHandlerWrapperImpl(
    QueryHandlerWrapper[TResponse], Generic[TQuery, TResponse]
):
    async def __call__(
        self, request: TQuery, service_provider: ServiceProvider
    ) -> Awaitable[TResponse]:
        actual_handler = cast( # Removed Union with AsyncQueryHandler
            QueryHandler[TQuery, TResponse],
            service_provider.get(request), # Changed from type(request) to request
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
        request: Command, # Removed Union with AsyncCommand
        service_provider: ServiceProvider
    ) -> Awaitable[None]:
        raise NotImplementedError


class CommandHandlerWrapperImpl(CommandHandlerWrapper, Generic[TCommand]):
    async def __call__(
        self, request: TCommand, service_provider: ServiceProvider
    ) -> Awaitable[None]:
        actual_handler = cast( # Removed Union with AsyncCommandHandler
            CommandHandler[TCommand],
            service_provider.get(request), # Changed from type(request) to request
        )
        if inspect.iscoroutinefunction(actual_handler.__call__):
            await actual_handler(request)
        else:
            actual_handler(request)
        return None # Explicit return None, becomes Awaitable[None]
