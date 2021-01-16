from datetime import datetime
from typing import NamedTuple


class CheckObjDto(NamedTuple):
    created_at: datetime
    updated_at: datetime
    name: str
    branch: str
    location: str
    type: str
    last_status: str
    note: str


class EditCheckObjDto(NamedTuple):
    filter_id: str
    filter_branch: str

    updated_at: datetime
    name: str
    branch: str
    location: str
    type: str
    note: str
