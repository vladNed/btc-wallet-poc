import hashlib
import pytest
from btc_wallet import crypto


def test_ripemd160_only_bytes():
    data = "hello world"
    with pytest.raises(TypeError):
        crypto.ripemd160(data)  # type: ignore


def test_ripemd160_returns_hash():
    data = b"hello world"
    result = crypto.ripemd160(data)
    assert not isinstance(result, bytes)
    assert result.digest() == b'\x98\xc6\x15xL\xcb_\xe5\x93o\xbc\x0c\xbe\x9d\xfd\xb4\x08\xd9/\x0f'


def test_hash160_only_publickey():
    # This is a dummy public key, it is not a valid public key
    public_key = b'not-a-pub-key'
    with pytest.raises(AttributeError):
        crypto.hash160(public_key)  # type: ignore


def test_checksum_only_bytes():
    version = "hello world"
    data = "hello world"
    with pytest.raises(TypeError):
        crypto.checksum(version, data)  # type: ignore


def test_checksum():
    version = b"\x00"
    data = b"hello world"
    result = crypto.checksum(version, data)
    assert result == hashlib.sha256(hashlib.sha256(version + data).digest()).digest()[:4]