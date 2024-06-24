import asyncio
import requests
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solana.exceptions import SolanaRpcException
from utils import get_balance_changes, verify_accounts
from datetime import datetime, timezone
import time


sol_price = None
coins = []
balance = 0.0

async def update_sol_price():
    global sol_price
    while True:
        try:
            response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd')
            if response.status_code == 200:
                price_data = response.json()
                sol_price = price_data['solana']['usd']
                print(f"Updated SOL price: {sol_price} USD")
            else:
                print("Failed to get SOL price")
        except Exception as e:
            print(f"Error fetching SOL price: {e}")
        await asyncio.sleep(120) 

async def get_transaction_details(client, signature, user_address, raydium_address):
    global balance
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
                if not verify_accounts(transaction_details, user_pubkey, raydium_pubkey):
                    return

                if meta and transaction:
                    user_balance_changes = get_balance_changes(transaction_details, user_pubkey)

                    # Check if there are balance changes excluding the system account
                    tokens = [token for token in user_balance_changes.keys() if token != "So11111111111111111111111111111111111111112"]
                    if tokens:
                        token = tokens[0]
                        amounts = [amount for token, amount in user_balance_changes.items() if token != "So11111111111111111111111111111111111111112"]
                        if amounts:
                            amount = amounts[0]
                            action = "bought" if amount > 0 else "sold"
                            color = '\033[91m' if amount > 0 else '\033[92m'
                            try:
                                cost = user_balance_changes["So11111111111111111111111111111111111111112"]
                                if sol_price:
                                    cost_usd = cost * sol_price
                                    if action == "bought":
                                        coins.append({"id": token, "amount": abs(amount), "cost": cost_usd})
                                        balance += cost_usd
                                        print(f"{color}User {action} {abs(amount)} of {token} for {cost} SOL ({cost_usd:.2f} USD)\033[0m")
                                        print(f"Current balance: {balance:.2f} USD")
                                    else:
                                        total_sold = abs(amount)
                                        total_cost_usd = 0.0
                                        for coin in coins:
                                            if coin["id"] == token:
                                                if coin["amount"] > total_sold:
                                                    coin["amount"] -= total_sold
                                                    total_cost_usd += total_sold * (coin["cost"] / coin["amount"])
                                                    break
                                                else:
                                                    total_sold -= coin["amount"]
                                                    total_cost_usd += coin["cost"]
                                                    coins.remove(coin)
                                        profit = cost_usd - total_cost_usd
                                        balance += cost_usd
                                        print(f"{color}User {action} {abs(amount)} of {token} for {cost} SOL ({cost_usd:.2f} USD)\033[0m")
                                        print(f"\nToken: {token}\nAmount Sold: {abs(amount)}\nPurchase Cost: {total_cost_usd:.2f} USD\nSale Price: {cost_usd:.2f} USD\nProfit: {profit:.2f} USD")
                                        print(f"\nCurrent balance: {balance:.2f} USD\n")

                                else:
                                    print(f"{color}User {action} {abs(amount)} of {token} for {cost} SOL\033[0m")
                            except KeyError:
                                print(f"{color}User {action} {abs(amount)} of {token}\033[0m")
                    else:
                        print("No relevant balance changes found in the transaction.")

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
        start_time = time.time()

        while True:
            try:
                response = await client.get_signatures_for_address(pubkey, limit=10)
                if response.value:  # Check if there are values in the response
                    for transaction in response.value:
                        # Convert the transaction block time to a comparable format
                        if transaction.block_time and transaction.block_time > start_time:
                            if transaction.signature not in confirmed_transactions:
                                confirmed_transactions.add(transaction.signature)
                                await callback(transaction.signature, client, address, raydium_address,
                                               datetime.now(timezone.utc).strftime("%m-%d-%Y %H:%M:%S"))
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

async def print_transaction(signature, client, user_address, raydium_address, time):
    print(f"New transaction: {signature}")
    print(f"Transaction Found at: {time}")
    await asyncio.sleep(5)  # Add delay between transactions
    await get_transaction_details(client, signature, user_address, raydium_address)
    await asyncio.sleep(5)  # Add delay after fetching details
    print("--------------------------------------------------")
