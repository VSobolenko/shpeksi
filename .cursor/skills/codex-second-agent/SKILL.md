---
name: codex-second-agent
description: Delegate work to Codex (a GPT-based agent) as an independent second agent — review, implementation, research, image generation — through the `codex` MCP tools or the `codex` CLI. Use when you need genuine model diversity, a second opinion, or to offload a large independent investigation.
disable-model-invocation: true
---

# Codex as a second agent

Codex is a full agent harness (its own loop, tools, sandbox, context window) running
OpenAI models. In this repo it is wired up as an MCP server, so you can dispatch work
to it exactly like any other tool.

## Why use it at all

**Model diversity is the point.** Subagents you spawn inherit *your* model, so they
share your blind spots — a reviewer that thinks like the author tends to miss the same
things. Codex runs a different model family, so its failure modes are uncorrelated with
yours. That makes it the strongest available second opinion for review work.

Secondary reasons:

- **Independent context** — a large investigation consumes Codex's context, not yours.
- **Stateful** — `threadId` lets you hold a multi-turn conversation (`codex-reply`).
- **Image generation** — its built-in `image_gen` tool needs no `OPENAI_API_KEY`.

## What Codex knows automatically (measured, not assumed)

Verified empirically on this repo:

- **Codex auto-reads the root `AGENTS.md`.** Asked "what code style does this repo
  require?" with no hints, it answered "StandardJS: no semicolons, single quotes,
  2-space indentation. Plain JavaScript, not TypeScript" and cited `AGENTS.md`.
  So the conventions in that file are enforced **without you doing anything**.
- **Codex does NOT auto-read** `.cursor/rules/*.mdc`, `.agents/skills/**`, or
  `openspec/specs/**`. Those are Cursor-side conventions.
- **`developer-instructions` is honoured.** Verified: injected "no semicolons,
  single quotes, 2-space indent; never TypeScript", asked for a JS function, and
  got exactly that (no semicolons, single quotes). Use it for constraints that are
  not already in `AGENTS.md`.

Consequence: `AGENTS.md` is the single channel that reaches Codex for free. The
`## Defaults to suppress` section there exists precisely for that — the *negations*
(TypeScript→plain JS, Expo Router→React Navigation, SQLAlchemy→Beanie) are what
stop a model from falling back on its priors. If you add a convention that an
external agent must follow, put it in `AGENTS.md`, not only in a `.mdc` rule.

## Accountability protocol (mandatory)

You launch Codex and you answer for its output. Codex's self-report is **never**
evidence. Run these four steps on every delegation that produces code.

### 1. Prevent

- Conventions that belong in `AGENTS.md` must be there — that is the free channel.
- Anything else (task-specific constraints, a narrower scope than the repo default)
  goes in `developer-instructions`, not buried in the middle of a long prompt.

### 2. Contain

- Writing work goes into a **separate git worktree** (`using-git-worktrees`), so a
  bad result can be discarded without touching your own tree.
- Read-only work stays on `sandbox: "read-only"` against the main tree.

### 3. Verify — objective, tool-based

```bash
node scripts/verify-changes.mjs            # uncommitted changes
node scripts/verify-changes.mjs --base main
```

With no flag it reads `git status` (uncommitted work). With `--base <ref>` it reads
`git diff <ref>...HEAD` — so it sees **only committed** changes; uncommitted edits
will not appear. Use the flag for branch review, no flag while iterating.

This runs the repo's own linters over **only the changed files**, so pre-existing
debt cannot produce a false failure and, more importantly, a changed file cannot
slip through unexamined. It exits non-zero on FAIL and on BLOCKED.

Then read the diff yourself. The script proves style and syntax, not intent — it
cannot tell you the logic is wrong, that a GraphQL field was renamed, or that a
user-facing string was added to only one locale.

**Coverage is uneven — know the hole.** Measured against this repo:

| Module | Objective style check | Notes |
|---|---|---|
| `CustomerApp` | **Yes** — eslint (`standard`) | catches semicolons, quotes, indent, spacing |
| `Admin Dashboard` | **Yes** — eslint, once `npm install` has run | reported BLOCKED until installed |
| `backend` | **No linter** | only `compileall` + pytest → syntax and logic, not style |
| `Website` | **No linter** | no eslint config exists at all |

So in `backend` and `Website`, a style violation by Codex is **not** mechanically
detectable. There, the diff must be read by hand. Do not report a green gate as if
it covered those modules — the script prints them as UNVERIFIED for this reason.

### 4. Reject and correct

