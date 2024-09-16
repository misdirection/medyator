from abc import ABC
from typing import Generic, TypeVar

TResponse = TypeVar("TResponse")


class BaseRequest(ABC):
    pass


class Command(BaseRequest):
    pass


class Query(Generic[TResponse], BaseRequest):
    pass
