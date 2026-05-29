# Agent Field Kit

Agent Field Kit is a portable bootstrap bundle for local AI coding environments.
It installs the habits and helper checks that make an agent usable on a busy
machine without baking in the original user's personal paths, names, tokens, or
service choices.

The first supported capabilities are:

- portbroker-aware server startup rules
- prose hygiene command discovery
- GitHub CLI publishing readiness checks
- Google Apps Script `clasp` readiness checks
- Codex, Claude, and OpenCode instruction templates

## Why This Exists

The useful part of a tuned agent setup is not just a pile of binaries. It is the
combination of:

- local tools
- credentials owned by the current user
- agent instructions that explain when to use those tools
- repeatable checks that prove the environment is ready

Agent Field Kit keeps those layers separate. The repo contains templates and a
wizard. Each user supplies their own settings and authenticates their own tools.

## Quick Start

```sh
./install.sh
```

That launches the wizard and writes:

- `~/.config/agent-field-kit/config.json`
- optional generated agent instruction files
- optional pre-commit hook snippets

No secrets are stored in this repository.

The default `clasp` auth check is `clasp show-authorized-user`, because modern
`clasp` versions do not support `clasp login --status`.

## Commands

```sh
bin/agent-field-kit wizard
bin/agent-field-kit doctor
bin/agent-field-kit render --agent codex
bin/agent-field-kit render --agent claude
bin/agent-field-kit render --agent opencode
```

## Design

Agent Field Kit is intentionally boring:

- Python standard library only
- no network dependency during wizard or rendering
- explicit user-owned auth for GitHub and Google
- templates with simple placeholders
- generated files include a marker header

## Suggested Publish Flow

```sh
gh auth status
git init
git add .
git commit -m "Initial Agent Field Kit"
gh repo create agent-field-kit --source . --public --push
```

Use a private repository first if you want to review generated docs or examples
before publishing.

