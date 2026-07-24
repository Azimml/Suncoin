# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0]

### Added

- Pure-Python `Transaction` model supporting transfers, coinbase mining rewards
  and solar-production rewards that carry the kWh that earned them.
- `Block` dataclass with deterministic SHA-256 hashing of a canonical payload.
- `Blockchain` class with a fixed genesis block, a pending-transaction pool,
  proof-of-work mining with a configurable difficulty and mining reward, full
  chain validation / tamper detection, balances, and on-chain CO2 accounting.
- `suncoin` command-line interface (record solar, transfer, mine, balance,
  validate, stats) with JSON chain persistence.
- Optional Flask HTTP API mirroring the original "Suncoin Web" backend, including
  the legacy `POST /api/data` solar-reading endpoint.
- Test suite (pytest) covering hashing determinism, proof-of-work difficulty,
  validation/tamper detection, the transaction flow, the CLI and the API.
- Runnable examples, packaging (`pyproject.toml`), ruff config, Makefile,
  requirements files, editorconfig and GitHub issue/PR templates.

### Changed

- Ported the project from JavaScript/Solidity to Python; the ERC-20
  `SolarCoin.sol` token and the Express/MongoDB/React/IoT prototype were replaced
  by a self-contained blockchain that no longer needs an external chain.

### Removed

- Legacy JavaScript and Solidity sources (`Suncoin Blockchain/`, `Suncoin Web/`)
  after the Python port landed. The project presentation is retained.
