from __future__ import annotations

from .contracts import BaseRequest


class RequestAlreadyRegistered(Exception):
    @classmethod
    def for_command(cls, command_type: str) -> RequestAlreadyRegistered:
        return cls(f"`{command_type}` has been already registered!")


class HandlerNotFound(Exception):
    @classmethod
    def for_request(cls, request: BaseRequest) -> HandlerNotFound:
        return cls(f"No handler has been found for {request}!")
