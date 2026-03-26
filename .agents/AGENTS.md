# 🤖 Agent Configuration — Contoso Universe Generator

This `.agents/` folder contains AI agent skills, workflows, and automation for CUG.

## Structure

```
.agents/
├── AGENTS.md                              ← You are here
├── skills/
│   └── contoso-universe-gen/              ← CUG Agent Skill
│       ├── SKILL.md                       ← Main skill instructions
│       ├── config/
│       │   └── CUG-CONFIG.template.md     ← Copy to project root as CUG-CONFIG.md
│       ├── examples/
│       │   └── basic_usage.md             ← Common usage scenarios
│       └── evals/
│           └── evals.json                 ← Test cases for skill validation
└── workflows/
    ├── execute-master-plan.md             ← 🎯 Orchestrator: runs all phases in order
    ├── phase1-cleanup.md                  ← Phase 1: Remove junk, fix links, unify URLs
    ├── phase2-language.md                 ← Phase 2: Rename and translate docs to English
    ├── verify-iter1.md                    ← Iter-1: Technical verification gate (10 checks)
    ├── phase3-consistency.md              ← Phase 3: Fix schemas, structure, scaling bug
    ├── phase4-polish.md                   ← Phase 4: PyPI metadata, tests, CI
    ├── verify-iter2.md                    ← Iter-2: UX/Docs verification gate (10 checks)
    ├── verify-iter3.md                    ← Iter-3: Fresh clone simulation (10 checks)
    └── phase5-release.md                  ← Phase 5: Public release (requires user GO)
```

## Workflows (Slash Commands)

Workflows automate the Master Publication Plan. All workflows use `// turbo-all`
to auto-approve safe commands without user intervention.

| Command | Description | Auto-run |
|---------|-------------|----------|
| `/execute-master-plan` | Full orchestration of all phases | ✅ |
| `/phase1-cleanup` | Critical cleanup (H-01 to H-06) | ✅ |
| `/phase2-language` | Language normalization (H-07) | ✅ |
| `/verify-iter1` | Technical verification gate | ✅ |
| `/phase3-consistency` | Technical consistency (H-08 to H-12) | 🔜 |
| `/phase4-polish` | Final polish (H-13 to H-16) | 🔜 |
| `/verify-iter2` | UX/Docs verification gate | 🔜 |
| `/verify-iter3` | Fresh clone simulation | 🔜 |
| `/phase5-release` | Public release | ⚠️ Manual |

### Execution Flow

```
Phase 1 → Phase 2 → ITER-1 → Phase 3 → Phase 4 → ITER-2 → ITER-3 → Phase 5
                      GATE                          GATE     GATE     MANUAL
```

**Rule:** No phase advances past a GATE until the verification passes 10/10.

## Using the Skill

### Antigravity / Gemini agents

The skill at `skills/contoso-universe-gen/SKILL.md` is self-contained.
Copy it to your global agent skills directory:

```
~/.gemini/antigravity/skills/contoso-universe-gen/SKILL.md
```

### Other AI agents (Claude, Cursor, etc.)

Point your agent at `skills/contoso-universe-gen/SKILL.md` — it works with any
tool-calling agent that can read files and run shell commands.

### Setup (once per machine)

1. Install CUG: `pip install contoso-universe-gen` (or `uv add contoso-universe-gen`)
2. Copy `config/CUG-CONFIG.template.md` → `CUG-CONFIG.md` at your project root
3. Edit the three placeholders in `SKILL.md` (project_root, python, sql_server_instance)
4. Ask the agent: *"Generate a test dataset"* — the skill handles the rest

## Notes

- `CUG-CONFIG.md` at the project root is **gitignored** (user-specific settings)
- `skills/` is **committed** — part of the public repository for community use
- `workflows/` is **gitignored** — internal automation, not published
- Plans and session files are stored in `_pal-internal/` (gitignored)
