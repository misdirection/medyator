import types
from kink import Container
from typing import Union, cast

from ..medyator import Medyator
from ..contracts import ServiceProvider, BaseRequest, Command, Query
from ..request_handler import CommandHandler, QueryHandler

Handler = Union[CommandHandler, QueryHandler]

class KinkServiceProvider(ServiceProvider):
    def __init__(self, di: Container) -> None:
        self.di = di

    def get(self, request: BaseRequest) -> Handler:
        if isinstance(request, Command):
            return cast(CommandHandler, self.di[type(request)])
        elif isinstance(request, Query):
            return cast(QueryHandler, self.di[type(request)])
        else:
            raise NotImplementedError


def add_medyator(self) -> None:
    medyator = Medyator(KinkServiceProvider(self))
    self[Medyator] = medyator

setattr(Container, "add_medyator", add_medyator)
