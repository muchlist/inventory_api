from datetime import datetime
from typing import NamedTuple, List


class PingState(NamedTuple):
    time_second: float
    time_date: datetime
    status: str


class CctvDto(NamedTuple):
    created_at: datetime
    updated_at: datetime
    cctv_name: str
    ip_address: str
    inventory_number: str
    author: str
    branch: str
    location: str
    year: datetime
    merk: str
    tipe: str
    last_status: str
    note: str
    deactive: bool
    ping_state: List[PingState]


class CctvEditDto(NamedTuple):
    filter_id: str
    filter_timestamp: datetime
    filter_branch: str

    updated_at: datetime
    cctv_name: str
    ip_address: str
    inventory_number: str
    author: str
    location: str
    year: datetime
    merk: str
    tipe: str
    note: str
    deactive: bool
