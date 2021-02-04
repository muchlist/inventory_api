from datetime import datetime
from typing import NamedTuple
from typing import List


class CheckObjDto(NamedTuple):
    created_at: datetime
    updated_at: datetime
    name: str
    branch: str
    location: str
    type: str
    last_status: str
    shifts: List[int]
    note: str


class EditCheckObjDto(NamedTuple):
    filter_id: str
    filter_branch: str

    updated_at: datetime
    name: str
    branch: str
    location: str
    type: str
    shifts: List[int]
    note: str


class EditCheckObjBySystemDto(NamedTuple):
    filter_id: str
    updated_at: datetime
    checked_note: str
    have_problem: bool
    is_resolve: bool
