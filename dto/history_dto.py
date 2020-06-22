import collections

HistoryDto = collections.namedtuple(
    'History', ['parent_id', 'category', 'author', 'branch', 'status', 'note', 'date',])
