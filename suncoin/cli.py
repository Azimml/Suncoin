"""Command-line interface for Suncoin.

Provides a small, scriptable way to drive the chain without the HTTP API:
mine blocks, record solar production, move coins and inspect the ledger. State
is kept in a JSON file so successive invocations build on the same chain.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from suncoin import CO2_GRAMS_PER_KWH, Blockchain
from suncoin.block import Block
from suncoin.transaction import Transaction

DEFAULT_STATE = Path("suncoin_chain.json")


def load_chain(path: Path, difficulty: int, reward: float) -> Blockchain:
    """Load a chain from ``path`` or create a fresh one if it does not exist."""
    if not path.exists():
        return Blockchain(difficulty=difficulty, mining_reward=reward)
    data = json.loads(path.read_text())
    bc = Blockchain(difficulty=data["difficulty"], mining_reward=data["mining_reward"])
    bc.chain = [Block.from_dict(b) for b in data["chain"]]
    bc.pending_transactions = [Transaction.from_dict(t) for t in data["pending_transactions"]]
    return bc


def save_chain(bc: Blockchain, path: Path) -> None:
    """Persist the chain to ``path`` as JSON."""
    path.write_text(json.dumps(bc.to_dict(), indent=2))


def _print(obj: object) -> None:
    print(json.dumps(obj, indent=2, default=str))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="suncoin", description="Suncoin blockchain CLI")
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE, help="chain state file")
    parser.add_argument("--difficulty", type=int, default=3, help="PoW difficulty for a new chain")
    parser.add_argument("--reward", type=float, default=50.0, help="mining reward for a new chain")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("show", help="print the whole chain")

    p_solar = sub.add_parser("solar", help="record solar production and reward an address")
    p_solar.add_argument("address")
    p_solar.add_argument("kwh", type=float)
    p_solar.add_argument("--rate", type=float, default=0.1)

    p_send = sub.add_parser("send", help="queue a transfer between two addresses")
    p_send.add_argument("sender")
    p_send.add_argument("recipient")
    p_send.add_argument("amount", type=float)

    p_mine = sub.add_parser("mine", help="mine the pending transactions")
    p_mine.add_argument("miner")

    p_bal = sub.add_parser("balance", help="show an address balance")
    p_bal.add_argument("address")

    sub.add_parser("validate", help="verify chain integrity")
    sub.add_parser("stats", help="show solar and CO2 statistics")

    args = parser.parse_args(argv)
    bc = load_chain(args.state, args.difficulty, args.reward)

    if args.command == "show":
        _print(bc.to_dict())
    elif args.command == "solar":
        tx = bc.reward_solar_production(args.address, args.kwh, rate=args.rate)
        save_chain(bc, args.state)
        _print({"queued_reward": tx.to_dict()})
    elif args.command == "send":
        bc.add_transaction(Transaction(args.sender, args.recipient, args.amount))
        save_chain(bc, args.state)
        print(f"queued: {args.sender} -> {args.recipient} : {args.amount} SLC")
    elif args.command == "mine":
        block = bc.mine_pending_transactions(args.miner)
        save_chain(bc, args.state)
        _print({"mined_block": block.index, "hash": block.hash, "nonce": block.nonce})
    elif args.command == "balance":
        print(f"{args.address}: {bc.balance_of(args.address)} SLC")
    elif args.command == "validate":
        ok = bc.is_valid()
        print("chain valid" if ok else "CHAIN INVALID")
        return 0 if ok else 1
    elif args.command == "stats":
        _print(
            {
                "blocks": len(bc.chain),
                "total_solar_kwh": bc.total_solar_kwh(),
                "co2_avoided_grams": bc.co2_avoided_grams(),
                "co2_grams_per_kwh": CO2_GRAMS_PER_KWH,
            }
        )
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
