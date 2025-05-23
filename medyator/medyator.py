from abc import ABC
from typing import Awaitable, Callable, Dict, Type, TypeVar, Union, cast, overload

from .contracts import (
    AsyncCommand,
    AsyncQuery,
    BaseRequest,
    Command,
    Query,
    ServiceProvider,
)
from .errors import HandlerNotFound
from .request_handler import (
    AsyncCommandHandler,
    AsyncQueryHandler,
    CommandHandler,
    QueryHandler,
)
from .sender import Sender
from .wrappers import (
    CommandHandlerWrapper,
    CommandHandlerWrapperImpl,
    QueryHandlerWrapper,
    QueryHandlerWrapperImpl,
    RequestHandlerBase,
)

Handler = Union[QueryHandler, CommandHandler, AsyncQueryHandler, AsyncCommandHandler]
TResponse = TypeVar("TResponse")
TCommand = TypeVar("TCommand", bound=Union[Command, AsyncCommand])
TQuery = TypeVar("TQuery", bound=Union[Query, AsyncQuery])


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
    async def send(self, request: Command) -> Awaitable[None]: ...

    @overload
    async def send(self, request: Query[TResponse]) -> Awaitable[TResponse]: ...

    @overload
    async def send(self, request: AsyncCommand) -> Awaitable[None]: ...

    @overload
    async def send(self, request: AsyncQuery[TResponse]) -> Awaitable[TResponse]: ...

    async def send(
        self, request: Union[Command, Query[TResponse], AsyncCommand, AsyncQuery[TResponse]]
    ) -> Union[Awaitable[None], Awaitable[TResponse]]:
        try:
            if isinstance(request, (Command, AsyncCommand)):
                handler = cast(
                    CommandHandlerWrapper,
                    self.__handlers.get_or_add(
                        type(request),
                        lambda: CommandHandlerWrapperImpl[type(request)](),  # type: ignore
                    ),
                )
                # Assuming handler.__call__ (the wrapper's call) will be async and return None for commands.
                await handler(request, self.__service_provider)
                return None # Becomes Awaitable[None] as send is async def.
            elif isinstance(request, (Query, AsyncQuery)):
                handler = cast(
                    QueryHandlerWrapper[TResponse],  # type: ignore
                    self.__handlers.get_or_add(
                        type(request),
                        lambda: QueryHandlerWrapperImpl[type(request), TResponse](),  # type: ignore
                    ),
                )
                # Assuming handler.__call__ (the wrapper's call) will be async and return TResponse for queries.
                return await handler(request, self.__service_provider)
            else:
                raise TypeError("Unsupported request type")
        except KeyError:
            raise HandlerNotFound.for_request(request)

