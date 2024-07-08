# Medyator
[![PyPI version](https://badge.fury.io/py/Medyator.svg)](https://badge.fury.io/py/Medyator)

In-process messaging in python.

Currently supports Commands and Queries using kink di.


## Installation


```bash
pip install medyator kink
```
    

## How to use

Import medyator, kink and medytor.kink to use kink di as serviceprovider.
Container.add_medyator() adds medyator to the di container and registers the container as the service provider for medyator.

```python
from medyator import Medyator
from kink import di
import medyator.kink

di.add_medyator()
medyator = di[Medyator]
medyator.send_command(AddAddressCommand("test"))

```

Look at the test for more examples.

## Planned Features

| Feature          |  Status  | 
|:-----------------|:--------:|
|  Async           | planned  | 
|  Notifications   | planned  |   
|  Pipelines       | planned  | 

## Feedback

If you have any feedback, please reach out to us at misdirection@live.de


## Acknowledgements

 - [this project is heavily inspired by: Mediatr](https://github.com/jbogard/MediatR)
