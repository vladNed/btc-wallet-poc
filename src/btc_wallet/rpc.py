import httpx
import asyncio


def call(method: str, params: list[str | int] = []):
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }


async def http_call(data: list | dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url="http://localhost:18443",
            json=data,
            headers={"content-type": "text/plain"},
            auth=("test1", "test")
        )

    if response.status_code != 200:
        raise Exception(f"Error: {response.text}")

    return response


async def get_block_count():
    data = call("getblockcount")
    resp = await http_call(data)

    return int(resp.json().get("result", 0))


async def get_block_batch(vals: list[int]):
    data = [call("getblockhash", [val]) for val in vals]
    resp = await http_call(data)

    blocks_hashes = [r.get("result", "") for r in resp.json()]
    block_data = [call("getblock", [hash]) for hash in blocks_hashes]
    block_resp = await http_call(block_data)

    return [r.get("result", "") for r in block_resp.json()]


async def get_tx_batch(ids: list[str]):
    data = [call("getrawtransaction", [txid, True]) for txid in ids]
    resp = await http_call(data)

    return [r.get("result", "") for r in resp.json() if r.get("result", None) is not None]


async def extract_utxos(tx: dict, address: str, unspent_utxos: dict, spent_utxos: dict):
    for i, vout in enumerate(tx.get("vout", [])):
        if address in vout.get("scriptPubKey", {}).get("address", []):
            unspent_utxos[tx.get("txid")] = {
                "txid": tx.get("txid"),
                "vout": i,
                "amount": vout.get("value"),
                "scriptPubKey": vout.get("scriptPubKey")
            }

    for vin in tx.get("vin", []):
        if vin.get("txid") in unspent_utxos:
            spent_utxos[vin.get("txid")] = True
            unspent_utxos.pop(vin.get("txid"), None)


async def sync_utxos(address: str) -> dict[str, dict]:
    block_count = await get_block_count()
    print(f"Syncing wallet -> {block_count}")
    batch_size = 200
    unspent_utxos = {}
    spent_utxos = {}
    for i, block_id in enumerate(range(0, block_count, batch_size)):
        print(f"Sync process batch {i + 1}/{block_count // batch_size}")
        block_ids = list(range(block_id, block_id + batch_size))
        block_hashes = await get_block_batch(block_ids)
        block_hashes_filtered = [block for block in block_hashes if block is not None]
        tx_hashes = [tx for block in block_hashes_filtered for tx in block.get("tx", [])]
        tasks = [
            extract_utxos(tx, address, unspent_utxos, spent_utxos)
            for tx in await get_tx_batch(tx_hashes)
        ]

        await asyncio.gather(*tasks)

    print(f"UTXOS -> {unspent_utxos}")
    return unspent_utxos
