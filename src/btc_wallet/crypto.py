import hashlib

import secp256k1
from Crypto.Hash import RIPEMD160


def ripemd160(data: bytes) -> RIPEMD160.RIPEMD160Hash:
    """Returns the RIPEMD-160 hash of the data"""
    h = RIPEMD160.new()
    h.update(data)

    return h


def generate_key_pair() -> secp256k1.PrivateKey:
    """Generates a new private key and returns the key pair"""
    return secp256k1.PrivateKey()


def hash160(public_key: bytes) -> bytes:
    """Returns the public key hash as stated in the bitcoin wiki:
    https://en.bitcoin.it/wiki/Technical_background_of_version_1_Bitcoin_addresses

    This is fairly named hash160 because it is the result of the hash functions.
    """
    sha256_hash = hashlib.sha256(public_key).digest()
    ripemd_hash = ripemd160(sha256_hash).digest()

    return ripemd_hash


def checksum(version: bytes, data: bytes) -> bytes:
    """Returns the checksum of the version and data"""
    return hashlib.sha256(hashlib.sha256(version + data).digest()).digest()[:4]


def double_hash(data: bytes) -> bytes:
    """Returns a double sha256 hash of the data"""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()
