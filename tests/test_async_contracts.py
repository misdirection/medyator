import pytest
from typing import TypeVar, Generic
from abc import ABC, abstractmethod

from medyator.contracts import Command, Query, AsyncCommand, AsyncQuery
from medyator.request_handler import (
    CommandHandler,
    QueryHandler,
    AsyncCommandHandler,
    AsyncQueryHandler,
)

# Test AsyncCommand
class MyAsyncCommand(AsyncCommand):
    def __init__(self, data: str):
        self.data = data

def test_async_command_instantiation():
    cmd = MyAsyncCommand(data="test_async_cmd")
    assert isinstance(cmd, AsyncCommand)
    assert isinstance(cmd, Command) # Inherits from Command
    assert cmd.data == "test_async_cmd"

# Test AsyncQuery
TResponseConcrete = TypeVar("TResponseConcrete")

class MyAsyncQuery(AsyncQuery[TResponseConcrete], Generic[TResponseConcrete]):
    def __init__(self, query_id: int):
        self.query_id = query_id

def test_async_query_instantiation():
    # Test with a specific type for TResponseConcrete, e.g., str
    query = MyAsyncQuery[str](query_id=123)
    assert isinstance(query, AsyncQuery)
    assert isinstance(query, Query) # Inherits from Query
    assert query.query_id == 123

# Test AsyncCommandHandler
class MyAsyncCommandHandler(AsyncCommandHandler[MyAsyncCommand]):
    async def handle(self, request: MyAsyncCommand) -> None:
        print(f"Handled MyAsyncCommand with data: {request.data}")
        # In a real handler, you'd await something or perform async operations.
        # For this test, just ensuring the signature is compatible is enough.
        pass 

async def test_async_command_handler_instantiation_and_handle_signature():
    handler = MyAsyncCommandHandler()
    cmd = MyAsyncCommand(data="test_async_cmd_handler")
    
    # Check if handle is awaitable
    import inspect
    assert inspect.iscoroutinefunction(handler.handle)
    
    await handler.handle(cmd) # Call it to ensure no runtime errors with signature

def test_async_command_handler_is_abstract_by_default():
    # Test that the base AsyncCommandHandler.handle is abstract
    class DefaultAsyncCmdHandler(AsyncCommandHandler[MyAsyncCommand]):
        pass # Does not implement handle

    handler = DefaultAsyncCmdHandler()
    with pytest.raises(NotImplementedError):
        # Need to create a coroutine to call it, as it's an async def
        async def call_handle():
            await handler.handle(MyAsyncCommand(data="test"))
        
        # Run the coroutine
        import asyncio
        asyncio.run(call_handle())


# Test AsyncQueryHandler
class MyAsyncQueryHandler(AsyncQueryHandler[MyAsyncQuery[str], str]): # TResponse is str
    async def handle(self, request: MyAsyncQuery[str]) -> str:
        # In a real handler, you'd await something or perform async operations.
        return f"Result for MyAsyncQuery id {request.query_id}"

async def test_async_query_handler_instantiation_and_handle_signature():
    handler = MyAsyncQueryHandler()
    query = MyAsyncQuery[str](query_id=456)

    import inspect
    assert inspect.iscoroutinefunction(handler.handle)

    result = await handler.handle(query)
    assert result == "Result for MyAsyncQuery id 456"

def test_async_query_handler_is_abstract_by_default():
    # Test that the base AsyncQueryHandler.handle is abstract
    class DefaultAsyncQryHandler(AsyncQueryHandler[MyAsyncQuery[int], int]):
        pass # Does not implement handle

    handler = DefaultAsyncQryHandler()
    with pytest.raises(NotImplementedError):
        async def call_handle():
            await handler.handle(MyAsyncQuery[int](query_id=1))
        
        import asyncio
        asyncio.run(call_handle())

# Test that sync handlers are distinct
class MySyncCommand(Command): pass
class MySyncQuery(Query[str]): pass

class MySyncCommandHandler(CommandHandler[MySyncCommand]):
    def __call__(self, request: MySyncCommand) -> None: pass

