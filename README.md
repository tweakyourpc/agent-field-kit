# Agent Field Kit

![Agent Field Kit hero: portable operations kit for AI coding agents](assets/agent-field-kit-hero.png)

Agent Field Kit is a portable bootstrap bundle for local AI coding environments.
It installs the habits, helper tools, checks, and publishing workflows that make
an agent usable on a busy machine without baking in the original user's personal
paths, names, tokens, or service choices.

Supported capabilities:

- install or update `portbroker` from a local source or GitHub fallback
- install or update `prose-hygiene` from a local source or GitHub fallback
- install Google Apps Script `clasp` with npm
- install EnvSentinel for `.env` contract validation
- install Engramize as an optional memory workflow scaffold
- check GitHub CLI availability and auth
- install prose-hygiene and optional EnvSentinel pre-commit hooks
- initialize and check EnvSentinel contracts
- write an Engramize-oriented memory protocol into a repo
- render Codex, Claude, and OpenCode instruction files
- create or push GitHub repos through `gh`
- create or connect `.clasp.json` projects and optionally push with `clasp`

## Why This Exists

The useful part of a tuned agent setup is not just a pile of binaries. It is the
combination of:

- local tools
- credentials owned by the current user
- agent instructions that explain when to use those tools
- repeatable checks that prove the environment is ready

Agent Field Kit keeps those layers separate. The repo contains templates and a
wizard. Each user supplies their own settings and authenticates their own tools.

No secrets are stored in this repository. Doctor output redacts email addresses,
GitHub account names, common token shapes, Google OAuth client IDs, and home
paths.

## Quick Start

```sh
./install.sh
```

That launches the wizard and writes:

- `~/.config/agent-field-kit/config.json` by default
- optional generated agent instruction files
- optional tool installs when run with `--install-tools`

Set `AGENT_FIELD_KIT_CONFIG=/path/to/config.json` to use a separate config file
for another machine, project, or agent persona.

## Commands

```sh
bin/agent-field-kit wizard
bin/agent-field-kit wizard --install-tools
bin/agent-field-kit doctor
bin/agent-field-kit doctor --strict
bin/agent-field-kit doctor --include-optional
bin/agent-field-kit install-tools
bin/agent-field-kit install-tools portbroker prose-hygiene envsentinel engramize
bin/agent-field-kit install-hooks --repo /path/to/repo --include-envsentinel
bin/agent-field-kit init-env-contract --repo /path/to/repo
bin/agent-field-kit check-env --repo /path/to/repo
bin/agent-field-kit setup-memory --repo /path/to/repo --install
bin/agent-field-kit publish-github --repo . --name my-repo --private --push
bin/agent-field-kit setup-clasp --repo . --script-id SCRIPT_ID
bin/agent-field-kit setup-clasp --repo . --create --title "My Script" --push
bin/agent-field-kit render --agent codex
bin/agent-field-kit render --agent claude
bin/agent-field-kit render --agent opencode
```

Every mutating command that can affect outside state supports `--dry-run` except
the interactive wizard. Installer commands preflight required tools such as
`git`, `pip`, and `npm` before mutating local state, and interrupted clones are
cleaned up when Agent Field Kit created the target directory.

## Tool Sources

Defaults are intentionally configurable in the wizard:

- `portbroker`: `git@github.com:tweakyourpc/portbroker.git`
- `prose-hygiene`: `git@github.com:tweakyourpc/prose-hygiene.git`
- `envsentinel`: `git@github.com:tweakyourpc/envsentinel.git`
- `engramize`: `git@github.com:tweakyourpc/engramize.git`

If a matching local source path exists, Agent Field Kit uses that instead of
cloning. On this machine those defaults point at local development checkouts.

## Capability Packs

EnvSentinel adds a configuration contract layer. Agent Field Kit can create a
starter `envsentinel.json`, generate `.env.example`, check `.env` files, and add
an EnvSentinel hook to the local pre-commit dispatcher.

Engramize adds a memory workflow layer. Agent Field Kit can install the source
package and write `.agent-field-kit/memory-protocol.md` into a repository so
agents have an explicit approval-gated memory workflow.

## Auth Boundary

Agent Field Kit does not copy credentials. Each machine/user must run their own
authentication:

```sh
gh auth login
clasp login
```

The default `clasp` auth check is `clasp show-authorized-user`, because modern
`clasp` versions do not support `clasp login --status`.

## Design

Agent Field Kit is intentionally boring:

- Python standard library only for the kit itself
- no required network dependency during template rendering or doctor checks
- explicit user-owned auth for GitHub and Google
- templates with simple placeholders
- generated files include a marker header

## Publish This Kit

```sh
bin/agent-field-kit publish-github --repo . --name agent-field-kit --private --push
```

Use a private repository first if you want to review generated docs or examples
before publishing publicly.
