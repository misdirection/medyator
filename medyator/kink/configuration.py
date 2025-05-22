from typing import Optional
from kink import Container
from ..medyator import Medyator
from ..registration import HandlerRegistry, default_handler_registry
from .kink_service_provider import KinkServiceProvider
from ..contracts import ServiceProvider # For type hinting if KinkServiceProvider is registered

def configure_medyator(
    di: Container,
    registry: Optional[HandlerRegistry] = None
) -> Medyator:
    """
    Configures and registers Medyator and its KinkServiceProvider with a kink DI container.

    Args:
        di: The kink Container instance.
        registry: An optional HandlerRegistry instance. If None, the
                  default_handler_registry will be used.

    Returns:
        The configured Medyator instance.
    """
    actual_registry = registry if registry is not None else default_handler_registry

    service_provider = KinkServiceProvider(di=di, registry=actual_registry)
    medyator_instance = Medyator(service_provider=service_provider)

    # Register Medyator instance in the DI container
    di[Medyator] = medyator_instance

    # Optionally, register the KinkServiceProvider instance itself.
    # This might be useful if other services need direct access to it,
    # though Medyator is the primary interface.
    di[ServiceProvider] = service_provider # Registering against the protocol
    di[KinkServiceProvider] = service_provider # Registering against concrete type

    return medyator_instance

__all__ = ["configure_medyator"]
