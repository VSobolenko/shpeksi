#!/usr/bin/env node

// setup-mcp.mjs — verify the project's MCP servers (`.cursor/mcp.json`) can be
// resolved and installed, and print what each developer still has to do
// manually (authentication, secrets). Cross-platform: Node is the only prereq.
//
// Usage: node scripts/setup-mcp.mjs

import { execFile } from 'node:child_process'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const here = dirname(fileURLToPath(import.meta.url))
const root = join(here, '..')
const mcpPath = join(root, '.cursor', 'mcp.json')

// Remote servers can't be "resolved" via npx; they need their own account/OAuth.
const REMOTE_NOTES = {
  'https://mcp.expo.dev/mcp': 'Expo remote server — needs OAuth (Expo account)'
}

// Credential-bearing servers: each developer provides their own secrets.
const MANUAL_NOTES = {
  firebase: 'needs `firebase login` + a Firebase project',
  mongodb: 'needs MDB_MCP_CONNECTION_STRING pointing at a reachable Mongo'
}

function runNpx(pkg) {
  return new Promise((resolve) => {
    execFile('npx', ['-y', pkg, '--help'], { timeout: 180000 }, (err, stdout, stderr) => {
      if (err && err.killed) {
        resolve({ ok: false, output: 'timed out after 180s' })
        return
      }
      const out = (stdout || '') + (stderr || '')
      const failed = /could not find|not found|E404|ECONNREFUSED|ENOTFOUND|Cannot find module/i.test(out)
      const firstLine = out.trim().split(/\r?\n/)[0]
      resolve({ ok: !failed, output: firstLine || (err && err.message) || '' })
    })
  })
}

async function main() {
  let raw
  try {
    raw = readFileSync(mcpPath, 'utf8')
  } catch (e) {
    console.error('[FAIL] .cursor/mcp.json not found at', mcpPath)
    process.exit(1)
  }

  let cfg
  try {
    cfg = JSON.parse(raw)
  } catch (e) {
    console.error('[FAIL] .cursor/mcp.json is not valid JSON:', e.message)
    process.exit(1)
  }

  const servers = cfg.mcpServers || {}
  const names = Object.keys(servers)
  console.log('Checking', names.length, 'MCP server(s) from .cursor/mcp.json ...\n')

  const needsManual = []

  for (const name of names) {
    const s = servers[name]
    const isRemote = typeof s.url === 'string' && !s.command
    if (isRemote) {
      const note = REMOTE_NOTES[s.url] || 'remote server — may need OAuth/account'
      console.log('[SETUP]', name + ':', note)
      needsManual.push(name + ': ' + note)
      continue
    }
    if (s.command === 'npx' && Array.isArray(s.args) && s.args.length) {
      const pkg = s.args.find((a) => !a.startsWith('-')) || s.args[0]
      process.stdout.write('[  .. ] ' + name + ': resolving ' + pkg + ' ...')
      const r = await runNpx(pkg)
      console.log(r.ok ? ' [OK]' : ' [FAIL]')
      if (!r.ok && r.output) console.log('         ' + r.output)
      if (MANUAL_NOTES[name]) needsManual.push(name + ': ' + MANUAL_NOTES[name])
      continue
    }
    console.log('[SKIP]', name + ': unsupported command shape')
  }

  if (needsManual.length) {
    console.log('\nStill needs per-developer setup (expected — do NOT commit these):')
    for (const n of needsManual) console.log('  - ' + n)
  }

  console.log('\nDone. Then in Cursor: Settings > MCP > enable the servers, and Reload Window.')
  console.log('The config itself is committed — teammates get it on clone; packages install via `npx -y`.')
}

main()
