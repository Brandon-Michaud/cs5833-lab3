import requests
import json
import hashlib
import time
import random
import threading


# Global synchronization objects
num_miners = 64
new_blocks = events = [threading.Event() for _ in range(num_miners)]
latest_block = {}


def get_latest_block():
    # URL of GET endpoint
    url = 'https://miners.sooners.us/latest_block.php'

    # Send a GET request to URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
    else:
        raise Exception("Error getting latest block")
    return data['data']


def compute_hash(index, previous_hash, timestamp, data, nonce):
    # Concatenate information together
    base_string = str(index) + previous_hash + str(timestamp) + json.dumps(data) + str(nonce)

    # Encode the string to bytes
    encoded_string = base_string.encode()

    # Calculate SHA-256 hash of string
    hash_object = hashlib.sha256()
    hash_object.update(encoded_string)
    hash_digest = hash_object.hexdigest()
    return hash_digest


def mine_block(difficulty, latest_block, new_block):
    # URL of POST endpoint
    url = 'https://miners.sooners.us/submit_block.php'

    # Mine blocks
    while True:
        # Get latest block data
        index = latest_block['index'] + 1
        previous_hash = latest_block['hash']
        print(f'Started mining new block {index}')

        # Use my name for data field
        data = "Brandon Michaud"
        
        # Random starting value for nonce
        nonce = random.randint(-2147483648, 2147483647)

        while not new_block.is_set():
            # Generate timestamp
            timestamp = int(time.time())

            # Compute hash with nonce
            hash = compute_hash(index, previous_hash, timestamp, data, nonce)

            # Check if hash satisfies difficulty
            if hash[:difficulty] == '0' * difficulty:
                valid_block = {
                    "index": index, 
                    "previousHash": previous_hash,
                    "timestamp": str(timestamp),
                    "data": data,
                    "nonce": str(nonce)
                }
                print('Nonce found!')
                print(hash)
                print(valid_block)

                json_data = json.dumps(valid_block)
                headers = {
                    'Content-Type': 'application/json'
                }
                # Send a POST request
                response = requests.post(url, data=json_data, headers=headers)

                # Check the response
                if response.status_code == 200:
                    print('Successfully submitted block')
                else:
                    print('Block submission failed')

            # Update nonce
            nonce += 1
        new_block.clear()


def check_new_blocks(interval):
    global latest_block
    while True:
        block_data = get_latest_block()
        if block_data != latest_block:
            with threading.Lock():
                latest_block.update(block_data)
            for new_block in new_blocks:
                new_block.set()
            print(f"New block detected with index {block_data['index']}.")
        time.sleep(interval)


def setup_threads(check_interval, difficulty):
    checker_thread = threading.Thread(target=check_new_blocks, args=(check_interval,))
    checker_thread.start()
    print('Started checker thread')

    time.sleep(1)
    
    mining_threads = []
    for i in range(num_miners):
        thread = threading.Thread(target=mine_block, args=(difficulty, latest_block, new_blocks[i]))
        mining_threads.append(thread)
        thread.start()
        print(f'Started miner thread {i}')

    checker_thread.join()
    print('Checker thread terminated')
    for i, thread in enumerate(mining_threads):
        thread.join()
        print(f'Miner thread {i} terminated')


if __name__ == '__main__':
    print('test')
    setup_threads(15, 7)
