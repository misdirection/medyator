import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import medyator.kink  # for extension of Container  # noqa: F401
import pytest
from kink import di, inject
import asyncio
from medyator import Medyator
from medyator.contracts import Command, Query
from medyator.errors import HandlerNotFound
from medyator.request_handler import CommandHandler, QueryHandler


@pytest.fixture
def test_query():
    class TestQuery(Query):
        def __init__(self, value: int) -> None:
            self.value = value

    class TestQueryHandler(QueryHandler[TestQuery, int]):
        def __call__(self, request: TestQuery) -> int:
            return request.value + 9000

    return TestQuery, TestQueryHandler()


@pytest.fixture
def test_command():
    class TestCommand(Command):
        def __init__(self, value: str) -> None:
            self.value = value

    @inject(alias=TestCommand)
    class TestCommandHandler(CommandHandler[TestCommand]):
        def __init__(self) -> None:
            self.value = None

        def __call__(self, request: TestCommand) -> None:
            self.value = request.value

    return TestCommand, TestCommandHandler()


async def test_query_should_execute_query_handler_twice_and_return_same_value(test_query):
    di.clear_cache() # Ensure clean state for DI
    di.add_medyator()
    query, query_handler = test_query
    di[query] = query_handler
    medyator = di[Medyator]

    # should get handler from serviceprovider (di container)
    result = await medyator.send(query(1))
    assert result == 9001

    # should get handler from medyator container
    result = await medyator.send(query(1))
    assert result == 9001


async def test_should_execute_command_handler_and_set_the_value(test_command):
    di.clear_cache() # Ensure clean state for DI
    di.add_medyator()
    command, _ = test_command # TestCommandHandler is registered via @inject by fixture
    medyator = di[Medyator]

    await medyator.send(command("Hello, World!"))
    handler = di[command] # Get the handler instance from DI
    assert handler.value == "Hello, World!"


async def test_should_raise_HandlerNotFound_error_when_query_handler_is_not_found(test_query):
    di.clear_cache() # Ensure clean state for DI
    di.add_medyator()
    medyator = di[Medyator]
    query, _ = test_query # Handler not registered for this query type
    with pytest.raises(HandlerNotFound):
        await medyator.send(query(1))

# --- Tests for Async Handlers Start Here ---

# Fixture for Command with an Asynchronous Handler
@pytest.fixture
def command_with_async_handler_fixture():
    class MyCommandForAsyncHandler(Command): # Inherits from Command
        def __init__(self, value: str):
            self.value = value

    class MyAsyncExecutingCommandHandler(CommandHandler[MyCommandForAsyncHandler]): # Inherits from CommandHandler
        def __init__(self):
            self.handled_value = None

        async def __call__(self, request: MyCommandForAsyncHandler) -> None: # __call__ is async
            await asyncio.sleep(0.01) # Simulate async work
            self.handled_value = request.value
            print(f"MyAsyncExecutingCommandHandler handled: {self.handled_value}")

    return MyCommandForAsyncHandler, MyAsyncExecutingCommandHandler


async def test_sends_command_to_async_handler_correctly(command_with_async_handler_fixture):
    di.clear_cache()
    di.add_medyator()
    medyator = di[Medyator]

    CmdRequiringAsyncHandling, AsyncHandler = command_with_async_handler_fixture
    async_handler_instance = AsyncHandler()
    di[CmdRequiringAsyncHandling] = async_handler_instance # Register handler instance

    cmd_instance = CmdRequiringAsyncHandling("async hello command")
    await medyator.send(cmd_instance)

    assert async_handler_instance.handled_value == "async hello command"

# Fixture for Query with an Asynchronous Handler
@pytest.fixture
def query_with_async_handler_fixture():
    class MyQueryForAsyncHandler(Query[str]): # Inherits from Query
        def __init__(self, value: int):
            self.value = value

    class MyAsyncExecutingQueryHandler(QueryHandler[MyQueryForAsyncHandler, str]): # Inherits from QueryHandler
        async def __call__(self, request: MyQueryForAsyncHandler) -> str: # __call__ is async
            await asyncio.sleep(0.01) # Simulate async work
            return f"async query result: {request.value + 100}"

    return MyQueryForAsyncHandler, MyAsyncExecutingQueryHandler


async def test_sends_query_to_async_handler_correctly(query_with_async_handler_fixture):
    di.clear_cache()
    di.add_medyator()
    medyator = di[Medyator]

    QryRequiringAsyncHandling, AsyncHandler = query_with_async_handler_fixture
    async_handler_instance = AsyncHandler()
    di[QryRequiringAsyncHandling] = async_handler_instance # Register handler instance

    qry_instance = QryRequiringAsyncHandling(42)
    result = await medyator.send(qry_instance)

    assert result == "async query result: 142"
