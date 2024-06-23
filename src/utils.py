def verify_accounts (transaction_details, user_pubkey, raydium_pubkey):
    meta = transaction_details.value.transaction.meta
    pre_token_balances = meta.pre_token_balances if meta.pre_token_balances else []

    owners = []
    for balance in pre_token_balances:
        if balance.owner not in owners:
            owners.append (balance.owner)

    if user_pubkey in owners and raydium_pubkey in owners:
        return True
    else:
        return False


def get_balance_changes(transaction_details, user_pubkey):
    # Extracting relevant data
    meta = transaction_details.value.transaction.meta
    pre_token_balances = meta.pre_token_balances if meta.pre_token_balances else []
    post_token_balances = meta.post_token_balances if meta.post_token_balances else []

    # Initialize dictionaries to store balance changes for each address
    user_balance_changes = {}

    # Function to update the balance changes
    def update_balance_changes(pre_balance, post_balance):
        if not pre_balance or not post_balance:
            return None

        pre_amount = float(pre_balance.ui_token_amount.ui_amount) if pre_balance.ui_token_amount.ui_amount else 0.0
        post_amount = float(post_balance.ui_token_amount.ui_amount) if post_balance.ui_token_amount.ui_amount else 0.0
        change = post_amount - pre_amount

        if change != 0:
            return {
                "token_mint": str(pre_balance.mint),
                "balance_change": change
            }
        return None

    # Iterate through pre and post balance lists and calculate the changes
    for pre_balance, post_balance in zip(pre_token_balances, post_token_balances):
        pre_owner = pre_balance.owner
        post_owner = post_balance.owner

        if pre_owner and post_owner and pre_owner == post_owner:
            if pre_owner == user_pubkey:
                result = update_balance_changes(pre_balance, post_balance)
                if result:
                    user_balance_changes[result["token_mint"]] = result["balance_change"]

    return user_balance_changes