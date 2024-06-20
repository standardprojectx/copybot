import asyncio
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey

async def monitor_transactions(address: str, callback):
    async with AsyncClient("https://api.mainnet-beta.solana.com") as client:
        pubkey = Pubkey.from_string(address)
        confirmed_transactions = set()

        while True:
            response = await client.get_signatures_for_address(pubkey, limit=10)
            if response.value:  # Verifique se há valores na resposta
                for transaction in response.value:
                    if transaction.signature not in confirmed_transactions:
                        confirmed_transactions.add(transaction.signature)
                        await callback(transaction)
            await asyncio.sleep(10)
