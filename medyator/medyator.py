from abc import ABC
from typing import Any, Callable, Dict, Type, TypeVar, Union, cast

from .contracts import BaseRequest, Query, Command, ServiceProvider
from .errors import HandlerNotFound
from .request_handler import QueryHandler, CommandHandler
from .sender import Sender
from .wrappers import (
    RequestHandlerBase,
    QueryHandlerWrapper,
    QueryHandlerWrapperImpl,
    CommandHandlerWrapper,
    CommandHandlerWrapperImpl,
)

Handler = Union[QueryHandler, CommandHandler]
TResponse = TypeVar("TResponse")


class MedyatorBase(Sender, ABC):
    pass


class HandlerContainer(Dict[Type[BaseRequest], RequestHandlerBase]):
    def get_or_add(self, key: Type[BaseRequest], factory: Callable) -> RequestHandlerBase:
        if key not in self:
            self[key] = factory()
        return self[key]


class Medyator(MedyatorBase):
    def __init__(self, service_provider: ServiceProvider) -> None:
        self.__service_provider = service_provider
        self.__handlers = HandlerContainer()

    def send_command(self, request: Command) -> None:
        try:
            handler = cast(
                CommandHandlerWrapper,
                self.__handlers.get_or_add(type(request), lambda: CommandHandlerWrapperImpl[type(request)]()),
            )
            return handler(request, self.__service_provider)
        except KeyError:
            raise HandlerNotFound.for_request(request)

    def send_query(self, request: Query[TResponse]) -> TResponse:
        try:
            handler = cast(
                QueryHandlerWrapper,
                self.__handlers.get_or_add(type(request), lambda: QueryHandlerWrapperImpl[type(request), TResponse]()),
            )

            return handler(request, self.__service_provider)
        except KeyError:
            raise HandlerNotFound.for_request(request)
