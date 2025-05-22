import pytest
from kink import di, Container
from medyator import Medyator, HandlerRegistry, default_handler_registry, ServiceProvider
from medyator.kink import KinkServiceProvider, configure_medyator
from medyator.contracts import Command, Query
from medyator.request_handler import CommandHandler, QueryHandler
from medyator.registration import command_handler, query_handler
from medyator.errors import HandlerNotFound

# Sample Commands and Queries
class ConfigTestCommand(Command):
    pass

class ConfigTestQuery(Query[str]):
    pass

# Sample Handlers
@command_handler(ConfigTestCommand)
class ConfigTestCommandHandler(CommandHandler[ConfigTestCommand]):
    def __call__(self, request: ConfigTestCommand) -> None:
        print(f"Handled {type(request).__name__}")

@query_handler(ConfigTestQuery)
class ConfigTestQueryHandler(QueryHandler[ConfigTestQuery, str]):
    def __call__(self, request: ConfigTestQuery) -> str:
        return f"Result for {type(request).__name__}"

@pytest.fixture(autouse=True)
def setup_kink_and_registry():
    """Clears kink's di and default_handler_registry before and after each test."""
    di.clear_cache() # Clears kink's cache of singletons/scoped services
    if isinstance(di, Container): # If di is a Container instance, reset it
         for k in list(di._factories.keys()): # Access internal _factories if necessary and possible
            if k not in (type, Container): # Don't remove kink's own registrations
                del di._factories[k] # type: ignore

    default_handler_registry.clear()
    yield
    default_handler_registry.clear()
    di.clear_cache()
    if isinstance(di, Container):
         for k in list(di._factories.keys()):
            if k not in (type, Container):
                del di._factories[k] # type: ignore


def test_configure_medyator_registers_medyator_and_service_provider():
    # Handlers are already registered with default_handler_registry via decorators
    # Register handler types themselves in kink
    di[ConfigTestCommandHandler] = ConfigTestCommandHandler()
    di[ConfigTestQueryHandler] = ConfigTestQueryHandler()
    
    medyator_instance = configure_medyator(di)

    assert isinstance(medyator_instance, Medyator)
    assert di[Medyator] is medyator_instance
    assert isinstance(di[ServiceProvider], KinkServiceProvider)
    assert isinstance(di[KinkServiceProvider], KinkServiceProvider)
    assert di[ServiceProvider] is di[KinkServiceProvider]

@pytest.mark.asyncio # Changed to async test
async def test_configure_medyator_with_custom_registry(): # Changed to async def
    custom_registry = HandlerRegistry()

    @command_handler(ConfigTestCommand, registry=custom_registry)
    class CustomRegistryCommandHandler(CommandHandler[ConfigTestCommand]):
        def __call__(self, request: ConfigTestCommand) -> None: pass
    
    di[CustomRegistryCommandHandler] = CustomRegistryCommandHandler() # Register handler in kink

    medyator_instance = configure_medyator(di, registry=custom_registry)
    ksp = di[KinkServiceProvider]

    assert ksp.registry is custom_registry
    
    # Test that it can resolve through the custom registry
    await medyator_instance.send(ConfigTestCommand()) # Changed to await


@pytest.mark.asyncio
async def test_kink_service_provider_get_command_handler():
    # ConfigTestCommandHandler is registered with default_handler_registry by its decorator
    di[ConfigTestCommandHandler] = ConfigTestCommandHandler() # Register handler instance in kink
    
    configure_medyator(di) # Uses default_handler_registry
    medyator = di[Medyator]
    
    # This should work as KinkServiceProvider will use the registry to find ConfigTestCommandHandler
    # and then resolve ConfigTestCommandHandler from kink
    await medyator.send(ConfigTestCommand()) # No error expected, changed to await

@pytest.mark.asyncio
async def test_kink_service_provider_get_query_handler():
    # ConfigTestQueryHandler is registered with default_handler_registry by its decorator
    di[ConfigTestQueryHandler] = ConfigTestQueryHandler() # Register handler instance in kink

    configure_medyator(di) # Uses default_handler_registry
    medyator = di[Medyator]
    
    result = await medyator.send(ConfigTestQuery()) # Changed to await
    assert result == f"Result for {ConfigTestQuery.__name__}"

@pytest.mark.asyncio
async def test_kink_service_provider_handler_not_in_registry():
    # Handler type is registered in kink
    di[ConfigTestCommandHandler] = ConfigTestCommandHandler()
    
    # But ConfigTestCommand is NOT registered in any registry used by KinkServiceProvider
    # (default_handler_registry is cleared by fixture)
    configure_medyator(di) # This sets up KSP with an empty default_handler_registry
    medyator = di[Medyator]

    with pytest.raises(HandlerNotFound, match=f"No handler has been found for request type {ConfigTestCommand.__name__}!"):
        await medyator.send(ConfigTestCommand()) # Changed to await

