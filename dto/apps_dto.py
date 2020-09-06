from datetime import datetime
from typing import NamedTuple, List


class AppsDto(NamedTuple):
    created_at: datetime
    updated_at: datetime
    apps_name: str
    description: str
    url: str
    platform: str
    branches: List[str]
    programmers: List[str]
    note: str


class AppsEditDto(NamedTuple):
    filter_id: str
    filter_timestamp: datetime

    updated_at: datetime
    apps_name: str
    description: str
    url: str
    platform: str
    branches: List[str]
    programmers: List[str]
    note: str


class AppsCounterDto(NamedTuple):
    filter_id: str
    trouble: int
    minute: int
