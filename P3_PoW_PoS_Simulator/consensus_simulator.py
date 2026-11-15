import hashlib
import time
import random
from collections import Counter
from typing import List, Tuple

def sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def mine_block(header: str, difficulty: int) -> Tuple[int, str, float]:
    target_prefix = "0" * difficulty
    nonce = 0
    start = time.time()
    while True:
        candidate = f"{header}{nonce}"
        block_hash = sha256(candidate)
        if block_hash.startswith(target_prefix):
            return nonce, block_hash, time.time() - start
        nonce += 1

def simulate_pow(num_blocks=20, target_interval=1.5, initial_difficulty=3):
    print("\n" + "="*60)
    print("PROOF-OF-WORK SIMULATION")
    print("="*60)
    difficulty = initial_difficulty
    results = []
    total_nonces = 0

    for i in range(1, num_blocks + 1):
        header = f"Block-{i}-PrevHash-{random.getrandbits(64):016x}"
        nonce, block_hash, elapsed = mine_block(header, difficulty)
        results.append({"block": i, "difficulty": difficulty, "nonce": nonce, "elapsed": elapsed})
        total_nonces += nonce
        print(f"Block {i:2d} | Diff={difficulty} | Nonce={nonce:8d} | Time={elapsed:6.3f}s | Hash={block_hash[:20]}...")
        if i % 5 == 0:
            avg_time = sum(r["elapsed"] for r in results[-5:]) / 5
            old = difficulty
            if avg_time < target_interval * 0.8:
                difficulty += 1
            elif avg_time > target_interval * 1.2:
                difficulty = max(1, difficulty - 1)
            print(f"  → Difficulty adjust: avg_time={avg_time:.3f}s → {old} → {difficulty}")

    print(f"\nTotal nonces checked : {total_nonces}")
    return results

class PoSNode:
    def __init__(self, name: str, stake: int):
        self.name = name
        self.stake = stake
        self.blocks_produced = 0

def select_validator(nodes: List[PoSNode], seed: int) -> PoSNode:
    total = sum(n.stake for n in nodes)
    rng = random.Random(seed)
    r = rng.uniform(0, total)
    cumulative = 0
    for node in nodes:
        cumulative += node.stake
        if r <= cumulative:
            return node
    return nodes[-1]

def simulate_pos(num_rounds=100):
    print("\n" + "="*60)
    print("PROOF-OF-STAKE SIMULATION")
    print("="*60)
    nodes = [PoSNode("Node-1", 50), PoSNode("Node-2", 20), PoSNode("Node-3", 15),
             PoSNode("Node-4", 10), PoSNode("Node-5", 5)]
    total = sum(n.stake for n in nodes)
    print("Validators and stakes:")
    for n in nodes:
        print(f"  {n.name}: {n.stake} tokens ({n.stake/total*100:.1f}%)")
    selections = []
    for r in range(1, num_rounds+1):
        winner = select_validator(nodes, seed=r*7919)
        winner.blocks_produced += 1
        selections.append(winner.name)
    counter = Counter(selections)
    print(f"\nValidator selection over {num_rounds} rounds:")
    for name, count in counter.most_common():
        print(f"  {name}: {count:3d} blocks ({count/num_rounds*100:5.1f}%)")
    print("\nEnergy comparison: PoW = many SHA256 iterations, PoS = almost zero energy")
    return counter

if __name__ == "__main__":
    print("TCS 332 – Assignment 2 – Practical P3")
    simulate_pow()
    simulate_pos()
    print("\nP3 completed successfully.")