@pytest.mark.asyncio
async def test_kink_service_provider_handler_in_registry_but_not_in_kink():
    # ConfigTestCommandHandler is registered with default_handler_registry by its decorator
    # BUT ConfigTestCommandHandler is NOT registered in kink DI
    
    configure_medyator(di) # Sets up KSP with default_handler_registry
    medyator = di[Medyator]

    with pytest.raises(HandlerNotFound, match=f"Handler type {ConfigTestCommandHandler.__name__} for request {ConfigTestCommand.__name__} was found in registry but not registered in the DI container."):
        await medyator.send(ConfigTestCommand()) # Changed to await

class UnregisteredCommand(Command): pass # Keep this definition if not already global in file

def test_kink_service_provider_unsupported_request_type():
    # This test ensures KinkServiceProvider.get raises TypeError for non-Command/Query
    # However, Medyator itself checks isinstance(request, Command/Query) first.
    # So, to test KSP.get directly, we'd need to instantiate it and call get.
    
    ksp = KinkServiceProvider(di, default_handler_registry)
    
    class NotARequest: pass # Not inheriting from BaseRequest

    with pytest.raises(TypeError, match="Unsupported request type: NotARequest"):
        ksp.get(NotARequest) # type: ignore

    # Also, BaseRequest itself if not Command or Query (though BaseRequest is abstract)
    class DirectBaseRequest(Query[None]): pass # Make it a query to be valid for registry
    # but if KSP's logic was flawed and didn't see it as Query/Command
    
    # The current KSP logic:
    # if issubclass(request_type, Command): ...
    # elif issubclass(request_type, Query): ...
    # else: raise TypeError
    # This correctly handles all subclasses of Command and Query.
    # An instance of BaseRequest that is *neither* Command nor Query is hard to construct
    # if Command and Query are the only concrete BaseRequest types.
    # Let's assume this is fine for now.

@pytest.mark.asyncio # Added pytest.mark.asyncio
async def test_configure_medyator_uses_default_registry_if_none_passed(): # Changed to async def
    # ConfigTestCommandHandler is registered with default_handler_registry by its decorator
    di[ConfigTestCommandHandler] = ConfigTestCommandHandler() # Register handler in kink
    
    configure_medyator(di) # Passing None for registry
    ksp = di[KinkServiceProvider]

    assert ksp.registry is default_handler_registry
    # Verify it works
    medyator = di[Medyator]
    # This test was missing await, but it's also missing @pytest.mark.asyncio
    # It should be an async test.
    await medyator.send(ConfigTestCommand())

@pytest.mark.asyncio # Ensure all async tests are marked
async def test_handler_instance_caching_in_wrapper_via_medyator():
    # This test checks if the handler instance is cached by the wrapper
    # by verifying if the DI container (kink) is asked for the handler only once.
    
    call_count = {"count": 0}
    class CountingCommandHandler(CommandHandler[ConfigTestCommand]):
        def __init__(self):
            call_count["count"] += 1 # Count instantiations
        def __call__(self, request: ConfigTestCommand) -> None: pass

    # Register with default registry
    default_handler_registry.register_command_handler(ConfigTestCommand, CountingCommandHandler)
    
    # Register in kink. Kink's default is transient for di[Type] = Type()
    # but if we do di[Type] = instance, it's a singleton.
    # Let's test with transient behavior for the handler type itself.
    di.add_transient(CountingCommandHandler) # New instance each time kink is asked for it

    configure_medyator(di)
    medyator = di[Medyator]

    assert call_count["count"] == 0 # Not instantiated yet

    await medyator.send(ConfigTestCommand()) # First send, changed to await
    # KSP.get -> registry.get_command_handler -> kink.di[CountingCommandHandler] (1st instantiation)
    # Wrapper caches this instance.
    assert call_count["count"] == 1 

    await medyator.send(ConfigTestCommand()) # Second send for the same command type, changed to await
    # Wrapper should use its cached handler instance, not ask kink again.
    assert call_count["count"] == 1 # Should still be 1 if wrapper caching works

    # Now for a different command type, to ensure Medyator's cache is per-request-type
    class AnotherConfigCommand(Command): pass
    
    call_count_another = {"count": 0}
    class AnotherCountingCommandHandler(CommandHandler[AnotherConfigCommand]):
        def __init__(self):
            call_count_another["count"] += 1
        def __call__(self, request: AnotherConfigCommand) -> None: pass

    default_handler_registry.register_command_handler(AnotherConfigCommand, AnotherCountingCommandHandler)
    di.add_transient(AnotherCountingCommandHandler)

    await medyator.send(AnotherConfigCommand()) # Changed to await
    assert call_count_another["count"] == 1

    await medyator.send(AnotherConfigCommand()) # Changed to await
    assert call_count_another["count"] == 1

    # And the first handler's count should remain unchanged
    assert call_count["count"] == 1

