# 🤖 Agent Configuration — Contoso Universe Generator

This `.agents/` folder contains AI agent skills and plans for the CUG project.

## Structure

```
.agents/
├── AGENTS.md                          ← You are here
└── skills/
    └── contoso-universe-gen/          ← CUG Agent Skill
        ├── SKILL.md                   ← Main skill instructions
        ├── config/
        │   └── CUG-CONFIG.template.md ← Copy to project root as CUG-CONFIG.md
        ├── examples/
        │   └── basic_usage.md         ← Common usage scenarios
        └── evals/
            └── evals.json             ← Test cases for skill validation
```

## Using the Skill

### Antigravity / Gemini agents

Copy `skills/contoso-universe-gen/SKILL.md` to your global agent skills directory:

```
# Windows:
~/.gemini/antigravity/skills/contoso-universe-gen/SKILL.md

# Or register in your agent config
```

### Other AI agents (Claude, Cursor, etc.)

Point your agent at `skills/contoso-universe-gen/SKILL.md` — it is self-contained
and works with any tool-calling agent that can read files and run shell commands.

### Setup (once per machine)

1. Install CUG: `pip install contoso-universe-gen` (or `uv add contoso-universe-gen`)
2. Copy `config/CUG-CONFIG.template.md` → `CUG-CONFIG.md` at your project root
3. Edit the three placeholders in `SKILL.md` (project_root, python, sql_server_instance)
4. Ask the agent: *"Generate a test dataset"* — the skill handles the rest

## Notes

- `CUG-CONFIG.md` at the project root is **gitignored** (user-specific settings)
- `skills/` is **committed** — part of the public repository for community use
- Plans and session files are stored in `.agents/plans/` (auto-created, gitignored)
