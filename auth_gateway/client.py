from typing import Tuple, Union

import aiohttp

from .enums import AuthLocation


class AuthValidationClient:
    def __init__(self, url: str, headers: dict, timeout: int, location: str, key: str):
        self.url = url
        self.headers: dict = headers
        self.timeout: int = timeout
        self.cooked_value: Union[str, None] = None
        self.header_value: Union[str, None] = None
        self.location: Union[str, None] = location
        self.key: Union[str, None] = key

    async def validate_auth(self) -> Tuple[bool, Union[dict, None]]:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as session:
            async with session.get(
                url=self.url,
                headers=self.headers,
                ssl=False,
            ) as response:
                if response.status != 200:
                    return False, await response.json()
                if self.location == AuthLocation.COOKIE.value:
                    self.cooked_value = response.cookies.get(self.key)
                elif self.location == AuthLocation.HEADER.value:
                    self.header_value = response.headers.get("Authorization")

                return True, await response.json()
