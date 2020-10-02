auth-client
================

Helper package for accessing platform HTTP APIs.

Supported grant types:
+ [resource-owner-password](https://docs.identityserver.io/en/aspnetcore2/topics/grant_types.html#resource-owner-password)
+ [client-credentials](https://docs.identityserver.io/en/aspnetcore2/topics/grant_types.html#client-credentials)

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

Install the `auth-client` package via pip by issuing the following command in combination with a desired version X.X.X from the available git tags:

`pip install git+https://github.com/PlatonaM/auth-client.git@X.X.X`

Upgrade to new version: `pip install --upgrade git+https://github.com/PlatonaM/auth-client.git@X.X.X`

Uninstall: `pip uninstall auth-client`

Client API
-----------------

### Client object

Create a client object with:

    auth_client.Client(url, client_id, secret=None, user=None, password=None, timeout=15)

+ `url` URL of authorization endpoint.
+ `client_id` Client ID required by the authorization endpoint.
+ `secret` Secret, required by the client-credentials grant type [optional]
+ `user` Username, required by the resource-owner-password grant type [optional]
+ `password` Password, required by the resource-owner-password grant type [optional]
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

The package can be used with your favorite HTTP library. The below examples use the popular python [requests](https://requests.readthedocs.io/en/master/) library.

#### resource-owner-password grant type:

    import auth_client
    import logging
    import requests

    # enable logging and set level to debug
    auth_client.logger.init(logging.DEBUG)
    
    # create a client object by providing the necessary credetials
    ac = auth_client.Client(
        url="https://auth.platform.com/token",
        client_id="my-client-id"
        user="my-user",
        password="my-password"
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

#### client-credentials grant type:

    import auth_client
    
    # create a client object by providing the necessary credetials
    ac = auth_client.Client(
        url="https://auth.platform.com/token",
        client_id="my-client-id",
        secret="my-secret"
    )