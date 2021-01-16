from datetime import datetime
from typing import NamedTuple


class CheckObjEmbedDto(NamedTuple):
    id: str
    name: str
    is_checked: bool
    checked_at: datetime
    checked_note: str
    is_resolve: bool
    location: str
    type: str


class CheckObjEmbedEditDto(NamedTuple):
    filter_id: str

    is_checked: bool
    checked_at: datetime
    checked_note: str
    is_resolve: bool


class CheckDto(NamedTuple):
    created_at: datetime
    created_by: datetime
    updated_at: datetime
    shift: int
    branch: str
    is_finish: bool
    checks_obj: []  # CheckObjEmbedDto
    checks_cctv: []  # CheckObjEmbedDto


class EditCheckObjDto(NamedTuple):
    filter_id: str
    filter_branch: str

    updated_at: datetime
    shift: int
    branch: str
    is_finish: bool
