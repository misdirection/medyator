import os
import sys

from medyator.errors import HandlerNotFound

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from medyator.medyator import Medyator
from medyator.contracts import Query, Command
from medyator.request_handler import QueryHandler, CommandHandler

from kink import di, inject
import medyator.kink  # for extension of Container


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


def test_query_should_execute_query_handler_twice_and_return_same_value(test_query):
    di.add_medyator()
    query, query_handler = test_query
    di[query] = query_handler
    medyator = di[Medyator]

    # should get handler from serviceprovider (di container)
    result = medyator.send_query(query(1))
    assert result == 9001

    # should get handler from medyator container
    result = medyator.send_query(query(1))
    assert result == 9001


def test_should_execute_command_handler_and_set_the_value(test_command):
    di.add_medyator()
    command, _ = test_command
    medyator = di[Medyator]

    medyator.send_command(command("Hello, World!"))
    handler = di[command]
    assert handler.value == "Hello, World!"


def test_should_raise_HandlerNotFound_error_when_query_handler_is_not_found(test_query):
    di.add_medyator()
    medyator = di[Medyator]
    query, _ = test_query
    with pytest.raises(HandlerNotFound):
        medyator.send_query(query(1))
