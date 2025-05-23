from typing import Awaitable, Generic, TypeVar

from .contracts import Command, Query

# Clarification:
# Concrete implementations of CommandHandler and QueryHandler can define __call__
# as either a standard synchronous method or as an 'async def' coroutine.
# The Medyator pipeline will correctly handle either approach.

TCommand = TypeVar("TCommand", bound=Command)
TQuery = TypeVar("TQuery", bound=Query)
TResponse = TypeVar("TResponse")


class CommandHandler(Generic[TCommand]):
    """
    Handles a command.
    The __call__ method can be implemented as a standard synchronous method
    or as an 'async def' coroutine.
    """
    def __call__(self, request: TCommand) -> None:
        raise NotImplementedError


class QueryHandler(Generic[TQuery, TResponse]):
    """
    Handles a query and returns a response.
    The __call__ method can be implemented as a standard synchronous method
    or as an 'async def' coroutine.
    """
    def __call__(self, request: TQuery) -> TResponse:
        raise NotImplementedError
