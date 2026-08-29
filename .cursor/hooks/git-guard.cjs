// Guards against destructive/irreversible git commands.
const fs = require('fs')

let input = ''
try {
  input = fs.readFileSync(0, 'utf8')
} catch (e) {}

let command = ''
try {
  command = JSON.parse(input).command || ''
} catch (e) {
  command = input
}

const c = command.trim()
const isGit = /\bgit\b/.test(c)

// Block force-push to protected branches.
if (
  isGit &&
  /\bpush\b/.test(c) &&
  /(--force|--force-with-lease|-f\b)/.test(c) &&
  /(main|master)/.test(c)
) {
  console.log(
    JSON.stringify({
      permission: 'deny',
      user_message:
        'Blocked a force push to main/master. Force pushing to protected branches is not allowed.',
      agent_message: 'git-guard blocked a force push to a protected branch.'
    })
  )
  process.exit(0)
}

// Block destructive history/working-tree commands.
if (isGit && /\b(reset --hard|clean -fdx|clean -fd)\b/.test(c)) {
  console.log(
    JSON.stringify({
      permission: 'deny',
      user_message:
        'Blocked a destructive git command (reset --hard / clean). If you are sure, ask the user to run it manually.',
      agent_message: 'git-guard blocked a destructive git command.'
    })
  )
  process.exit(0)
}

console.log(JSON.stringify({ permission: 'allow' }))
process.exit(0)
