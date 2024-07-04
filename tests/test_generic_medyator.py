import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from src.generic_medyator import GenericMedyator
from src.request import Request, RequestWithResponse
from src.request_handler import RequestHandler, RequestHandlerWithResponse


class TestRequest(Request):
    def __init__(self, value: int) -> None:
        self.value = value


class TestRequestHandler(RequestHandler[TestRequest]):
    def __call__(self, request: TestRequest) -> None:
        request.value += 1


class TestRequestWithResponse(RequestWithResponse):
    def __init__(self, value: int) -> None:
        self.value = value


class TestRequestHandlerWithResponse(RequestHandlerWithResponse[TestRequestWithResponse, int]):
    def __call__(self, request: TestRequestWithResponse) -> int:
        return request.value + 1


def test_register_handler():
    medyator = GenericMedyator()

    medyator.register_handler(TestRequest, TestRequestHandler())

    medyator.send(TestRequest(1))


def test_register_handler_with_response():
    medyator = GenericMedyator()

    medyator.register_handler(TestRequestWithResponse, TestRequestHandlerWithResponse())

    response = medyator.send(TestRequestWithResponse(1))

    assert response == 2
