from datetime import datetime
from typing import NamedTuple


class HandheldDto(NamedTuple):
    created_at: datetime
    updated_at: datetime
    handheld_name: str
    ip_address: str
    inventory_number: str
    author: str
    branch: str
    location: str
    year: datetime
    merk: str
    tipe: str
    phone: str
    note: str
    last_status: str
    deactive: bool


class HandheldEditDto(NamedTuple):
    filter_id: str
    filter_timestamp: datetime
    filter_branch: str

    updated_at: datetime
    handheld_name: str
    ip_address: str
    inventory_number: str
    author: str
    location: str
    year: datetime
    merk: str
    tipe: str
    phone: str
    note: str
    deactive: bool


class HandheldChangeActiveDto(NamedTuple):
    filter_id: str
    filter_timestamp: datetime
    filter_branch: str

    updated_at: datetime
    deactive: bool
