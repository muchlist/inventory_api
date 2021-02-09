from datetime import datetime
from typing import NamedTuple


class HistoryDto2(NamedTuple):
    parent_id: str
    parent_name: str
    category: str
    author: str
    author_id: str
    status: str
    branch: str
    note: str
    date: datetime  # start_date
    timestamp: datetime  # update_at

    created_at: datetime
    end_date: datetime
    location: str
    duration: int
    resolve_note: str
    # is_complete: bool
    complete_status: int # 0 progress, 1 pending, 2 complete
    updated_by: str
    updated_by_id: str


class EditHistoryDto2(NamedTuple):
    filter_id: str
    filter_timestamp: datetime
    filter_branch: str

    status: str
    location: str
    date: datetime
    end_date: datetime
    duration: int
    note: str
    resolve_note: str
    # is_complete: bool
    complete_status: int  # 0 progress, 1 pending, 2 complete
    updated_by: str
    updated_by_id: str
