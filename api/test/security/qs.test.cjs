'use strict';

const assert = require('node:assert/strict');
const test = require('node:test');
const qs = require('qs');

test('bracket arrays respect their configured boundary', () => {
  const options = { arrayLimit: 2, throwOnLimitExceeded: true };
  assert.deepEqual(qs.parse('a[]=one&a[]=two', options), { a: ['one', 'two'] });
  assert.throws(() => qs.parse('a[]=one&a[]=two&a[]=three', options), RangeError);
});

test('comma arrays respect the same boundary', () => {
  const options = { comma: true, arrayLimit: 2, throwOnLimitExceeded: true };
  assert.deepEqual(qs.parse('a=one,two', options), { a: ['one', 'two'] });
  assert.throws(() => qs.parse('a=one,two,three', options), RangeError);
});

test('null and undefined comma elements serialize consistently', () => {
  for (const value of [null, undefined]) {
    assert.equal(qs.stringify({ a: [value, 'ok'] }, {
      arrayFormat: 'comma', encodeValuesOnly: true,
    }), 'a=,ok');
    assert.equal(qs.stringify({ a: [value, 'ok'] }, { arrayFormat: 'comma' }), 'a=%2Cok');
  }
});

test('a parsed constructor.isBuffer property remains data during serialization', () => {
  const input = 'x[constructor][isBuffer]=text';
  for (const options of [{ plainObjects: true }, { allowPrototypes: true }]) {
    const parsed = qs.parse(input, options);
    const encoded = qs.stringify(parsed);
    assert.equal(encoded, 'x%5Bconstructor%5D%5BisBuffer%5D=text');
    assert.deepEqual(qs.parse(encoded, options), parsed);
  }
});

test('comma serialization handles object elements without a callable toString', () => {
  const inputs = [
    JSON.parse('{"a":[{"toString":"text"},"ok"]}'),
    qs.parse('a[0][toString]=text&a[1]=ok', { allowPrototypes: true }),
    qs.parse('a[0][value]=text&a[1]=ok', { plainObjects: true }),
    { a: [[{ toString: 'text' }], 'ok'] },
  ];
  for (const input of inputs) {
    for (const encodeValuesOnly of [false, true]) {
      const result = qs.stringify(input, { arrayFormat: 'comma', encodeValuesOnly });
      assert.equal(new URLSearchParams(result).get('a'), '[object Object],ok');
    }
  }
});

test('ordinary arrays, nested query objects and custom string conversions remain usable', () => {
  const input = { filter: { type: 'archetype', title: 'PRISMA 2020' }, ids: ['one', 'two'] };
  assert.deepEqual(qs.parse(qs.stringify(input)), input);
  assert.equal(qs.stringify({ a: ['one', 'two'] }, { arrayFormat: 'comma' }), 'a=one%2Ctwo');
  assert.equal(qs.stringify({ a: [{ toString: () => 'label' }] }, { arrayFormat: 'comma' }), 'a=label');
});
