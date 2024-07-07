import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from src.medyator import Medyator
from src.contracts import Query, Command
from src.request_handler import QueryHandler, CommandHandler
import src.kink
from kink import di
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

    class TestCommandHandler(CommandHandler[TestCommand]):
        def __init__(self) -> None:
            self.value = None

        def __call__(self, request: TestCommand) -> None:
            self.value = request.value

    return TestCommand, TestCommandHandler()


def test_query_handler(test_command, test_query):
    di.add_medyator()
    query, query_handler = test_query
    di[query] = query_handler
    # service_provider.register_handler(query, query_handler)
    # command, command_handler = test_command
    # service_provider.register_handler(command, command_handler)
    medyator = di[Medyator]
    result = medyator.sendQuery(query(1))
    assert result == 9001

    result = medyator.sendQuery(query(1))
    assert result == 9001

    # medyator.sendCommand(command('World'))
    # assert command_handler.value == 'World'
