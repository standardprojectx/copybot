import asyncio
from watcher import monitor_transactions, get_transaction_details

async def print_transaction(transaction, client):
    print(f"New transaction: {transaction}")
    await asyncio.sleep(5)  # Add delay between transactions
    await get_transaction_details(client, transaction.signature)
    await asyncio.sleep(5)  # Add delay after fetching details

if __name__ == "__main__":
    user_address = "BXjJ8aCCqHtYcMvbGa9yw62qkhYfBczLSMFkKH1NBvTG"
    asyncio.run(monitor_transactions(user_address, print_transaction))
