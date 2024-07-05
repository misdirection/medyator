from typing import Dict, Type, Any
from .request import BaseRequest
from .medyator import Medyator, HandlerType, RequestType
from .errors import RequestAlreadyRegistered, HandlerNotFound
from .request_handler import RequestHandler, RequestHandlerWithResponse


class GenericMedyator(Medyator):
    def __init__(self) -> None:
        self._handlers: Dict[Type[RequestType], HandlerType] = {}

    def register_handler(self, request: Type[RequestType], handler: HandlerType) -> None:
        if request in self._handlers:
            raise RequestAlreadyRegistered.for_command(request.__name__)

        self._handlers[request] = handler

    def send(self, request: RequestType) -> Any:
        try:
            handler = self._handlers[type(request)]
            if isinstance(handler, RequestHandler):
                handler(request)
            elif isinstance(handler, RequestHandlerWithResponse):
                return handler(request)
        except KeyError:
            raise HandlerNotFound.for_command(request)



medyator = GenericMedyator()
