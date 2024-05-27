import argparse
import json
import logging
import os
import random
import time
from hashlib import sha256
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
from flask import Flask, jsonify, request

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DIFFICULTIES = {
    "Easy": 2,
    "Medium": 3,
    "Hard": 4
}

# Blockchain and Mining Configuration
CHAIN = []
REWARD = 50  # Initial mining reward
HALVING_INTERVAL = 210000  # Number of blocks between reward halving
TARGET_TIME = 10 * 60  # Target time for mining a block (10 minutes)

# Flask Web Server for Monitoring
app = Flask(__name__)
mining_info = {
    "status": "idle",
    "current_block": None,
    "difficulty": "Medium",
    "hash_rate": 0,
    "mining_time": 0,
}

def SHA256(text):
    return sha256(text.encode("ascii")).hexdigest()

def to_string(data):
    """
    Converts block data dictionary to a JSON string for hashing.
    """
    return json.dumps(data, sort_keys=True)

def calculate_target(difficulty):
    """
    Calculates the target hash value based on difficulty.
    """
    return 2 ** (256 - difficulty)

def mine_nonce(args):
    block_data, nonce_start, nonce_end, target, queue = args
    for nonce in tqdm(range(nonce_start, nonce_end), desc="Mining", position=queue):
        block_data['nonce'] = nonce
        text = to_string(block_data)
        new_hash = SHA256(text)
        if int(new_hash, 16) < target:
            block_data['hash'] = new_hash
            return block_data
    return None

def mine(block_data, target_difficulty, num_workers=None):
    """
    Simulates mining a block with a specific difficulty.

    Args:
        block_data: A dictionary containing block data like block number, transactions, and previous hash.
        target_difficulty: The target difficulty level (number of leading zeros required in the hash).
        num_workers: Number of parallel processes to use for mining.

    Returns:
        A dictionary containing the mined block data (including the mined hash) or None if not found within limit.
    """
    if num_workers is None:
        num_workers = cpu_count()

    target = calculate_target(target_difficulty)
    max_nonce = 2 ** 32  # Reasonable limit for a nonce
    nonce_step = max_nonce // num_workers

    pool = Pool(num_workers)
    args = [(block_data.copy(), i * nonce_step, (i + 1) * nonce_step, target, i) for i in range(num_workers)]
    start_time = time.time()
    results = pool.map(mine_nonce, args)

    pool.close()
    pool.join()

    elapsed_time = time.time() - start_time
    hash_rate = max_nonce / elapsed_time
    mining_info["hash_rate"] = hash_rate
    logging.info(f"Hash rate: {hash_rate:.2f} hashes/second")

    for result in results:
        if result:
            mining_info["mining_time"] = elapsed_time
            return result

    return None

