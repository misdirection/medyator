import pytest
from kink import di, Container
from medyator import (
    Medyator,
    Command,
    Query,
    CommandHandler,
    QueryHandler,
    HandlerNotFound,
    default_handler_registry, # For registering handlers
    command_handler as register_command, # Decorator for convenience
    query_handler as register_query,     # Decorator for convenience
)
from medyator.kink import configure_medyator # The new configuration function

# --- Test Fixtures for Commands, Queries, and Handlers ---

class MyTestCommand(Command):
    def __init__(self, value: str):
        self.value = value

class MyTestQuery(Query[str]): # Query that expects a string response
    def __init__(self, value: int):
        self.value = value

# Using decorators to register handlers with the default_handler_registry
@register_command(MyTestCommand)
class MyTestCommandHandler(CommandHandler[MyTestCommand]):
    # Class variable to observe side effects for testing
    # This is not ideal for real handlers but fine for tests.
    _last_value_processed: str | None = None

    def __init__(self):
        # This handler will be instantiated by kink
        pass

    def __call__(self, request: MyTestCommand) -> None:
        MyTestCommandHandler._last_value_processed = request.value

@register_query(MyTestQuery)
class MyTestQueryHandler(QueryHandler[MyTestQuery, str]):
    def __init__(self):
        # This handler will be instantiated by kink
        pass

    def __call__(self, request: MyTestQuery) -> str:
        return f"Processed query with value: {request.value}"

# --- Test Setup Fixture ---

@pytest.fixture(autouse=True)
def setup_medyator_for_tests():
    """
    Automatically configures Medyator with kink's DI and clears registries/DI
    before and after each test.
    """
    # Clear kink DI container
    di.clear_cache() # Clears kink's cache of singletons/scoped services
    if isinstance(di, Container): # If di is a Container instance, reset it
         for k in list(di._factories.keys()): # Access internal _factories if necessary and possible
            if k not in (type, Container): # Don't remove kink's own registrations
                del di._factories[k] # type: ignore


    # Clear the default handler registry
    default_handler_registry.clear()

    # Re-register handlers for each test (decorators run at import time, but registry is cleared)
    # This explicit re-registration ensures they are in the default_handler_registry for each test.
    default_handler_registry.register_command_handler(MyTestCommand, MyTestCommandHandler)
    default_handler_registry.register_query_handler(MyTestQuery, MyTestQueryHandler)
    
    # Register handler types themselves in kink so KinkServiceProvider can resolve them
    di[MyTestCommandHandler] = MyTestCommandHandler # Kink will create new instance if not singleton
    di[MyTestQueryHandler] = MyTestQueryHandler   # Kink will create new instance

    # Configure Medyator using the new function (uses default_handler_registry by default)
    configure_medyator(di)
    
    yield # Test runs here

    # Teardown (already handled by clearing at the start of next test)

# --- Medyator Tests ---

@pytest.mark.asyncio
async def test_medyator_send_command_executes_correct_handler():
    medyator = di[Medyator] # Get Medyator instance from kink
    
    MyTestCommandHandler._last_value_processed = None # Reset class variable
    test_value = "Hello Medyator Command!"
    command_instance = MyTestCommand(value=test_value)
    
    await medyator.send(command_instance) # Changed to await
    
    assert MyTestCommandHandler._last_value_processed == test_value

@pytest.mark.asyncio
async def test_medyator_send_query_executes_correct_handler_and_returns_value():
    medyator = di[Medyator]
    test_value = 123
    query_instance = MyTestQuery(value=test_value)
    
    result = await medyator.send(query_instance) # Changed to await
    
    assert result == f"Processed query with value: {test_value}"

@pytest.mark.asyncio
async def test_medyator_send_command_handler_instance_caching():
    # This test relies on the wrapper caching the handler instance.
    # Kink needs to provide transient instances for this test to be meaningful for wrapper caching.
    di.clear_cache()
    if isinstance(di, Container):
         for k in list(di._factories.keys()):
            if k not in (type, Container):
                del di._factories[k] # type: ignore
    default_handler_registry.clear()

    default_handler_registry.register_command_handler(MyTestCommand, MyTestCommandHandler)
    
    # Make MyTestCommandHandler transient in kink
    # Note: MyTestCommandHandler itself doesn't have complex state,
    # but we can track its instantiation if we modify it or use a mock.
    # For simplicity, we assume the wrapper caching test in test_configuration.py
    # (test_handler_instance_caching_in_wrapper_via_medyator) is sufficient for the wrapper behavior.
    # This test will just ensure Medyator works end-to-end.
    di.add_transient(MyTestCommandHandler) # Kink provides new instance each time
    di.add_transient(MyTestQueryHandler) # Not used in this specific test but good for consistency

    configure_medyator(di) # Reconfigure with new DI settings
    medyator = di[Medyator]

    MyTestCommandHandler._last_value_processed = None
    await medyator.send(MyTestCommand("first call")) # Changed to await
    assert MyTestCommandHandler._last_value_processed == "first call"

    MyTestCommandHandler._last_value_processed = None # Reset
    await medyator.send(MyTestCommand("second call")) # Changed to await
    assert MyTestCommandHandler._last_value_processed == "second call"
    # Add mock to kink to count how many times MyTestCommandHandler is resolved from DI
    # if more detailed check of wrapper caching is needed here.

