// Blocks file writes that contain known hardcoded secret patterns.
const fs = require('fs')

const SECRET_PATTERNS = [
  { name: 'Firebase/Google API key', regex: /AIza[0-9A-Za-z_-]{35}/ },
  { name: 'Stripe live secret key', regex: /sk_live_[0-9a-zA-Z]{16,}/ },
  { name: 'Stripe live publishable key', regex: /pk_live_[0-9a-zA-Z]{16,}/ },
  { name: 'Stripe restricted key', regex: /rk_live_[0-9a-zA-Z]{16,}/ },
  { name: 'AWS access key', regex: /AKIA[0-9A-Z]{16}/ },
  { name: 'GitHub token', regex: /ghp_[0-9A-Za-z]{36}/ },
  { name: 'GitHub fine-grained token', regex: /github_pat_[0-9A-Za-z_]{22,}/ },
  { name: 'Private key block', regex: /-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----/ }
]

function findSecrets(text) {
  if (!text) return []
  const found = []
  for (const p of SECRET_PATTERNS) {
    if (p.regex.test(text)) found.push(p.name)
  }
  return found
}

let input = ''
try {
  input = fs.readFileSync(0, 'utf8')
} catch (e) {}

let toolName = ''
let candidates = []

try {
  const data = JSON.parse(input)
  toolName = data.tool_name || ''
  const ti = data.tool_input || {}
  candidates = [ti.contents, ti.content, ti.new_string].filter((s) => typeof s === 'string')
} catch (e) {
  candidates = [input]
}

// Only guard write/edit tools; allow everything else.
if (!/^(Write|StrReplace|EditNotebook)$/.test(toolName)) {
  console.log(JSON.stringify({ permission: 'allow' }))
  process.exit(0)
}

for (const text of candidates) {
  const found = findSecrets(text)
  if (found.length) {
    console.log(
      JSON.stringify({
        permission: 'deny',
        user_message:
          'Blocked writing a hardcoded secret: ' +
          found.join(', ') +
          '. Move the value to .env instead.',
        agent_message: 'secret-guard blocked a file edit containing a hardcoded secret.'
      })
    )
    process.exit(0)
  }
}

console.log(JSON.stringify({ permission: 'allow' }))
process.exit(0)
