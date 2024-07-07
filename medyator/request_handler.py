from typing import Generic, TypeVar
from .contracts import Query, Command

TCommand = TypeVar("TCommand", bound=Command)
TQuery = TypeVar("TQuery", bound=Query)
TResponse = TypeVar("TResponse")


class CommandHandler(Generic[TCommand]):
    def __call__(self, request: TCommand) -> None:
        raise NotImplementedError


class QueryHandler(Generic[TQuery, TResponse]):
    def __call__(self, request: TQuery) -> TResponse:
        raise NotImplementedError
