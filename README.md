# FastAPI Authentication Gateway Middleware

This module provides middleware for verifying authorization tokens from request headers or cookies in a FastAPI application. It ensures secure authentication by validating tokens against an external authentication service.

# Features

- Middleware for FastAPI that intercepts requests for authentication validation.

- Supports token authentication via headers or cookies.

- Configurable validation service URL, headers, and timeout.

- Custom error messages and headers.

- Ability to exclude specific URLs from authentication.

## Installation

You can install the package using `pip`:

```sh
pip install fastapi-auth-gateway

Alternatively, if you prefer to use poetry for package dependencies:
```sh
poetry shell
poetry add fastapi-auth-gateway
```

# Usage

## Middleware Setup

To use the authentication middleware, include it in your FastAPI application:

```sh
from fastapi_auth_gateway import FastAPIAuthGateway, AuthLocation

app = FastAPI()

app.add_middleware(
    FastAPIAuthGateway,
    validation_service_url="https://auth.example.com/validate",
    key="Authorization",
    auth_location=AuthLocation.HEADER,
    timeout=10,
    custom_headers={"X-Custom-Header": "Value"},
    custom_error={"error": "Unauthorized access"},
    exclude_urls=["/public", "/health"]
)
```

## Token Validation Process

- The middleware extracts the token from either the request header (Authorization) or a cookie.

- If a token is missing, it returns a 401 Unauthorized response.

- The token is validated against an external authentication service via AuthValidationClient.

- If the token is invalid, it returns the error response from the authentication service.

- If the token is valid, the request proceeds to the next middleware or endpoint.


# Components

`FastAPIAuthGateway`

A middleware that intercepts requests and verifies authentication tokens before allowing access to endpoints.

`AuthValidationClient`

A client that handles the authentication validation process using aiohttp to communicate with an external validation service.

`AuthLocation`

An enumeration defining where authentication tokens can be extracted from:

- `HEADER`: Extract token from request headers.

- `COOKIE`: Extract token from request cookies.

# Configuration Options

| Parameter | Type | Description |
| --- | --- | --- |
| `validation_service_url` | `str` | The URL of the authentication validation service. |
| `key` | `str` | The key used for token extraction (e.g., "Authorization"). |
| `auth_location` | `AuthLocation` | Defines whether authentication is handled via headers or cookies. |
| `timeout` | `int` | Timeout for authentication requests (in seconds). |
| `custom_headers` | `dict`(optional) | Custom headers to include in authentication requests. |
| `custom_error` | `dict`(optional) | Custom error message response for unauthorized access. |
| `exclude_urls` | `list`(optional) | List of endpoint paths to exclude from authentication. |

Example Response

If authentication fails, the middleware returns a `401 Unauthorized` response:
```sh
{
    "message": "Unauthorized"
}
```

# License

This project is licensed under the MIT License.
