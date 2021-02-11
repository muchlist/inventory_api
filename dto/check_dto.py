from datetime import datetime
from typing import NamedTuple, Optional, List


class CheckObjEmbedDto(NamedTuple):
    id: str
    name: str
    is_checked: bool
    checked_at: Optional[datetime]
    checked_note: str
    have_problem: bool
    # is_resolve: bool
    complete_status: int  # 0 progress, 1 pending, 2 complete
    location: str
    type: str
    image_path: str
    tag_one: List[str]
    tag_two: List[str]
    tag_one_selected: str
    tag_two_selected: str


class CheckObjEmbedEditDto(NamedTuple):
    filter_parent_id: str
    filter_id: str
    filter_author: str

    is_checked: bool
    checked_at: datetime
    checked_note: str
    have_problem: bool
    # is_resolve: bool
    complete_status: int  # 0 progress, 1 pending, 2 complete
    tag_one_selected: str
    tag_two_selected: str


class CheckObjEmbedInsertPhotoDto(NamedTuple):
    filter_parent_id: str
    filter_id: str
    filter_author: str

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
    filter_author: str

    updated_at: datetime
    shift: int
    branch: str
    is_finish: bool
