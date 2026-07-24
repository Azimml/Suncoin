"""Mine a few Suncoin blocks from solar production and print the ledger.

Run with::

    python examples/mine_blocks.py
"""

from __future__ import annotations

from suncoin import Blockchain, Transaction


def main() -> None:
    chain = Blockchain(difficulty=3, mining_reward=50.0)

    # Three households report the solar energy their panels produced (in kWh).
    # Each reading is rewarded with Suncoin, then confirmed by mining a block.
    for household, kwh in [("alice", 120.0), ("bob", 80.0), ("carol", 200.0)]:
        chain.reward_solar_production(household, kwh)
        block = chain.mine_pending_transactions(miner_address="grid-operator")
        print(f"mined block #{block.index}  nonce={block.nonce}  hash={block.hash[:16]}...")

    # A regular transfer between two households, then mine it.
    chain.add_transaction(Transaction("carol", "alice", 5.0, memo="thanks for the panels"))
    chain.mine_pending_transactions("grid-operator")

    print("\n--- Balances (SLC) ---")
    for who in ["alice", "bob", "carol", "grid-operator"]:
        print(f"  {who:14s} {chain.balance_of(who):8.2f}")

    print("\n--- CO2 impact ---")
    print(f"  total solar recorded : {chain.total_solar_kwh():.1f} kWh")
    print(f"  CO2 avoided          : {chain.co2_avoided_grams() / 1000:.1f} kg")

    print(f"\nchain length : {len(chain.chain)} blocks")
    print(f"chain valid  : {chain.is_valid()}")


if __name__ == "__main__":
    main()
