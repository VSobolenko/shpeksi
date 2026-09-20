#!/usr/bin/env node
/**
 * Objective verification gate for agent-produced changes.
 *
 * Purpose: after Codex (or any agent) writes code, verify it with the repo's own
 * tools instead of trusting the agent's self-report. Checks only the files that
 * actually changed, so pre-existing repo debt does not produce false failures.
 *
 * Usage:
 *   node scripts/verify-changes.mjs                  # uncommitted changes
 *   node scripts/verify-changes.mjs --base <ref>     # changes vs a git ref
 *   node scripts/verify-changes.mjs --build          # also run module builds (slow)
 *
 * Exit codes:
 *   0 = every check that could run passed
 *   1 = a check failed, or could not run (BLOCKED), or the scope was empty
 *
 * A module with no available check is reported UNVERIFIED. That does not fail the
 * run by itself, but it is printed prominently: it means the diff must be
 * inspected by hand.
 */

import { spawnSync } from 'node:child_process'
import { existsSync } from 'node:fs'
import path from 'node:path'
import process from 'node:process'

const ROOT = process.cwd()
const ARGV = process.argv.slice(2)
const baseIdx = ARGV.indexOf('--base')
const BASE_REF = baseIdx !== -1 ? ARGV[baseIdx + 1] : null
const RUN_BUILD = ARGV.includes('--build')

/**
 * Module definitions. `lint` is null where the module has no lint configuration
 * (backend has no linter in pyproject.toml; Website has no eslint config at all).
 * Being explicit about that is the point — a silent skip would read as a pass.
 */
const MODULES = [
  {
    name: 'backend',
    match: (f) => f.startsWith('backend/'),
    lint: null,
    compile: (relFiles) => {
      const py = relFiles.filter((f) => f.endsWith('.py')).map((f) => path.relative('backend', f))
      if (py.length === 0) return null
      return run('python', ['-m', 'compileall', '-q', ...py], 'backend')
    },
    build: null
  },
  {
    name: 'Admin Dashboard',
    match: (f) => f.startsWith('Admin Dashboard/'),
    lint: { exts: ['.js', '.jsx'], bin: 'node_modules/eslint/bin/eslint.js' },
    compile: null,
    build: 'build'
  },
  {
    name: 'CustomerApp',
    match: (f) => f.startsWith('CustomerApp/'),
    lint: { exts: ['.js', '.jsx'], bin: 'node_modules/eslint/bin/eslint.js' },
    compile: null,
    build: null
  },
  {
    name: 'Website',
    match: (f) => f.startsWith('Website/'),
    lint: null,
    compile: null,
    build: 'build'
  }
]

/**
 * Run a command in a module directory.
 * Shell is used only for npm, which is a .cmd shim on Windows. All other tools
 * are launched directly, so paths containing spaces are never word-split.
 */
function run(cmd, cmdArgs, cwdModule, { useShell = false } = {}) {
  const res = spawnSync(cmd, cmdArgs, {
    cwd: path.join(ROOT, cwdModule),
    encoding: 'utf8',
    shell: useShell
  })
  const out = ((res.stdout || '') + (res.stderr || '')).trim()
  if (res.error) {
    return { ok: false, missing: res.error.code === 'ENOENT', out: String(res.error.message) }
  }
  return { ok: res.status === 0, status: res.status, out }
}

function gitLines(gitArgs, { trim = true } = {}) {
  const res = spawnSync('git', gitArgs, { cwd: ROOT, encoding: 'utf8' })
  if (res.status !== 0) {
    console.error('verify-changes: git failed:\n' + (res.stderr || ''))
    process.exit(1)
  }
  const lines = res.stdout.split('\n').filter(Boolean)
  return trim ? lines.map((s) => s.trim()) : lines
}

/** Repo-relative paths of changed files. */
function changedFiles() {
  if (BASE_REF) {
    // `diff --name-only` emits one bare path per line.
    return gitLines(['diff', '--name-only', '--diff-filter=ACMR', `${BASE_REF}...HEAD`])
  }

  // `status --porcelain` emits "XY PATH": two status columns, then a space.
  // The leading space is significant (e.g. " M path"), so these lines must NOT
  // be trimmed before slicing off the status — doing so would eat the first
  // character of the path itself.
  return gitLines(['status', '--porcelain'], { trim: false })
    .map((line) => {
      let p = line.slice(3)
      const arrow = p.indexOf(' -> ')
      if (arrow !== -1) p = p.slice(arrow + 4)
      return p.replace(/^"|"$/g, '').trim()
    })
    .filter(Boolean)
}

