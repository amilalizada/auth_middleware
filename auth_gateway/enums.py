from enum import Enum


class AuthLocation(str, Enum):
    HEADER = "header"
    COOKIE = "cookie"

    @classmethod
    def check_location(cls, auth_location: str):
        if auth_location not in cls._value2member_map_:
            raise ValueError(f"Auth location '{auth_location}' is not supported")
