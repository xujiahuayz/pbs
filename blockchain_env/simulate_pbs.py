import random
import os
import csv
import time
import multiprocessing as mp
from blockchain_env.user import User
from blockchain_env.builder import Builder

# Constants
BLOCKNUM = 1000
BLOCK_CAP = 100
USERNUM = 50
BUILDERNUM = 20
VISIBLE_PERCENT = 80

# Seed for reproducibility
random.seed(16)

# Determine the number of CPU cores and set the number of processes
num_cores = os.cpu_count()
num_processes = max(num_cores - 1, 1)  # Use all cores except one, but at least one

def transaction_number():
    random_number = random.randint(0, 100)
    if random_number < 50:
        return 1
    elif random_number < 80:
        return 0
    elif random_number < 95:
        return 2
    else:
        return random.randint(3, 5)

def process_block(block_num, users, builders):
    all_block_transactions = []
    for user in users:
        num_transactions = transaction_number()
        for _ in range(num_transactions):
            tx = user.create_transactions(block_num)
            if tx:
                all_block_transactions.append(tx)
                user.broadcast_transactions(tx)
    
    builder_results = []
    for builder in builders:
        selected_transactions = builder.select_transactions(block_num)
        bid_value = builder.bid(selected_transactions)
        builder_results.append((builder.id, selected_transactions, bid_value))
    
    highest_bid = max(builder_results, key=lambda x: x[2])
    highest_bid_builder = next(b for b in builders if b.id == highest_bid[0])
    
    for position, tx in enumerate(highest_bid[1]):
        tx.position = position
        tx.included_at = block_num
    
    all_block_transactions.extend(highest_bid[1])
    total_gas_fee = sum(tx.gas_fee for tx in highest_bid[1])
    total_mev = sum(tx.mev_potential for tx in highest_bid[1])

    block_content = {
        "block_num": block_num,
        "builder_id": highest_bid_builder.id,
        "transactions": highest_bid[1]
    }

    for builder in builders:
        builder.clear_mempool(block_num)

    return block_content, all_block_transactions

def simulate_pbs(num_attacker_builders, num_attacker_users):
    builders = [Builder(f"builder_{i}", i < num_attacker_builders) for i in range(BUILDERNUM)]
    users = [User(f"user_{i}", i < num_attacker_users, builders) for i in range(USERNUM)]

    with mp.Pool(processes=num_processes) as pool:
        results = pool.starmap(process_block, [(block_num, users, builders) for block_num in range(BLOCKNUM)])
    
    blocks, all_transactions = zip(*results)
    all_transactions = [tx for block_txs in all_transactions for tx in block_txs]

    # Save data to CSV
    filename = f"data/same_seed/visible80/pbs_transactions_builders{num_attacker_builders}_users{num_attacker_users}.csv"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', newline='') as f:
        if all_transactions:
            fieldnames = all_transactions[0].to_dict().keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for tx in all_transactions:
                writer.writerow(tx.to_dict())

    return blocks

if __name__ == "__main__":
    start_time = time.time()

    for num_attacker_builders in range(BUILDERNUM + 1):
        for num_attacker_users in range(USERNUM + 1):
            simulate_pbs(num_attacker_builders, num_attacker_users)

    end_time = time.time()
    print(f"Simulation completed in {end_time - start_time:.2f} seconds")
