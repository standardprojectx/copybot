import asyncio
import threading
from watcher import monitor_transactions, print_transaction, update_sol_price

if __name__ == "__main__":
    user_address = "BXjJ8aCCqHtYcMvbGa9yw62qkhYfBczLSMFkKH1NBvTG"
    raydium_address = "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1"
    print("\nStarting to monitor!")
    print("--------------------------------------------------")
    
    # Inicia a thread para atualizar o preço do SOL
    price_thread = threading.Thread(target=asyncio.run, args=(update_sol_price(),))
    price_thread.daemon = True
    price_thread.start()
    
    asyncio.run(monitor_transactions(user_address, raydium_address, print_transaction))
