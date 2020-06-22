from typing import NamedTuple
from datetime import datetime

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
    spec: SpecDto