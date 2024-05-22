from .input import TxOutpoint
from .utils import txid_to_internal, txid_to_display

__all__ = [
    "txid_to_internal",
    "txid_to_display",
]

from bitcoin.core import CTxIn, COutPoint, CTxOut, script, CMutableTransaction, CTxInWitness, CScriptWitness, CTxWitness


class TransactionGenerator:

    def __init__(self, outpoints: list[TxOutpoint], amount: int, script_pub_key: script.CScript, sender: bytes):
        self.inputs = outpoints
        self.amount = amount
        self.script_pub_key = script_pub_key
        self.sender = sender
        self.raw = self.get_raw()

    def get_raw(self) -> CMutableTransaction:
        txins = []
        spend_amount = self.amount
        change = 0
        for txin in self.inputs:
            t = CTxIn(prevout=COutPoint(hash=txin.txid, n=int.from_bytes(txin.n, "little")))
            txins.append(t)
            if txin.amount >= spend_amount:
                change = txin.amount - spend_amount
                spend_amount = 0
                break

        txout_transfer = CTxOut(self.amount, self.script_pub_key)
        if change > 0:
            fees = int(0.0001 * 100000000)
            change -= fees
            txout_change = CTxOut(change, script.CScript([script.OP_0, self.sender]))  # type: ignore
            return CMutableTransaction(txins, [txout_transfer, txout_change])

        return CMutableTransaction(txins, [txout_transfer])

    def get_sig_hash(self, redeem_script: bytes, txin_index: int, txin_amount: int):
        return script.SignatureHash(
            redeem_script,
            self.raw,
            txin_index,
            script.SIGHASH_ALL,
            txin_amount,
            sigversion=script.SIGVERSION_WITNESS_V0
        )

    def serialize(self, witnesses: list[tuple[bytes, bytes]]) -> bytes:
        witness_structure = [
            CTxInWitness(CScriptWitness([signature, public_key]))
            for signature, public_key in witnesses
        ]
        tx = self.raw
        tx.wit = CTxWitness(witness_structure)

        return tx.serialize()