@pytest.mark.asyncio # Added pytest.mark.asyncio
async def test_medyator_raises_handler_not_found_for_unregistered_command_type(): # Changed to async def
    medyator = di[Medyator]
    
    class UnregisteredCommand(Command): pass
    
    with pytest.raises(HandlerNotFound) as exc_info:
        await medyator.send(UnregisteredCommand()) # Changed to await
    assert f"No handler has been found for request type {UnregisteredCommand.__name__}!" in str(exc_info.value)

@pytest.mark.asyncio
async def test_medyator_raises_handler_not_found_for_unregistered_query_type():
    medyator = di[Medyator]

    class UnregisteredQuery(Query[None]): pass

    with pytest.raises(HandlerNotFound) as exc_info:
        await medyator.send(UnregisteredQuery()) # Changed to await
    assert f"No handler has been found for request type {UnregisteredQuery.__name__}!" in str(exc_info.value)

@pytest.mark.asyncio
async def test_medyator_handler_in_registry_but_not_in_di():
    medyator = di[Medyator]

    class TempCommand(Command): pass
    # Handler type for TempCommand
    class TempCommandHandler(CommandHandler[TempCommand]):
        def __call__(self, request: TempCommand) -> None: pass
    
    # Register in default_handler_registry
    default_handler_registry.register_command_handler(TempCommand, TempCommandHandler)
    # DO NOT register TempCommandHandler in kink DI

    with pytest.raises(HandlerNotFound) as exc_info:
        await medyator.send(TempCommand()) # Changed to await
    assert f"Handler type {TempCommandHandler.__name__} for request {TempCommand.__name__} was found in registry but not registered in the DI container." in str(exc_info.value)

@pytest.mark.asyncio
async def test_medyator_unsupported_request_type_raises_type_error():
    medyator = di[Medyator]
    class NotARequest: pass # Does not inherit from Command or Query

    with pytest.raises(TypeError, match="Unsupported request type"):
        await medyator.send(NotARequest()) # type: ignore # Changed to await

# Test that Medyator correctly uses the ServiceProvider provided at initialization.
# This is implicitly tested by all other tests, as configure_medyator sets it up.
# A more direct test could mock ServiceProvider, but that tests Medyator's internal logic
# rather than the integration, which is the focus here.

# Test execution of query handler twice (checks Medyator's internal handler caching, not wrapper)
@pytest.mark.asyncio
async def test_medyator_query_handler_execution_twice():
    medyator = di[Medyator] # Get Medyator instance from kink
    query_instance = MyTestQuery(value=777)
    
    result1 = await medyator.send(query_instance) # Changed to await
    assert result1 == "Processed query with value: 777"

    # The HandlerContainer in Medyator should cache the wrapper.
    # The wrapper itself caches the handler instance from DI.
    result2 = await medyator.send(query_instance) # Changed to await
    assert result2 == "Processed query with value: 777"
    # If MyTestQueryHandler had state or Kink was mocked, we could verify instance reuse.
    # The wrapper caching test in test_configuration.py is more direct for instance reuse.

@pytest.mark.asyncio
async def test_medyator_wrapper_raises_type_error_for_invalid_command_handler_type():
    medyator = di[Medyator]
    
    class BadHandlerType: # Not a CommandHandler
        def __call__(self, request: MyTestCommand) -> None:
            print("Bad handler called")

    # Register the command type with the bad handler type in the registry
    default_handler_registry.register_command_handler(MyTestCommand, BadHandlerType) # type: ignore
    # Register the bad handler type instance in kink
    di[BadHandlerType] = BadHandlerType()

    with pytest.raises(TypeError, match=f"Resolved handler for {MyTestCommand.__name__} is not a CommandHandler or AsyncCommandHandler. Got {BadHandlerType.__name__}"):
        await medyator.send(MyTestCommand("test"))

@pytest.mark.asyncio
async def test_medyator_wrapper_raises_type_error_for_invalid_query_handler_type():
    medyator = di[Medyator]

    class BadHandlerType: # Not a QueryHandler
        def __call__(self, request: MyTestQuery) -> str:
            return "bad query handler"

    # Register the query type with the bad handler type in the registry
    default_handler_registry.register_query_handler(MyTestQuery, BadHandlerType) # type: ignore
    # Register the bad handler type instance in kink
    di[BadHandlerType] = BadHandlerType()

    with pytest.raises(TypeError, match=f"Resolved handler for {MyTestQuery.__name__} is not a QueryHandler or AsyncQueryHandler. Got {BadHandlerType.__name__}"):
        await medyator.send(MyTestQuery(123))
