from btc_wallet import constants, crypto


def b58encode_check(version: bytes, data: bytes, no_leading_zeros: int = 0) -> str:
    """Encodes the data in base58 format and returns the encoded string"""
    data_to_encode = version + data + crypto.checksum(version, data)
    x: int = int.from_bytes(data_to_encode, byteorder="big")

    output_str: list[str] = []

    while x > 0:
        x, remainder = divmod(x, 58)
        output_str.append(constants.BASE58_ALPHABET[remainder])

    for _ in range(no_leading_zeros):
        output_str.append(constants.BASE58_ALPHABET[0])

    return "".join(output_str[::-1])