On a violation, reply on the **same thread** with `codex-reply` — do not start a
new session. Give the exact violation from the linter, not a vague "it's wrong":

```
codex-reply({
  threadId: "<id>",
  prompt: `The linter rejects your change. Fix exactly these and nothing else:
  - src/Foo.js:12 — Extra semicolon (semi)
  - src/Foo.js:18 — Expected indentation of 2 spaces but found 4 (indent)
  Re-run the linter before reporting done.`
})
```

Re-verify after it answers. Loop until the gate is green, then still read the diff.

## The two MCP tools

### `codex` — start a session

Required: `prompt`. Returns `{ threadId, content }`.

| Parameter | Values | Notes |
|---|---|---|
| `prompt` | string | **Required.** The initial user prompt. |
| `cwd` | string | Working directory. Relative paths resolve against the MCP server's cwd (the workspace root). |
| `sandbox` | `read-only` \| `workspace-write` \| `danger-full-access` | Default is Codex's own config. **Set this explicitly, always.** |
| `approval-policy` | `untrusted` \| `on-request` \| `never` | Whether Codex must ask before running generated shell commands. |
| `model` | e.g. `gpt-5.6-terra` | Optional override. |
| `config` | object | Per-call overrides of `~/.codex/config.toml`. |
| `base-instructions` | string | Replaces Codex's default system instructions entirely. |
| `developer-instructions` | string | Injected as a developer-role message (prefer this over `base-instructions`). |
| `compact-prompt` | string | Prompt used when compacting the conversation. |

### `codex-reply` — continue a session

Required: `prompt`, plus the `threadId` returned by the first call. Returns
`{ threadId, content }`. Use `threadId` (`conversationId` is deprecated).

## Models

| Slug | Description | Context |
|---|---|---|
| `gpt-5.6-terra` | Balanced agentic coding model. Default reasoning: medium. | 272k (max 872k) |
| `gpt-5.6-sol` | Reliable agentic workhorse. Default reasoning: low. | 272k (max 872k) |
| `gpt-5.6-luna` | Fast and affordable agentic coding model. | 272k (max 872k) |
| `gpt-5.5` | Previous generation. | 272k (no expansion) |
| `codex-auto-review` | **Not for code review** — this is the model that decides whether to auto-approve commands. | 272k |

Pick `gpt-5.6-luna` for cheap mechanical work, `gpt-5.6-terra` for judgement work,
`gpt-5.6-sol` for long autonomous runs.

## Safety rules

1. **Always set `sandbox` explicitly.** Default to `read-only` for anything that only
   needs to read (review, research, analysis). Use `workspace-write` only when Codex
   must produce files.
2. **Never combine `sandbox: "danger-full-access"` with `approval-policy: "never"`**
   on an unattended run. That is an unrestricted agent with no guardrails.
3. This project is registered as `trust_level = "trusted"` in `~/.codex/config.toml`,
   and `[windows] sandbox = "elevated"`. Codex **can** run shell commands and modify
   the repo. Treat it as a peer developer, not a sandboxed function call.
4. **Never accept a Codex change without an objective check.** Its "done", its
   self-reported test results, and its summary are all claims, not evidence. Run
   `scripts/verify-changes.mjs` and read the diff. This is the single most important
   rule here: you own what it produces.
5. The `/ship` guardrails apply to Codex too: no commit / merge / push / archive
   without the human checkpoint — including when Codex does the work.
6. `secret-guard.cjs` only guards *your* writes. Codex writing a secret is **not**
   intercepted — the hook never sees its tool calls. Verify its output before staging.

## Concurrency hazard

Two agents editing one worktree will clobber each other. Before delegating writing
work, isolate it:

- Run `codex` with `cwd` pointed at a **separate git worktree**
  (see the `using-git-worktrees` skill), or
- Keep Codex on `read-only` while you edit.

Concurrent *read-only* review against the same worktree is safe.

## Delegation patterns

### 1. Independent reviewer — highest-value use

Run it *alongside* your own review, not instead of it. Keep it read-only.

