# Contributing to Contoso Universe Generator

Thank you for your interest in contributing! CUG is a Python-native synthetic data generator for Power BI and analytics workflows.

---

## Setting up your dev environment

We use [`uv`](https://docs.astral.sh/uv/) for dependency management.

```bash
git clone https://github.com/CSalcedoDataBI/contoso-universe-gen.git
cd contoso-universe-gen

# Create venv and install with dev extras
uv pip install -e ".[dev]"
```

### Dev dependencies (`[dev]` extra)

- `pytest` — test runner
- `ruff` — linter and formatter

---

## Running the test suite

```bash
pytest tests/ -v --tb=short
```

All tests live in `tests/`. The baseline is `tests/test_smoke.py`. New contributions should include tests.

---

## Code style

We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting. Configuration is in `pyproject.toml`.

```bash
# Lint
ruff check cug/

# Auto-fix
ruff check cug/ --fix

# Format
ruff format cug/
```

CI will fail if lint or format checks fail.

---

## Creating a YAML category plugin

The fastest way to contribute new product categories is via the plugin system — no Python code required.

1. Read the plugin schema in [`docs/category-plugins.md`](docs/category-plugins.md)
2. Create your YAML file (e.g., `fashion_category.yaml`)
3. Test it locally:

   ```bash
   cug generate -n 1000 -f csv -c my_config.toml
   ```

4. Open a PR with your YAML file and a brief description of the industry/use case

Community category plugins are very welcome!

---

## Opening issues

Before opening an issue, please:

- Check existing issues for duplicates
- For bugs: include the command you ran, CUG version (`cug --version`), and OS
- For features: describe the use case, not just the implementation

---

## Pull request process

1. Fork the repo and create a feature branch
2. Make your changes with appropriate tests
3. Ensure `pytest tests/ -v` passes
4. Ensure `ruff check cug/` passes
5. Open a PR with a clear description of what and why

PRs that break existing tests will not be merged.

---

## Project structure

```
cug/
├── __init__.py          # Version and public exports
├── __main__.py          # CLI entrypoint
├── config.py            # Pydantic config schema (AppConfig)
├── engine.py            # Core orchestration engine
├── generators/          # Per-table data generators
│   ├── customers.py
│   ├── products.py
│   ├── sales.py
│   └── ...
├── writers/             # Output format writers
│   ├── csv_writer.py
│   ├── parquet_writer.py
│   └── ...
└── categories/
    └── builtin/         # Built-in YAML category definitions
```

---

## License

By contributing, you agree your contributions will be licensed under the [MIT License](LICENSE).
