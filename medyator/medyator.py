from abc import ABC
from typing import Callable, Dict, Type, TypeVar, Union, cast, overload

from .contracts import BaseRequest, Command, Query, ServiceProvider
from .errors import HandlerNotFound
from .request_handler import CommandHandler, QueryHandler
from .sender import Sender
from .wrappers import (
    CommandHandlerWrapper,
    CommandHandlerWrapperImpl,
    QueryHandlerWrapper,
    QueryHandlerWrapperImpl,
    RequestHandlerBase,
)

Handler = Union[QueryHandler, CommandHandler]
TResponse = TypeVar("TResponse")


class MedyatorBase(Sender, ABC):
    pass


class HandlerContainer(Dict[Type[BaseRequest], RequestHandlerBase]):
    def get_or_add(
        self, key: Type[BaseRequest], factory: Callable[[], RequestHandlerBase]
    ) -> RequestHandlerBase:
        if key not in self:
            self[key] = factory()
        return self[key]


class Medyator(MedyatorBase):
    def __init__(self, service_provider: ServiceProvider) -> None:
        self.__service_provider = service_provider
        self.__handlers = HandlerContainer()

    @overload
    def send(self, request: Command) -> None: ...

    @overload
    def send(self, request: Query[TResponse]) -> TResponse: ...

    def send(self, request: Union[Command, Query[TResponse]]) -> Union[None, TResponse]:
        try:
            if isinstance(request, Command):
                handler = cast(
                    CommandHandlerWrapper,
                    self.__handlers.get_or_add(
                        type(request),
                        lambda: CommandHandlerWrapperImpl[type(request)](),
                    ),
                )
                handler(request, self.__service_provider)
                return None
            elif isinstance(request, Query):
                handler = cast(
                    QueryHandlerWrapper[TResponse],
                    self.__handlers.get_or_add(
                        type(request),
                        lambda: QueryHandlerWrapperImpl[type(request), TResponse](),
                    ),
                )
                return handler(request, self.__service_provider)
            else:
                raise TypeError("Unsupported request type")
        except KeyError:
            raise HandlerNotFound.for_request(request)

