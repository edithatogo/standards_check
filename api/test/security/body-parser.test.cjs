'use strict';

const assert = require('node:assert/strict');
const test = require('node:test');
const { deflateSync, gzipSync } = require('node:zlib');
const bodyParser = require('body-parser');
const express = require('express');

async function endpoint(t, parser) {
  const app = express();
  app.use(parser);
  app.post('/', (req, res) => res.json(req.body));
  app.use((error, _req, res, _next) => {
    res.status(error.status || 500).json({ type: error.type });
  });
  const server = app.listen(0, '127.0.0.1');
  t.after(() => new Promise((resolve, reject) => {
    server.close((error) => error ? reject(error) : resolve());
    server.closeAllConnections();
  }));
  await new Promise((resolve, reject) => {
    server.once('listening', resolve);
    server.once('error', reject);
  });
  const url = `http://127.0.0.1:${server.address().port}/`;
  return (body, headers = {}) => fetch(url, {
    method: 'POST',
    headers: { 'content-type': 'application/json', ...headers },
    body,
    signal: AbortSignal.timeout(2000),
  });
}

test('Express JSON parsing preserves valid input and rejects malformed JSON', { timeout: 5000 }, async (t) => {
  const post = await endpoint(t, express.json());
  const valid = await post('{"id":"prisma-2020","items":[1,2]}');
  assert.equal(valid.status, 200);
  assert.deepEqual(await valid.json(), { id: 'prisma-2020', items: [1, 2] });
  const malformed = await post('{"id":');
  assert.equal(malformed.status, 400);
  assert.equal((await malformed.json()).type, 'entity.parse.failed');
});

test('default and explicit JSON limits reject oversized bodies with 413', { timeout: 5000 }, async (t) => {
  const defaultPost = await endpoint(t, bodyParser.json());
  const oversized = await defaultPost(JSON.stringify({ value: 'x'.repeat(100 * 1024) }));
  assert.equal(oversized.status, 413);
  assert.equal((await oversized.json()).type, 'entity.too.large');

  const limitedPost = await endpoint(t, bodyParser.json({ limit: 32 }));
  const valid = await limitedPost('{"value":"ok"}');
  assert.equal(valid.status, 200);
  assert.deepEqual(await valid.json(), { value: 'ok' });
  const tooLarge = await limitedPost(JSON.stringify({ value: 'x'.repeat(32) }));
  assert.equal(tooLarge.status, 413);
  assert.equal((await tooLarge.json()).type, 'entity.too.large');
});

// Exercise ordinary decompression without reproducing process-crash payloads.
test('valid gzip and deflate JSON retain decompression compatibility', { timeout: 5000 }, async (t) => {
  const post = await endpoint(t, express.json());
  const expected = { id: 'prisma-2020', items: ['ordinary fixture'] };
  const bytes = Buffer.from(JSON.stringify(expected));
  for (const [encoding, compress] of [['gzip', gzipSync], ['deflate', deflateSync]]) {
    const response = await post(compress(bytes), { 'content-encoding': encoding });
    assert.equal(response.status, 200, encoding);
    assert.deepEqual(await response.json(), expected, encoding);
  }
});

test('unsupported charsets return 415 before verify, while valid JSON still verifies', { timeout: 5000 }, async (t) => {
  let verifications = 0;
  const post = await endpoint(t, bodyParser.json({ verify: () => { verifications += 1; } }));
  const unsupported = await post(gzipSync('{"value":"ok"}'), {
    'content-type': 'application/json; charset=utf-unsupported',
    'content-encoding': 'gzip',
  });
  assert.equal(unsupported.status, 415);
  assert.equal((await unsupported.json()).type, 'charset.unsupported');
  assert.equal(verifications, 0);
  const valid = await post('{"value":"ok"}');
  assert.equal(valid.status, 200);
  assert.deepEqual(await valid.json(), { value: 'ok' });
  assert.equal(verifications, 1);
});

test('parser constructors reject invalid limits instead of removing the size cap', () => {
  for (const name of ['json', 'raw', 'text', 'urlencoded']) {
    for (const limit of ['', 'invalid', NaN, true, {}]) {
      assert.throws(
        () => bodyParser[name]({ extended: false, limit }),
        TypeError,
        `${name} accepted invalid limit ${String(limit)}`,
      );
    }
  }
});

test('parser constructors preserve defaults and valid numeric or string limits', () => {
  for (const name of ['json', 'raw', 'text', 'urlencoded']) {
    assert.equal(typeof bodyParser[name](), 'function', name);
    for (const limit of [undefined, null, 1024, '1kb']) {
      assert.equal(typeof bodyParser[name]({ extended: false, limit }), 'function', name);
    }
  }
});

for (const extended of [false, true]) {
  test(`URLencoded parameter limit accepts 10 and rejects 11 (extended=${extended})`, { timeout: 5000 }, async (t) => {
    const post = await endpoint(t, bodyParser.urlencoded({ extended, parameterLimit: 10 }));
    const entries = Array.from({ length: 10 }, (_, index) => [`key${index}`, `value${index}`]);
    const headers = { 'content-type': 'application/x-www-form-urlencoded' };
    const valid = await post(new URLSearchParams(entries).toString(), headers);
    assert.equal(valid.status, 200);
    assert.deepEqual(await valid.json(), Object.fromEntries(entries));
    const excessive = await post(new URLSearchParams([...entries, ['extra', 'value']]).toString(), headers);
    assert.equal(excessive.status, 413);
    assert.equal((await excessive.json()).type, 'parameters.too.many');
  });
}
