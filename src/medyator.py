from abc import ABC, abstractmethod
from typing import Any, Type, Union
from .request import BaseRequest, RequestWithResponse, Request
from .request_handler import RequestHandler, RequestHandlerWithResponse

HandlerType = Union[RequestHandler, RequestHandlerWithResponse]
RequestType = Union[Request, RequestWithResponse]

class Medyator(ABC):
    @abstractmethod
    def register_handler(self, request: Type[RequestType], handler: HandlerType) -> None:
        pass

    @abstractmethod
    def send(self, request: RequestType) -> Any:
        pass
