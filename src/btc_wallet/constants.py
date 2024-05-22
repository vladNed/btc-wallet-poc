import enum

# Base58check version prefix
P2PKH = b"\x00"
P2SH = b"\x05"
TESTNET_P2PKH = b"\x6f"
TESTNET_P2SH = b"\xc4"

# Base58check alphabet
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


class Hrp(enum.Enum):
    MAINET = "bc"
    TESTNET = "tb"
    REGTEST = "bcrt"


class Network(enum.Enum):
    MAINNET = 0
    TESTNET = 1
    REGTEST = 2

    def get_hrp(self) -> Hrp:
        match self:
            case Network.MAINNET:
                return Hrp.MAINET
            case Network.TESTNET:
                return Hrp.TESTNET
            case Network.REGTEST:
                return Hrp.REGTEST


# TRANSACTION DEFAULTS
DEFAULT_SEGWIT_SCRIPT = bytes([0x00])
DEFAULT_SEGWIT_SEQUENCE = bytes([0xFD, 0xFF, 0xFF, 0xFF])
