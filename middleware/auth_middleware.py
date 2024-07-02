import aiohttp
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from middleware.client import Client

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, validation_service_url: str, location: str, key: str, timeout: int = 10):
        super().__init__(app)
        self.validation_service_url = validation_service_url
        self.timeout = timeout
        self.location = location
        self.key = key

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if self.location == "header":
            token = request.headers.get("Authorization")
        elif self.location == "cookie":
            token = request.cookies.get(self.key)
        if token is None:
            return Response(content={"status_code": 401, "message": "Unauthorized"}, status_code=401)
        custom_headers = dict(request.headers)
        custom_headers["Authorization"] = token
        if not token.startswith("Bearer "):
            token = f"Bearer {token}"

        client = Client(url=self.validation_service_url, headers=custom_headers, timeout=self.timeout)
        check_result = await client.check()
        if not check_result:
            return Response(content={"status_code": 401, "message": "Unauthorized"}, status_code=401)
        
        response = await call_next(request)
        response.set_cookie(key=self.key, value=client.cooked_value, httponly=True)
                
        return response
