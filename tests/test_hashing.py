"""Tests for deterministic SHA-256 block hashing."""

from __future__ import annotations

import hashlib

from suncoin import Block, Transaction


def make_block() -> Block:
    return Block(
        index=1,
        timestamp=1700000000.0,
        transactions=[Transaction("alice", "bob", 10.0)],
        previous_hash="abc",
        nonce=7,
    )


def test_hash_is_deterministic():
    a, b = make_block(), make_block()
    assert a.compute_hash() == b.compute_hash()


def test_hash_is_sha256_hex():
    digest = make_block().compute_hash()
    assert len(digest) == 64
    assert all(ch in "0123456789abcdef" for ch in digest)


def test_hash_matches_manual_sha256():
    import json

    block = make_block()
    encoded = json.dumps(block.payload(), sort_keys=True, separators=(",", ":")).encode()
    assert block.compute_hash() == hashlib.sha256(encoded).hexdigest()


def test_nonce_change_changes_hash():
    block = make_block()
    before = block.compute_hash()
    block.nonce += 1
    assert block.compute_hash() != before


def test_transaction_change_changes_hash():
    block = make_block()
    before = block.compute_hash()
    block.transactions[0] = Transaction("alice", "bob", 11.0)
    assert block.compute_hash() != before


def test_seal_stores_hash():
    block = make_block()
    assert block.hash == ""
    returned = block.seal()
    assert block.hash == returned == block.compute_hash()
