"""Tests for the Flask HTTP API (skipped when Flask is not installed)."""

from __future__ import annotations

import pytest

pytest.importorskip("flask")

from suncoin import Blockchain  # noqa: E402
from suncoin.api import create_app  # noqa: E402


@pytest.fixture
def client():
    app = create_app(Blockchain(difficulty=2))
    app.testing = True
    return app.test_client()


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_solar_and_balance_flow(client):
    resp = client.post("/api/data", json={"power": 120, "address": "alice"})
    assert resp.status_code == 201
    client.post("/mine", json={"miner": "m1"})
    bal = client.get("/balance/alice").get_json()
    assert bal["balance"] == pytest.approx(12.0)


def test_transaction_and_mine(client):
    client.post("/api/data", json={"power": 100, "address": "alice"})
    client.post("/mine", json={"miner": "m1"})
    resp = client.post("/transactions", json={"sender": "alice", "recipient": "bob", "amount": 3})
    assert resp.status_code == 201
    client.post("/mine", json={"miner": "m1"})
    assert client.get("/balance/bob").get_json()["balance"] == pytest.approx(3.0)


def test_invalid_transaction_returns_400(client):
    resp = client.post("/transactions", json={"sender": "alice"})
    assert resp.status_code == 400


def test_chain_validity_endpoint(client):
    client.post("/api/data", json={"power": 10, "address": "alice"})
    client.post("/mine", json={"miner": "m1"})
    assert client.get("/chain/valid").get_json()["valid"] is True


def test_stats_endpoint(client):
    client.post("/api/data", json={"power": 80, "address": "alice"})
    client.post("/mine", json={"miner": "m1"})
    stats = client.get("/stats").get_json()
    assert stats["total_solar_kwh"] == pytest.approx(80.0)
    assert stats["co2_avoided_grams"] > 0
