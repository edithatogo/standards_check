const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const http = require('node:http');
const path = require('node:path');
const { once } = require('node:events');
const { after, before, test } = require('node:test');
const app = require('../server');

const corpus = path.resolve(__dirname, '../../markdown/en');
let server;

before(async () => {
  server = app.listen(0, '127.0.0.1');
  await once(server, 'listening');
});

after(async () => {
  if (server) {
    server.closeAllConnections();
    await new Promise((resolve, reject) => {
      server.close(error => error ? reject(error) : resolve());
    });
  }
});

function getJson(route) {
  return new Promise((resolve, reject) => {
    const request = http.get({
      host: '127.0.0.1',
      port: server.address().port,
      path: route,
      agent: false,
    }, response => {
      let body = '';
      response.setEncoding('utf8');
      response.on('data', chunk => { body += chunk; });
      response.once('error', reject);
      response.once('end', () => {
        try {
          resolve({ status: response.statusCode, body: JSON.parse(body) });
        } catch (error) {
          reject(error);
        }
      });
    });
    request.once('error', reject);
  });
}

test('GET /api/checklists lists the complete checked-in English corpus', { timeout: 5000 }, async () => {
  const expected = [];
  for (const [directory, type] of [['archetypes', 'archetype'], ['variants', 'variant']]) {
    const files = await fs.readdir(path.join(corpus, directory));
    for (const filename of files.filter(file => file.endsWith('.md'))) {
      expected.push(`${type}:${filename.slice(0, -3)}`);
    }
  }

  const response = await getJson('/api/checklists');
  assert.equal(response.status, 200);
  assert.ok(expected.length > 0);
  assert.deepEqual(response.body.map(item => `${item.type}:${item.id}`).sort(), expected.sort());
});

test('GET /api/checklists/prisma-2020 serves the real checklist content', { timeout: 5000 }, async () => {
  const response = await getJson('/api/checklists/prisma-2020');
  assert.equal(response.status, 200);
  assert.equal(response.body.id, 'prisma-2020');
  assert.equal(response.body.title, 'PRISMA 2020 Checklist');
  assert.ok(response.body.items.some(item => (
    item.section === 'Title' && item.item.includes('Identify the report as a systematic review.')
  )));
});

test('list entries and individual responses agree for every checklist', { timeout: 10000 }, async () => {
  const listed = await getJson('/api/checklists');
  for (const { type, ...checklist } of listed.body) {
    const response = await getJson(`/api/checklists/${checklist.id}`);
    assert.equal(response.status, 200, checklist.id);
    assert.deepEqual(response.body, checklist);
  }
});

test('unknown identifiers return 404 without fabricating a checklist', async () => {
  const response = await getJson('/api/checklists/not-a-real-checklist');
  assert.equal(response.status, 404);
  assert.deepEqual(response.body, { error: 'Checklist not found' });
});

test('invalid identifiers cannot alias a real checklist or escape the corpus', async () => {
  for (const id of ['..%2Fprisma-2020', 'archetypes%2Fprisma-2020', '..%5Cprisma-2020', 'prisma-2020%00', 'prisma-2020.md']) {
    const response = await getJson(`/api/checklists/${id}`);
    assert.equal(response.status, 400, id);
    assert.deepEqual(response.body, { error: 'Invalid checklist ID' });
  }
});

test('file read failures return 500 without exposing internal details', async t => {
  t.mock.method(fs, 'readFile', async () => { throw new Error('private fixture path'); });
  const logged = t.mock.method(console, 'error', () => {});
  for (const [route, message] of [
    ['/api/checklists', 'Failed to fetch checklists'],
    ['/api/checklists/prisma-2020', 'Failed to fetch checklist'],
  ]) {
    const response = await getJson(route);
    assert.equal(response.status, 500, route);
    assert.deepEqual(response.body, { error: message });
  }
  assert.equal(logged.mock.calls[1].arguments[0], 'Error fetching checklist %s:');
  assert.equal(logged.mock.calls[1].arguments[1], 'prisma-2020');
  assert.ok(logged.mock.calls[1].arguments[2] instanceof Error);
});