const indent = (s, pad = '        ') =>
  !s ? pad + '(no output)' : s.split('\n').map((l) => pad + l).join('\n')

const tail = (s, n) => s.split('\n').slice(-n).join('\n')

// --- Collect scope -----------------------------------------------------------

const tracked = [...new Set(changedFiles())]
const files = tracked.filter((f) => /\.(js|jsx|mjs|cjs|py|json|md|css|scss)$/.test(f))

console.log('## Change verification\n')
console.log(`Scope: ${BASE_REF ? `changes vs ${BASE_REF}` : 'uncommitted changes'} — ${tracked.length} file(s)`)

if (tracked.length === 0) {
  console.log('\nNothing changed. Nothing to verify.')
  process.exit(1)
}

let failed = false
let blocked = false
const unverified = []
const touched = []

// --- Per-module checks -------------------------------------------------------

for (const mod of MODULES) {
  const matched = files.filter(mod.match)
  if (matched.length === 0) continue

  // Deleted files cannot carry style or syntax violations, and passing a
  // non-existent path to eslint/compileall makes the tool abort the whole run.
  const present = matched.filter((f) => existsSync(path.join(ROOT, f)))
  const deleted = matched.length - present.length
  const rel = present.map((f) => path.relative(mod.name, f))

  touched.push(mod.name)

  console.log(
    `\n### ${mod.name} (${rel.length} file${rel.length === 1 ? '' : 's'}` +
      `${deleted > 0 ? `, ${deleted} deleted` : ''})`
  )

  if (rel.length === 0) {
    console.log('  SKIP        every changed file was deleted — nothing to check')
    continue
  }

  // Lint — the objective style gate (catches semicolons, quotes, indent, spacing).
  if (!mod.lint) {
    console.log('  UNVERIFIED  lint — no lint configuration in this module')
    unverified.push(mod.name)
  } else {
    const targets = rel.filter((f) => mod.lint.exts.some((e) => f.endsWith(e)))
    if (targets.length > 0) {
      const bin = path.join(ROOT, mod.name, mod.lint.bin)
      if (!existsSync(bin)) {
        console.log(`  BLOCKED     lint — eslint is not installed in "${mod.name}"`)
        console.log(`              fix: cd "${mod.name}" && npm install`)
        console.log('              Not a pass. Nothing about this diff is style-verified.')
        blocked = true
      } else {
        const r = run('node', [mod.lint.bin, ...targets], mod.name)
        if (r.ok) {
          console.log(`  PASS        lint — clean (${targets.length} file(s))`)
        } else {
          console.log('  FAIL        lint — violations:')
          console.log(indent(r.out))
          failed = true
        }
      }
    }
  }

  if (mod.compile) {
    const r = mod.compile(present)
    if (r) {
      if (r.ok) console.log('  PASS        compile — syntax OK')
      else if (r.missing) {
        console.log('  BLOCKED     compile — python not found on PATH')
        blocked = true
      } else {
        console.log('  FAIL        compile — syntax errors:')
        console.log(indent(r.out))
        failed = true
      }
    }
  }

  if (RUN_BUILD && mod.build) {
    const r = run('npm', ['run', mod.build], mod.name, { useShell: true })
    if (r.ok) console.log(`  PASS        build (npm run ${mod.build})`)
    else {
      console.log(`  FAIL        build (npm run ${mod.build}):`)
      console.log(indent(tail(r.out, 25)))
      failed = true
    }
  }
}

// --- Verdict -----------------------------------------------------------------

console.log('\n---')
console.log(`Modules touched: ${touched.join(', ') || 'none'}`)
if (unverified.length > 0) {
  console.log(
    `No objective style check: ${[...new Set(unverified)].join(', ')} — inspect these diffs by hand.`
  )
}

if (failed) {
  console.log('\nVERDICT: FAIL — fix the violations above before accepting this work.')
  process.exit(1)
}
if (blocked) {
  console.log('\nVERDICT: BLOCKED — a check could not run. Install the tooling and re-run.')
  console.log('Do not accept the work on trust.')
  process.exit(1)
}
console.log('\nVERDICT: PASS — every available objective check is green.')
