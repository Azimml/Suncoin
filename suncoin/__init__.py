"""Suncoin - a from-scratch proof-of-work blockchain with a CO2-reduction concept.

Suncoin rewards clean solar-energy production with a digital currency. Solar
panels report the kilowatts they generate; that production is turned into
Suncoin transactions and permanently recorded on an append-only, SHA-256 hashed,
proof-of-work blockchain. The design mirrors the original SolarCoin project's
idea (reward solar generation, cut CO2 emissions) but implements the ledger
itself in pure Python instead of an ERC-20 smart contract.
"""

from suncoin.transaction import Transaction

__version__ = "0.1.0"

# grams of CO2 avoided per kWh of grid electricity displaced by solar,
# roughly the value used in the Suncoin whitepaper (~8.5 tons/household/year).
CO2_GRAMS_PER_KWH = 475.0

__all__ = ["Transaction", "CO2_GRAMS_PER_KWH", "__version__"]
