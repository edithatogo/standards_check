const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const http = require('node:http');
const path = require('node:path');
const { once } = require('node:events');
const { after, before, test } = require('node:test');
const express = require('express');

const corpus = path.resolve(__dirname, '../../markdown/en');
let server;

before(async () => {
  // Exercise the production app and corpus, changing only its listener to an
  // ephemeral loopback port so parallel tests do not compete for port 3000.
  const listen = express.application.listen;
  express.application.listen = function () {
    server = listen.call(this, 0, '127.0.0.1');
    return server;
  };
  try {
    require('../server');
  } finally {
    express.application.listen = listen;
  }
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
