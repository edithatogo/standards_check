'use strict';

const assert = require('node:assert/strict');
const test = require('node:test');
const yaml = require('js-yaml');

test('YAML merges keep __proto__ as data instead of an inherited checklist title', () => {
  for (const document of [
    '__proto__: {title: inherited}\n',
    'payload: &ref {title: inherited}\n<<: {__proto__: *ref}\n',
  ]) {
    const parsed = yaml.load(document);
    assert.equal(Object.getPrototypeOf(parsed), Object.prototype);
    assert.ok(Object.hasOwn(parsed, '__proto__'));
    assert.equal(parsed.title, undefined);
    assert.equal({}.title, undefined);
  }
  assert.deepEqual(yaml.load('defaults: &d {title: default}\nitem: {<<: *d, title: explicit}').item,
    { title: 'explicit' });
});

test('repeated merge aliases consume the cumulative work budget', () => {
  const document = 'a: &a {k: 1}\nb: {<<: [*a, *a, *a]}';
  assert.deepEqual(yaml.load(document, { maxTotalMergeKeys: 6 }).b, { k: 1 });
  assert.throws(() => yaml.load(document, { maxTotalMergeKeys: 5 }), /maxTotalMergeKeys/);
});

test('chained merges consume the same budget while ordinary chains retain values', () => {
  const document = [
    'a0: &a0 {k0: 0}',
    'a1: &a1 {<<: *a0, k1: 1}',
    'a2: &a2 {<<: *a1, k2: 2}',
    'a3: &a3 {<<: *a2, k3: 3}',
  ].join('\n');
  assert.deepEqual(yaml.load(document, { maxTotalMergeKeys: 9 }).a3,
    { k0: 0, k1: 1, k2: 2, k3: 3 });
  assert.throws(() => yaml.load(document, { maxTotalMergeKeys: 8 }), /maxTotalMergeKeys/);
});

test('empty merge sources consume the budget too', () => {
  const document = 'empty: &empty {}\nmerged: {<<: [*empty, *empty, *empty]}';
  assert.deepEqual(yaml.load(document, { maxTotalMergeKeys: 3 }).merged, {});
  assert.throws(() => yaml.load(document, { maxTotalMergeKeys: 2 }), /maxTotalMergeKeys/);
});

test('merge sequences accept 100 entries and reject 101', () => {
  const document = (count) => `empty: &empty {}\nmerged: {<<: [${Array(count).fill('*empty').join(',')}]}`;
  assert.deepEqual(yaml.load(document(100)).merged, {});
  assert.throws(() => yaml.load(document(101)), /abnormal merge sequence size/);
});

test('ordered maps preserve key order and reject duplicate ordinary or special keys', () => {
  const keys = ['__proto__', 'constructor', 'toString', ...Array.from({ length: 128 }, (_, n) => `key${n}`)];
  const document = `!!omap\n${keys.map((key, n) => `- ${key}: ${n}`).join('\n')}\n`;
  const parsed = yaml.load(document);
  assert.deepEqual(parsed.map((entry) => Object.keys(entry)[0]), keys);
  assert.throws(() => yaml.load(`${document}- key127: duplicate\n`), yaml.YAMLException);
  assert.throws(() => yaml.load(`${document}- __proto__: duplicate\n`), yaml.YAMLException);
});

test('loadAll shares a merge budget across documents and separate load calls reset it', () => {
  const document = 'a: &a {x: 1, y: 2}\nb: {<<: *a}\n';
  const stream = `${document}---\n${document}`;
  assert.equal(yaml.loadAll(stream, { maxTotalMergeKeys: 6 }).length, 2);
  assert.throws(() => yaml.loadAll(stream, { maxTotalMergeKeys: 3 }), /maxTotalMergeKeys/);
  for (let n = 0; n < 2; n += 1) {
    assert.deepEqual(yaml.load(document, { maxTotalMergeKeys: 3 }).b, { x: 1, y: 2 });
  }
});
