# btc-wallet-py

## Abstract
This project focuses on creating a modern and secure bitcoin wallet library that can be easily used in any python project.
I started learning about bitcoin internals a while back and I see a lot of libraries that do not put emphasis on modern
implementation practices. Also, all the libraries I've used (some might be outdated, some I never found) specially use
the wallet RPC to interact with a bitcoin node. While this is very convenient, I wanted a library that can be used as is,
in any python project without using the wallet RPC.

> BIG NOTE: This library is under heavy development and I will be adding more features as I learn more about bitcoin
internals.

## Introduction
This library is a modern implementation of a bitcoin wallet. It uses the bitcoin-core library to interact with the
bitcoin network.

## Installation

> NOTE: Under heavy development, not on PyPi yet.

### Clone repository

Activate a Python 3.12.2 virtual environment and clone the repository.
Using poetry is recommended.

Install the project
```shell
poetry install
```

## Usage

### Wallet address usage

```python
from btc_wallet import wallet

# Generate a brand new bitcoin wallet
wallet: wallet.BitcoinWallet = wallet.generate_bitcoin_wallet()

# Print legacy P2PKH address
print(wallet.p2pkh())

# Print SegWit P2WPKH address
print(wallet.p2wpkh())
```

### Transfer

```python
from btc_wallet import wallet

# Generate a brand new bitcoin wallet
wallet: wallet.BitcoinWallet = wallet.generate_bitcoin_wallet()

# Create a raw transaction
raw_transaction = wallet.transfer_raw(
    to_address="bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
    amount=1000,
    prev_txid="f5d8ee39asdasdas...",
    prev_index=0
)
```

## Features roadmap

- [] Wallet creation
    - [x] Create a new wallet
    - [] Load an existing wallet
- [] Wallet addresses
    - [x] Generate LEGACY addresses
    - [x] Generate SigWit BECH32 addresses
    - [] Generate Taproot BECH32 addresses
- [] Transactions
    - [x] Create a raw transaction
    - [x] Sign a raw transaction
    - [] Broadcast a raw transaction
    - [] Wallet balance
