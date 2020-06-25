from datetime import datetime
from typing import NamedTuple, List


class StockDto(NamedTuple):
    author: str
    branch: str
    location: str
    created_at: datetime
    updated_at: datetime
    stock_name: str
    category: str
    unit: str
    threshold: float
    note: str
    qty: float
    increment: List
    decrement: List
    deactive: bool


class StockEditDto(NamedTuple):
    filter_id: str
    filter_timestamp: datetime
    filter_branch: str

    author: str
    location: str
    updated_at: datetime
    stock_name: str
    category: str
    unit: str
    threshold: float
    note: str
    deactive: bool


class UseStockDto(NamedTuple):
    parent_id: str
    branch: str
    author: str
    qty: float
    ba_number: str
    note: str
    time: datetime
