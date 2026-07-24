"""Flask HTTP API for Suncoin.

Mirrors the original "Suncoin Web" / Express backend. The old server accepted
solar sensor readings at ``POST /api/data`` and minted coins from the reported
power; this API keeps that endpoint and adds first-class blockchain routes to
view the chain, queue transfers, mine blocks and read balances.

Run with::

    python -m suncoin.api            # or: flask --app suncoin.api run

Flask is an optional dependency; install it with ``pip install suncoin[api]``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from suncoin import Blockchain
from suncoin.transaction import Transaction

if TYPE_CHECKING:  # pragma: no cover
    from flask import Flask


def create_app(chain: Blockchain | None = None) -> Flask:
    """Application factory. Pass an existing ``chain`` or a fresh one is made."""
    from flask import Flask, jsonify, request

    app = Flask(__name__)
    app.config["CHAIN"] = chain or Blockchain()

    def bc() -> Blockchain:
        return app.config["CHAIN"]

    @app.get("/health")
    def health():
        return jsonify(status="ok", blocks=len(bc().chain))

    @app.get("/chain")
    def get_chain():
        return jsonify(bc().to_dict())

    @app.get("/chain/valid")
    def validate():
        return jsonify(valid=bc().is_valid())

    @app.post("/transactions")
    def add_transaction():
        body = request.get_json(force=True)
        try:
            tx = Transaction(
                sender=body["sender"],
                recipient=body["recipient"],
                amount=float(body["amount"]),
                memo=body.get("memo", ""),
            )
        except (KeyError, ValueError, TypeError) as exc:
            return jsonify(error=str(exc)), 400
        index = bc().add_transaction(tx)
        return jsonify(message="transaction queued", block_index=index), 201

    @app.post("/api/data")
    def solar_data():
        """Accept a solar reading and reward the producer (legacy endpoint)."""
        body = request.get_json(force=True)
        try:
            power = float(body["power"])  # kW reported by the panel/indicator
            address = body.get("address", "solar-producer")
        except (KeyError, ValueError, TypeError) as exc:
            return jsonify(error=str(exc)), 400
        tx = bc().reward_solar_production(address, power)
        return jsonify(message="solar reading recorded", reward=tx.to_dict()), 201

    @app.post("/mine")
    def mine():
        body = request.get_json(silent=True) or {}
        miner = body.get("miner", "network")
        block = bc().mine_pending_transactions(miner)
        return jsonify(message="block mined", block=block.to_dict()), 201

    @app.get("/balance/<address>")
    def balance(address: str):
        return jsonify(address=address, balance=bc().balance_of(address))

    @app.get("/stats")
    def stats():
        return jsonify(
            blocks=len(bc().chain),
            total_solar_kwh=bc().total_solar_kwh(),
            co2_avoided_grams=bc().co2_avoided_grams(),
        )

    return app


def main() -> None:  # pragma: no cover
    create_app().run(host="127.0.0.1", port=3000)


if __name__ == "__main__":  # pragma: no cover
    main()
