from kink import di
from typing import Type, Union, cast
from ..contracts import ServiceProvider, BaseRequest, Command, Query
from ..request_handler import CommandHandler, QueryHandler

Handler = Union[CommandHandler, QueryHandler]

class KinkServiceProvider(ServiceProvider):
    def __init__(self) -> None:
        self.di = di

    def get(self, request: BaseRequest) -> Handler:
        if isinstance(request, Command):
            return cast(CommandHandler, self.di[request.__class__])
        elif isinstance(request, Query):
            return cast(QueryHandler, self.di[request.__class__])
        else:
            raise NotImplementedError

    def register_handler(self, request_type: Type[BaseRequest], handler: Handler) -> None:
        self.di[request_type] = handler
