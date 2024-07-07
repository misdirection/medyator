from __future__ import annotations

from .contracts import BaseRequest


class HandlerNotFound(Exception):
    @classmethod
    def for_request(cls, request: BaseRequest) -> HandlerNotFound:
        return cls(f"No handler has been found for {request}!")
