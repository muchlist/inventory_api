from datetime import datetime
from typing import NamedTuple


class AppsHistoDto(NamedTuple):
    created_at: datetime
    updated_at: datetime
    parent_id: str
    parent_name: str
    category: str
    author: str
    author_id: str
    branch: str
    location: str
    start_date: datetime
    end_date: datetime
    duration: int
    title: str
    desc: str


class AppsEditHistoDto(NamedTuple):
    filter_id: str
    filter_timestamp: datetime
    filter_branch: str

    category: str
    author: str
    author_id: str
    branch: str
    location: str
    start_date: datetime
    end_date: datetime
    duration: int
    title: str
    desc: str
