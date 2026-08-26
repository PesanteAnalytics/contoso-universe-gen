# Security Policy

## Supported versions

CUG has not had a tagged release yet, so the only supported version is the
current `master`. Fixes land there. Once releases begin, this section will say
which of them still receive them.

## Reporting a vulnerability

Please **do not open a public issue** for a security problem.

Use GitHub's [private vulnerability reporting][advisory] on this repository, or
email **support@pesanteanalytics.com**. Either reaches the maintainers directly.

Helpful things to include: what you found, how to reproduce it, and what an
attacker could actually do with it. A proof of concept is welcome but not
required.

This is a small project maintained alongside other work. You will get a reply
from a person — please allow a few days rather than a few hours. If a report
turns out to be a real vulnerability, you will be credited in the fix unless you
prefer otherwise.

## What is worth reporting

CUG generates synthetic data locally. It has no server, no accounts and no
network calls at generation time, so the interesting surface is narrower than
for most projects. Worth reporting:

- **Code execution through configuration.** TOML config files and YAML category
  plugins are parsed by the tool. Anything that turns a config or a plugin into
  arbitrary code execution is a vulnerability, not a feature.
- **Path traversal on write.** Output paths, database names and workbook names
  come from user input. A value that escapes the intended output directory is a
  problem.
- **SQL injection in the SQL Server writer.** It builds statements against a
  database you point it at.
- **Anything that transmits data off the machine.** CUG is meant to be fully
  offline at generation time. A build or dependency that phones home would be a
  finding in itself.
- **Dependency vulnerabilities** that CUG actually reaches. Dependabot watches
  the manifest, but a reachable exploit path is worth a direct report.

## What is not a vulnerability

- **The generated data is not secret.** It is synthetic by design and safe to
  publish. Reading it is not a finding.
- **`--strict` aborting a run** on foreign-key violations is the documented
  behaviour, not a denial of service.
- **Generating a very large dataset exhausts disk or memory.** That is the tool
  doing what it was asked. Ask for less.

[advisory]: https://github.com/PesanteAnalytics/contoso-universe-gen/security/advisories/new
