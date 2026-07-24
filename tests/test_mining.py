"""Tests for proof-of-work mining."""

from __future__ import annotations

import pytest

from suncoin import Blockchain


def test_mined_block_meets_difficulty(chain: Blockchain):
    block = chain.mine_pending_transactions("miner")
    assert block.hash.startswith("0" * chain.difficulty)


def test_higher_difficulty_requires_matching_prefix():
    bc = Blockchain(difficulty=3)
    block = bc.mine_pending_transactions("miner")
    assert block.hash.startswith("000")


def test_mining_appends_exactly_one_block(chain: Blockchain):
    before = len(chain.chain)
    chain.mine_pending_transactions("miner")
    assert len(chain.chain) == before + 1


def test_mining_awards_reward(chain: Blockchain):
    chain.mine_pending_transactions("miner")
    assert chain.balance_of("miner") == chain.mining_reward


def test_mining_clears_pending_pool(chain: Blockchain):
    chain.reward_solar_production("alice", 10)
    assert chain.pending_transactions
    chain.mine_pending_transactions("miner")
    assert chain.pending_transactions == []


def test_proof_of_work_finds_valid_nonce(chain: Blockchain):
    block = chain.mine_pending_transactions("miner")
    assert chain.is_valid_proof(block)
    # nonce should be reproducible: recomputing the hash still meets target
    assert block.compute_hash().startswith(chain.target_prefix)


def test_difficulty_must_be_positive():
    with pytest.raises(ValueError):
        Blockchain(difficulty=0)
