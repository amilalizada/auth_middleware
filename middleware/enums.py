from enum import Enum


class LocationEnum(str, Enum):
    HEADER = "header"
    COOKIE = "cookie"