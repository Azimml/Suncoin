"""Tests for chain validation and tamper detection."""

from __future__ import annotations

import pytest

from suncoin import Blockchain, Transaction
from suncoin.block import Block


def build_chain() -> Blockchain:
    bc = Blockchain(difficulty=2)
    bc.reward_solar_production("alice", 100)
    bc.mine_pending_transactions("miner")
    bc.add_transaction(Transaction("alice", "bob", 4))
    bc.mine_pending_transactions("miner")
    return bc


def test_fresh_chain_is_valid():
    assert Blockchain(difficulty=2).is_valid()


def test_mined_chain_is_valid():
    assert build_chain().is_valid()


def test_tampered_amount_is_detected():
    bc = build_chain()
    bc.chain[1].transactions[0] = Transaction("alice", "eve", 9999)
    assert not bc.is_valid()


def test_tampered_hash_is_detected():
    bc = build_chain()
    bc.chain[1].hash = "0" * 64
    assert not bc.is_valid()


def test_broken_link_is_detected():
    bc = build_chain()
    bc.chain[2].previous_hash = "deadbeef"
    assert not bc.is_valid()


def test_reordered_blocks_are_detected():
    bc = build_chain()
    bc.chain[1], bc.chain[2] = bc.chain[2], bc.chain[1]
    assert not bc.is_valid()


def test_add_block_rejects_bad_link():
    bc = Blockchain(difficulty=2)
    orphan = Block(index=1, timestamp=1.0, transactions=[], previous_hash="wrong")
    bc.proof_of_work(orphan)
    with pytest.raises(ValueError):
        bc.add_block(orphan)


def test_add_block_rejects_insufficient_proof():
    bc = Blockchain(difficulty=3)
    block = Block(index=1, timestamp=1.0, transactions=[], previous_hash=bc.last_block.hash)
    block.seal()  # sealed but not mined -> almost certainly fails difficulty
    if block.hash.startswith("000"):
        pytest.skip("unmined hash happened to satisfy difficulty")
    with pytest.raises(ValueError):
        bc.add_block(block)
