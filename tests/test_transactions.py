"""Tests for the transaction flow, balances and CO2 accounting."""

from __future__ import annotations

import pytest

from suncoin import CO2_GRAMS_PER_KWH, Blockchain, Transaction
from suncoin.transaction import COINBASE


def test_negative_amount_rejected():
    with pytest.raises(ValueError):
        Transaction("alice", "bob", -1)


def test_missing_recipient_rejected():
    with pytest.raises(ValueError):
        Transaction("alice", "", 1)


def test_reward_is_coinbase():
    tx = Transaction.reward("alice", 50)
    assert tx.is_reward
    assert tx.sender == COINBASE


def test_roundtrip_serialisation():
    tx = Transaction("alice", "bob", 5, solar_kwh=2.0, memo="hi", metadata={"k": 1})
    assert Transaction.from_dict(tx.to_dict()) == tx


def test_balance_tracks_transfers(chain: Blockchain):
    chain.reward_solar_production("alice", 100)  # +10 SLC
    chain.add_transaction(Transaction("alice", "bob", 4))
    chain.mine_pending_transactions("miner")
    assert chain.balance_of("alice") == pytest.approx(6.0)
    assert chain.balance_of("bob") == pytest.approx(4.0)
    assert chain.balance_of("miner") == pytest.approx(chain.mining_reward)


def test_solar_reward_conversion(chain: Blockchain):
    tx = chain.reward_solar_production("alice", 250, rate=0.1)
    assert tx.amount == pytest.approx(25.0)
    assert tx.solar_kwh == 250


def test_co2_accounting(chain: Blockchain):
    chain.reward_solar_production("alice", 100)
    chain.reward_solar_production("bob", 50)
    chain.mine_pending_transactions("miner")
    assert chain.total_solar_kwh() == pytest.approx(150.0)
    assert chain.co2_avoided_grams() == pytest.approx(150.0 * CO2_GRAMS_PER_KWH)


def test_pending_transaction_targets_next_block(chain: Blockchain):
    index = chain.add_transaction(Transaction("alice", "bob", 1))
    assert index == chain.last_block.index + 1
