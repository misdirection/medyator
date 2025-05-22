# Medyator
[![PyPI version](https://badge.fury.io/py/Medyator.svg)](https://badge.fury.io/py/Medyator) ![Mediator tests](https://github.com/misdirection/medyator/actions/workflows/python-app.yml/badge.svg)


In-process messaging in Python, supporting both synchronous and asynchronous operations.

Leverages `kink` for dependency injection to resolve handlers.

## Key Features

*   Synchronous and Asynchronous Command/Query handling.
*   Decorator-based handler registration.
*   Integration with `kink` for dependency injection.

## Installation

`kink` is a direct dependency and will be installed automatically.

```bash
pip install medyator
```

## How to Use

### 1. Define Your Requests and Handlers

Requests can be simple commands (actions) or queries (data retrieval). Handlers process these requests.

**Synchronous Example:**

```python
from medyator import Command, Query, CommandHandler, QueryHandler
from medyator import command_handler, query_handler # Decorators

# Define a command
class MySyncCommand(Command):
    def __init__(self, message: str):
        self.message = message

# Define a handler for the command
@command_handler(MySyncCommand)
class MySyncCommandHandler(CommandHandler[MySyncCommand]):
    def __init__(self):
        # This handler can have its dependencies injected by kink
        print(f"{type(self).__name__} initialized")

    # For sync handlers, implement __call__
    def __call__(self, request: MySyncCommand) -> None:
        print(f"Sync command handled with message: {request.message}")

# Define a query
class MySyncQuery(Query[str]): # Expects a string response
    def __init__(self, query_id: int):
        self.query_id = query_id

# Define a handler for the query
@query_handler(MySyncQuery)
class MySyncQueryHandler(QueryHandler[MySyncQuery, str]):
    def __init__(self):
        print(f"{type(self).__name__} initialized")

    # For sync handlers, implement __call__
    def __call__(self, request: MySyncQuery) -> str:
        return f"Sync query result for ID: {request.query_id}"
```

### 2. Configure Medyator and Kink DI

Register your handlers with `kink` and then configure `medyator`.

```python
from kink import di
from medyator import Medyator
from medyator.kink import configure_medyator
import asyncio # For running async code

# Register your handler types with kink's DI container
# Kink will manage their instantiation (e.g., as singletons or transients)
di[MySyncCommandHandler] = MySyncCommandHandler
di[MySyncQueryHandler] = MySyncQueryHandler
# Or use di.add_singleton, di.add_transient, etc.
# di.add_singleton(MySyncCommandHandler) 
# di.add_singleton(MySyncQueryHandler)


# Configure Medyator to use kink and the default handler registry
# (where @command_handler and @query_handler register by default)
configure_medyator(di)

# Resolve Medyator instance from kink
medyator = di[Medyator]
```

### 3. Sending Requests (Now Asynchronous)

All `send` operations are now asynchronous, even for synchronous handlers.

```python
async def main_sync_example():
    # Send a command
    await medyator.send(MySyncCommand("Hello from sync command!"))

    # Send a query
    query_result = await medyator.send(MySyncQuery(query_id=101))
    print(query_result)

if __name__ == "__main__":
    asyncio.run(main_sync_example())
```

### Async Operations

Medyator also supports fully asynchronous requests and handlers.

**Asynchronous Example:**

```python
from medyator import AsyncCommand, AsyncQuery, AsyncCommandHandler, AsyncQueryHandler
# Decorators @command_handler and @query_handler work for async handlers too.

# Define an async command
class MyAsyncCommand(AsyncCommand):
    def __init__(self, task_id: int):
        self.task_id = task_id

# Define an async handler for the command
@command_handler(MyAsyncCommand) # Uses the same decorator
class MyAsyncCommandHandler(AsyncCommandHandler[MyAsyncCommand]):
    def __init__(self):
        print(f"{type(self).__name__} initialized")

    # For async handlers, implement `async def handle`
    async def handle(self, request: MyAsyncCommand) -> None:
        print(f"Starting async command for task: {request.task_id}")
        await asyncio.sleep(0.1) # Simulate async work
        print(f"Finished async command for task: {request.task_id}")

# Define an async query
class MyAsyncQuery(AsyncQuery[str]): # Expects a string response
    def __init__(self, user_id: str):
        self.user_id = user_id

# Define an async handler for the query
@query_handler(MyAsyncQuery) # Uses the same decorator
class MyAsyncQueryHandler(AsyncQueryHandler[MyAsyncQuery, str]):
    def __init__(self):
        print(f"{type(self).__name__} initialized")

    # For async handlers, implement `async def handle`
    async def handle(self, request: MyAsyncQuery) -> str:
        print(f"Fetching data asynchronously for user: {request.user_id}")
        await asyncio.sleep(0.1) # Simulate async work
        return f"Async data for {request.user_id}"

# Register async handlers with kink (similar to sync handlers)
di[MyAsyncCommandHandler] = MyAsyncCommandHandler
di[MyAsyncQueryHandler] = MyAsyncQueryHandler
# Or:
# di.add_singleton(MyAsyncCommandHandler)
# di.add_singleton(MyAsyncQueryHandler)

# No need to call configure_medyator(di) again if already called.
```

**Sending Async Requests:**

```python
async def main_async_example():
    # Send an async command
    await medyator.send(MyAsyncCommand(task_id=202))

    # Send an async query
    async_query_result = await medyator.send(MyAsyncQuery(user_id="user_abc"))
    print(async_query_result)

if __name__ == "__main__":
    # You would typically integrate this into your application's main async loop
    # For standalone example:
    # Assuming main_sync_example() might have already run and configured Medyator
    # If running this independently, ensure Medyator is configured.
    asyncio.run(main_async_example())
```

Look at the tests for more examples, especially on how handlers are registered with the `HandlerRegistry` via decorators and then provided to `kink`.

## Planned Features

| Feature          |  Status      | 
|:-----------------|:------------:|
|  Async           | Implemented  | 
|  Notifications   | planned      |   
|  Pipelines       | planned      | 

## Feedback

If you have any feedback, please reach out to us at misdirection@live.de


## Acknowledgements

 - [this project is heavily inspired by: Mediatr](https://github.com/jbogard/MediatR)

## License

This project is licensed under the MIT License. See the LICENSE file for more details.