import asyncio
from watcher import monitor_transactions, get_transaction_details

async def print_transaction(signature, client, user_address, raydium_address):
    print(f"New transaction: {signature}")
    await asyncio.sleep(5)  # Add delay between transactions
    await get_transaction_details(client, signature, user_address, raydium_address)
    await asyncio.sleep(5)  # Add delay after fetching details
    print ("--------------------------------------------------")

if __name__ == "__main__":
    user_address = "BXjJ8aCCqHtYcMvbGa9yw62qkhYfBczLSMFkKH1NBvTG"
    raydium_address = "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1"
    asyncio.run(monitor_transactions(user_address, raydium_address, print_transaction))