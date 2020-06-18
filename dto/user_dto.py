import collections

UserDto = collections.namedtuple(
    'User', ['username', 'password', 'email', 'isAdmin', 'isEndUser', 'branch'])
