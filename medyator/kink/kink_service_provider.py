from typing import Type, Union, cast

from typing import Type, cast # Removed Union as it's not directly used here anymore

from kink import Container
from kink.errors import ServiceNotFoundError

# Import the correct Handler type from contracts
from ..contracts import BaseRequest, Command, Query, ServiceProvider, Handler
from ..errors import HandlerNotFound
from ..registration import HandlerRegistry
# request_handler imports are not directly needed here if Handler from contracts is used.

# Local Handler alias is no longer needed if using the one from contracts.


class KinkServiceProvider(ServiceProvider):
    def __init__(self, di: Container, registry: HandlerRegistry) -> None:
        self.di = di
        self.registry = registry

    def get(self, request_type: Type[BaseRequest]) -> Handler: # Return type uses contracts.Handler
        # The type of resolved_handler_type_from_registry can be complex,
        # e.g. Type[CommandHandler[SpecificCommand]] or Type[AsyncQueryHandler[SpecificQuery, int]]
        # So, using 'Any' or a broader Type[Any] for the intermediate variable might be practical
        # if direct typing is too complex for the registry's methods' current return types.
        # However, registry methods are typed as `-> Type[CommandHandler[TCommand]] | None` etc.
        
        resolved_handler_type_from_registry: Type[Handler] | None = None # Use the contracts.Handler

        if issubclass(request_type, Command): # This includes AsyncCommand
            # get_command_handler returns Type[CommandHandler[TCommand]] or Type[AsyncCommandHandler[TAsyncCommand]]
            # based on how it's registered or if registry is updated for async.
            # Assuming registry methods are updated to return appropriate async/sync handler types.
            # The registry currently returns CommandHandler or QueryHandler, not their async counterparts.
            # This will need to be addressed in HandlerRegistry or here by trying both.
            # For now, let's assume registry returns the correct type (sync or async).
            # The `type: ignore` was there because the registry.get_command_handler's TCommand
            # might not perfectly align with request_type in the static checker's eyes.
            resolved_handler_type_from_registry = self.registry.get_command_handler(request_type) # type: ignore
        elif issubclass(request_type, Query): # This includes AsyncQuery
            resolved_handler_type_from_registry = self.registry.get_query_handler(request_type) # type: ignore
        else:
            raise TypeError(f"Unsupported request type: {request_type.__name__}")

        if resolved_handler_type_from_registry is None:
            raise HandlerNotFound.for_request_type(request_type)

        try:
            # Resolve the handler instance from kink DI container
            # Assuming handlers are registered by their own type in kink
            # The resolved_handler_type_from_registry is Type[SpecificHandler],
            # and di[Type[SpecificHandler]] should return an instance of SpecificHandler.
            # The cast ensures the return type matches the ServiceProvider.get signature.
            return cast(Handler, self.di[resolved_handler_type_from_registry])
        except ServiceNotFoundError:
            # This means the resolved_handler_type_from_registry (e.g., MyQueryHandler) found in the registry
            # was not actually registered in the kink DI container.
            raise HandlerNotFound(
                f"Handler type {handler_type.__name__} for request {request_type.__name__} "
                f"was found in registry but not registered in the DI container."
            )
        except Exception as e: # Catch other potential DI errors
            raise HandlerNotFound(
                f"Could not resolve handler {handler_type.__name__} for request {request_type.__name__} "
                f"from DI container. Original error: {e}"
            )
