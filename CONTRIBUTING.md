# Contributing to Suncoin

Thanks for your interest in improving Suncoin! This project is a small, readable
proof-of-work blockchain, and contributions that keep it clear and well-tested
are very welcome.

## Getting set up

```bash
git clone https://github.com/Azimml/Suncoin.git
cd Suncoin
python -m venv .venv && source .venv/bin/activate
python -m pip install -e ".[dev,api]"
```

## Before you open a pull request

1. **Run the tests** — every change must keep the suite green:
   ```bash
   make test        # or: python -m pytest
   ```
2. **Lint** — the codebase is ruff-clean:
   ```bash
   make lint        # ruff check .
   make format      # auto-fix + format
   ```
3. **Add tests** for new behaviour. Blockchains are easy to get subtly wrong, so
   new functionality without a test will usually be asked to add one.

## Coding guidelines

- Target Python 3.10+ and prefer standard-library solutions; the core chain has
  no third-party runtime dependencies (Flask is optional, for the API only).
- Keep public functions documented and type-annotated.
- One logical change per commit; use [Conventional Commits](https://www.conventionalcommits.org/)
  (`feat:`, `fix:`, `test:`, `docs:`, `chore:`, `refactor:`).

## Reporting bugs and requesting features

Please use the GitHub issue templates. For security-sensitive reports, note that
this is an educational project and **must not be used to secure real value** —
see the limitations section of the README.
