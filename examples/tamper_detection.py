"""Show how Suncoin detects tampering with a confirmed block.

Run with::

    python examples/tamper_detection.py
"""

from __future__ import annotations

from suncoin import Blockchain, Transaction


def main() -> None:
    chain = Blockchain(difficulty=2)
    chain.reward_solar_production("alice", 100.0)
    chain.mine_pending_transactions("grid-operator")
    chain.add_transaction(Transaction("alice", "bob", 4.0))
    chain.mine_pending_transactions("grid-operator")

    print(f"chain valid before tampering : {chain.is_valid()}")

    # An attacker rewrites a confirmed transaction to steal coins.
    chain.chain[1].transactions[0] = Transaction("alice", "attacker", 9999.0)

    print(f"chain valid after tampering  : {chain.is_valid()}")
    print("The stored block hash no longer matches its recomputed hash, so")
    print("is_valid() rejects the whole chain - the tampering is caught.")


if __name__ == "__main__":
    main()
