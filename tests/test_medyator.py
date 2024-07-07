import os
import sys
from typing import Type, cast
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from src.medyator import Medyator
from src.contracts import BaseRequest, Query, Command
from src.request_handler import QueryHandler, CommandHandler
from src.contracts.service_provider import ServiceProvider
from kink import di

Handler = CommandHandler | QueryHandler

class TestQuery(Query):
    def __init__(self, value: int) -> None:
        self.value = value

class TestQueryHandler(QueryHandler[TestQuery, int]):
    def __call__(self, request: TestQuery) -> int:
        return request.value + 9000

class KinkServiceProvider(ServiceProvider):
    def __init__(self) -> None:
        self.di = di
    def get(self, request: BaseRequest) -> Handler:
        if isinstance(request, Command):
            return cast(CommandHandler, self.di[request.__class__])
        elif isinstance(request, Query):
            return cast(QueryHandler, self.di[request.__class__])
        else:
            raise NotImplementedError

    def register_handler(self, request_type: Type[BaseRequest], handler: Handler) -> None:
        self.di[request_type] = handler


def test_query_handler():
    service_provider = KinkServiceProvider()
    service_provider.register_handler(TestQuery, TestQueryHandler())
    medyator = Medyator(service_provider)

    result = medyator.sendQuery(TestQuery(1))
    assert result == 9001

    result = medyator.sendQuery(TestQuery(1))
    assert result == 9001
