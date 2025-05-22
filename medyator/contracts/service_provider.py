from typing import Protocol, Union, Type, Any
from ..request_handler import (
    CommandHandler,
    QueryHandler,
    AsyncCommandHandler,
    AsyncQueryHandler,
)
from .request import BaseRequest

# Represents any handler type (sync or async, command or query)
Handler = Union[
    CommandHandler[Any],
    QueryHandler[Any, Any],
    AsyncCommandHandler[Any],
    AsyncQueryHandler[Any, Any],
]


class ServiceProvider(Protocol):
    def get(self, request_type: Type[BaseRequest]) -> Handler:
        raise NotImplementedError
