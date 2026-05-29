# Project Plan

## Name

Agent Field Kit

The name is meant to signal a portable bundle an agent can carry into a fresh
machine: local tools, instructions, checks, and setup prompts.

## MVP

- `wizard`: ask for local settings and write config
- `doctor`: verify command presence and auth status
- `render`: output Codex, Claude, or OpenCode instructions
- templates without personal information
- clear separation between shipped defaults and user-owned credentials

## Next Features

- optional dependency installers by platform
- migration command to import existing Codex or Claude rules
- `gh repo create` helper with dry-run mode
- `clasp` project bootstrap helper
- managed pre-commit hook installation
- signed release archives

## Data Boundary

The repository should never include:

- `.clasprc.json`
- GitHub tokens
- SSH private keys
- personal path registries
- existing portbroker reservation files
- generated user config