def parse_args():
    """
    Parses command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Bitcoin Mining Simulation")
    parser.add_argument('--difficulty', choices=DIFFICULTIES.keys(), default='Medium', help='Set mining difficulty')
    parser.add_argument('--block_number', type=int, default=5, help='Block number')
    parser.add_argument('--transactions', type=str, default="Dhaval->Bhavin->20,Mando->Cara->45", help='Transactions')
    parser.add_argument('--previous_hash', type=str, default="0000000xa036944e29568d0cff17edbe038f81208fecf9a66be9a2b8321c6ec7", help='Previous hash')
    parser.add_argument('--num_workers', type=int, default=None, help='Number of parallel workers for mining')
    parser.add_argument('--config_file', type=str, help='Path to configuration file for custom block data')
    parser.add_argument('--save_file', type=str, default="mined_block.json", help='File to save the mined block')
    return parser.parse_args()

def load_block_data(config_file):
    """
    Loads block data from a configuration file.
    """
    with open(config_file, 'r') as file:
        return json.load(file)

def save_block_data(block_data, save_file):
    """
    Saves mined block data to a file.
    """
    with open(save_file, 'w') as file:
        json.dump(block_data, file, indent=4)
    logging.info(f"Mined block saved to {save_file}")

def adjust_difficulty(start_time, target_time):
    """
    Adjusts the difficulty level based on the time taken to mine the last block.
    """
    elapsed_time = time.time() - start_time
    if elapsed_time < target_time:
        return 1  # Increase difficulty
    elif elapsed_time > target_time:
        return -1  # Decrease difficulty
    return 0  # No change

def add_block_to_chain(block):
    """
    Adds a mined block to the blockchain.
    """
    CHAIN.append(block)
    logging.info(f"Block {block['block_number']} added to the blockchain.")

def retarget_difficulty():
    """
    Retargets the difficulty based on the average mining time of the last set of blocks.
    """
    if len(CHAIN) > 1 and len(CHAIN) % 10 == 0:  # Example: adjust every 10 blocks
        avg_time = sum(block['mining_time'] for block in CHAIN[-10:]) / 10
        if avg_time < TARGET_TIME:
            return 1  # Increase difficulty
        elif avg_time > TARGET_TIME:
            return -1  # Decrease difficulty
    return 0  # No change

@app.route('/status', methods=['GET'])
def status():
    """
    Endpoint to get the current mining status.
    """
    return jsonify(mining_info)

@app.route('/mine', methods=['POST'])
def start_mining():
    """
    Endpoint to start mining a new block.
    """
    global REWARD  # Declare global REWARD at the beginning of the function

    data = request.json
    difficulty = data.get('difficulty', 'Medium')
    num_workers = data.get('num_workers', None)
    block_number = len(CHAIN) + 1
    previous_hash = CHAIN[-1]['hash'] if CHAIN else '0' * 64
    transactions = data.get('transactions', "Example transaction")

    block_data = {
        "block_number": block_number,
        "transactions": transactions,
        "previous_hash": previous_hash,
    }

    target_difficulty = DIFFICULTIES[difficulty]
    mining_info.update({
        "status": "mining",
        "current_block": block_number,
        "difficulty": difficulty
    })
    
    start_time = time.time()
    mined_block = mine(block_data, target_difficulty, num_workers)

    if mined_block:
        total_time = time.time() - start_time
        mined_block['mining_time'] = total_time
        mined_block['reward'] = REWARD
        logging.info(f"Mined block successfully! Hash: {mined_block['hash']}")
        logging.info(f"Mining took: {total_time:.2f} seconds")
        save_block_data(mined_block, f"block_{block_number}.json")
        add_block_to_chain(mined_block)

        # Halving the reward every HALVING_INTERVAL blocks
        if len(CHAIN) % HALVING_INTERVAL == 0:
            REWARD /= 2
            logging.info(f"Block reward halved! New reward: {REWARD} units")

        # Adjust difficulty for the next block
        difficulty_adjustment = retarget_difficulty()
        if difficulty_adjustment == 1:
            logging.info("Increasing difficulty for the next block")
        elif difficulty_adjustment == -1:
            logging.info("Decreasing difficulty for the next block")
        else:
            logging.info("Difficulty remains unchanged for the next block")

        mining_info["status"] = "idle"
        return jsonify(mined_block), 200
    else:
        mining_info["status"] = "idle"
        return jsonify({"error": "Failed to mine the block"}), 500

if __name__ == '__main__':
    args = parse_args()

    if args.config_file:
        block_data = load_block_data(args.config_file)
    else:
        block_data = {
            "block_number": args.block_number,
            "transactions": args.transactions,
            "previous_hash": args.previous_hash,
        }

    target_difficulty = DIFFICULTIES[args.difficulty]

    start_time = time.time()
    logging.info(f"Start mining for block {block_data['block_number']} with difficulty {args.difficulty}")

    mined_block = mine(block_data, target_difficulty, args.num_workers)

    if mined_block:
        total_time = time.time() - start_time
        logging.info(f"Mined block successfully! Hash: {mined_block['hash']}")
        logging.info(f"Mining took: {total_time:.2f} seconds")
        mined_block['mining_time'] = total_time
        mined_block['reward'] = REWARD
        save_block_data(mined_block, args.save_file)
        add_block_to_chain(mined_block)
    else:
        max_attempts = 2 ** (256 - target_difficulty)
        logging.warning(f"Couldn't find a valid hash within {max_attempts} attempts.")

    # Start the Flask web server for monitoring
    app.run(host='0.0.0.0', port=5000)
