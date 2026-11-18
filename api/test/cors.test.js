const assert = require('node:assert/strict');
const http = require('node:http');
const { once } = require('node:events');
const test = require('node:test');
const cors = require('cors');
const { createCorsOptions } = require('../cors-options');

async function requestOrigin(value, origin, method = 'GET') {
  const middleware = cors(createCorsOptions(value));
  const server = http.createServer((request, response) => {
    middleware(request, response, error => {
      response.statusCode = error ? 500 : 200;
      response.end(error ? error.message : 'checklist');
    });
  });
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  try {
    return await new Promise((resolve, reject) => {
      const headers = origin === undefined ? {} : { Origin: origin };
      if (method === 'OPTIONS') headers['Access-Control-Request-Method'] = 'GET';
      const request = http.request({
        host: '127.0.0.1',
        port: server.address().port,
        method,
        headers,
        agent: false,
      }, response => {
        response.resume();
        response.once('end', () => resolve({ status: response.statusCode, headers: response.headers }));
        response.once('error', reject);
      });
      request.once('error', reject);
      request.end();
    });
  } finally {
    await new Promise((resolve, reject) => server.close(error => error ? reject(error) : resolve()));
  }
}

test('the default allows the local frontend and does not grant credentials', async () => {
  const response = await requestOrigin(undefined, 'http://localhost:3000');
  assert.equal(response.headers['access-control-allow-origin'], 'http://localhost:3000');
  assert.equal(response.headers['access-control-allow-credentials'], undefined);
  assert.equal(response.headers.vary, 'Origin');
});

test('the default denies unrelated browser origins', async () => {
  const response = await requestOrigin(undefined, 'https://untrusted.example');
  assert.equal(response.headers['access-control-allow-origin'], undefined);
});

test('blank settings use the documented localhost default', async () => {
  const response = await requestOrigin(' , ', 'http://localhost:3000');
  assert.equal(response.headers['access-control-allow-origin'], 'http://localhost:3000');
});

test('a comma-separated list trims whitespace and matches complete origins', async () => {
  const value = ' https://first.example, https://second.example, ';
  for (const origin of ['https://first.example', 'https://second.example']) {
    const response = await requestOrigin(value, origin);
    assert.equal(response.headers['access-control-allow-origin'], origin);
  }
  const response = await requestOrigin(value, 'https://second.example.untrusted.example');
  assert.equal(response.headers['access-control-allow-origin'], undefined);
});

test('a single explicit wildcard permits public cross-origin reads', async () => {
  const response = await requestOrigin(' * ', 'https://any.example');
  assert.equal(response.headers['access-control-allow-origin'], '*');
  assert.equal(response.headers['access-control-allow-credentials'], undefined);
});

test('a wildcard mixed with an allow-list fails configuration', () => {
  assert.throws(() => createCorsOptions('https://allowed.example,*'), /must be used by itself/);
});

test('requests without Origin remain usable without CORS response headers', async () => {
  const response = await requestOrigin(undefined, undefined);
  assert.equal(response.status, 200);
  assert.equal(response.headers['access-control-allow-origin'], undefined);
});

test('preflight responses preserve the legacy 200 status and enforce the allow-list', async () => {
  const allowed = await requestOrigin('https://allowed.example', 'https://allowed.example', 'OPTIONS');
  assert.equal(allowed.status, 200);
  assert.equal(allowed.headers['access-control-allow-origin'], 'https://allowed.example');
  const denied = await requestOrigin('https://allowed.example', 'https://denied.example', 'OPTIONS');
  assert.equal(denied.headers['access-control-allow-origin'], undefined);
});
