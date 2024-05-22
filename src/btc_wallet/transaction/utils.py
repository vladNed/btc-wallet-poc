import binascii
import re
import struct


def _unhex(txid: str) -> bytes | None:
    """Validates the transaction id to be a 64-character hex string."""
    if len(txid) != 64 or not re.match("^[0-9a-fA-F]*$", txid):
        return None

    try:
        return binascii.unhexlify(txid)
    except binascii.Error:
        return None


def txid_to_internal(txid: str) -> bytes:
    """Converts a transaction id to internal byte order"""
    txid_bytes = _unhex(txid)
    if txid_bytes is None:
        raise ValueError("Invalid transaction id")

    return txid_bytes[::-1]


def txid_to_display(txid: bytes) -> str:
    """Converts a transaction id to display byte order"""
    return binascii.hexlify(txid[::-1]).decode("ascii")


def to_varInt(data: int) -> bytes:
    """Converts an integer to a variable integer format also called compact size integers."""
    if 0 <= data <= 0xFC:
        return struct.pack("<B", data)
    if 0xFD <= data <= 0xFFFF:
        return b"\xFD" + struct.pack("<H", data)
    if 0x10000 <= data <= 0xFFFFFFFF:
        return b"\xFE" + struct.pack("<I", data)
    if 0x100000000 <= data <= 0xFFFFFFFFFFFFFFFF:
        return b"\xFF" + struct.pack("<Q", data)

    raise ValueError("Invalid data")
