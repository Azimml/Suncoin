# Suncoin

**A from-scratch proof-of-work blockchain that rewards clean solar-energy production with a CO2-reduction-backed digital currency.**

Suncoin turns the kilowatts a solar panel produces into a cryptocurrency. Every
reward and transfer is recorded on an append-only, SHA-256 hashed, proof-of-work
blockchain, so the ledger also doubles as an auditable record of how much CO2 the
network has helped avoid.

This repository is a pure-Python implementation of the Suncoin concept. It was
originally prototyped in JavaScript/Solidity (an ERC-20 token plus an Express +
MongoDB backend and a React/IoT frontend); it has since been **ported to Python**
and reimplemented as a self-contained blockchain so the ledger no longer depends
on a third-party chain or smart-contract platform.

---

## The concept

> Suncoin is an innovative project aimed at promoting the use of solar panels by
> converting the amount of solar energy produced (kW) into a digital currency
> called *Suncoin*. Users install solar panels, an indicator device measures the
> kilowatts produced, and that production is converted into Suncoins that can be
> exchanged for real money — a financial incentive to adopt solar energy.

The environmental thesis (from the project whitepaper/presentation):

- Replacing fossil-fuel electricity with solar avoids large amounts of CO2.
- A typical household solar system can avoid **~8.5 tons of CO2 per year** — about
  the same as taking three cars off the road.
- Rewarding solar output with currency creates an incentive loop: more panels →
  less fossil generation → lower emissions.

Suncoin encodes this directly: solar production creates coins, and the amount of
energy (and therefore the estimated CO2 avoided) is stored on-chain alongside the
reward.

---

## Architecture

```
suncoin/
├── transaction.py   Transaction model (transfers + coinbase/solar rewards)
├── block.py         Block dataclass with deterministic SHA-256 hashing
├── blockchain.py    Genesis, proof-of-work mining, validation, balances, CO2
├── cli.py           Scriptable command-line interface (JSON-persisted chain)
└── api.py           Optional Flask HTTP API (mirrors the old "Suncoin Web")
```

| Original (JavaScript / Solidity)                | Python port                                  |
| ----------------------------------------------- | -------------------------------------------- |
| `SolarCoin.sol` ERC-20 token (`mint`/`burn`)    | `Blockchain` with coinbase reward minting    |
| `deploy.js` / `web3.js` (Infura, gas, nonce)    | in-process ledger — no external chain needed |
| Express `server.js` `POST /api/data`            | `POST /api/data` on the Flask API            |
| `power * 0.1` conversion of solar power → coins | `reward_solar_production(addr, kwh, rate)`   |
| MongoDB persistence of readings                 | on-chain transactions + JSON chain file      |
| React `useBalance` reading on-chain balance     | `GET /balance/<address>` / `balance_of()`    |

---

## How mining and validation work

**Blocks.** Each block holds an index, a timestamp, its list of transactions, the
previous block's hash, and a nonce. The block hash is
`SHA-256(json(payload, sorted keys))`, so hashing is fully deterministic and any
change to any field changes the hash.

**Proof of work.** To mine a block the network increments the nonce until the
block's hash starts with `difficulty` leading zeros (e.g. difficulty 3 → a hash
starting `000…`). This is deliberately expensive to produce and trivial to check.

**Mining reward.** Mining a block bundles the pending transactions plus a coinbase
reward for the miner. Solar-production rewards are also coinbase transactions —
they mint new coins the same way the original ERC-20 `mint` did, but here the
minting is gated by proof-of-work instead of an `onlyOwner` call.

**Validation & tamper detection.** `Blockchain.is_valid()` walks the chain and,
for every block, (1) recomputes the hash and checks it matches the stored one,
(2) checks each block's `previous_hash` links to the real hash of its predecessor,
and (3) confirms the hash still meets the difficulty target. Rewriting a confirmed
transaction, editing a stored hash, breaking a link, or reordering blocks all make
`is_valid()` return `False`.

