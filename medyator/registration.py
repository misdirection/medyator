from typing import Dict, Type, TypeVar, Callable, Any, Union, cast
import inspect # To check for async methods
from .contracts import Command, Query, BaseRequest, AsyncCommand, AsyncQuery
from .request_handler import (
    CommandHandler,
    QueryHandler,
    AsyncCommandHandler,
    AsyncQueryHandler,
)

# Type variables for requests
TRequest = TypeVar("TRequest", bound=BaseRequest) # General request
TCommand = TypeVar("TCommand", bound=Command) # Sync command
TQuery = TypeVar("TQuery", bound=Query[Any]) # Sync query with any response
TAsyncCommand = TypeVar("TAsyncCommand", bound=AsyncCommand) # Async command
TAsyncQuery = TypeVar("TAsyncQuery", bound=AsyncQuery[Any]) # Async query with any response

# Type variable for responses
TResponse = TypeVar("TResponse")

# Union types for handler types
AnyCommandHandlerType = Union[Type[CommandHandler[Any]], Type[AsyncCommandHandler[Any]]]
AnyQueryHandlerType = Union[Type[QueryHandler[Any, Any]], Type[AsyncQueryHandler[Any, Any]]]
AnyHandlerType = Union[AnyCommandHandlerType, AnyQueryHandlerType]


class HandlerRegistry:
    """
    Stores mappings from request types to their corresponding handler types (sync or async).
    """
    def __init__(self) -> None:
        self._command_handlers: Dict[Type[Command], AnyCommandHandlerType] = {}
        self._query_handlers: Dict[Type[Query[Any]], AnyQueryHandlerType] = {}

    def register_command_handler(
        self,
        command_type: Type[Union[TCommand, TAsyncCommand]], # Accepts Command or AsyncCommand types
        handler_type: Union[Type[CommandHandler[TCommand]], Type[AsyncCommandHandler[TAsyncCommand]]],
    ) -> None:
        """Registers a command handler type (sync or async) for a given command type."""
        if not issubclass(command_type, Command): # Command is base for AsyncCommand too
            raise TypeError(f"{command_type.__name__} must be a subclass of Command or AsyncCommand.")
        
        # Basic check: if command_type is AsyncCommand, handler_type should be AsyncCommandHandler
        # This is not foolproof due to generics but better than nothing.
        is_async_command = issubclass(command_type, AsyncCommand)
        is_async_handler = hasattr(handler_type, 'handle') and inspect.iscoroutinefunction(getattr(handler_type, 'handle', None))
        
        if is_async_command and not is_async_handler:
            raise TypeError(f"Handler {handler_type.__name__} for AsyncCommand {command_type.__name__} must be an AsyncCommandHandler (with async def handle).")
        if not is_async_command and is_async_handler:
             raise TypeError(f"Handler {handler_type.__name__} for Command {command_type.__name__} must be a sync CommandHandler (with __call__).")

        self._command_handlers[command_type] = handler_type # type: ignore

    def register_query_handler(
        self,
        query_type: Type[Union[TQuery, TAsyncQuery]], # Accepts Query or AsyncQuery types
        handler_type: Union[Type[QueryHandler[TQuery, TResponse]], Type[AsyncQueryHandler[TAsyncQuery, TResponse]]],
    ) -> None:
        """Registers a query handler type (sync or async) for a given query type."""
        if not issubclass(query_type, Query): # Query is base for AsyncQuery too
            raise TypeError(f"{query_type.__name__} must be a subclass of Query or AsyncQuery.")

        is_async_query = issubclass(query_type, AsyncQuery)
        is_async_handler = hasattr(handler_type, 'handle') and inspect.iscoroutinefunction(getattr(handler_type, 'handle', None))

        if is_async_query and not is_async_handler:
            raise TypeError(f"Handler {handler_type.__name__} for AsyncQuery {query_type.__name__} must be an AsyncQueryHandler (with async def handle).")
        if not is_async_query and is_async_handler:
            raise TypeError(f"Handler {handler_type.__name__} for Query {query_type.__name__} must be a sync QueryHandler (with __call__).")

        self._query_handlers[query_type] = handler_type # type: ignore

    def get_command_handler(
        self, command_type: Type[Union[TCommand, TAsyncCommand]]
    ) -> Union[Type[CommandHandler[TCommand]], Type[AsyncCommandHandler[TAsyncCommand]], None]:
        """Retrieves the registered command handler type (sync or async) for a given command type."""
        return self._command_handlers.get(command_type) # type: ignore

    def get_query_handler(
        self, query_type: Type[Union[TQuery, TAsyncQuery]]
    ) -> Union[Type[QueryHandler[TQuery, TResponse]], Type[AsyncQueryHandler[TAsyncQuery, TResponse]], None]:
        """Retrieves the registered query handler type (sync or async) for a given query type."""
        return self._query_handlers.get(query_type) # type: ignore

    def clear(self) -> None:
        """Clears all registered handlers. Useful for testing."""
        self._command_handlers.clear()
        self._query_handlers.clear()

