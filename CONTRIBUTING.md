# Contributing to Contoso Universe Generator

Thank you for your interest in contributing! CUG is a Python-native synthetic data generator for Power BI and analytics workflows.

---

## Setting up your dev environment

We use [`uv`](https://docs.astral.sh/uv/) for dependency management.

```bash
git clone https://github.com/PesanteAnalytics/contoso-universe-gen.git
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

We use [Ruff](https://github.com/astral-sh/ruff) for linting. Configuration is in `pyproject.toml`.

```bash
# Lint — this is what CI runs, and it must be clean
ruff check cug/ tests/

# Auto-fix what can be fixed mechanically
ruff check cug/ tests/ --fix
```

CI fails if `ruff check` reports anything.

> **Please do not run `ruff format`.** The codebase is not formatted with it, and running it would rewrite roughly 2,200 lines across 37 files — flattening aligned data tables such as the currency registry, and burying your actual change in the diff. Whether to adopt it is an open question tracked in [#12](https://github.com/PesanteAnalytics/contoso-universe-gen/issues/12); until that is decided, formatting is not a gate and not expected.

---

## Creating a YAML category plugin

The fastest way to contribute new product categories is via the plugin system — no Python code required.

There are two kinds of plugin, and they are wired up differently:

| | Where the file goes | How it is loaded |
|---|---|---|
| **Builtin** — ships with CUG, what a contribution normally is | `cug/categories/builtin/<id>.yaml` | Only if its id is listed in `enabled` (see step 3) |
| **Custom** — your own, stays out of the repo | anywhere on disk | Always, via `custom_paths` in your TOML |

### Contributing a builtin category

1. **Read the schema** in [`docs/category-plugins.md`](docs/category-plugins.md).

2. **Create the file** as `cug/categories/builtin/<plugin_id>.yaml`. The filename must match the `plugin_id` inside it — that is how the loader finds it.

3. **Enable it** in [`cug/configs/default.toml`](cug/configs/default.toml). This step is easy to miss and nothing will warn you:

   ```toml
   [categories]
   enabled      = ["electronics", "home", "gaming", "media", "fashion", "your_category"]
   ```

   Without it your category is invisible to generation. Worse, `cug categories` will still list it — that command loads every YAML in the builtin directory, while generation loads only what `enabled` names. So the tool appears to know about your category and then refuses to generate it.

4. **Translate it into all eight languages.** Every `display_names` block, on the category and on each subcategory, needs `en`, `es`, `pt`, `fr`, `de`, `zh`, `ja`, `ar`. The product catalogue is the one dimension CUG localizes completely, and a category missing a language regresses that.

5. **Test it locally:**

   ```bash
   cug categories                              # your category and subcategories appear
   cug generate -n 20000 -f csv --strict       # integrity check passes
   pytest tests/ -v                            # suite still green
   ```

   Then look at `DimProduct` and confirm your category is actually in the output — that is the check that catches a missing step 3.

6. **Open a PR** with a brief description of the industry and use case.

### Things worth getting right

**Margins.** `margin_range` is the fraction of the price that is *not* cost, so `[0.40, 0.65]` means a 40–65% margin. Thin margins are supported and realistic — gaming hardware starts at 2% — and the generator caps cost just below list price so a unit is never sold at a loss.

**Trends.** The optional per-year `trend` map is real, not decoration: the schema reads it and it shapes how much that subcategory sells each year. It is the natural place to express something like a 2020 dip.

**Product counts are not yours to set.** The generator draws 5–15 products per subcategory at random, so catalogue size follows from how many subcategories you add, not from anything you can declare.

Community category plugins are very welcome.

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

```text
cug/
├── __init__.py              # Version and public exports
├── __main__.py              # CLI entrypoint
├── cli.py                   # Typer CLI commands
├── config.py                # Pydantic config schema (AppConfig)
├── models.py                # Shared data models
├── orchestrator.py          # Pipeline orchestration
├── engine/                  # Core engine components
│   ├── seeder.py            # Deterministic random seeding
│   ├── temporal.py          # Date/time and seasonality logic
│   ├── validator.py         # FK validation
│   └── weights.py           # Distribution weights
├── generators/              # Per-table data generators
│   ├── calendar.py          # DimDate
│   ├── currency.py          # DimCurrency
│   ├── currency_exchange.py # DimCurrencyExchange
│   ├── customers.py         # DimCustomer
│   ├── products.py          # DimProduct
│   ├── sales.py             # FactSales
│   └── stores.py            # DimStore
├── writers/                 # Output format writers (7 formats)
│   ├── csv_writer.py
│   ├── parquet_writer.py
│   ├── json_writer.py
│   ├── excel_writer.py
│   ├── delta_writer.py
│   ├── duckdb_writer.py
│   └── sqlserver_writer.py
├── i18n/                    # Internationalization (8 locales)
│   └── locales.py
└── categories/              # Product category system
    ├── base.py              # Category plugin base class
    ├── registry.py          # Plugin discovery and loading
    └── builtin/             # Built-in YAML definitions
        ├── electronics.yaml
        ├── gaming.yaml
        ├── home.yaml
        └── media.yaml
```

---

## License

By contributing, you agree your contributions will be licensed under the [MIT License](LICENSE).
