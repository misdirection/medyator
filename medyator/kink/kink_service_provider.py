from typing import Union, cast

from kink import Container

from ..contracts import (
    BaseRequest,
    Command,
    Query,
    ServiceProvider,
)
from ..medyator import Medyator
from ..request_handler import (
    CommandHandler,
    QueryHandler,
)

Handler = Union[CommandHandler, QueryHandler]


class KinkServiceProvider(ServiceProvider):
    def __init__(self, di: Container) -> None:
        self.di = di

    def get(self, request: BaseRequest) -> Handler:
        # The DI container (kink) is expected to be populated with request types as keys
        # and their corresponding handler instances as values.
        # e.g., container[MyCommand] = MyCommandHandler()
        # The handler instance itself can be a sync or async handler (by having an async __call__).
        
        # Kink's __getitem__ can take a type directly.
        handler_instance = self.di[type(request)]
        
        # The returned instance should conform to one of the types in the Handler union.
        # The cast here is mostly for type checking systems; kink returns the registered instance.
        return cast(Handler, handler_instance)


def add_medyator(self) -> None:
    medyator = Medyator(KinkServiceProvider(self))
    self[Medyator] = medyator


setattr(Container, "add_medyator", add_medyator)
