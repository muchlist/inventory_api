import collections

UserDto = collections.namedtuple(
    'User', ['username', 'password', 'name', 'email', 'isAdmin', 'isEndUser', 'branch'])
