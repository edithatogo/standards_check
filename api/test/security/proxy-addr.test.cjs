'use strict';

const assert = require('node:assert/strict');
const test = require('node:test');
const proxyaddr = require('proxy-addr');

// GHSA-jqcg-44mw-7w3h / Dependabot #15. Addresses are synthetic fixtures.
const client = '203.0.113.9';
const spoofed = '192.0.2.100';

function request(remoteAddress, forwardedFor) {
  return {
    socket: { remoteAddress },
    headers: { 'x-forwarded-for': forwardedFor },
  };
}

test('short IPv4-mapped IPv6 prefixes do not trust arbitrary IPv4 clients', () => {
  const trust = proxyaddr.compile('::ffff:10.0.0.0/8');
  assert.equal(trust(client), false);
  assert.equal(trust('10.20.30.40'), false);
  assert.equal(proxyaddr(request(client, spoofed), trust), client);
});

test('unrelated IPv6 subnets do not accept spoofed IPv4 forwarding headers', () => {
  const trust = proxyaddr.compile('::/1');
  assert.equal(trust(client), false);
  assert.equal(proxyaddr(request(client, spoofed), trust), client);
});

test('mixed trust lists reject both IPv4 representations of an untrusted client', () => {
  const trust = proxyaddr.compile(['::ffff:10.0.0.0/8', '::/1']);
  for (const address of [client, `::ffff:${client}`]) {
    assert.equal(trust(address), false);
    assert.equal(proxyaddr(request(address, spoofed), trust), address);
  }
});

test('mixed trust lists preserve legitimate IPv4-mapped and native IPv6 proxies', () => {
  const trust = proxyaddr.compile(['10.0.0.0/8', '2001:db8::/32']);
  for (const address of ['10.20.30.40', '::ffff:10.20.30.40', '2001:db8::1']) {
    assert.equal(trust(address), true);
    assert.equal(proxyaddr(request(address, client), trust), client);
  }
});

test('correct IPv4 and mapped IPv6 trust subnets retain legitimate proxy behavior', () => {
  for (const subnet of ['10.0.0.0/8', '::ffff:10.0.0.0/104']) {
    const trust = proxyaddr.compile(subnet);
    assert.equal(trust('10.20.30.40'), true);
    assert.equal(trust(client), false);
    assert.equal(proxyaddr(request('10.20.30.40', client), trust), client);
    assert.equal(proxyaddr(request(client, spoofed), trust), client);
  }
});

test('the first untrusted hop ends a chain even when an earlier header is spoofed', () => {
  const trust = proxyaddr.compile('10.0.0.0/8');
  assert.equal(proxyaddr(request('10.20.30.40', `${spoofed}, ${client}`), trust), client);
});
