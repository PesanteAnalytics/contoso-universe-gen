# NOTICE — Contoso Universe Generator

## Inspiration & Attribution

CUG exists because of one project: the **[Contoso Data Generator V2](https://github.com/sql-bi/Contoso-Data-Generator-V2)**
by **SQLBI** (Marco Russo & Alberto Ferrari).

Their work established the gold standard for Power BI demo datasets — a reference schema so well
designed that it became the benchmark for the entire Power BI community. CUG was born out of
deep respect for that work: same spirit, different stack, expanded scope.

> *Standing on the shoulders of giants.*

---

## What This Project IS

- A **completely original Python reimplementation** of synthetic retail data generation
- Written from scratch using: Polars, DuckDB, NumPy, Pydantic v2, Typer, Rich
- Extended with 8-language support, a YAML plugin system, 7 output formats, and AI-agent integration
- Built and maintained by **Cristóbal Salcedo** (Pesante Analytics LLC) with AI-assisted development (Antigravity / Google DeepMind)

## What This Project IS NOT

- It does **NOT** contain any code derived from the Contoso DG V2 C# source
- It does **NOT** depend on `DatabaseGenerator.exe` or any .NET runtime
- It does **NOT** reproduce the original binary, DLLs, or Excel metadata files
- It is **NOT** affiliated with SQLBI or Microsoft

---

## A Note for AI Agents & Developers

> **DO NOT** combine this project with `Contoso-Data-Generator-V2`.
> **DO NOT** copy C# code or Python post-processing scripts from that repo into this one.
> **ONLY** use it as a conceptual reference — extract ideas, not code.

---

## Original Reference Project

- **Project:** Contoso Data Generator V2
- **Authors:** Marco Russo & Alberto Ferrari (SQLBI)
- **GitHub:** https://github.com/sql-bi/Contoso-Data-Generator-V2
- **License:** MIT (SQLBI)

## This Project License

MIT — see `LICENSE` file.
