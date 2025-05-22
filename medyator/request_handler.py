from typing import Generic, TypeVar

from .contracts import Command, Query

TCommand = TypeVar("TCommand", bound=Command)
TQuery = TypeVar("TQuery", bound=Query)
TResponse = TypeVar("TResponse")


class CommandHandler(Generic[TCommand]):
    def __call__(self, request: TCommand) -> None:
        raise NotImplementedError


class QueryHandler(Generic[TQuery, TResponse]):
    def __call__(self, request: TQuery) -> TResponse:
        raise NotImplementedError


# Type variables for Async Handlers
TAsyncCommand = TypeVar("TAsyncCommand", bound="AsyncCommand")
TAsyncQuery = TypeVar("TAsyncQuery", bound="AsyncQuery") # TResponse is bound by AsyncQuery's TResponse


class AsyncCommandHandler(Generic[TAsyncCommand]):
    async def handle(self, request: TAsyncCommand) -> None:
        """Asynchronously handles an async command."""
        raise NotImplementedError


class AsyncQueryHandler(Generic[TAsyncQuery, TResponse]):
    async def handle(self, request: TAsyncQuery) -> TResponse:
        """Asynchronously handles an async query and returns a response."""
        raise NotImplementedError

# Need to import AsyncCommand and AsyncQuery for the TypeVar bounds if used directly
# from .contracts import AsyncCommand, AsyncQuery
# However, forward references (strings) are often better for TypeVars to avoid circular imports
# if request_handler.py were imported by contracts.py for some reason.
# In this case, contracts.py is imported by request_handler.py, so direct imports are fine.
from .contracts import AsyncCommand, AsyncQuery # Added this line
