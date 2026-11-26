"""Select a bounded Searchright plan; no provider authorization or execution."""
from collections import Counter


def _index(jobs):
    result = {}
    for job in jobs:
        key = job['strategy']['strategy_id']
        ids, persistent = job['catalogue_ids'], job['persistent_ids']
        if (not key or key in result or not ids or len(ids) != len(set(ids))
                or len(persistent) != len(set(persistent)) or not set(persistent) <= set(ids)
                or job.get('execution_authorized') is not False):
            raise ValueError('invalid or duplicate strategy')
        result[key] = job
    return result


def summarize_batch(jobs, batch):
    indexed = _index(jobs)
    if len(batch) != len(set(batch)) or not set(batch) <= set(indexed):
        raise ValueError('invalid batch identities')
    selected = [indexed[key] for key in batch]
    ids = {i for job in selected for i in job['catalogue_ids']}
    persistent = {i for job in selected for i in job['persistent_ids']}
    tokens = {(job['kind'], job['strategy']['query']['term']['text']) for job in selected}
    return {'slots': len(batch), 'catalogue_ids': len(ids), 'persistent_ids': len(persistent),
            'catalogue_id_list': sorted(ids), 'persistent_id_list': sorted(persistent),
            'distinct_query_tokens': len(tokens), 'by_provider': dict(Counter(job['strategy']['dialect'] for job in selected))}


def choose_batch(jobs, *, budget=8, provider_limit=2, already_observed=()):
    """Maximize marginal persistent-ID coverage before corroboration, deterministically.

    Already-observed metadata leads are lower priority, not qualified sources.
    Provider cap is hard; an insufficient pool returns fewer slots, not new requests.
    """
    if type(budget) is not int or not 0 <= budget <= 8 or type(provider_limit) is not int or not 1 <= provider_limit <= 2:
        raise ValueError('invalid bounded budget')
    indexed = _index(jobs)
    covered = set(already_observed)
    counts = Counter()
    tokens = set()
    batch = []
    while len(batch) < budget:
        candidates = [(key, job) for key, job in indexed.items() if key not in batch and counts[job['strategy']['dialect']] < provider_limit]
        if not candidates:
            break
        def priority(pair):
            key, job = pair
            token = (job['kind'], job['strategy']['query']['term']['text'])
            return (-len(set(job['persistent_ids']) - covered), -len(set(job['catalogue_ids']) - covered),
                    token in tokens, job['kind'] == 'title', counts[job['strategy']['dialect']], key)
        key, job = min(candidates, key=priority)
        batch.append(key)
        covered.update(job['catalogue_ids'])
        tokens.add((job['kind'], job['strategy']['query']['term']['text']))
        counts[job['strategy']['dialect']] += 1
    return batch
