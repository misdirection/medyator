from abc import ABC
from typing import Callable, Dict, Type, TypeVar, Union, cast, overload, Awaitable # Added Awaitable

from .contracts import BaseRequest, Command, Query, ServiceProvider, AsyncCommand, AsyncQuery # Added Async types
from .errors import HandlerNotFound
# Removed direct import of sync handlers, wrappers will handle dispatch
# from .request_handler import CommandHandler, QueryHandler
from .sender import Sender
from .wrappers import (
    CommandHandlerWrapper, # This is now the generic one handling sync/async
    QueryHandlerWrapper,   # This is now the generic one handling sync/async
    RequestHandlerBase,    # Base for type hint in HandlerContainer
)

# Handler type hint is not strictly needed here anymore as wrappers are opaque
TResponse = TypeVar("TResponse")


class MedyatorBase(Sender, ABC): # Sender itself will become async
    pass


class HandlerContainer(Dict[Type[BaseRequest], RequestHandlerBase]): # RequestHandlerBase needs to be compatible
    def get_or_add(
        self, key: Type[BaseRequest], factory: Callable[[], RequestHandlerBase]
    ) -> RequestHandlerBase:
        if key not in self:
            self[key] = factory()
        return self[key]


class Medyator(MedyatorBase):
    def __init__(self, service_provider: ServiceProvider) -> None:
        self.__service_provider = service_provider
        # The values in __handlers are CommandHandlerWrapper or QueryHandlerWrapper instances
        self.__handlers: HandlerContainer = HandlerContainer()


    @overload
    async def send(self, request: Command) -> None: ... # Changed to async, returns None directly

    @overload
    async def send(self, request: Query[TResponse]) -> TResponse: ... # Changed to async

    # Overloads for Async types (optional but good for clarity if they differ in return type nuances)
    # If AsyncCommand always returns None and AsyncQuery[TResponse] always TResponse,
    # existing overloads might suffice due to structural typing if AsyncCommand/Query are subtypes.
    # However, being explicit is safer.
    @overload
    async def send(self, request: AsyncCommand) -> None: ...

    @overload
    async def send(self, request: AsyncQuery[TResponse]) -> TResponse: ...

    async def send(
        self, request: Union[Command, Query[TResponse], AsyncCommand, AsyncQuery[TResponse]]
    ) -> Union[None, TResponse]: # Return type is now direct, not Awaitable, due to async def
        try:
            # isinstance checks for Command will also catch AsyncCommand if it's a subclass.
            # Similarly for Query and AsyncQuery.
            if isinstance(request, (Command, AsyncCommand)):
                # CommandHandlerWrapper is now the one that handles both sync and async commands
                handler_wrapper = cast(
                    CommandHandlerWrapper[Command], # Use base Command type for the wrapper
                    self.__handlers.get_or_add(
                        type(request),
                        # Pass the specific command type to the wrapper if it needs it for TCommand
                        # The current CommandHandlerWrapper is Generic[TCommand]
                        # lambda: CommandHandlerWrapper[type(request)]() -> This was the old error
                        lambda: CommandHandlerWrapper(), # Correct instantiation
                    ),
                )
                # The handler_wrapper.__call__ is now async
                await handler_wrapper(request, self.__service_provider)
                return None
            elif isinstance(request, (Query, AsyncQuery)):
                # QueryHandlerWrapper handles both sync and async queries
                handler_wrapper = cast(
                    QueryHandlerWrapper[Query[TResponse], TResponse], # Use base Query type
                    self.__handlers.get_or_add(
                        type(request),
                        lambda: QueryHandlerWrapper(), # Correct instantiation
                    ),
                )
                # The handler_wrapper.__call__ is now async
                return await handler_wrapper(request, self.__service_provider)
            else:
                # This path should ideally not be reached if request types are constrained
                raise TypeError(f"Unsupported request type: {type(request).__name__}")
        except KeyError: # This might occur if type(request) is not in __handlers after get_or_add fails unexpectedly
            raise HandlerNotFound.for_request(request)
        # Note: Removed type: ignore comments as the wrapper instantiation is now simpler.
        # The `cast` is used to satisfy the type checker for the specific `handler_wrapper` variable.
        # The wrapper's `__call__` method is responsible for handling the request type correctly.

