import asyncio
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solana.exceptions import SolanaRpcException
from utils import get_balance_changes

async def get_token_details(client, pubkey):
    try:
        token_details = await client.get_account_info(pubkey)
        return token_details.value
    except Exception as e:
        print(f"Error getting token details: {e}")
        return None

async def get_transaction_details(client, signature, user_address, raydium_address):
    user_pubkey = Pubkey.from_string(user_address)
    raydium_pubkey = Pubkey.from_string(raydium_address)

    for attempt in range(5):  # Retry logic with 5 attempts
        try:
            transaction_details = await client.get_transaction(
                signature, 
                max_supported_transaction_version=0
            )
            if transaction_details.value:
                meta = transaction_details.value.transaction.meta
                transaction = transaction_details.value.transaction.transaction

                # Check if both the user and Raydium addresses are involved in the transaction
                relevant_accounts = transaction.message.account_keys
                if user_pubkey not in relevant_accounts or raydium_pubkey not in relevant_accounts:
                    return

                if meta and transaction:
                    # Assuming transaction_details is already fetched and is a GetTransactionResp object
                    user_balance_changes = get_balance_changes(transaction_details, user_pubkey)

                    # Print results
                    # print("User Balance Changes:")
                    # for token, change in user_balance_changes.items():
                    #     print(f"Token: {token}, Balance Change: {change}")
                    token = [token for token in user_balance_changes.keys() if token != "So11111111111111111111111111111111111111112"][0]
                    amount = [amount for token,amount in user_balance_changes.items() if token != "So11111111111111111111111111111111111111112"][0]
                    # cost = abs (amount/user_balance_changes ["So11111111111111111111111111111111111111112"])
                    action = "Bought" if amount > 0 else "Sold"
                    print (f"User {action} {abs (amount)} of {token}")
                            # - At the cost of {cost}/SOL")

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

async def monitor_transactions(address: str, raydium_address: str, callback):
    async with AsyncClient("https://api.mainnet-beta.solana.com") as client:
        pubkey = Pubkey.from_string(address)
        confirmed_transactions = set()

        while True:
            try:
                response = await client.get_signatures_for_address(pubkey, limit=10)
                if response.value:  # Verifique se há valores na resposta
                    for transaction in response.value:
                        if transaction.signature not in confirmed_transactions:
                            confirmed_transactions.add(transaction.signature)
                            await callback(transaction.signature, client, address, raydium_address)
                await asyncio.sleep(15)
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