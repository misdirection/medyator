import inspect # For checking coroutine functions
from typing import TypeVar, Generic, Type, Optional, Any, Awaitable
from ..contracts import Command, Query, ServiceProvider, BaseRequest, AsyncCommand, AsyncQuery
from ..request_handler import (
    CommandHandler,
    QueryHandler,
    AsyncCommandHandler,
    AsyncQueryHandler,
)

TCommand = TypeVar("TCommand", bound=Command)
TAsyncCommand = TypeVar("TAsyncCommand", bound=AsyncCommand)

TQuery = TypeVar("TQuery", bound=Query[Any]) # Ensure Query is generic
TAsyncQuery = TypeVar("TAsyncQuery", bound=AsyncQuery[Any]) # Ensure AsyncQuery is generic

TResponse = TypeVar("TResponse")

# Protocol for the __call__ method, now async
class AsyncRequestHandlerCallable(Generic[TRequest, TResponse]): # type: ignore
    async def __call__(self, request: TRequest, service_provider: ServiceProvider) -> TResponse:
        raise NotImplementedError

class RequestHandlerBase: # Common base, __call__ will be async
    # This base can be empty or define common structure if needed.
    # The actual __call__ signature will be in the specific wrappers.
    pass

class CommandHandlerWrapper(RequestHandlerBase, Generic[TCommand]): # TCommand can be sync or async
    def __init__(self) -> None:
        # Stores resolved handler instance (sync or async)
        self._handler_instance: Optional[AnyCommandHandler] = None 

    async def __call__(self, request: TCommand, service_provider: ServiceProvider) -> None:
        if self._handler_instance is None:
            resolved_handler = service_provider.get(type(request))
            # We expect CommandHandler or AsyncCommandHandler
            if not (isinstance(resolved_handler, CommandHandler) or 
                    isinstance(resolved_handler, AsyncCommandHandler)):
                raise TypeError(
                    f"Resolved handler for {type(request).__name__} is not a "
                    f"CommandHandler or AsyncCommandHandler. Got {type(resolved_handler).__name__}."
                )
            self._handler_instance = resolved_handler
        
        # Now self._handler_instance is set
        if isinstance(self._handler_instance, AsyncCommandHandler) and \
           hasattr(self._handler_instance, 'handle') and \
           inspect.iscoroutinefunction(self._handler_instance.handle):
            await self._handler_instance.handle(request) # type: ignore
        elif isinstance(self._handler_instance, CommandHandler) and \
             callable(self._handler_instance): # Check if it's callable (i.e. has __call__)
            self._handler_instance(request) # type: ignore
        else:
            # This should not happen if the initial type check and DI registration are correct
            raise TypeError(
                f"Handler for {type(request).__name__} is not a valid sync or async command handler."
            )

class QueryHandlerWrapper(RequestHandlerBase, Generic[TQuery, TResponse]): # TQuery can be sync or async
    def __init__(self) -> None:
        # Stores resolved handler instance (sync or async)
        self._handler_instance: Optional[AnyQueryHandler] = None

    async def __call__(self, request: TQuery, service_provider: ServiceProvider) -> TResponse:
        if self._handler_instance is None:
            resolved_handler = service_provider.get(type(request))
            if not (isinstance(resolved_handler, QueryHandler) or
                    isinstance(resolved_handler, AsyncQueryHandler)):
                raise TypeError(
                    f"Resolved handler for {type(request).__name__} is not a "
                    f"QueryHandler or AsyncQueryHandler. Got {type(resolved_handler).__name__}."
                )
            self._handler_instance = resolved_handler # type: ignore
        
        # Now self._handler_instance is set
        if isinstance(self._handler_instance, AsyncQueryHandler) and \
           hasattr(self._handler_instance, 'handle') and \
           inspect.iscoroutinefunction(self._handler_instance.handle):
            return await self._handler_instance.handle(request) # type: ignore
        elif isinstance(self._handler_instance, QueryHandler) and \
             callable(self._handler_instance):
            return self._handler_instance(request) # type: ignore
        else:
            raise TypeError(
                f"Handler for {type(request).__name__} is not a valid sync or async query handler."
            )

# Type Aliases for convenience and for Medyator.py
AnyCommandHandler = CommandHandler[Any] | AsyncCommandHandler[Any]
AnyQueryHandler = QueryHandler[Any, Any] | AsyncQueryHandler[Any, Any]

# These Impl versions are what Medyator.py will use.
# They are now the same as the base wrappers due to merging sync/async logic.
CommandHandlerWrapperImpl = CommandHandlerWrapper
QueryHandlerWrapperImpl = QueryHandlerWrapper

# Type variable for AsyncRequestHandlerCallable
TRequest = TypeVar("TRequest", bound=BaseRequest)

__all__ = [
    "CommandHandlerWrapper",
    "QueryHandlerWrapper",
    "CommandHandlerWrapperImpl",
    "QueryHandlerWrapperImpl",
    "RequestHandlerBase",
    "AsyncRequestHandlerCallable" # Exporting the protocol if needed by Medyator for typing
]
