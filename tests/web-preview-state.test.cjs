const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const script = fs.readFileSync(path.join(__dirname, '..', 'assets', 'js', 'app.js'), 'utf8');
const context = {document: {addEventListener() {}}};
vm.createContext(context);
vm.runInContext(script, context);
const validate = context.validateProgressSnapshot;
const source = {page: '/standards_check/archetypes/prisma-2020.html', sha256: 'a'.repeat(64)};
const sample = () => ({
  schema: 1, source, checkboxes: {'item-0': true, 'item-1': false},
  notes: {'item-0': 'synthetic note'}
});

test('valid same-page edition progress preserves only valid entries', () => {
  const result = validate(sample(), source, 2);
  assert.ok(result);
  assert.equal(result.checkboxes['item-0'], true);
  assert.equal(result.notes['item-0'], 'synthetic note');
});

test('rejects malformed, obsolete, cross-edition and cross-page imports', () => {
  assert.equal(validate(null, source, 2), null);
  assert.equal(validate([], source, 2), null);
  assert.equal(validate({checkboxes: {}, notes: {}}, source, 2), null);
  for (const changedSource of [
    {...source, sha256: 'b'.repeat(64)},
    {...source, page: '/standards_check/archetypes/other.html'}
  ]) {
    assert.equal(validate(sample(), changedSource, 2), null);
  }
  const extra = {...sample(), untrusted: true};
  assert.equal(validate(extra, source, 2), null);
});

test('rejects out-of-range IDs, unknown keys and bad checkbox/note types', () => {
  for (const [checks, notes] of [
    [{'item-2': true}, {}],
    [{'item-0': 'true'}, {}],
    [{'item-01': true}, {}],
    [{'__proto__': true, 'item-01': false}, {}],
    [{}, {'item-2': 'stale'}],
    [{}, {'item-0': null}],
    [{}, {'item-0': 'x'.repeat(2001)}]
  ]) {
    assert.equal(validate({...sample(), checkboxes: checks, notes}, source, 2), null);
  }
});
