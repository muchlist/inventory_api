from datetime import datetime
from typing import NamedTuple


class SpecDto(NamedTuple):
    processor: int
    ram: int
    hardisk: int
    score: int


class ComputerDto(NamedTuple):
    created_at: datetime
    updated_at: datetime
    client_name: str
    hostname: str  # = "1" untuk default
    ip_address: str
    inventory_number: str
    author: str
    branch: str
    location: str
    division: str
    seat_management: bool
    year: datetime
    merk: str
    tipe: str
    operation_system: str
    last_status: str
    note: str
    deactive: bool
    spec: SpecDto


class ComputerEditDto(NamedTuple):
    filter_id: str
    filter_timestamp: datetime
    filter_branch: str

    updated_at: datetime
    client_name: str
    hostname: str
    ip_address: str
    inventory_number: str
    author: str
    location: str
    division: str
    seat_management: bool
    year: datetime
    merk: str
    operation_system: str
    note: str
    deactive: bool
    spec: SpecDto
