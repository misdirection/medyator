from typing import Protocol, Type, Union
from ..request_handler import CommandHandler, QueryHandler
from .request import BaseRequest

Handler = Union[CommandHandler, QueryHandler]


class ServiceProvider(Protocol):
    def get(self, request: BaseRequest) -> Handler:
        ...
