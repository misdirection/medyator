from abc import ABC, abstractmethod
from typing import Any, Type, Union
from .request import BaseRequest
from .request_handler import RequestHandler, RequestHandlerWithResponse

HandlerType = Union[RequestHandler, RequestHandlerWithResponse]


class Medyator(ABC):
    @abstractmethod
    def register_handler(self, request: Type[BaseRequest], handler: HandlerType) -> None:
        pass

    @abstractmethod
    def send(self, request: BaseRequest) -> Any:
        pass
