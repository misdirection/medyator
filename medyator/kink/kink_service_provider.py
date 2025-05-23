from typing import Union, cast, Any

from kink import Container

from ..contracts import (
    AsyncCommand,
    AsyncQuery,
    BaseRequest,
    Command,
    Query,
    ServiceProvider,
)
from ..medyator import Medyator
from ..request_handler import (
    AsyncCommandHandler,
    AsyncQueryHandler,
    CommandHandler,
    QueryHandler,
)

# Updated Handler type alias to include asynchronous handlers
Handler = Union[
    CommandHandler[Any, Any], # Using Any for generic params for brevity in Union
    QueryHandler[Any, Any, Any],
    AsyncCommandHandler[Any, Any],
    AsyncQueryHandler[Any, Any, Any],
]
# A more precise Handler might be too complex for a simple alias here if we try to keep all typevars.
# The goal is that the .get method returns "some kind of handler".
# The consuming code (wrappers) will cast to a more specific handler type.
# For simplicity, we can also use Handler = Any here and rely on casts in wrappers,
# but a Union is slightly more descriptive.
# Let's refine Handler to be more practical for the cast:
AnyHandler = Union[CommandHandler, QueryHandler, AsyncCommandHandler, AsyncQueryHandler]


class KinkServiceProvider(ServiceProvider):
    def __init__(self, di: Container) -> None:
        self.di = di

    def get(self, request: BaseRequest) -> AnyHandler: # Return type uses the updated Handler alias
        # The DI container (kink) is expected to be populated with request types as keys
        # and their corresponding handler instances as values.
        # e.g., container[MyCommand] = MyCommandHandler()
        # e.g., container[MyAsyncQuery] = MyAsyncQueryHandler()
        
        # Kink's __getitem__ can take a type directly.
        handler_instance = self.di[type(request)]
        
        # The returned instance should conform to one of the types in the AnyHandler union.
        # The cast here is mostly for type checking systems; kink returns the registered instance.
        return cast(AnyHandler, handler_instance)


def add_medyator(self) -> None:
    medyator = Medyator(KinkServiceProvider(self))
    self[Medyator] = medyator


setattr(Container, "add_medyator", add_medyator)
