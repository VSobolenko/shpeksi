---
name: "/review"
id: "review"
category: "Review"
description: "Dispatch reviewer subagents (bugbot + security-review) as a verification gate"
---

Run the writer/reviewer gate: hand the current work to independent reviewer
subagents, collect their findings, and report a PASS / CHANGES REQUIRED verdict.
The reviewing agent does NOT rewrite code — it verifies and reports.

This is the "second agent" in the harness. Run it after `/opsx-apply` (or after
any significant edit) and before `/opsx-archive` or before telling the user the
work is done.

## Steps

1. **Determine review scope (Diff)**

   Pick one, in order of preference:
   - If the user names an OpenSpec change → `Diff: branch changes` (the change
     work should be on a branch); if it is uncommitted, use
     `Diff: uncommitted changes`.
   - Otherwise default to `Diff: uncommitted changes` (most common mid-session).
   - Confirm by running `git status --short` and `git diff --stat` to see what is
     actually in scope, and report it before dispatching reviewers.

2. **Gather the spec/contract context**

   The reviewer must verify conformance, not style. Read the authoritative specs:
   - `openspec/specs/**/*.md` (the synced main specs — the product contract).
   - If the change is active, `openspec status --change "<name>" --json` and the
     change's `proposal.md` / `specs/**` / `tasks.md`.
   - `AGENTS.md` and the `.cursor/rules/*.mdc` (conventions + security rules).
   Note any fixed contracts the diff must not break (GraphQL operation/field
   names, snake_case, `subscriptions-transport-ws` protocol, self-pickup-only
   model, no third-party brand/delivery/rider remnants).

3. **Run lightweight verification as evidence (do not claim without output)**

   Run the relevant checks and capture real output:
   - **Any code change → `node scripts/verify-changes.mjs`** first. It is fast
     (seconds) and lints only the changed files, so it isolates this diff from
     pre-existing repo debt. It fails on violations *and* on checks that could not
     run. Note its coverage: `CustomerApp` and `Admin Dashboard` are style-checked;
     `backend` and `Website` have no linter and are reported UNVERIFIED — those
     diffs need reading, not just a green exit code.
   - Backend changed → `python -m pytest -q` and `python -m compileall -q app tests`
     (from `backend/`).
   - Admin changed → `npm run build` (from `Admin Dashboard/`).
   - CustomerApp changed → `npx expo export` (from `CustomerApp/`).
   - Any spec/planning change → `openspec validate --strict "<change-name>"`.
   Report each result (pass/fail + key line), never assume.

4. **Dispatch the reviewer subagents (in parallel, one message)**

   Launch exactly one `bugbot` and exactly one `security-review` subagent,
   both with `run_in_background: false`, using these exact contracts:

   - **bugbot** — description exactly `Bugbot`, prompt:
     ```
     Full Repository Path: <repo root>
     Diff: <uncommitted changes | branch changes>
     Change Description: <one line on what this work does>
     Custom Instructions: Verify the diff conforms to the OpenSpec specs in
     openspec/specs/ (GraphQL contract, self-pickup-only model, "Pikupo" naming). Flag any spec drift, broken contract, or missing evidence, not
     just style. Include file paths and line numbers for each finding.
     ```
   - **security-review** — description exactly `Security Review`, prompt:
     ```
     Full Repository Path: <repo root>
     Diff: <uncommitted changes | branch changes>
     Custom Instructions: Pay special attention to the security-secrets rules
     (no hardcoded keys, .env only, google-services*.json git-ignored), input
     validation, and any new endpoint/credential handling.
     ```

   Launch both in a single message so they run in parallel.

4b. **Dispatch the independent reviewer (Codex)**

   Also run **Codex** as a third reviewer. `bugbot` and `security-review` inherit
   this session's model; Codex runs a different model family, so its blind spots
   are uncorrelated with theirs. That independence is the whole value — do not
   skip it, and do not replace the other two with it.

   Call the `codex` MCP tool (see the `codex-second-agent` skill) with
   `sandbox: "read-only"` so it cannot modify the repo, and `cwd` set to the repo
   root. It does not know this repo's rules, so name them in the prompt:

   ```
   codex({
     sandbox: "read-only",
     cwd: "<repo root>",
     prompt: `You are an independent code reviewer. Read AGENTS.md,
     .cursor/rules/project-conventions.mdc, and openspec/specs/** first.
     Review the <uncommitted changes | branch changes> using git diff and git status.
     Report ONLY blocking findings as file:line — what is wrong and why it matters.
     Check for: GraphQL contract drift (operation/field names, snake_case, _id),
     violations of the self-pickup-only model (no rider/delivery code), leftover
     "Forkly" branding, hardcoded secrets, and spec drift.
     Do not modify any files. If nothing is blocking, say so plainly.`
   })
   ```

   Record its `threadId`: if a finding is unclear, push back with `codex-reply`
   instead of accepting it blindly.

5. **Triage and verify (technical rigor, not performative agreement)**

   Read both reports. For each finding, decide whether it is:
   - **Blocking** — real spec drift, broken contract, a secret, a failing check.
   - **Non-blocking / false positive** — e.g. a pre-existing issue outside the
     diff, or a suggestion that conflicts with a fixed convention.
   Do NOT blindly accept every suggestion. If a reviewer's claim conflicts with
   the spec or a repo convention, note the conflict and why it is not applied.

6. **Report a verdict — the gate**

   Output one of:
   - **PASS** — no blocking findings, all verification checks green. State that
     the work is ready for `/opsx-archive` (or to be shown as done).
   - **CHANGES REQUIRED** — list blocking findings (file + line + what to fix),
     grouped by reviewer. Do NOT fix them here; hand the list back to the writer
     (the user can re-run `/opsx-apply` or ask you to fix, then re-run `/review`).

   Do not mark anything complete, archive, or claim success on the basis of this
   command alone — `/review` only produces a verdict and evidence.

## Output

```
## Review

**Scope:** <uncommitted changes | branch changes> (<N> files)
**Spec basis:** <list of specs consulted>

### Verification
- pytest: <pass/fail + line>
- build/export: <pass/fail + line>
- openspec validate: <pass/fail + line>

### Findings
- [blocking|non-blocking] <file:line> — <description> (reviewer)

### Verdict
PASS / CHANGES REQUIRED
```

## Guardrails

- Never rewrite code in this workflow; report only.
- Always capture real command output before asserting a check passed.
- Always launch both reviewers; do not skip one unless the user explicitly says so.
- Always run the Codex reviewer too — its value is model diversity, so an
  all-same-model review is a weaker gate.
- Never give the Codex reviewer write access: `sandbox: "read-only"` only.
- Do not treat a reviewer's claim as true without checking it against the spec.
- Keep the diff scope explicit — reviewers must know what is in and out of scope.
