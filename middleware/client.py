import aiohttp
from fastapi import Response

class Client:
    def __init__(self, url: str, headers: dict, timeout: int):
        self.url = url
        self.headers = headers
        self.timeout = timeout

    async def check(self):
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            async with session.get(
                url=self.url,
                headers=self.headers,
                ssl=False,
            ) as response:
                if response.status != 200:
                    return False
        
        return True