"""The Suncoin blockchain: genesis, mining, validation and CO2 accounting.

This replaces the original ERC-20 ``SolarCoin.sol`` contract with a
self-contained ledger. New coins enter circulation the same way they did in the
original project - as a reward for producing clean solar energy - but here they
are minted through coinbase transactions confirmed by proof-of-work mining
instead of an ``onlyOwner`` ``mint`` call.
"""

from __future__ import annotations

import time
from typing import Any

from suncoin import CO2_GRAMS_PER_KWH
from suncoin.block import Block
from suncoin.transaction import COINBASE, Transaction


class Blockchain:
    """An append-only chain of proof-of-work mined blocks."""

    def __init__(self, difficulty: int = 3, mining_reward: float = 50.0) -> None:
        if difficulty < 1:
            raise ValueError("difficulty must be at least 1")
        self.difficulty = difficulty
        self.mining_reward = mining_reward
        self.pending_transactions: list[Transaction] = []
        self.chain: list[Block] = [self._create_genesis_block()]

    # ------------------------------------------------------------------ #
    # Construction
    # ------------------------------------------------------------------ #
    def _create_genesis_block(self) -> Block:
        """Create the fixed first block that anchors the chain."""
        genesis = Block(
            index=0,
            timestamp=0.0,  # fixed so every fresh chain shares the same genesis
            transactions=[Transaction(COINBASE, "network", 0.0, memo="genesis")],
            previous_hash="0",
            nonce=0,
        )
        genesis.seal()
        return genesis

    @property
    def last_block(self) -> Block:
        """The most recently added block (the current chain tip)."""
        return self.chain[-1]

    # ------------------------------------------------------------------ #
    # Proof of work
    # ------------------------------------------------------------------ #
    @property
    def target_prefix(self) -> str:
        """The leading-zero prefix a valid hash must start with."""
        return "0" * self.difficulty

    def is_valid_proof(self, block: Block) -> bool:
        """True when the block's stored hash is correct and meets difficulty."""
        return block.hash == block.compute_hash() and block.hash.startswith(self.target_prefix)

    def proof_of_work(self, block: Block) -> str:
        """Increment the nonce until the block hash meets the difficulty target."""
        block.nonce = 0
        computed = block.compute_hash()
        while not computed.startswith(self.target_prefix):
            block.nonce += 1
            computed = block.compute_hash()
        block.hash = computed
        return computed

    # ------------------------------------------------------------------ #
    # Transactions and mining
    # ------------------------------------------------------------------ #
    def add_transaction(self, transaction: Transaction) -> int:
        """Queue a transaction; returns the index of the block it will land in."""
        self.pending_transactions.append(transaction)
        return self.last_block.index + 1

    def reward_solar_production(self, recipient: str, kwh: float, rate: float = 0.1) -> Transaction:
        """Mint a solar reward: ``kwh`` of clean energy -> ``kwh * rate`` Suncoin.

        The 0.1 default rate mirrors the ``power * 0.1`` conversion used by the
        original Express ``/api/data`` endpoint.
        """
        if kwh < 0:
            raise ValueError("kwh must not be negative")
        tx = Transaction(
            sender=COINBASE,
            recipient=recipient,
            amount=kwh * rate,
            solar_kwh=kwh,
            memo="solar production reward",
        )
        self.add_transaction(tx)
        return tx

    def mine_pending_transactions(self, miner_address: str) -> Block:
        """Bundle pending transactions plus a mining reward into a new block.

        Returns the freshly mined block. The pending pool is cleared and a new
        coinbase reward for the miner is queued for the next block, exactly as a
        real coinbase works.
        """
        rewarded = [*self.pending_transactions, Transaction.reward(miner_address, self.mining_reward)]
        block = Block(
            index=self.last_block.index + 1,
            timestamp=time.time(),
            transactions=rewarded,
            previous_hash=self.last_block.hash,
        )
        self.proof_of_work(block)
        self.chain.append(block)
        self.pending_transactions = []
        return block

    def add_block(self, block: Block) -> Block:
        """Append an already-mined block after validating its link and proof."""
        if block.previous_hash != self.last_block.hash:
            raise ValueError("block does not link to the current chain tip")
        if not self.is_valid_proof(block):
            raise ValueError("block does not satisfy proof-of-work difficulty")
        self.chain.append(block)
        return block

    # ------------------------------------------------------------------ #
    # Validation and accounting
    # ------------------------------------------------------------------ #
    def is_valid(self) -> bool:
        """Return True when the whole chain is internally consistent.

        Catches tampering: recomputes every hash, checks each ``previous_hash``
        link, and confirms every block (except genesis) meets difficulty.
        """
        for i, block in enumerate(self.chain):
            if block.hash != block.compute_hash():
                return False
            if i == 0:
                if block.previous_hash != "0":
                    return False
                continue
            if block.previous_hash != self.chain[i - 1].hash:
                return False
            if not block.hash.startswith(self.target_prefix):
                return False
        return True

    def balance_of(self, address: str) -> float:
        """Net Suncoin balance for an address across the whole chain."""
        balance = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx.recipient == address:
                    balance += tx.amount
                if tx.sender == address:
                    balance -= tx.amount
        return balance

    def total_solar_kwh(self) -> float:
        """Sum of all solar energy (kWh) recorded on the chain."""
        return sum(tx.solar_kwh for block in self.chain for tx in block.transactions)

    def co2_avoided_grams(self) -> float:
        """Estimated grams of CO2 avoided by the solar energy on the chain."""
        return self.total_solar_kwh() * CO2_GRAMS_PER_KWH

    # ------------------------------------------------------------------ #
    # Serialisation
    # ------------------------------------------------------------------ #
    def to_dict(self) -> dict[str, Any]:
        """Serialise the chain and its parameters (used by the API/CLI)."""
        return {
            "difficulty": self.difficulty,
            "mining_reward": self.mining_reward,
            "length": len(self.chain),
            "pending_transactions": [tx.to_dict() for tx in self.pending_transactions],
            "chain": [block.to_dict() for block in self.chain],
        }
