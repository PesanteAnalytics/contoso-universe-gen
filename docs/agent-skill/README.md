# 🤖 Contoso Universe Generator — Agent Skill

> **Portable AI agent skill** for generating 100% relational synthetic retail datasets (Contoso star schema) with realistic temporal patterns — COVID impact, Black Friday, weekday seasonality, and more.

---

## 📋 Contents

| File / Folder | Description |
|---|---|
| [`SKILL.md`](./SKILL.md) | **Main skill file** — copy this to your agent's skills directory |
| [`CHANGELOG.md`](./CHANGELOG.md) | Version history and release notes |
| [`examples/basic_usage.md`](./examples/basic_usage.md) | Common use cases and quick recipes |
| [`examples/advanced_usage.md`](./examples/advanced_usage.md) | Advanced configurations (events, plugins, multi-format) |
| [`config/CUG-CONFIG.template.md`](./config/CUG-CONFIG.template.md) | Configuration card template — copy to your project root |

---

## 🚀 Quick Integration (3 Steps)

### 1. Copy the skill file

```bash
# For Antigravity / Gemini agents (Windows):
copy docs\agent-skill\SKILL.md .agent\skills\contoso-universe-gen\SKILL.md

# For Antigravity / Gemini agents (Mac/Linux):
cp docs/agent-skill/SKILL.md .agent/skills/contoso-universe-gen/SKILL.md
```

### 2. Update the three placeholders in `SKILL.md`

Open the copied `SKILL.md` and replace:

| Placeholder | Replace with | Example |
|---|---|---|
| `<project_root>` | Absolute path to CUG | `C:\projects\contoso-universe-gen` |
| `<python>` | Python executable in your venv | `.venv/Scripts/python` |
| `<sql_server_instance>` | SQL Server instance (if used) | `localhost\SQLEXPRESS` |

### 3. Start generating

Tell your agent:
- `"Generate a 100K retail dataset in Parquet"`
- `"Generar datos Contoso para Power BI"`
- `"Create test data for my workshop"`

The agent will create a `CUG-CONFIG.md` in your project root and manage all configuration through it.

---

## 🎯 What This Skill Does

When triggered, the agent follows a **5-step file-driven workflow**:

```
Step 1 → Ensure CUG-CONFIG.md exists (creates from template if needed)
Step 2 → Read & parse the configuration card
Step 3 → Detect intent & apply user-requested changes
Step 4 → Translate config → TOML + build CLI command
Step 5 → Execute generation & update the config footer
```

The **`CUG-CONFIG.md`** file acts as a persistent, human-readable configuration card that users can view and edit directly in their IDE.

---

## 📦 Supported Output Formats

| Format | Use Case |
|---|---|
| `parquet` | Default — Power BI, Spark, DuckDB |
| `csv` | Universal compatibility |
| `duckdb` | Local analytics with 3 pre-built views |
| `delta` | Microsoft Fabric, Databricks |
| `json` / `ndjson` | APIs, document stores |
| `excel` | Quick demos *(max ~1M rows)* |
| `sqlserver` | Direct SQL Server injection |

---

## 📚 Related Documentation

> These files live in the parent `docs/` directory:

- [`docs/installation.md`](../installation.md) — Installation guide
- [`docs/toml-configuration.md`](../toml-configuration.md) — Full TOML reference
- [`docs/output-formats.md`](../output-formats.md) — Format-specific details
- [`docs/data-schema.md`](../data-schema.md) — Generated star schema
- [`docs/category-plugins.md`](../category-plugins.md) — YAML plugin system
- [`docs/i18n-reference.md`](../i18n-reference.md) — Language & locale guide
- [`docs/recipes.md`](../recipes.md) — CLI quick recipes

---

## 🔖 Version

| Field | Value |
|---|---|
| Skill version | `1.0.0` |
| Compatible with CUG | `≥ 0.1.0` |
| Python required | `3.12+` |
| Last updated | `2026-03-20` |
