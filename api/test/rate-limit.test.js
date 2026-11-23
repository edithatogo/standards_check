const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const http = require('node:http');
const { once } = require('node:events');
const { test } = require('node:test');
const app = require('../server');

function request(server, route, headers = {}, body = '') {
  return new Promise((resolve, reject) => {
    const req = http.request({
      host: '127.0.0.1',
      port: server.address().port,
      path: route,
      method: 'GET',
      headers: { ...headers, 'Content-Length': Buffer.byteLength(body) },
      agent: false,
    }, response => {
      let content = '';
      response.setEncoding('utf8');
      response.on('data', chunk => { content += chunk; });
      response.once('error', reject);
      response.once('end', () => {
        try {
          resolve({ status: response.statusCode, headers: response.headers, body: JSON.parse(content) });
        } catch (error) {
          reject(error);
        }
      });
    });
    req.once('error', reject);
    req.end(body);
  });
}

test('both checklist routes share a bounded budget before parsing or I/O, then recover after expiry', { timeout: 10000 }, async t => {
  t.mock.timers.enable({ apis: ['Date'], now: Date.now() });
  const server = app.listen(0, '127.0.0.1');
  await once(server, 'listening');
  t.after(async () => {
    server.closeAllConnections();
    await new Promise((resolve, reject) => server.close(error => error ? reject(error) : resolve()));
  });
  assert.equal(app.get('trust proxy'), false);

  const first = await request(server, '/api/checklists/prisma-2020', { Origin: 'http://localhost:3000' });
  assert.equal(first.status, 200);
  assert.equal(typeof first.headers.ratelimit, 'string');
  assert.match(first.headers.ratelimit, /\br=99\b/);
  assert.match(first.headers['ratelimit-policy'], /\bq=100\b/);
  assert.match(first.headers['ratelimit-policy'], /\bw=60\b/);
  assert.equal(first.headers['retry-after'], undefined);
  assert.equal(first.headers['x-ratelimit-limit'], undefined);
  assert.deepEqual(first.headers['access-control-expose-headers'].split(',').sort(), ['RateLimit', 'RateLimit-Policy', 'Retry-After']);
  const listed = await request(server, '/api/checklists');
  assert.equal(listed.status, 200);
  assert.match(listed.headers.ratelimit, /\br=98\b/);

  for (let count = 3; count <= 100; count += 1) {
    const response = await request(server, '/api/checklists/not-a-real-checklist', {
      'X-Forwarded-For': `192.0.2.${count}`,
    });
    assert.equal(response.status, 404);
    assert.match(response.headers.ratelimit, new RegExp(`\\br=${100 - count}\\b`));
  }

  let ioCalls = 0;
  const mocks = ['access', 'readFile', 'readdir'].map(method => t.mock.method(fs, method, async () => {
    ioCalls += 1;
    throw new Error('The exhausted client must not reach corpus I/O');
  }));
  for (const route of ['/api/checklists', '/api/checklists/prisma-2020']) {
    const blocked = await request(server, route, { 'X-Forwarded-For': '2001:db8::1' });
    assert.equal(blocked.status, 429);
    assert.deepEqual(blocked.body, { error: 'Too many checklist requests; retry after the indicated delay' });
    assert.match(blocked.headers.ratelimit, /\br=0\b/);
    assert.equal(Number(blocked.headers['retry-after']), 60);
  }
  const malformedBody = await request(server, '/api/checklists', { 'Content-Type': 'application/json' }, '{broken');
  assert.equal(malformedBody.status, 429);
  assert.equal(ioCalls, 0);
  for (const mocked of mocks) mocked.mock.restore();

  t.mock.timers.tick(60001);
  const recovered = await request(server, '/api/checklists/prisma-2020');
  assert.equal(recovered.status, 200);
  assert.equal(recovered.body.id, 'prisma-2020');
  assert.match(recovered.headers.ratelimit, /\br=99\b/);
  assert.equal(recovered.headers['retry-after'], undefined);
});
