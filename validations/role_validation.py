def isAdmin(claims: dict) -> bool:
    return claims["isAdmin"]

def isEndUser(claims: dict) -> bool:
    return claims["isEndUser"]