```
codex({
  sandbox: "read-only",
  cwd: "<repo root>",
  model: "gpt-5.6-terra",
  prompt: `You are an independent code reviewer. Read AGENTS.md,
  .cursor/rules/project-conventions.mdc, and openspec/specs/** first.

  Review the uncommitted changes (use \`git diff\` and \`git status\`).

  Report ONLY blocking findings, each as: file:line, what is wrong, why it
  matters. Check specifically for:
  - GraphQL contract drift (operation/field names, snake_case, _id)
  - violations of the self-pickup-only model (no rider/delivery code)
  - leftover "Forkly" branding that should be "Pikupo"
  - hardcoded secrets
  - spec drift against openspec/specs/**

  Do not modify any files. If you find nothing blocking, say so plainly.`
})
```

### 2. Implementer in an isolated worktree

Always pair a writing delegation with a worktree and a verification pass.

```
codex({
  sandbox: "workspace-write",
  approval-policy: "on-request",
  cwd: "<worktree path>",
  model: "gpt-5.6-sol",
  developer-instructions: `This repository uses plain JavaScript (never
  TypeScript). StandardJS: no semicolons, single quotes, 2-space indent,
  \`function(x)\` spacing. See AGENTS.md, especially the
  "Defaults to suppress" section.`,
  prompt: `Read AGENTS.md first — it is authoritative.

  Task: <task>.
  Run \`node scripts/verify-changes.mjs\` (or the module's own lint/test) before
  reporting done, and include the raw output in your report.`
})
```

Then verify independently — never take its "done" at face value:

```bash
node scripts/verify-changes.mjs
```

`developer-instructions` is used here rather than only the prompt because it is
delivered as a developer-role message, so it outranks the user prompt and is not
lost in a long task description.

### 3. Large independent investigation

Use `read-only`. Ask for a **structured** answer so the result stays compact in your
own context. Example: "map every place the string `forkly` still appears, grouped by
module, each with file:line" — one call, and its exploration never touches your context.

### 4. Multi-turn collaboration

Use the returned `threadId` with `codex-reply` to push back, ask follow-ups, or have it
revise. This is the difference between a one-shot tool and a real collaborator — use it
when its first answer is wrong but close.

### 5. Image generation

```
codex({
  sandbox: "workspace-write",
  cwd: "<repo root>",
  prompt: `Use your imagegen skill and built-in image_gen tool to generate
  <description>. Save the final PNG into <workspace path> and reply with the
  absolute path only.`
})
```

Notes:
- The built-in `image_gen` tool requires **no** `OPENAI_API_KEY`.
- Codex saves to `$CODEX_HOME/generated_images/...` by default; you must ask it to copy
  into the workspace, or the asset is not in the repo.
- Measured: ~52 s and ~11.5k tokens for one 1254×1254 PNG. It is slow.

## Network access — measured, and it is NOT what you'd expect

Verified on this machine (Windows, `~/.codex/config.toml` → `[windows] sandbox = "elevated"`):

| Path | Result |
|---|---|
| Shell command egress (default) | **BLOCKED** — `curl: (7) Failed to connect` / `http_code=000` |
| + `config: {sandbox_workspace_write: {network_access: true}}` | **BLOCKED** |
| + `config: {features: {network_proxy: true}}` | **BLOCKED** |
| Built-in web search | **UNAVAILABLE** — `codex features list` shows `search_tool` as `removed`, so it cannot be enabled |
| Browser tool | **UNAVAILABLE** in an MCP-server session |
| Codex's own model calls | **WORK** — it answers |
| Built-in `image_gen` | **WORKS** — generated a real PNG |
| Your own shell | **Has full internet** (DNS + HTTPS 200, no proxy configured) |

So the precise statement is: **the Codex process is online, but every command it runs is
network-isolated, and it has no search or browser tool.** It cannot fetch live
information from the internet. Do not delegate anything that needs it.

Consequences:

- **Its answer to "what's the current time?" is a shell read (`Get-Date`), not proof of
  internet.** Local clock and network access are different things. When you actually
  need to test egress, require an *external source* and forbid the local clock.
- **Never let it fetch URLs, install packages, or call web APIs.** Have it work from
  what is already in the repo, or fetch the data yourself and pass it in the prompt.
- **Network attempts can hang for many minutes.** Observed: a delegation that tried to
  reach the internet ran ~14 minutes without terminating, because Codex retried. If a
  task might touch the network, say "run exactly one command, do not retry, stop
  immediately on failure" — with that instruction failures returned in ~27 s instead.
- This repo's `.cursor/mcp.json` has no bearing on it: sandbox egress is a Codex-side
  setting, not a Cursor one.

## Multi-turn sessions are process-scoped

`codex-reply` only finds a `threadId` **within the same MCP server process**. Verified:
continuing a thread in-process worked (the session was resumed and executed a follow-up
command), while the identical `threadId` from a *different* process returned
`Session not found for thread_id: ...`.

In normal use this is fine — Cursor keeps the MCP server alive, so `codex-reply` works
throughout a session. It matters if you drive Codex through one-shot CLI spawns: there,
each invocation is a new process and continuation is impossible. Persisted sessions can
be resumed with `codex resume` / `codex exec resume`, but that is a separate mechanism
from the MCP `threadId`.

## Measuring cost

Codex calls are **slow and token-heavy** compared to a normal tool call. Measured on
this machine:

- Trivial prompt ("reply with one token"): **~14 s**, ~18.5k input tokens.
- Current time via shell (`Get-Date`): **~37 s**.
- One image generation: **~52 s**, ~11.5k tokens.
- Repository-wide brand audit (28 findings, 19 files): **~105 s**.
- **Worst observed: ~14 minutes** — a network-touching task that retried until killed.
  Bound it with explicit one-shot instructions whenever the network could be involved.

Do not fan out many Codex calls in a loop. Batch the work into one well-specified
prompt, or use it where its independence actually buys something.

## CLI fallback

If the MCP server is unavailable, drive the same agent through the shell:

```bash
codex exec --json -s read-only -C "<dir>" "<prompt>"
```

Useful flags: `-s/--sandbox`, `-C/--cd`, `-m/--model`, `--json` (JSONL events),
`-o/--output-last-message <file>`, `-i/--image <file>`, `--skip-git-repo-check`.

The binary lives inside a versioned editor extension, so it is usually **not** on
`PATH`. Resolve it through the launcher:

```bash
node .cursor/mcp/codex-launcher.cjs exec -s read-only "<prompt>"
```

## Setup in this repo

`.cursor/mcp.json` registers the server as:

```json
"codex": {
  "command": "node",
  "args": ["${workspaceFolder}/.cursor/mcp/codex-launcher.cjs", "mcp-server"]
}
```

Two deliberate choices:

- **`${workspaceFolder}` interpolation**, not a relative path. Cursor documents
  `${workspaceFolder}` as "the folder that contains `.cursor/mcp.json`". Relative
  paths in `args` have an **undocumented** resolution base, so relying on them is a
  guess. Other documented literals: `${env:NAME}`, `${userHome}`,
  `${workspaceFolderBasename}`, `${pathSeparator}`. Supported fields: `command`,
  `args`, `env`, `url`, `headers`.
- **A launcher script**, because the Codex binary lives inside a *versioned*
  extension directory (`openai.chatgpt-<version>-<platform>/bin/...`). Hardcoding the
  version would break the server on every extension update. The launcher re-resolves
  it on each start.

The launcher is deliberately **cwd-independent**: it discovers the binary via the
Windows registry (`InstallLocation` of VS Code / Cursor / Windsurf / Trae), the paths
of running editor processes, and well-known per-user extension roots — never via the
current directory. That matters precisely because Cursor's cwd for the server process
is not documented.

## Verifying the integration

```bash
# Should print the two tools: `codex` and `codex-reply`.
node .cursor/mcp/codex-launcher.cjs mcp-server

# Show which binary was resolved and with what arguments (stderr).
# Run this first whenever the server fails to start.
CODEX_LAUNCHER_DEBUG=1 node .cursor/mcp/codex-launcher.cjs mcp-server
```

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `could not locate the Codex binary` | The Codex/ChatGPT extension is not installed in any editor the launcher can see. Install it, or set `CODEX_BIN` to the full path of the executable. |
| Server starts but no `codex` tool appears | The MCP server list is read at startup — reload the Cursor window and enable the server in Settings → MCP. |
| Worked yesterday, dead today | The extension auto-updated. This is exactly what the launcher exists to absorb — run the debug command above; if it still fails, the extension layout changed and `PLATFORM_SUBPATHS` needs updating. |
| Calls hang for minutes | Expected. Codex runs a full agent loop (measured 14 s–105 s). It is not a fast tool call. |

Override the binary explicitly with `CODEX_BIN` when testing a non-standard install.

## Quick decision table

| Situation | Use Codex? |
|---|---|
| Need an independent review from a different model family | **Yes** — strongest case |
| Bounded mechanical edit in this repo, conventions matter | No — use a subagent; it inherits the rules |
| Need to produce a raster image | **Yes** |
| Large investigation whose detail you don't want in your context | **Yes** |
| You disagree with its first answer | **Yes** — `codex-reply` on the same thread |
| Need it to run many shell commands unattended | Only with an explicitly chosen sandbox |
| **Needs live data from the internet** | **No** — egress is blocked and search is removed; fetch it yourself and pass it in |
