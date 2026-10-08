# Privacy policy — contoso-universe-gen

*Effective 2026-10-07. Maintainer: Pesante Analytics LLC — support@pesanteanalytics.com*

This policy covers the **contoso-universe-gen** plugin for Claude. The website
[pesanteanalytics.com](https://www.pesanteanalytics.com) has its own policy.

## What the plugin collects

**Nothing.** The plugin is one skill plus the source of the Contoso Universe Generator
(CUG), a Python CLI. It ships no hooks, no MCP server, no telemetry, no analytics and no
background process. It has no server of its own, so nothing you do with it reaches the
maintainer.

## What it reads and sends

| When | What happens | Where it goes |
|---|---|---|
| The skill is used | Claude reads the skill's Markdown and JSON from the installed plugin folder | Nowhere: local reads only |
| The skill sets up a run | Claude creates or edits `CUG-CONFIG.md` and a TOML config in your CUG folder | Your disk only |
| The skill generates data | Claude runs `python -m cug generate`; the data is random, built on your machine from bundled lists | Files under the output folder you choose (Parquet, CSV, DuckDB, Delta, JSON, Excel) |
| You pick the SQL Server format | CUG connects through ODBC to the instance you name, creates the database if missing and, by default, drops and recreates its tables | That SQL Server instance only, with Windows authentication or the SQL login you configure |
| You run CUG through `uv` with no environment yet | `uv` downloads the Python dependencies listed in `pyproject.toml` | The Python package index `uv` is configured to use |

The generated data is synthetic: no real customer, sale or person is read or produced.
The plugin keeps no copy of your configuration or your data and retains nothing.

The test suite, CI workflows and maintainer scripts in this repository are **not** run by
the plugin; they run only when a maintainer starts them.

## Children

The plugin is a developer tool and is not directed at anyone under 18.

## Changes and contact

Changes to this policy are made in this file and recorded in the repository history.
Questions: support@pesanteanalytics.com.
