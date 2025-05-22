import pytest
import asyncio # For sleep
from kink import di, Container
from medyator import (
    Medyator,
    AsyncCommand,
    AsyncQuery,
    AsyncCommandHandler,
    AsyncQueryHandler,
    HandlerNotFound,
    default_handler_registry,
    command_handler as register_command,
    query_handler as register_query,
)
from medyator.kink import configure_medyator

# --- Async Test Fixtures ---

class MyAsyncTestCommand(AsyncCommand):
    def __init__(self, data: str):
        self.data = data

class MyAsyncTestQuery(AsyncQuery[str]): # Expects a string response
    def __init__(self, query_id: int):
        self.query_id = query_id

# Using decorators to register async handlers with default_handler_registry
@register_command(MyAsyncTestCommand)
class MyAsyncTestCommandHandler(AsyncCommandHandler[MyAsyncTestCommand]):
    _last_processed_data: str | None = None
    _call_count = 0

    async def handle(self, request: MyAsyncTestCommand) -> None:
        MyAsyncTestCommandHandler._call_count += 1
        await asyncio.sleep(0.01) # Simulate async work
        MyAsyncTestCommandHandler._last_processed_data = request.data

@register_query(MyAsyncTestQuery)
class MyAsyncTestQueryHandler(AsyncQueryHandler[MyAsyncTestQuery, str]):
    _call_count = 0
    async def handle(self, request: MyAsyncTestQuery) -> str:
        MyAsyncTestQueryHandler._call_count += 1
        await asyncio.sleep(0.01) # Simulate async work
        return f"Async result for query id {request.query_id}"

# --- Test Setup Fixture ---

@pytest.fixture(autouse=True)
def setup_async_medyator_for_tests():
    di.clear_cache()
    if isinstance(di, Container):
         for k in list(di._factories.keys()):
            if k not in (type, Container):
                del di._factories[k] # type: ignore
    default_handler_registry.clear()

    # Register async handlers (decorators do this at import, but registry is cleared)
    default_handler_registry.register_command_handler(MyAsyncTestCommand, MyAsyncTestCommandHandler)
    default_handler_registry.register_query_handler(MyAsyncTestQuery, MyAsyncTestQueryHandler)

    # Register handler types in kink
    di[MyAsyncTestCommandHandler] = MyAsyncTestCommandHandler
    di[MyAsyncTestQueryHandler] = MyAsyncTestQueryHandler
    
    configure_medyator(di)
    
    # Reset call counts for handlers
    MyAsyncTestCommandHandler._call_count = 0
    MyAsyncTestCommandHandler._last_processed_data = None
    MyAsyncTestQueryHandler._call_count = 0
    yield

# --- Async Medyator Tests ---

@pytest.mark.asyncio
async def test_medyator_send_async_command_executes_correct_handler():
    medyator = di[Medyator]
    test_data = "Hello Async Command!"
    command = MyAsyncTestCommand(data=test_data)

    await medyator.send(command)

    assert MyAsyncTestCommandHandler._last_processed_data == test_data
    assert MyAsyncTestCommandHandler._call_count == 1

@pytest.mark.asyncio
async def test_medyator_send_async_query_executes_correct_handler_and_returns_value():
    medyator = di[Medyator]
    test_id = 789
    query = MyAsyncTestQuery(query_id=test_id)

    result = await medyator.send(query)

    assert result == f"Async result for query id {test_id}"
    assert MyAsyncTestQueryHandler._call_count == 1

@pytest.mark.asyncio
async def test_medyator_send_async_handler_instance_caching():
    # Kink setup for transient handlers to test wrapper caching
    di.clear_cache()
    if isinstance(di, Container):
         for k in list(di._factories.keys()):
            if k not in (type, Container):
                del di._factories[k] # type: ignore
    default_handler_registry.clear()
    
    default_handler_registry.register_command_handler(MyAsyncTestCommand, MyAsyncTestCommandHandler)
    di.add_transient(MyAsyncTestCommandHandler) # New instance each time kink is asked

    configure_medyator(di)
    medyator = di[Medyator]

    MyAsyncTestCommandHandler._call_count = 0 # Reset

    # First call, handler should be instantiated by Kink
    await medyator.send(MyAsyncTestCommand("call 1"))
    # The _call_count inside the handler counts handle() calls, not instantiations.
    # To test Kink instantiations, MyAsyncTestCommandHandler.__init__ would need a counter.
    # The wrapper caching test in test_configuration.py covers Kink call counts.
    # This test ensures the async flow works and handler logic is executed.
    assert MyAsyncTestCommandHandler._call_count == 1 

    # Second call, wrapper should use cached handler instance
    await medyator.send(MyAsyncTestCommand("call 2"))
    assert MyAsyncTestCommandHandler._call_count == 2 # handle() is called again on the same (cached) instance

