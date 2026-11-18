'use strict';

const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const test = require('node:test');
const express = require('express');
const { match, pathToRegexp } = require('path-to-regexp');

// Dependabot #4 / GHSA-j3q9-mxjg-w52f.
test('rejects routes with excessive optional-group expansion', () => {
  assert.throws(
    () => pathToRegexp(Array(10).fill('{/x}').join('')),
    /Too many path combinations/,
  );
});

test('ordinary optional groups and the existing checklist routes remain valid', () => {
  const collection = match('/api/checklists');
  const detail = match('/api/checklists/:id');
  assert.ok(collection('/api/checklists'));
  assert.ok(collection('/API/CHECKLISTS/'));
  assert.equal(collection('/api/checklists/prisma-2020'), false);
  assert.equal(detail('/api/checklists/prisma-2020').params.id, 'prisma-2020');
  assert.equal(detail('/api/checklists/a%20b').params.id, 'a b');
  assert.equal(detail('/api/checklists'), false);
  assert.equal(detail('/api/checklists/a/b'), false);
  assert.throws(() => detail('/api/checklists/%E0%A4%A'), URIError);
  const optional = match('/api/checklists{/:id}');
  assert.ok(optional('/api/checklists'));
  assert.equal(optional('/api/checklists/prisma-2020').params.id, 'prisma-2020');
});

// Dependabot #5 / GHSA-27v5-c462-wpq7. A subprocess bounds any regression.
test('multiple-wildcard near misses finish without excessive backtracking', () => {
  const child = spawnSync(process.execPath, ['-e', `
    const assert = require('node:assert/strict');
    const { match } = require(${JSON.stringify(require.resolve('path-to-regexp'))});
    const route = match('/*foo-*bar-:baz');
    assert.ok(route('/alpha-beta-gamma'));
    assert.equal(route('/' + '-'.repeat(20000) + '/x'), false);
  `], { encoding: 'utf8', timeout: 5000 });
  assert.ifError(child.error);
  assert.equal(child.status, 0, child.stderr);
});

test('Express and its router serve the existing route shapes', { timeout: 5000 }, async (t) => {
  const app = express();
  app.get('/api/checklists', (_req, res) => res.json(['prisma-2020']));
  app.get('/api/checklists/:id', (req, res) => res.json({ id: req.params.id }));
  const server = app.listen(0, '127.0.0.1');
  t.after(() => new Promise((resolve, reject) => {
    server.close((error) => error ? reject(error) : resolve());
    server.closeAllConnections();
  }));
  await new Promise((resolve, reject) => {
    server.once('listening', resolve);
    server.once('error', reject);
  });
  const base = `http://127.0.0.1:${server.address().port}`;
  const collection = await fetch(`${base}/api/checklists`);
  assert.equal(collection.status, 200);
  assert.deepEqual(await collection.json(), ['prisma-2020']);
  const detail = await fetch(`${base}/api/checklists/prisma-2020`);
  assert.equal(detail.status, 200);
  assert.deepEqual(await detail.json(), { id: 'prisma-2020' });
  assert.equal((await fetch(`${base}/api/checklists/a/b`)).status, 404);
});
