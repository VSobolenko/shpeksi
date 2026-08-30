---
name: "/ship"
id: "ship"
category: "Workflow"
description: "Autonomous orchestrator: propose → implement → verify → review → finish → archive, one entry point"
---

# /ship — autonomous agent harness

Single entry point for end-to-end autonomous work. The user hands over a task
once; this command plans it, implements it (fresh implementer subagent per task
+ task review + fix loop), verifies it with evidence, dispatches the checker
agents, and returns "done + evidence" — stopping for the human only at two
checkpoints (plan approval, integration decision).

This command is glue over already-installed tooling. Do not reimplement the
roles below; invoke them.

## Roles (all already installed)

| Role | Implementation |
|------|----------------|
| Orchestrator (controller) | this command — you, the current agent |
| Contract | OpenSpec specs (`openspec/specs/**`) + `/opsx-propose`, `/opsx-apply`, `/opsx-archive` |
| Writer / implementer | fresh `generalPurpose` subagent per task — `.agents/skills/subagent-driven-development/implementer-prompt.md` |
| Task checker | task reviewer subagent — `.agents/skills/subagent-driven-development/task-reviewer-prompt.md` |
| Final checker (bugs) | `bugbot` subagent (see `/review`) |
| Final checker (security) | `security-review` subagent (see `/review`) |
| Runtime UI checker | `/ui-verify` — change-impact sweep (web: Playwright, native: Maestro) |
| Policy enforcer (secrets) | hook `secret-guard.cjs` — runs automatically on write |
| Policy enforcer (git) | hook `git-guard.cjs` — runs automatically on shell git |
| Evidence gate | `.agents/skills/verification-before-completion/SKILL.md` |
| Integration gate | `.agents/skills/finishing-a-development-branch/SKILL.md` |

## The two human checkpoints

Only these stop the loop. Everything else runs autonomously.

1. **Plan approval** — after proposing, present proposal + specs + tasks and
   STOP until the human says go.
2. **Integration** — after review is green, present merge/PR/keep options and
   STOP for the human's choice.

Committing, merging, pushing, and archiving are integration decisions: do not
perform them silently. (Per-task WIP commits by implementers are fine.)

## Steps

### 0. Classify and plan (OpenSpec)

- If no OpenSpec change exists for this task, run `/opsx-propose <task>`.
  Read `AGENTS.md`, `.cursor/rules/*.mdc`, and existing `openspec/specs/**`
  first, so the plan honors conventions and the fixed contract.
- If a change already exists, reuse it (run `openspec status --change "<name>" --json`).
- Present the plan (proposal + specs + tasks). **CHECKPOINT 1** — stop until "go".
  Do not begin implementation in the same turn.

### 1. Implement (subagent-driven)

Follow `.agents/skills/subagent-driven-development/SKILL.md` over the OpenSpec
`tasks.md`:

- Isolate work first: use `.agents/skills/using-git-worktrees/SKILL.md` (or
  verify the existing workspace). Never implement on main/master without consent.
- Start the ledger at `.superpowers/sdd/<plan>/progress.md` (the recovery map).
- For each task: extract its brief from `tasks.md` + its spec, dispatch ONE fresh
  implementer subagent (never parallel), then ONE task reviewer. Run the fix loop
  (≤5 rounds) on spec/quality failures. Ledger every completion and every ruling.
- Do NOT pause between tasks to check in. Continuous execution.
- Use the least-powerful model that fits each role (mechanical task → cheap;
  integration/judgment → standard; final review → most capable). Specify the
  model explicitly on every dispatch.

### 2. Verify (evidence)

Before any "done" claim, run the `.agents/skills/verification-before-completion/SKILL.md`
gates and capture real output (pass/fail + key line):

- backend changed → `python -m pytest -q` and `python -m compileall -q app tests` (from `backend/`)
- admin changed → `npm run build` (from `Admin Dashboard/`)
- customer changed → `npx expo export` (from `CustomerApp/`)
- spec/planning changed → `openspec validate --strict "<change>"`

### 3. Runtime UI verify (change-impact sweep)

Run `/ui-verify`. It launches the target and drives the runtime over everything
the change could have touched (blast radius, not a fixed list), catching blank
screens and dead navigation that build + static review both miss: Playwright for
the Admin web app, Maestro for the native CustomerApp. Failures enter the same
fix loop as code-review blockers (resume the implementer → scoped re-review →
re-run `/ui-verify` on the affected surface).

### 4. Review (checkers)

Dispatch `/review` (this launches `bugbot` + `security-review`). If it reports
CHANGES REQUIRED with blockers, run the fix loop: hand the findings back to the
implementer, then a scoped re-review — bounded (≤5 rounds). Adjudicate residuals
per `subagent-driven-development`'s breaker and ledger every ruling.

### 5. Finish (integration)

Run `.agents/skills/finishing-a-development-branch/SKILL.md`: re-run the test
suite, then **CHECKPOINT 2** — present exactly the merge/PR/keep options and wait
for the human's choice. Execute the choice; do not merge or push without it.

### 6. Archive

After integration completes, run `/opsx-archive` to sync the change's delta specs
into `openspec/specs/` and close the change.

## Output

```
## /ship complete — <task>

**Change:** <change-name>
**Plan:** <proposal path>
**Implementation:** N tasks, commits <base>..<head>

### Verification (evidence)
- pytest: <pass/fail + line>
- build/export: <pass/fail + line>
- openspec validate: <pass/fail + line>

### Review
- bugbot: <findings count>
- security-review: <findings count>
- ui-verify: <screens passed / failed>

### Rulings I made
- <each ruling + what it costs if wrong>

### Integration
<merge/PR/keep — pending your decision at Checkpoint 2>
```

## Guardrails

- Only the two checkpoints stop the loop; do not stall for anything else.
- Never commit/merge/push/archive without the corresponding checkpoint.
- The ledger is the recovery map — update it in the same message as other
  bookkeeping; trust it over recollection after context loss.
- Never let an implementer spawn its own reviewer — review comes from you.
- Never fix findings yourself in the controller session; resume the implementer.
- Evidence before "done", always (no "should pass", no trusting agent success reports).
- Preserve the GraphQL contract and pickup-only model (see AGENTS.md); never
  commit secrets (the `secret-guard` hook is the backstop, not a license to relax).