@pytest.mark.asyncio
async def test_handler_in_registry_kink_cannot_resolve_due_to_its_dependencies():
    class Dependency: pass

    class HandlerWithDeps(CommandHandler[ConfigTestCommand]):
        def __init__(self, dep: Dependency): # kink needs to know about Dependency
            self.dep = dep
        def __call__(self, request: ConfigTestCommand) -> None: pass

    default_handler_registry.register_command_handler(ConfigTestCommand, HandlerWithDeps)
    # HandlerWithDeps is registered in registry, but not in kink, nor is its Dependency.
    # kink will fail to instantiate HandlerWithDeps if we try di[HandlerWithDeps] = HandlerWithDeps()
    # or if we do di.add_transient(HandlerWithDeps) without registering Dependency.
    
    di.add_transient(HandlerWithDeps) # Tell kink about HandlerWithDeps, but not Dependency

    configure_medyator(di)
    medyator = di[Medyator]

    with pytest.raises(HandlerNotFound) as exc_info: # kink.errors.ServiceNotFoundError is caught by KSP
        await medyator.send(ConfigTestCommand()) # Changed to await
    
    # Check the error message to confirm it's because kink couldn't resolve it
    # The exact message depends on kink's internal error for dependency resolution.
    # KinkServiceProvider wraps this in HandlerNotFound.
    assert f"Could not resolve handler {HandlerWithDeps.__name__}" in str(exc_info.value)
    assert f"Original error: Cannot resolve {Dependency}" in str(exc_info.value) # Kink's typical message
    # This confirms KSP's error wrapping.
    
    # Now, if we register the dependency, it should work.
    di.clear_cache()
    if isinstance(di, Container):
         for k in list(di._factories.keys()):
            if k not in (type, Container):
                del di._factories[k] # type: ignore
    # Re-register HandlerWithDeps as transient, and its dependency
    di.add_transient(HandlerWithDeps)
    di.add_singleton(Dependency) # Or transient, doesn't matter for this test

    # Re-configure Medyator (or use the same instance if KSP is already set up with the registry)
    # If Medyator and KSP are already configured, we just need the DI state to be correct.
    # The KSP instance inside Medyator already has the right di and registry.
    
    await medyator.send(ConfigTestCommand()) # Should now work, changed to await
    
    # Clean up default_handler_registry for other tests
    default_handler_registry.clear()
    # kink di is cleared by fixture

# Test that KinkServiceProvider.get itself doesn't swallow kink's ServiceNotFoundError
# when the handler_type is simply not known to kink at all (not just dependency issue).
# This is covered by test_kink_service_provider_handler_in_registry_but_not_in_kink
# which checks for the specific HandlerNotFound message from KSP.
# The key is that KSP catches ServiceNotFoundError and wraps it.

# Test that if a handler is registered as a singleton in Kink, the wrapper gets the same instance.
@pytest.mark.asyncio
async def test_singleton_handler_from_kink_is_cached_by_wrapper():
    singleton_instance_id = {"id": None}
    class SingletonCommandHandler(CommandHandler[ConfigTestCommand]):
        def __init__(self):
            singleton_instance_id["id"] = id(self)
        def __call__(self, request: ConfigTestCommand) -> None: pass

    default_handler_registry.register_command_handler(ConfigTestCommand, SingletonCommandHandler)
    
    # Register as singleton in kink
    # di[SingletonCommandHandler] = SingletonCommandHandler() # This creates one instance and kink serves it.
    # OR
    di.add_singleton(SingletonCommandHandler) # Kink creates it on first request and serves same one.

    configure_medyator(di)
    medyator = di[Medyator]

    await medyator.send(ConfigTestCommand()) # Changed to await
    first_id = singleton_instance_id["id"]
    assert first_id is not None

    # If wrapper caches, kink is not asked again. If wrapper didn't cache, kink would be asked again.
    # Since it's a singleton in kink, kink would return the same instance anyway.
    # This test thus primarily verifies that a singleton from kink behaves as expected,
    # and the wrapper correctly uses whatever instance kink provides.
    # The crucial test for wrapper caching is `test_handler_instance_caching_in_wrapper_via_medyator`
    # using transient handlers in kink.
    await medyator.send(ConfigTestCommand()) # Changed to await
    second_id = singleton_instance_id["id"]
    assert second_id == first_id
```
