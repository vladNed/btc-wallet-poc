import binascii
import hashlib
import asyncio
from typing import Self
from dataclasses import dataclass

import ecdsa
import ecdsa.util
from bitcoin.core import script
from bitcoin.wallet import CBitcoinSecret

from btc_wallet import constants, crypto, encoding, rpc
from btc_wallet.transaction import TransactionGenerator
from btc_wallet.transaction.input import TxOutpoint
from btc_wallet.transaction.utils import txid_to_display, txid_to_internal

COIN = 100_000_000


@dataclass
class BitcoinWallet:
    key_pair: CBitcoinSecret
    utxos: dict[str, dict]

    @classmethod
    def load(cls, private_key_str: str) -> Self:
        sk = CBitcoinSecret.from_secret_bytes(binascii.unhexlify(private_key_str))

        wallet = cls(sk, {})
        wallet.sync(constants.Network.REGTEST)

        return wallet

    def sync(self, network: constants.Network = constants.Network.MAINNET):
        p2wpkh = self.p2wpkh(network=network)
        loop = asyncio.get_event_loop()
        self.utxos = loop.run_until_complete(rpc.sync_utxos(p2wpkh))

    def get_public_key(self) -> bytes:
        """Returns the public key of the private key generated with secp256k1

        NOTE: This is not the public key hash, but the public key itself.
        Usually, the public key hash is used to generate the bitcoin address
        as stated here: https://en.bitcoin.it/wiki/Technical_background_of_version_1_Bitcoin_addresses
        """
        pub_key = self.key_pair.pub
        if pub_key is None:
            raise TypeError("Error getting public key")

        return pub_key

    def _get_public_key_commitment(self) -> bytes:
        return crypto.hash160(self.get_public_key())

    def p2wpkh(self, network: constants.Network = constants.Network.MAINNET) -> str:
        """Returns the Pay-To-Witness-Public-Key-Hash (P2WPKH) address of the wallet"""
        public_key_hash = self._get_public_key_commitment()
        hrp = network.get_hrp().value
        btc_address = encoding.b32encode(hrp, 0, list(public_key_hash))

        if btc_address is None:
            raise ValueError("Error encoding P2WPKH address")

        return btc_address

    def p2wsh(self, script: bytes, network: constants.Network = constants.Network.MAINNET) -> str:
        """Returns the Pay-To-Witness-Script-Hash (P2WSH) address of the wallet"""
        wit_script_hash = hashlib.sha256(script).digest()
        hrp = network.get_hrp().value
        btc_address = encoding.b32encode(hrp, 0, list(wit_script_hash))

        if btc_address is None:
            raise ValueError("Error encoding P2WSH address")

        return btc_address

    def sign(self, data: bytes) -> bytes:
        """Signs the data with the private key of the wallet"""
        sig = self.key_pair.sign(data)
        if sig is None:
            raise ValueError("Error signing data")

        return sig

    def send_to(self, address: str, amount: int, network: constants.Network = constants.Network.MAINNET) -> str:
        self.sync(network)
        utxo_to_spend = []
        amount_to_spend = amount
        for utxo in self.utxos.values():
            utxo_amount = utxo["amount"] * COIN
            if utxo_amount >= amount_to_spend:
                utxo_to_spend.append(utxo)
                break

            utxo_to_spend.append(utxo)
            amount_to_spend -= utxo_amount

        txins = [
            TxOutpoint(
                txid=txid_to_internal(utxo["txid"]),
                n=utxo.get("vout", 0).to_bytes(4, "little"),
                amount=utxo["amount"] * COIN
                )
            for utxo in utxo_to_spend
        ]
        hrp = network.get_hrp().value
        _, decoded_address = encoding.b32decode(hrp, address)
        if decoded_address is None:
            raise ValueError("Error decoding address")
        script_pub_key = script.CScript([script.OP_0, bytes(decoded_address)])  # type: ignore

        tx = TransactionGenerator(
            sender=self._get_public_key_commitment(),
            outpoints=txins,
            amount=amount,
            script_pub_key=script_pub_key
        )

        signatures = []
        for i, txin in enumerate(txins):
            tx_to_display = txid_to_display(txin.txid)
            utxo = self.utxos.get(tx_to_display)
            if utxo is None:
                raise ValueError(f"Error getting UTXO: {tx_to_display=}")

            txin_script = binascii.unhexlify(utxo["scriptPubKey"]["hex"])
            redeem_script = script.CScript()
            if len(txin_script) == 22:
                redeem_script = script.CScript([
                    script.OP_DUP,
                    script.OP_HASH160,
                    self._get_public_key_commitment(),
                    script.OP_EQUALVERIFY,
                    script.OP_CHECKSIG
                ])  # type: ignore
            else:
                raise NotImplementedError("Only P2PKH scripts are supported")

            sig_hash = tx.get_sig_hash(redeem_script, i, txin.amount)
            signature = self.sign(sig_hash) + bytes([script.SIGHASH_ALL])
            signatures.append(signature)

        witnesses = [
            (signature, self.get_public_key())
            for signature in signatures
        ]

        return binascii.hexlify(tx.serialize(witnesses)).decode("ascii")


def generate_new_wallet() -> BitcoinWallet:
    """Generates a new key pair using cryuptographically secure random numbers
    from ECDSA secp256k1 curve.
    """
    sk = CBitcoinSecret.from_secret_bytes(ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1).to_string())

    return BitcoinWallet(sk, {})
