# Project Plan

## Name

Agent Field Kit

The name is meant to signal a portable bundle an agent can carry into a fresh
machine: local tools, instructions, checks, and setup prompts.

## Current Scope

- `wizard`: ask for local settings and write config
- `doctor`: verify command presence and auth status
- `install-tools`: install `portbroker`, `prose-hygiene`, `envsentinel`, `engramize`, `clasp`, or report GitHub CLI install guidance
- `install-hooks`: install a dispatcher pre-commit hook plus prose hygiene and optional EnvSentinel hooks
- `publish-github`: create or push repositories using `gh`
- `setup-clasp`: connect or create Apps Script projects and optionally push
- `init-env-contract`: create EnvSentinel schema and `.env.example` files
- `check-env`: validate environment files through EnvSentinel
- `setup-memory`: install Engramize support and write a memory protocol
- `render`: output Codex, Claude, or OpenCode instructions
- templates without personal information
- clear separation between shipped defaults and user-owned credentials

## Next Features

- named capability packs such as `core`, `quality`, `memory`, and `google`
- platform-specific GitHub CLI installation helpers
- release archive generation
- config import from existing Codex or Claude rules
- signed release archives
- automated smoke tests in CI

## Data Boundary

The repository should never include:

- `.clasprc.json`
- GitHub tokens
- SSH private keys
- personal path registries
- existing portbroker reservation files
- generated user config
