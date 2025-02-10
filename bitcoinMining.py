import hashlib
import time
import random

# Set mining difficulty (higher = harder)
DIFFICULTY = 5  # Requires hash to start with 5 leading zeros

def mine_block(block_number, previous_hash, transactions):
    nonce = 0
    start_time = time.time()

    while True:
        # Create a block string with nonce
        block_data = f"{block_number}{previous_hash}{transactions}{nonce}".encode()
        block_hash = hashlib.sha256(block_data).hexdigest()

        # Check if the hash meets the difficulty requirement
        if block_hash.startswith("0" * DIFFICULTY):
            end_time = time.time()
            print(f"\n✅ Block Mined Successfully!")
            print(f"⛏️ Block Number: {block_number}")
            print(f"🔗 Previous Hash: {previous_hash}")
            print(f"💰 Transactions: {transactions}")
            print(f"🔄 Nonce: {nonce}")
            print(f"🔑 Valid Hash: {block_hash}")
            print(f"⏳ Time Taken: {round(end_time - start_time, 2)} seconds")
            return block_hash  # Return the new block hash

        nonce += 1  # Increase nonce until a valid hash is found

# Simulating a Blockchain Network
previous_hash = "00000000000000000000000000000000"
block_number = 1

# Simulating Transactions
transactions = f"UserA -> UserB : {random.randint(1, 5)} BTC"

# Start mining the block
print(f"\n🚀 Starting mining for Block {block_number}...")
new_hash = mine_block(block_number, previous_hash, transactions)