from __future__ import annotations

from .contracts import BaseRequest


class HandlerNotFound(Exception):
    @classmethod
    def for_request(cls, request: BaseRequest) -> HandlerNotFound:
        return cls(f"No handler has been found for request of type {type(request).__name__}!")

    @classmethod
    def for_request_type(cls, request_type: type[BaseRequest]) -> HandlerNotFound:
        return cls(f"No handler has been found for request type {request_type.__name__}!")
