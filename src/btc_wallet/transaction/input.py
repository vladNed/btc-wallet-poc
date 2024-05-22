from typing import Annotated

from pydantic import AfterValidator, BaseModel

from . import validators


class TxOutpoint(BaseModel):
    txid: Annotated[bytes, AfterValidator(validators.validate_txid)]
    """A 256-bit hash of the transaction. This is in internal byte order"""
    n: Annotated[bytes, AfterValidator(validators.is_uint32)]
    """The index of the output in the transaction"""
    amount: int
    """TODO: deprecate"""

    def serialize(self) -> bytes:
        return b"".join([self.txid, self.n])
