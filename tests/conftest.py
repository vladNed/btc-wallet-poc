import pytest
import secp256k1


@pytest.fixture
def dummy_private_key():
    return secp256k1.PrivateKey()

