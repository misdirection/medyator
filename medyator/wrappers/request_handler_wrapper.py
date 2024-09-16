from typing import Any, Generic, Protocol, TypeVar, cast

from ..request_handler import QueryHandler, CommandHandler

from ..contracts.service_provider import ServiceProvider
from ..contracts import Command, Query

TQuery = TypeVar("TQuery", bound=Query)
TCommand = TypeVar("TCommand", bound=Command)
TResponse = TypeVar("TResponse")


class RequestHandlerBase(Protocol):
    def __call__(self, request: Any, service_provider: ServiceProvider) -> Any:
        raise NotImplementedError


class QueryHandlerWrapper(RequestHandlerBase, Generic[TResponse]):
    def __call__(
        self, request: Query[TResponse], service_provider: ServiceProvider
    ) -> TResponse:
        raise NotImplementedError


class QueryHandlerWrapperImpl(QueryHandlerWrapper, Generic[TQuery, TResponse]):
    def __call__(
        self, request: Query[TResponse], service_provider: ServiceProvider
    ) -> TResponse:
        handler = cast(QueryHandler, service_provider.get(request))
        return handler(request)


class CommandHandlerWrapper:
    def __call__(self, request: Command, service_provider: ServiceProvider) -> None:
        raise NotImplementedError


class CommandHandlerWrapperImpl(CommandHandlerWrapper, Generic[TCommand]):
    def __call__(self, request: Command, service_provider: ServiceProvider) -> None:
        handler = cast(CommandHandler, service_provider.get(request))
        return handler(request)
