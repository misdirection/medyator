import pytest
from medyator.errors import HandlerNotFound
from medyator.contracts import Command, Query, BaseRequest

class SampleErrorCommand(Command):
    pass

class SampleErrorQuery(Query[str]):
    pass

class SampleErrorBaseRequest(BaseRequest): # For testing with a direct BaseRequest subclass
    pass


def test_handler_not_found_for_request():
    command_instance = SampleErrorCommand()
    error = HandlerNotFound.for_request(command_instance)
    
    assert isinstance(error, HandlerNotFound)
    expected_msg = f"No handler has been found for request of type {type(command_instance).__name__}!"
    assert str(error) == expected_msg

def test_handler_not_found_for_request_type_command():
    command_type = SampleErrorCommand
    error = HandlerNotFound.for_request_type(command_type)
    
    assert isinstance(error, HandlerNotFound)
    expected_msg = f"No handler has been found for request type {command_type.__name__}!"
    assert str(error) == expected_msg

def test_handler_not_found_for_request_type_query():
    query_type = SampleErrorQuery
    error = HandlerNotFound.for_request_type(query_type)
    
    assert isinstance(error, HandlerNotFound)
    expected_msg = f"No handler has been found for request type {query_type.__name__}!"
    assert str(error) == expected_msg

def test_handler_not_found_for_request_type_base_request_subclass():
    # Test with a class that inherits BaseRequest but not Command or Query
    # This scenario is less common in normal usage but tests the method's flexibility
    request_type = SampleErrorBaseRequest
    error = HandlerNotFound.for_request_type(request_type)
    
    assert isinstance(error, HandlerNotFound)
    expected_msg = f"No handler has been found for request type {request_type.__name__}!"
    assert str(error) == expected_msg

def test_handler_not_found_direct_instantiation():
    custom_message = "A very specific handler was not found."
    error = HandlerNotFound(custom_message)
    assert str(error) == custom_message
```
