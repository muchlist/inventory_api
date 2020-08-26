def is_admin(claims: dict) -> bool:
    return claims["isAdmin"]


def is_end_user(claims: dict) -> bool:
    return claims["isEndUser"]
