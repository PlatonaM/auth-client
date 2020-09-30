auth-client
================

Helper package for accessing the platform HTTP API.

----------

+ [Installation](#installation)
+ [Client API](#client-api)
    + [Client object](#client-object)
    + [Get Token](#get-token)
    + [Get Header](#get-header)
+ [Logging](#logging)
+ [Example](#example)

----------

Installation
-----------------

Install the `auth-client` package via pip by issuing the following command: 

`pip install git+https://github.com/PlatonaM/auth-client.git`

Upgrade to new version: `pip install --upgrade git+https://github.com/PlatonaM/auth-client.git`

Uninstall: `pip uninstall auth-client`

Client API
-----------------

### Client object

Create a client object with:

    auth_client.Client(url, usr, pw, id, timeout=15)

+ `url` URL of token provider
+ `usr` Username
+ `pw` Password
+ `id` Client ID required by the token provider.
+ `timeout` Request timeout [optional]

### Get Token

Retrieves new access token or refreshes existing access token. Returns access token as string.

    getAccessToken()

Raises `NoTokenError` if no token can be retrieved.

### Get Header

Convenience method wrapping getAccessToken. Returns authorization HTTP header with access token as dictionary.

    getHeader()

Raises `NoTokenError` if no token can be retrieved.

Logging
-----------------

The package utilizes the python logging facility to provide feedback during runtime. Enable logging via:
        
    auth_client.logger.init(level=logging.INFO, handler=None, formatter=None)

+ `level` Set log level [optional] ([see levels](https://docs.python.org/3/library/logging.html#logging-levels))
+ `handler` Output handler object [optional] ([see handlers](https://docs.python.org/3/library/logging.handlers.html#module-logging.handlers))
+ `formatter` Output formatter object [optional] ([see formatter](https://docs.python.org/3/library/logging.html#formatter-objects))

Example
-----------------

The package can be used with your favorite HTTP library. This example uses the popular python [requests](https://requests.readthedocs.io/en/master/) library.

    import auth_client
    import logging
    import requests

    # enable logging and set level to debug
    auth_client.logger.init(logging.DEBUG)
    
    # create a client object by providing the necessary credetials
    ac = auth_client.Client(
        url="https://auth.platform.com/token",
        usr="my-user",
        pw="my-password",
        id="my-client-id"
    )
    
    # send a request to the platform
    response = requests.get(
        url="https://api.platform.com/data/my-data",
        headers={"Authorization": "Bearer " + ac.getAccessToken()}
    )
    
    # or for convenience
    response = requests.get(
        url="https://api.platform.com/data/my-data",
        headers=ac.getHeader()
    )
