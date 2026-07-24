"""Transaction model for the Suncoin ledger.

A Suncoin transaction moves an ``amount`` of coins from ``sender`` to
``recipient``. Mining rewards and solar-production rewards use the reserved
sender ``COINBASE`` (they mint new coins rather than moving existing ones).

Solar-reward transactions may also carry the amount of clean energy that earned
them (``solar_kwh``) so the chain doubles as an auditable record of how much
CO2 was avoided.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Reserved "sender" for newly minted coins (mining + solar rewards).
COINBASE = "COINBASE"


@dataclass(frozen=True)
class Transaction:
    """An immutable transfer of Suncoin between two addresses."""

    sender: str
    recipient: str
    amount: float
    solar_kwh: float = 0.0
    memo: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("transaction amount must not be negative")
        if self.solar_kwh < 0:
            raise ValueError("solar_kwh must not be negative")
        if not self.recipient:
            raise ValueError("transaction requires a recipient")

    @property
    def is_reward(self) -> bool:
        """True for coinbase transactions that mint new coins."""
        return self.sender == COINBASE

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dict (used for hashing and the API)."""
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "solar_kwh": self.solar_kwh,
            "memo": self.memo,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Transaction:
        """Rebuild a transaction from its serialised form."""
        return cls(
            sender=data["sender"],
            recipient=data["recipient"],
            amount=float(data["amount"]),
            solar_kwh=float(data.get("solar_kwh", 0.0)),
            memo=data.get("memo", ""),
            metadata=dict(data.get("metadata", {})),
        )

    @classmethod
    def reward(cls, recipient: str, amount: float, memo: str = "mining reward") -> Transaction:
        """Create a coinbase reward transaction."""
        return cls(sender=COINBASE, recipient=recipient, amount=amount, memo=memo)