@pytest.mark.asyncio
async def test_medyator_raises_handler_not_found_for_unregistered_async_command():
    medyator = di[Medyator]
    class UnregisteredAsyncCmd(AsyncCommand): pass

    with pytest.raises(HandlerNotFound) as exc_info:
        await medyator.send(UnregisteredAsyncCmd())
    assert f"No handler has been found for request type {UnregisteredAsyncCmd.__name__}!" in str(exc_info.value)

@pytest.mark.asyncio
async def test_medyator_raises_handler_not_found_for_unregistered_async_query():
    medyator = di[Medyator]
    class UnregisteredAsyncQry(AsyncQuery[None]): pass

    with pytest.raises(HandlerNotFound) as exc_info:
        await medyator.send(UnregisteredAsyncQry())
    assert f"No handler has been found for request type {UnregisteredAsyncQry.__name__}!" in str(exc_info.value)

@pytest.mark.asyncio
async def test_medyator_async_handler_in_registry_but_not_in_di():
    medyator = di[Medyator]
    class TempAsyncCmd(AsyncCommand): pass
    class TempAsyncCmdHandler(AsyncCommandHandler[TempAsyncCmd]):
        async def handle(self, request: TempAsyncCmd) -> None: pass
    
    default_handler_registry.register_command_handler(TempAsyncCmd, TempAsyncCmdHandler)
    # DO NOT register TempAsyncCmdHandler in kink DI

    with pytest.raises(HandlerNotFound) as exc_info:
        await medyator.send(TempAsyncCmd())
    assert f"Handler type {TempAsyncCmdHandler.__name__} for request {TempAsyncCmd.__name__} was found in registry but not registered in the DI container." in str(exc_info.value)

# Test mixing sync and async (covered by updating tests/test_medyator.py)
# This file focuses on purely async scenarios.

@pytest.mark.asyncio
async def test_medyator_wrapper_raises_type_error_for_invalid_async_command_handler_type():
    medyator = di[Medyator]
    
    class BadAsyncHandlerType: # Not an AsyncCommandHandler or CommandHandler
        async def handle(self, request: MyAsyncTestCommand) -> None:
            print("Bad async handler called")

    # Register the async command type with the bad handler type in the registry
    default_handler_registry.register_command_handler(MyAsyncTestCommand, BadAsyncHandlerType) # type: ignore
    # Register the bad handler type instance in kink
    di[BadAsyncHandlerType] = BadAsyncHandlerType()

    with pytest.raises(TypeError, match=f"Resolved handler for {MyAsyncTestCommand.__name__} is not a CommandHandler or AsyncCommandHandler. Got {BadAsyncHandlerType.__name__}"):
        await medyator.send(MyAsyncTestCommand("test async"))

@pytest.mark.asyncio
async def test_medyator_wrapper_raises_type_error_for_invalid_async_query_handler_type():
    medyator = di[Medyator]

    class BadAsyncHandlerType: # Not an AsyncQueryHandler or QueryHandler
        async def handle(self, request: MyAsyncTestQuery) -> str:
            return "bad async query handler"

    # Register the async query type with the bad handler type in the registry
    default_handler_registry.register_query_handler(MyAsyncTestQuery, BadAsyncHandlerType) # type: ignore
    # Register the bad handler type instance in kink
    di[BadAsyncHandlerType] = BadAsyncHandlerType()

    with pytest.raises(TypeError, match=f"Resolved handler for {MyAsyncTestQuery.__name__} is not a QueryHandler or AsyncQueryHandler. Got {BadAsyncHandlerType.__name__}"):
        await medyator.send(MyAsyncTestQuery(456))
```
