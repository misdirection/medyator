from typing import Generic, TypeVar
from .request import Request, RequestWithResponse

TRequest = TypeVar("TRequest", bound=Request)
TResponse = TypeVar("TResponse")
TRequestWithResponse = TypeVar("TRequestWithResponse", bound=RequestWithResponse)


class RequestHandler(Generic[TRequest]):
    def __call__(self, request: TRequest) -> None:
        raise NotImplementedError


class RequestHandlerWithResponse(Generic[TRequestWithResponse, TResponse]):
    def __call__(self, request: TRequestWithResponse) -> TResponse:
        raise NotImplementedError
