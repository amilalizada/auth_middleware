import json
from http import HTTPStatus

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from token_middleware.client import Client
from typing import Optional, Dict, Any, Any
from .enums import LocationEnum

error_msg = {"message": HTTPStatus.UNAUTHORIZED.phrase}


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        validation_service_url: str,
        key: str,
        location: LocationEnum = LocationEnum.HEADER,
        timeout: int = 10,
        custom_headers: Optional[Dict[Any, Any]] = None,
        custom_error: Optional[Dict[Any, Any]] = None
    ):
        super().__init__(app)
        LocationEnum.check_location(location)
        self.validation_service_url = validation_service_url
        self.timeout = timeout
        self.location = location
        self.key = key
        self.custom_headers = custom_headers
        self.custom_error = custom_error

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if self.location == LocationEnum.HEADER.value:
            token = request.headers.get("Authorization")
        elif self.location == LocationEnum.COOKIE.value:
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
        if self.location == LocationEnum.COOKIE.value:
            request_headers["Authorization"] = token
        client = Client(
            url=self.validation_service_url,
            headers=request_headers,
            timeout=self.timeout,
            location=self.location,
            key=self.key,
        )
        result, client_response = await client.check()
        if not result:
            return Response(
                content=json.dumps(client_response),
                headers={"Content-Type": "application/json"},
            )
        response = await call_next(request)
        if self.location == LocationEnum.COOKIE.value:
            response.set_cookie(key=self.key, value=client.cooked_value, httponly=True)
        else:
            response.headers["Authorization"] = client.header_value

        return response
