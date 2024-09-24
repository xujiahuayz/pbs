import random
from blockchain_env.transaction import Transaction

BLOCK_CAP = 100

class Builder:
    def __init__(self, builder_id, is_attacker, balance):
        self.id = builder_id
        self.is_attacker = is_attacker
        self.balance = balance
        self.mempool = []

    def launch_attack(self, block_num, target_transaction):
        # this is for the attack builder, after identifying the target transaction, they will launch attack with 0 gas fee and 0 mev potential, they include this attack directly in the block that they are building
        mev_potential = 0
        gas_fee = 0
        creator_id = self.id
        created_at = block_num
        target_tx = target_transaction

        return Transaction(gas_fee, mev_potential, creator_id, created_at, target_tx)


    def select_transactions(self):
        # select transactions from the mempool
        # if is attacker, select transactions with highest mev_potential + gas fee
        # if not attacker, select transactions with highest gas fee
        # return the selected transactions
        if self.is_attacker == True:
            self.mempool.sort(key=lambda x: x['mev_potential'] + x['gas_fee'], reverse=True)
        else:
            self.mempool.sort(key=lambda x: x['gas_fee'], reverse=True)

        selected_transactions = []
        total_gas_fee = 0

        if self.is_attacker == False:
            for transaction in self.mempool:
                # include the transaction if it does not exceed the block limit of 100 trasnactions
                if len(selected_transactions) < BLOCK_CAP:
                    selected_transactions.append(transaction)
                    total_gas_fee += transaction['gas_fee']
                else:
                    break
        elif self.is_attacker == True:
            for transaction in self.mempool:
                # if the transaction has mev potential, the attacker can launch attack on it
                if transaction['mev_potential'] > 0:
                    # select the transaction as the attack target
                    target_transaction = transaction
                    attack_transaction = self.launch_attack(block_num, target_transaction)
                    
                    # find the index of the target transaction in the mempool
                    target_index = self.mempool.index(target_transaction)
                    
                    # insert the attack transaction next to the target transaction
                    if attack_transaction['attack_type'] == 'front':
                        selected_transactions.insert(target_index, attack_transaction)
                        selected_transactions.insert(target_index + 1, target_transaction)
                    elif attack_transaction['attack_type'] == 'back':
                        selected_transactions.insert(target_index, target_transaction)
                        selected_transactions.insert(target_index + 1, attack_transaction)
                    
                    # ensure the block limit is not exceeded
                    if len(selected_transactions) > BLOCK_CAP:
                        selected_transactions.pop()

        return selected_transactions
        
        # for the non-attacker builder, just select the trasnctions based on gas fee untill block limit is reached
        # for the attacker, if a trasnctions has mev potential: to get the profit, they need to attack it.

    def bid(self, selected_transaction):

        sum_gas_fee = 0
        for transaction in selected_transaction:
            sum_gas_fee += 

        # calculate the total block value, start with 50% of the block value as the bid
        # use reactive strategy
        bid = 0.5 * transaction['block_value']

        # react 5 round per block
        # the reaction is based on the history this block bid value which is put forward by all builders
        # increase the bid to 0.9-1.1 of the highest bid, make sure the bid is not higher than the block value
        # if highest bid: decrease to second bid + (0.5* (highest - second bid))

        for i in range(5):
            # react to the highest bid
            highest_bid = max([transaction['bid'] for transaction in self.mempool])
            if highest_bid > bid:
                bid = min(highest_bid, bid + 0.1 * highest_bid)
            else:
                second_highest_bid = sorted([transaction['bid'] for transaction in self.mempool], reverse=True)[1]
                bid = max(0.5 * (highest_bid + second_highest_bid), bid)


