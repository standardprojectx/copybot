import asyncio
from solana.rpc.async_api import AsyncClient
from solana.publickey import PublicKey

async def monitor_transactions(address: str, callback):
    async with AsyncClient("https://api.mainnet-beta.solana.com") as client:
        pubkey = PublicKey(address)
        confirmed_transactions = set()

        while True:
            response = await client.get_confirmed_signature_for_address2(pubkey, limit=10)
            for transaction in response['result']:
                if transaction['signature'] not in confirmed_transactions:
                    confirmed_transactions.add(transaction['signature'])
                    await callback(transaction)
            await asyncio.sleep(10)
