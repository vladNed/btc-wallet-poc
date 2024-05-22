def is_empty(value: bytes) -> bytes:
    if len(value) == 0:
        raise ValueError("Value cannot be empty")

    return value


def is_uint8(value: bytes) -> bytes:
    if len(value) != 1:
        raise ValueError("Value is not Uint8")

    return value


def is_uin16(value: bytes) -> bytes:
    if len(value) != 2:
        raise ValueError("Value is not Uint16")

    return value


def is_uint32(value: bytes) -> bytes:
    if len(value) != 4:
        raise ValueError("Value is not Uint32")

    return value


def is_uint64(value: bytes) -> bytes:
    if len(value) != 8:
        raise ValueError("Value is not Uint64")

    return value


def is_var_int(value: bytes) -> bytes:
    if len(value) == 1:
        return value

    match value[:1]:
        case b"\xfd":
            if len(value) != 3:
                raise ValueError("Value is not VarInt")
        case b"\xfe":
            if len(value) != 5:
                raise ValueError("Value is not VarInt")
        case b"\xff":
            if len(value) != 9:
                raise ValueError("Value is not VarInt")
        case _:
            raise ValueError("Value is not VarInt")

    return value


def is_list_empty(value: list) -> list:
    if len(value) == 0:
        raise ValueError("TX must have at least one input")

    return value


def validate_txid(txid: bytes) -> bytes:
    """Validates the transaction id internal byte order to be a 32-byte len"""
    if len(txid) != 32:
        raise ValueError("Invalid transaction id")

    return txid


def validate_pub_key_script(pubkey_script: bytes) -> bytes:
    """Validates the pubkey script to be a valid script"""
    ver, push_code, pubkey = pubkey_script[:1], pubkey_script[1:2], pubkey_script[2:]
    if ver != b"\x00":
        raise ValueError("Invalid pubkey script version")

    if push_code != len(pubkey).to_bytes():
        raise ValueError("Invalid pubkey script push code")

    if len(pubkey) != 20:
        raise ValueError("Invalid pubkey script length")

    return pubkey_script