---

## Quick start

```bash
git clone https://github.com/Azimml/Suncoin.git
cd Suncoin
python -m pip install -e ".[dev,api]"    # or: pip install -r requirements-dev.txt
```

### Library

```python
from suncoin import Blockchain, Transaction

chain = Blockchain(difficulty=3, mining_reward=50.0)

# A household's panels produced 120 kWh of clean energy -> reward it.
chain.reward_solar_production("alice", kwh=120)
chain.mine_pending_transactions(miner_address="grid-operator")

# A normal transfer, then mine it into a block.
chain.add_transaction(Transaction("alice", "bob", 5.0))
chain.mine_pending_transactions("grid-operator")

print(chain.balance_of("alice"))      # -> 7.0 SLC
print(chain.co2_avoided_grams())      # estimated CO2 avoided by the solar energy
print(chain.is_valid())               # -> True
```

### Command line

```bash
suncoin solar alice 120        # record 120 kWh of solar and queue a reward
suncoin send alice bob 5       # queue a transfer
suncoin mine grid-operator     # mine the pending transactions
suncoin balance alice          # -> alice: 7.0 SLC
suncoin validate               # verify chain integrity
suncoin stats                  # solar kWh + estimated CO2 avoided
```

The CLI persists the chain to `suncoin_chain.json` so successive commands build on
the same ledger.

### HTTP API

```bash
python -m suncoin.api          # serves on http://127.0.0.1:3000
```

| Method | Route                | Purpose                                          |
| ------ | -------------------- | ------------------------------------------------ |
| GET    | `/health`            | liveness + block count                           |
| GET    | `/chain`             | full chain as JSON                               |
| GET    | `/chain/valid`       | run `is_valid()`                                 |
| POST   | `/transactions`      | queue a transfer `{sender, recipient, amount}`   |
| POST   | `/api/data`          | legacy: record a solar reading `{power, address}`|
| POST   | `/mine`              | mine pending transactions `{miner}`              |
| GET    | `/balance/<address>` | balance of an address                            |
| GET    | `/stats`             | total solar kWh + CO2 avoided                    |

### Examples & tooling

```bash
python examples/mine_blocks.py       # mine a few blocks and print the ledger
python examples/tamper_detection.py  # watch validation catch tampering
make test                            # run the pytest suite
make lint                            # ruff check .
```

---

## Whitepaper summary

From the project presentation (`Suncoin_Presentation.pptx`, kept in this repo):

1. **Overview** — convert solar energy produced (kW) into a digital currency,
   *Suncoin*, using indicator devices attached to panels; exchange it for money.
2. **Target** — encourage eco-friendly solar instead of fossil-fuel electricity;
   cut CO2 emissions and combat climate change.
3. **How it works** — install panels → measure kWh → convert to Suncoin → redeem
   for money → more adoption → less fossil reliance.
4. **Environmental impact** — reduce air pollution and greenhouse gases, promote a
   sustainable future.
5. **Financial incentive** — the reward offsets installation cost and drives
   adoption.

---

## Limitations

This is an educational, single-node implementation. It is **not** production
money and intentionally omits:

- **Cryptographic signatures / wallets** — transactions are not signed, so
  anyone can create a transfer from any address. A real system would use
  public-key signatures and verify sender ownership.
- **Consensus / networking** — there is no peer-to-peer layer, gossip, or
  longest-chain fork resolution; the chain lives in a single process.
- **Double-spend & balance enforcement** — pending transactions are not checked
  against sender balances before mining.
- **Persistent, concurrent storage** — the CLI uses a plain JSON file and the API
  keeps the chain in memory.
- **Real CO2 measurement** — the CO2 figure is an estimate derived from a fixed
  grams-per-kWh factor, not a verified measurement.

These are deliberate scope choices that keep the core blockchain concepts clear
and fully testable.

---

## License

MIT — see [`LICENSE`](LICENSE).
