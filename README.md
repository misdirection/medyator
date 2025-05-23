# Medyator
[![PyPI version](https://badge.fury.io/py/Medyator.svg)](https://badge.fury.io/py/Medyator) ![Mediator tests](https://github.com/misdirection/medyator/actions/workflows/python-app.yml/badge.svg)


In-process messaging in Python.

Currently supports commands and queries using kink di.


## Installation


```bash
pip install medyator kink
```
    

## How to use

Container.add_medyator() from the medyator.kink module connects medyator with kink as the serviceprovider.

```python
from medyator import Medyator
from kink import di
import medyator.kink

di.add_medyator()
medyator = di[Medyator]

# Medyator.send() is now an asynchronous method and must be awaited.
# Assuming AddAddressCommand is a Command you have defined:
# await medyator.send(AddAddressCommand("test"))
# For a query:
# result = await medyator.send(YourQuery(query_params))

```

Look at the tests for more examples.

### Defining Handlers (Sync or Async)

Handlers for commands or queries are classes that implement `CommandHandler[YourCommand]` or `QueryHandler[YourQuery, YourResponse]`. The key change with async support is that the `__call__` method of your handler can be either a standard synchronous method or an `async def` coroutine. Medyator will correctly invoke it in either case.

You do not need to use special `AsyncCommand` or `AsyncQuery` base types; simply use `Command` and `Query`.

**Example of an asynchronous Command Handler:**

```python
from medyator import CommandHandler, Command
import asyncio # For example

# Define your command
class MyTaskCommand(Command):
    def __init__(self, task_id: int):
        self.task_id = task_id

# Define your asynchronous handler
class MyTaskCommandHandler(CommandHandler[MyTaskCommand]):
    async def __call__(self, request: MyTaskCommand) -> None:
        print(f"Starting asynchronous task: {request.task_id}")
        await asyncio.sleep(1) # Simulate I/O-bound work
        print(f"Asynchronous task {request.task_id} completed.")

# Registration (using Kink DI as an example):
# from kink import di
# di[MyTaskCommand] = MyTaskCommandHandler()

# Usage (in an async function):
# async def do_work():
#     medyator = di[Medyator]
#     await medyator.send(MyTaskCommand(123))
```

If `MyTaskCommandHandler.__call__` was a regular `def` method, Medyator would call it synchronously.

## Planned Features

| Feature          |  Status  | 
|:-----------------|:--------:|
|  Async           | ✅ Supported  | 
|  Notifications   | planned  |   
|  Pipelines       | planned  | 

## Feedback

If you have any feedback, please reach out to us at misdirection@live.de


## Acknowledgements

 - [this project is heavily inspired by: Mediatr](https://github.com/jbogard/MediatR)

## License

This project is licensed under the MIT License. See the LICENSE file for more details.