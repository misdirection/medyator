# Medyator
[![PyPI version](https://badge.fury.io/py/Medyator.svg)](https://badge.fury.io/py/Medyator) [![Mediator tests](https://github.com/misdirection/medyator/actions/workflows/python-app.yml/badge.svg)](https://github.com/misdirection/medyator/actions/workflows/python-app.yml/badge.svg)

Medyator is a Python library implementing the mediator pattern, drawing direct inspiration from the popular MediatR library in the .NET ecosystem. Its primary goal is to enable simple, in-process messaging, helping you create more decoupled, maintainable, and testable application architectures.

At its core, Medyator facilitates communication between components by dispatching requests (Commands or Queries) to their respective handlers. This means:

*   **Commands**: Objects that represent an intent to perform an action or change state. They are sent to a single handler.
*   **Queries**: Objects that represent a request for data. They are sent to a single handler which returns a response.
*   **Handlers**: Classes responsible for acting upon a specific type of Command or Query.

By using Medyator, you can avoid direct dependencies between components, instead allowing them to collaborate through messages. This promotes the Single Responsibility Principle and makes your system easier to evolve. Medyator integrates with the `kink` dependency injection library to resolve handlers and manage their dependencies.

## Key Features

*   **Command/Query Separation**: Clearly distinguishes between operations that change state (Commands) and operations that retrieve data (Queries).
*   **Decoupled Communication**: Enables components to interact without direct dependencies, using Medyator as the central dispatch.
*   **Synchronous & Asynchronous Handlers**: Supports both standard synchronous handlers (`def __call__`) and asynchronous handlers (`async def __call__`) for non-blocking operations. The `Medyator.send()` method is asynchronous and should always be `await`ed.
*   **Kink Dependency Injection Integration**: Seamlessly uses `kink` for resolving handlers and their dependencies.
*   **Lightweight & Focused**: Aims for a minimal implementation of the core mediator pattern without unnecessary complexity.
*   **Inspired by MediatR**: Follows the successful patterns of the well-regarded MediatR library.

## Installation

To get started, install Medyator and its peer dependency, `kink`:

```bash
pip install medyator kink
```

## Core Usage Example

Here's a basic example to illustrate how to use Medyator:

**1. Define your Requests (Commands/Queries):**

```python
# requests.py
from medyator import Command, Query

class PlaceOrderCommand(Command):
    def __init__(self, user_id: int, product_id: str, quantity: int):
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity

class GetProductQuery(Query[str]): # str is the expected response type
    def __init__(self, product_id: str):
        self.product_id = product_id
```

**2. Create Handlers for your Requests:**

Handlers can be synchronous or asynchronous. Medyator will correctly `await` asynchronous handlers.

```python
# handlers.py
from medyator import CommandHandler, QueryHandler
from .requests import PlaceOrderCommand, GetProductQuery
import asyncio # For async example

# Synchronous Command Handler
class PlaceOrderCommandHandler(CommandHandler[PlaceOrderCommand]):
    def __call__(self, request: PlaceOrderCommand) -> None:
        print(f"Order placed for user {request.user_id} "
              f"with product {request.product_id} (quantity: {request.quantity}).")
        # In a real application, you'd interact with a database or other services here.

# Asynchronous Query Handler
class GetProductQueryHandler(QueryHandler[GetProductQuery, str]):
    async def __call__(self, request: GetProductQuery) -> str:
        print(f"Fetching product {request.product_id}...")
        await asyncio.sleep(0.5) # Simulate async I/O
        return f"Product Data for {request.product_id}"
```

**3. Configure Dependency Injection and Send Requests:**

Medyator uses `kink` for dependency injection.

```python
# main.py
from kink import di
from medyator import Medyator
import medyator.kink # This applies the .add_medyator() extension to kink's container
import asyncio

from .requests import PlaceOrderCommand, GetProductQuery
from .handlers import PlaceOrderCommandHandler, GetProductQueryHandler

async def main_app_logic():
    # Register Medyator and your handlers with kink
    # This extension method registers an instance of Medyator, configured with KinkServiceProvider.
    di.add_medyator() 
    
    # Register your handlers with kink.
    # A common pattern is to use the request type as the key for the handler.
    di[PlaceOrderCommand] = PlaceOrderCommandHandler() 
    di[GetProductQuery] = GetProductQueryHandler()

    # Resolve Medyator from the DI container
    medyator_instance = di[Medyator]

    # Send a command (handler is sync, but send() is always awaited)
    await medyator_instance.send(PlaceOrderCommand(user_id=123, product_id="XYZ789", quantity=2))

    # Send a query (handler is async)
    product_data = await medyator_instance.send(GetProductQuery(product_id="ABC123"))
    print(f"Received: {product_data}")

if __name__ == "__main__":
    asyncio.run(main_app_logic())
```

This example demonstrates:
*   Defining `Command` and `Query` classes.
*   Implementing corresponding `CommandHandler` and `QueryHandler` (one sync, one async).
*   Setting up `kink` and registering Medyator along with the handlers using `di.add_medyator()`.
*   Sending commands and queries using `await medyator_instance.send()`.

## Future Enhancements (Planned Features)

While Medyator currently provides core command and query dispatching, the following features, common in comprehensive mediator implementations, are planned for future development:

| Feature         | Status  | Notes                                                                 |
|:----------------|:--------:|:----------------------------------------------------------------------|
| Notifications   | Planned | Support for publishing events to multiple handlers (one-to-many).     |
| Pipelines       | Planned | Allow defining behaviors to intercept and process requests/notifications. |

## Feedback

We welcome your feedback and contributions! If you have any suggestions or encounter issues, please feel free to [open an issue on GitHub](https://github.com/misdirection/medyator/issues) or reach out via email at misdirection@live.de.

## Acknowledgements

 - This project is heavily inspired by: [MediatR](https://github.com/jbogard/MediatR) by Jimmy Bogard.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
