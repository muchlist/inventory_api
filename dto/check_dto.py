from datetime import datetime
from typing import NamedTuple, Optional, List


class CheckObjEmbedDto(NamedTuple):
    id: str
    name: str
    is_checked: bool
    checked_at: Optional[datetime]
    checked_note: str
    is_resolve: bool
    location: str
    type: str
    image_path: str


class CheckObjEmbedEditDto(NamedTuple):
    filter_parent_id: str
    filter_id: str
    filter_type: str

    is_checked: bool
    checked_at: datetime
    checked_note: str
    is_resolve: bool


class CheckObjEmbedInsertPhotoDto(NamedTuple):
    filter_parent_id: str
    filter_type: str
    filter_id: str

    image_path: str


class CheckDto(NamedTuple):
    created_at: datetime
    created_by: datetime
    updated_at: datetime
    shift: int
    branch: str
    is_finish: bool
    checks_obj: List  # list of dict CheckObjEmbedDto


class EditCheckDto(NamedTuple):
    filter_id: str
    filter_branch: str

    updated_at: datetime
    shift: int
    branch: str
    is_finish: bool
