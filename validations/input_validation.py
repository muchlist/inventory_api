def is_ip_address_valid(ip_address: str) -> bool:
    dot = "."
    ip_split = ip_address.split(dot)
    if len(ip_split) != 4:
        return False

    if _not_more_than_254(ip_split[0]):
        if _not_more_than_254(ip_split[1]):
            if _not_more_than_254(ip_split[2]):
                if _not_more_than_254(ip_split[3]):
                    return True
    return False


def _not_more_than_254(ip_slice: str):
    try:
        ip_slice_int = int(ip_slice)
    except ValueError:
        ip_slice_int = -1

    if (ip_slice_int > 254) or (ip_slice_int < 0):
        return False
    return True
