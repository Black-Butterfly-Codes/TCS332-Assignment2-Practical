import hashlib
from typing import List, Tuple

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def hash_pair(left: str, right: str) -> str:
    combined = bytes.fromhex(left) + bytes.fromhex(right)
    return sha256(combined)

class MerkleTree:
    def __init__(self, transactions: List[str]):
        if not transactions:
            raise ValueError("Transaction list cannot be empty")
        self.leaves = [sha256(tx.encode("utf-8")) for tx in transactions]
        self.levels = []
        self.root = self._build_tree()

    def _build_tree(self) -> str:
        current_level = self.leaves[:]
        self.levels = [current_level]
        while len(current_level) > 1:
            if len(current_level) % 2 == 1:
                current_level.append(current_level[-1])
            next_level = []
            for i in range(0, len(current_level), 2):
                parent = hash_pair(current_level[i], current_level[i + 1])
                next_level.append(parent)
            current_level = next_level
            self.levels.append(current_level)
        return current_level[0]

    def get_root(self) -> str:
        return self.root

    def get_proof(self, tx_index: int) -> List[Tuple[str, str]]:
        if tx_index < 0 or tx_index >= len(self.leaves):
            raise IndexError("Transaction index out of range")
        proof = []
        index = tx_index
        for level in self.levels[:-1]:
            if len(level) % 2 == 1 and index == len(level) - 1:
                sibling = level[index]
                direction = "left"
            elif index % 2 == 0:
                sibling = level[index + 1]
                direction = "right"
            else:
                sibling = level[index - 1]
                direction = "left"
            proof.append((sibling, direction))
            index //= 2
        return proof

    @staticmethod
    def verify_proof(tx: str, proof: List[Tuple[str, str]], merkle_root: str) -> bool:
        current_hash = sha256(tx.encode("utf-8"))
        for sibling, direction in proof:
            if direction == "left":
                current_hash = hash_pair(sibling, current_hash)
            else:
                current_hash = hash_pair(current_hash, sibling)
        return current_hash == merkle_root