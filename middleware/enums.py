from enum import Enum


class LocationEnum(str, Enum):
    HEADER = "header"
    COOKIE = "cookie"

    @classmethod
    def check_location(cls, location: str):
        if location not in cls._value2member_map_:
            raise ValueError(f"Location '{location}' is not supported")
