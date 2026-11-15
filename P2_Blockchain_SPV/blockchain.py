import hashlib
import time
from typing import List, Dict, Any, Optional
from merkle_tree import MerkleTree, sha256

class Block:
    def __init__(self, index: int, transactions: List[str], previous_hash: str,
                 timestamp: Optional[float] = None, nonce: int = 0):
        self.index = index
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        if transactions:
            self.merkle_tree = MerkleTree(transactions)
            self.merkle_root = self.merkle_tree.get_root()
        else:
            self.merkle_tree = None
            self.merkle_root = sha256(b"")
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        header = f"{self.index}{self.timestamp}{self.previous_hash}{self.merkle_root}{self.nonce}"
        return sha256(header.encode("utf-8"))

    def __repr__(self) -> str:
        return f"Block(index={self.index}, hash={self.hash[:12]}..., merkle={self.merkle_root[:12]}..., txs={len(self.transactions)})"

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = Block(0, ["Genesis Transaction - Network Bootstrap"], "0"*64, 1700000000.0, 0)
        self.chain.append(genesis)

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, transactions: List[str], nonce: int = 0) -> Block:
        previous = self.get_latest_block()
        new_block = Block(previous.index + 1, transactions, previous.hash, nonce=nonce)
        self.chain.append(new_block)
        return new_block

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if current.previous_hash != previous.hash:
                print(f"[INVALID] Block {i}: previous_hash mismatch")
                return False
            if current.hash != current.calculate_hash():
                print(f"[INVALID] Block {i}: hash mismatch")
                return False
            if current.transactions:
                recomputed = MerkleTree(current.transactions)
                if current.merkle_root != recomputed.get_root():
                    print(f"[INVALID] Block {i}: Merkle root mismatch")
                    return False
        return True

    def get_spv_proof(self, block_index: int, tx_index: int):
        block = self.chain[block_index]
        proof = block.merkle_tree.get_proof(tx_index)
        return block.transactions[tx_index], proof, block.merkle_root

    def print_chain(self):
        print("\n========== BLOCKCHAIN ==========")
        for block in self.chain:
            print(block)
            print(f"  Prev : {block.previous_hash[:20]}...")
            print(f"  Root : {block.merkle_root[:20]}...")
            print(f"  Txs  : {block.transactions}")
            print("-" * 40)

if __name__ == "__main__":
    print("=" * 60)
    print("P2: Core Blockchain & Merkle SPV Verification Engine")
    print("=" * 60)

    bc = Blockchain()
    bc.add_block(["Alice pays Bob 10", "Charlie pays Dave 5"])
    bc.add_block(["Eve pays Frank 3", "Grace pays Heidi 7", "Ivan pays Judy 2"])
    bc.add_block(["Mallory pays Oscar 1"])
    bc.add_block(["Peggy pays Trent 9", "Victor pays Walter 4"])

    print("\n[1] Generated chain of 5 blocks:")
    bc.print_chain()

    print("\n[2] Chain validity check (should be True):")
    print("is_chain_valid() →", bc.is_chain_valid())

    print("\n[3] Tamper Detection Test")
    print("Mutating one character of a transaction in Block #2 ...")
    original = bc.chain[2].transactions[0]
    bc.chain[2].transactions[0] = original[:-1] + "X"
    print("is_chain_valid() after mutation →", bc.is_chain_valid())

    # restore
    bc.chain[2].transactions[0] = original
    bc.chain[2].merkle_tree = MerkleTree(bc.chain[2].transactions)
    bc.chain[2].merkle_root = bc.chain[2].merkle_tree.get_root()
    bc.chain[2].hash = bc.chain[2].calculate_hash()
    if len(bc.chain) > 3:
        bc.chain[3].previous_hash = bc.chain[2].hash
        bc.chain[3].hash = bc.chain[3].calculate_hash()
        if len(bc.chain) > 4:
            bc.chain[4].previous_hash = bc.chain[3].hash
            bc.chain[4].hash = bc.chain[4].calculate_hash()

    print("\n[4] SPV Inclusion Verification")
    tx, proof, root = bc.get_spv_proof(1, 0)
    print(f"Transaction : {tx}")
    print(f"Merkle Root : {root[:32]}...")
    print(f"Proof length: {len(proof)} hashes")
    print("SPV verify_proof →", MerkleTree.verify_proof(tx, proof, root))
    print("SPV verify_proof (fake) →", MerkleTree.verify_proof("Fake transaction", proof, root))

    print("\n[5] Final chain validity:")
    print("is_chain_valid() →", bc.is_chain_valid())
    print("\nAll P2 requirements demonstrated successfully.")