class MySyncQueryHandler(QueryHandler[MySyncQuery, str]):
    def __call__(self, request: MySyncQuery) -> str: return "sync"


def test_sync_handlers_are_not_async_handlers():
    sync_cmd_handler = MySyncCommandHandler()
    sync_qry_handler = MySyncQueryHandler()

    assert not isinstance(sync_cmd_handler, AsyncCommandHandler)
    assert not isinstance(sync_qry_handler, AsyncQueryHandler)

    # And vice-versa (though inheritance makes Async handlers also Command/Query handlers)
    async_cmd_handler = MyAsyncCommandHandler()
    async_qry_handler = MyAsyncQueryHandler()

    # This check is more about the method name and signature
    assert not hasattr(sync_cmd_handler, 'handle') or not callable(getattr(sync_cmd_handler, 'handle', None))
    assert hasattr(async_cmd_handler, 'handle') and callable(async_cmd_handler.handle)


# Test that type variables are correctly bound
# This is implicitly tested by the MyAsyncCommandHandler and MyAsyncQueryHandler definitions.
# If TAsyncCommand were not bound correctly, MyAsyncCommandHandler(AsyncCommandHandler[MyAsyncCommand])
# would be a type error.

# Example of what should be a type error if generics are mismatched
# (This would be caught by a static type checker like MyPy, not easily at runtime without complex checks)
# class MismatchedAsyncHandler(AsyncCommandHandler[MyAsyncCommand]):
#     async def handle(self, request: AnotherAsyncCommand) -> None: # AnotherAsyncCommand is not MyAsyncCommand
#         pass

# class AnotherAsyncCommand(AsyncCommand): pass

# This test is more about ensuring the ABC mechanism works for async def
@pytest.mark.asyncio # For pytest-asyncio if needed for running async tests
async def test_async_command_handler_abc():
    class AbstractHandler(AsyncCommandHandler[MyAsyncCommand]):
        # Missing async def handle
        pass
    
    instance = AbstractHandler()
    # The ABC check for async def methods isn't as straightforward as sync methods
    # at instantiation time without metaclass magic for async.
    # NotImplementedError is raised when the method *would be called*.
    with pytest.raises(NotImplementedError):
        await instance.handle(MyAsyncCommand("test"))

@pytest.mark.asyncio
async def test_async_query_handler_abc():
    class AbstractHandler(AsyncQueryHandler[MyAsyncQuery[str], str]):
        # Missing async def handle
        pass
    
    instance = AbstractHandler()
    with pytest.raises(NotImplementedError):
        await instance.handle(MyAsyncQuery[str](1))

# Check that the TResponse is correctly part of AsyncQuery and AsyncQueryHandler
class SpecificResponseQuery(AsyncQuery[int]): pass

class SpecificResponseHandler(AsyncQueryHandler[SpecificResponseQuery, int]):
    async def handle(self, request: SpecificResponseQuery) -> int:
        return 123

@pytest.mark.asyncio
async def test_specific_response_type_async_query():
    handler = SpecificResponseHandler()
    query = SpecificResponseQuery()
    result: int = await handler.handle(query)
    assert result == 123
    assert isinstance(result, int)

# Test inheritance from AsyncCommand and AsyncQuery
class DerivedAsyncCommand(MyAsyncCommand):
    def __init__(self, data: str, extra: int):
        super().__init__(data)
        self.extra = extra

class DerivedAsyncQuery(MyAsyncQuery[str]): # Inherits from MyAsyncQuery[str]
    def __init__(self, query_id: int, more_data: float):
        super().__init__(query_id)
        self.more_data = more_data

def test_derived_async_requests():
    derived_cmd = DerivedAsyncCommand("derived_cmd", 10)
    assert isinstance(derived_cmd, MyAsyncCommand)
    assert isinstance(derived_cmd, AsyncCommand)
    assert derived_cmd.data == "derived_cmd"
    assert derived_cmd.extra == 10

    derived_query = DerivedAsyncQuery(789, 3.14)
    assert isinstance(derived_query, MyAsyncQuery)
    assert isinstance(derived_query, AsyncQuery)
    assert derived_query.query_id == 789
    assert derived_query.more_data == 3.14
```
