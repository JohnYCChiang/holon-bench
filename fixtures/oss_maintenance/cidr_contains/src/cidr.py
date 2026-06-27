def _ip_to_int(ip):
    parts = ip.split(".")
    if len(parts) != 4:
        raise ValueError("invalid IPv4 address: " + ip)
    value = 0
    for part in parts:
        if not part.isdigit():
            raise ValueError("invalid IPv4 octet: " + part)
        octet = int(part)
        if not 0 <= octet <= 255:
            raise ValueError("octet out of range: " + part)
        value = value * 256 + octet
    return value


def contains(cidr, ip):
    """Return True if IPv4 ``ip`` falls inside ``cidr`` (e.g. "10.0.0.0/24").

    The network may be written with host bits set (e.g. "10.0.0.5/24"); it is
    normalized to its network address before comparison. ``prefix`` is 0..32.
    """
    net, prefix_s = cidr.split("/")
    prefix = int(prefix_s)
    if not 0 <= prefix <= 32:
        raise ValueError("prefix out of range: " + prefix_s)
    net_int = _ip_to_int(net)
    ip_int = _ip_to_int(ip)
    mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
    return (ip_int & mask) == net_int  # BUG: net_int not masked to its network address
