from abc import ABC
from typing import Generic, TypeVar

TResponse = TypeVar("TResponse")


class BaseRequest(ABC):
    pass


class Command(BaseRequest):
    pass


class Query(Generic[TResponse], BaseRequest):
    pass


# Async contracts
class AsyncCommand(Command):
    """Base class for asynchronous commands."""
    pass


class AsyncQuery(Query[TResponse], Generic[TResponse]):
    """Base class for asynchronous queries that return a value of type TResponse."""
    pass
