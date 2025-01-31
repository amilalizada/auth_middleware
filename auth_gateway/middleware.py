import json
from http import HTTPStatus
from typing import Any, Dict, List, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from auth_gateway.client import AuthValidationClient

from .enums import AuthLocation

error_msg = {"message": HTTPStatus.UNAUTHORIZED.phrase}


class AuthGateway(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        validation_service_url: str,
        key: str,
        auth_location: AuthLocation = AuthLocation.HEADER,
        timeout: int = 10,
        custom_headers: Optional[Dict[Any, Any]] = None,
        custom_error: Optional[Dict[Any, Any]] = None,
        exclude_urls: Optional[List[str]] = None
    ):
        super().__init__(app)
        AuthLocation.check_location(auth_location)
        self.validation_service_url = validation_service_url
        self.timeout = timeout
        self.auth_location = auth_location
        self.key = key
        self.custom_headers = custom_headers
        self.custom_error = custom_error
        self.exclude_urls = exclude_urls

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.url.path in self.exclude_urls:
            return await call_next(request)
        if self.auth_location == AuthLocation.HEADER.value:
            token = request.headers.get("Authorization")
        elif self.auth_location == AuthLocation.COOKIE.value:
            token = request.cookies.get(self.key)
        if token is None:
            return Response(
                content=json.dumps(self.custom_error) if self.custom_error else json.dumps(error_msg),
                status_code=401,
                headers={"Content-Type": "application/json"},
            )
        request_headers = dict(request.headers)
        if self.custom_headers:
            request_headers.update(self.custom_headers)
        if self.auth_location == AuthLocation.COOKIE.value:
            request_headers["Authorization"] = token
        
        auth_client = AuthValidationClient(
            url=self.validation_service_url,
            headers=request_headers,
            timeout=self.timeout,
            auth_location=self.auth_location,
            key=self.key,
        )
        result, client_response = await auth_client.validate_auth()
        if not result:
            return Response(
                content=json.dumps(client_response),
                headers={"Content-Type": "application/json"},
            )
        response = await call_next(request)
        if self.auth_location == AuthLocation.COOKIE.value:
            response.set_cookie(key=self.key, value=auth_client.cooked_value, httponly=True)
        else:
            response.headers["Authorization"] = auth_client.header_value

        return response
