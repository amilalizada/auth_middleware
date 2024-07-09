import aiohttp
from fastapi import Response
from .enums import LocationEnum

class Client:
    def __init__(self, url: str, headers: dict, timeout: int, location: str, key: str):
        self.url = url
        self.headers = headers
        self.timeout = timeout
        self.cooked_value = None
        self.header_value = None
        self.location = location
        self.key = key

    async def check(self):
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            async with session.get(
                url=self.url,
                headers=self.headers,
                ssl=False,
            ) as response:
                if not response.status.ok:
                    return False
                if self.location == LocationEnum.COOKIE.value:
                    self.cooked_value = response.cookies.get(self.key)
                elif self.location == LocationEnum.HEADER.value:
                    self.header_value = response.headers.get("Authorization")
        
        return True