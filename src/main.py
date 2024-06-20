import asyncio
from watcher import monitor_transactions

async def print_transaction(transaction):
    print(f"New transaction: {transaction}")

if __name__ == "__main__":
    user_address = "YourSolanaAddressHere"
    asyncio.run(monitor_transactions(user_address, print_transaction))
