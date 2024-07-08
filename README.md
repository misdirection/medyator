# Medyator
[![PyPI version](https://badge.fury.io/py/Medyator.svg)](https://badge.fury.io/py/Medyator)

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
medyator.send_command(AddAddressCommand("test"))

```

Look at the tests for more examples.

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
