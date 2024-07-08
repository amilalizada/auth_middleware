import aiohttp
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from middleware.client import Client
from .enums import LocationEnum

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, validation_service_url: str, key: str, location: str = LocationEnum, timeout: int = 10):
        super().__init__(app)
        self.__check_location(location)
        self.validation_service_url = validation_service_url
        self.timeout = timeout
        self.location = location
        self.key = key

    def __check_location(self, location: str):
        if location not in LocationEnum:
            raise ValueError(f"Location {location} is not supported")

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if self.location == "header":
            token = request.headers.get("Authorization")
        elif self.location == "cookie":
            token = request.cookies.get(self.key)
        if token is None:
            return Response(content={"status_code": 401, "message": "Unauthorized"}, status_code=401)
        custom_headers = dict(request.headers)
        if self.location == "cookie":
            custom_headers["Authorization"] = f"Bearer {token}"
        client = Client(url=self.validation_service_url, headers=custom_headers, timeout=self.timeout)
        check_result = await client.check()
        if not check_result:
            return Response(content={"status_code": 401, "message": "Unauthorized"}, status_code=401)
        response = await call_next(request)
        if self.location == "cookie":
            response.set_cookie(key=self.key, value=client.cooked_value, httponly=True)
        else:
            response.headers["Authorization"] = f"Bearer {client.cooked_value}"
        
        return response
