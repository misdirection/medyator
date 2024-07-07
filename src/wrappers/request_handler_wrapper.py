from typing import Any, Generic, Protocol, TypeVar, cast

from ..request_handler import QueryHandler

from ..contracts.service_provider import ServiceProvider
from ..contracts.request import Command, Query

TQuery = TypeVar("TQuery", bound=Query)
TResponse = TypeVar("TResponse")

class RequestHandlerBase(Protocol):
    def __call__(self, request: Any, service_provider: ServiceProvider) -> Any:
        raise NotImplementedError


class QueryHandlerWrapper(RequestHandlerBase, Generic[TResponse]):
    def __call__(self, request: Query[TResponse], service_provider: ServiceProvider) -> TResponse:
        raise NotImplementedError

class QueryHandlerWrapperImpl(QueryHandlerWrapper, Generic[TQuery, TResponse]):
    def __call__(self, request: Query[TResponse], service_provider: ServiceProvider) -> TResponse:

        handler = cast(QueryHandler, service_provider.get(request))
        return handler(request)


# class RequestHandlerWrapper (Generic[TRequest]):
#     def __call__(self, request: TRequest) -> None:
#         raise NotImplementedError


# class RequestHandlerWrapperImpl(RequestHandlerWrapper):
#     def __call__(self, request: Request) -> None:
#         raise NotImplementedError
