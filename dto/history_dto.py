import collections

HistoryDto = collections.namedtuple(
    'History', ['parent_id', 'parent_name', 'category', 'author', 'branch', 'status', 'note', 'date', ])
