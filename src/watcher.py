import asyncio
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solana.exceptions import SolanaRpcException

async def get_transaction_details(client, signature):
    for attempt in range(5):  # Retry logic with 5 attempts
        try:
            transaction_details = await client.get_transaction(
                signature, 
                max_supported_transaction_version=0
            )
            if transaction_details.value:
                meta = transaction_details.value.transaction.meta
                if meta:
                    pre_balances = meta.pre_balances
                    post_balances = meta.post_balances
                    for balance_change in zip(pre_balances, post_balances):
                        print(f"Pre-balance: {balance_change[0]}, Post-balance: {balance_change[1]}")
                    print(f"Transaction fee: {meta.fee}")
            return
        except SolanaRpcException as e:
            if "429" in str(e):  # Check for "429 Too Many Requests" in the exception message
                wait_time = (2 ** attempt) + (0.5 * attempt)
                print(f"Rate limit hit. Waiting {wait_time} seconds before retrying...")
                await asyncio.sleep(wait_time)
            else:
                raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            await asyncio.sleep(1)  # Short delay before retrying
        await asyncio.sleep(2)  # Add a fixed delay between retries

async def monitor_transactions(address: str, callback):
    async with AsyncClient("https://api.mainnet-beta.solana.com") as client:
        pubkey = Pubkey.from_string(address)
        confirmed_transactions = set()

        while True:
            try:
                response = await client.get_signatures_for_address(pubkey, limit=10)
                if response.value:
                    for transaction in response.value:
                        if transaction.signature not in confirmed_transactions:
                            confirmed_transactions.add(transaction.signature)
                            await callback(transaction, client)
                await asyncio.sleep(10)
            except SolanaRpcException as e:
                if "429" in str(e):
                    print("Rate limit hit during transaction monitoring. Waiting before retrying...")
                    await asyncio.sleep(30)  # Wait longer before retrying
                else:
                    raise
            except Exception as e:
                print(f"Unexpected error during transaction monitoring: {e}")
                await asyncio.sleep(5)  # Short delay before retrying
            await asyncio.sleep(2)  # Add a fixed delay between iterations