# Global instance of the registry for ease of use with decorators
default_handler_registry = HandlerRegistry()

# Type variable for the decorated handler class itself
DecoratedHandlerClass = TypeVar("DecoratedHandlerClass", bound=Type[Any])

def command_handler(
    command_type: Type[Union[Command, AsyncCommand]], registry: HandlerRegistry = default_handler_registry
) -> Callable[[DecoratedHandlerClass], DecoratedHandlerClass]:
    """
    Decorator to register a class as a CommandHandler or AsyncCommandHandler.
    The decorated class must be a subtype of CommandHandler or AsyncCommandHandler.
    """
    if not issubclass(command_type, Command): # Covers AsyncCommand as well
        raise TypeError(f"Command type {command_type.__name__} must be a subclass of Command or AsyncCommand.")

    def decorator(handler_class: DecoratedHandlerClass) -> DecoratedHandlerClass:
        # Perform runtime check to ensure handler_class is appropriate
        is_async_handler_class = hasattr(handler_class, 'handle') and inspect.iscoroutinefunction(getattr(handler_class, 'handle', None))
        is_sync_handler_class = callable(handler_class) and not is_async_handler_class # Simplistic check for __call__

        if not (issubclass(handler_class, CommandHandler) or issubclass(handler_class, AsyncCommandHandler)):
             raise TypeError(f"Decorated class {handler_class.__name__} must be a subclass of CommandHandler or AsyncCommandHandler.")
        
        # This cast is to satisfy the signature of register_command_handler
        # The runtime checks above and in register_command_handler provide safety.
        casted_handler_type = cast(Union[Type[CommandHandler[Any]], Type[AsyncCommandHandler[Any]]], handler_class)
        registry.register_command_handler(command_type, casted_handler_type)
        return handler_class
    return decorator


def query_handler(
    query_type: Type[Union[Query[Any], AsyncQuery[Any]]], registry: HandlerRegistry = default_handler_registry
) -> Callable[[DecoratedHandlerClass], DecoratedHandlerClass]:
    """
    Decorator to register a class as a QueryHandler or AsyncQueryHandler.
    The decorated class must be a subtype of QueryHandler or AsyncQueryHandler.
    """
    if not issubclass(query_type, Query): # Covers AsyncQuery as well
        raise TypeError(f"Query type {query_type.__name__} must be a subclass of Query or AsyncQuery.")

    def decorator(handler_class: DecoratedHandlerClass) -> DecoratedHandlerClass:
        if not (issubclass(handler_class, QueryHandler) or issubclass(handler_class, AsyncQueryHandler)):
            raise TypeError(f"Decorated class {handler_class.__name__} must be a subclass of QueryHandler or AsyncQueryHandler.")
            
        casted_handler_type = cast(Union[Type[QueryHandler[Any, Any]], Type[AsyncQueryHandler[Any, Any]]], handler_class)
        registry.register_query_handler(query_type, casted_handler_type)
        return handler_class
    return decorator

# Remove old type aliases for convenience as they are too simple now
# TCommand = TypeVar("TCommand", bound=Command)
# TQuery = TypeVar("TQuery", bound=Query)
# TResponse = TypeVar("TResponse")

__all__ = [
    "HandlerRegistry",
    "default_handler_registry",
    "command_handler",
    "query_handler",
    "AnyCommandHandlerType", # Exporting for potential external use
    "AnyQueryHandlerType",   # Exporting for potential external use
    "AnyHandlerType",        # Exporting for potential external use
]
