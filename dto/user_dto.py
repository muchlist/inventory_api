import collections

UserDto = collections.namedtuple(
    'User', ['username', 'password', 'name', 'email', 'is_admin', 'is_end_user', 'branch'])
