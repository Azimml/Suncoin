"""Tests for the command-line interface and JSON persistence."""

from __future__ import annotations

from pathlib import Path

from suncoin.cli import load_chain, main


def run(state: Path, *args: str) -> int:
    return main(["--state", str(state), "--difficulty", "2", *args])


def test_solar_send_mine_roundtrip(tmp_path: Path, capsys):
    state = tmp_path / "chain.json"
    assert run(state, "solar", "alice", "100") == 0
    assert run(state, "send", "alice", "bob", "3") == 0
    assert run(state, "mine", "miner1") == 0

    # state persisted across invocations
    bc = load_chain(state, 2, 50.0)
    assert bc.balance_of("alice") == 7.0
    assert bc.balance_of("bob") == 3.0
    assert bc.balance_of("miner1") == 50.0


def test_validate_command(tmp_path: Path, capsys):
    state = tmp_path / "chain.json"
    run(state, "solar", "alice", "10")
    run(state, "mine", "m")
    assert run(state, "validate") == 0
    assert "valid" in capsys.readouterr().out.lower()


def test_stats_command(tmp_path: Path, capsys):
    state = tmp_path / "chain.json"
    run(state, "solar", "alice", "40")
    run(state, "mine", "m")
    run(state, "stats")
    out = capsys.readouterr().out
    assert "co2_avoided_grams" in out
    assert "total_solar_kwh" in out


def test_load_creates_fresh_chain_when_missing(tmp_path: Path):
    bc = load_chain(tmp_path / "nope.json", 2, 50.0)
    assert len(bc.chain) == 1  # only genesis
