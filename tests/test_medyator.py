import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from medyator.medyator import Medyator
from medyator.contracts import Query, Command
from medyator.request_handler import QueryHandler, CommandHandler

from kink import di
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

    class TestCommandHandler(CommandHandler[TestCommand]):
        def __init__(self) -> None:
            self.value = None

        def __call__(self, request: TestCommand) -> None:
            self.value = request.value

    return TestCommand, TestCommandHandler()


def test_query_handler(test_query):

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
