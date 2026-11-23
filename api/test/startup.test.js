const assert = require('node:assert/strict');
const { spawn } = require('node:child_process');
const { once } = require('node:events');
const fs = require('node:fs/promises');
const os = require('node:os');
const path = require('node:path');
const { test } = require('node:test');

test('the documented CLI starts the production API on port 3000', { timeout: 5000 }, async t => {
  const directory = await fs.mkdtemp(path.join(os.tmpdir(), 'standardflow-cli-test-'));
  t.after(() => fs.rm(directory, { recursive: true, force: true }));
  const shutdown = path.join(directory, 'shutdown.cjs');
  // Preserve coverage from the actual CLI process before its owned shutdown.
  await fs.writeFile(shutdown, "process.on('SIGTERM', () => { require('node:v8').takeCoverage(); process.exit(0); });\n");
  const child = spawn(process.execPath, ['--require', shutdown, path.resolve(__dirname, '../server.js')], {
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  const stopped = once(child, 'exit');
  t.after(async () => {
    if (child.exitCode === null) child.kill('SIGTERM');
    await stopped;
  });
  let errors = '';
  child.stderr.setEncoding('utf8');
  child.stderr.on('data', chunk => { errors += chunk; });
  await new Promise((resolve, reject) => {
    let output = '';
    child.once('error', reject);
    child.once('exit', code => reject(new Error(`CLI exited ${code}: ${errors}`)));
    child.stdout.setEncoding('utf8');
    child.stdout.on('data', chunk => {
      output += chunk;
      if (output.includes('Checklist API server running at http://localhost:3000')) resolve();
    });
  });
  const response = await fetch('http://127.0.0.1:3000/api/checklists/prisma-2020');
  assert.equal(response.status, 200);
  assert.equal((await response.json()).id, 'prisma-2020');
  assert.match(response.headers.get('ratelimit'), /\br=99\b/);
  assert.equal(errors, '');
});
