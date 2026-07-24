"""Block model with deterministic SHA-256 hashing.

Each block links to the previous block through ``previous_hash``, forming the
tamper-evident chain. The hash covers every field that matters (index,
timestamp, transactions, previous hash and nonce), so changing any of them
changes the hash and breaks the link to the next block.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from suncoin.transaction import Transaction


@dataclass
class Block:
    """A single block in the Suncoin chain."""

    index: int
    timestamp: float
    transactions: list[Transaction]
    previous_hash: str
    nonce: int = 0
    hash: str = field(default="", compare=False)

    def payload(self) -> dict[str, Any]:
        """The canonical, hashable contents of the block (excludes ``hash``)."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
        }

    def compute_hash(self) -> str:
        """Return the SHA-256 hash of this block's canonical payload.

        ``json.dumps`` with ``sort_keys=True`` guarantees a stable byte
        representation so the same block always hashes to the same value.
        """
        encoded = json.dumps(self.payload(), sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()

    def seal(self) -> str:
        """Compute and store the block's hash, returning it."""
        self.hash = self.compute_hash()
        return self.hash

    def to_dict(self) -> dict[str, Any]:
        """Full serialisation including the stored hash."""
        data = self.payload()
        data["hash"] = self.hash
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Block:
        """Rebuild a block from its serialised form."""
        block = cls(
            index=int(data["index"]),
            timestamp=float(data["timestamp"]),
            transactions=[Transaction.from_dict(tx) for tx in data["transactions"]],
            previous_hash=data["previous_hash"],
            nonce=int(data.get("nonce", 0)),
        )
        block.hash = data.get("hash", "") or block.compute_hash()
        return block
