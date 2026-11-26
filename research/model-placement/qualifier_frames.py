"""Fixed clause-name alternatives for E10, reusing its exact offline model and evaluator."""
import argparse
import json
from pathlib import Path

FRAMES = {
    'clause-names': {
        'study scope phrase': ('applicability', 'Complete clause limiting the population, study design, report or setting.'),
        'conditional clause': ('condition', 'Complete contingent clause triggering a reporting obligation, including its connective.'),
        'exemption clause': ('exception', 'Complete clause removing an otherwise applicable reporting obligation, including its connective.'),
    },
    'operator-first': {
        'applicability restriction': ('applicability', 'Return the full restrictive scope phrase, including its scope marker when expressed, not just the study name.'),
        'triggering condition': ('condition', 'Return the whole triggering condition including if, when, or an equivalent operator and its argument; not the date or time being requested.'),
        'excluded circumstance': ('exception', 'Return the entire exclusion or exemption including unless, except, or an equivalent operator when expressed, and its argument.'),
    },
}


def schema(frame):
    if frame not in FRAMES:
        raise ValueError('unknown label frame')
    return ({label: description for label, (_, description) in FRAMES[frame].items()},
            {label: kind for label, (kind, _) in FRAMES[frame].items()})


def predictor_factory(frame, validate):
    from scripts.extractive_development import InvalidPrediction

    labels, mapping = schema(frame)

    def factory(extractor):
        def predict(text):
            raw = extractor.extract_entities(text, labels, include_spans=True,
                                             include_confidence=True, threshold=.5,
                                             overlap_policy='allow')
            try:
                entities = raw.get('entities') if isinstance(raw, dict) else None
                if not isinstance(entities, dict) or not set(entities) <= set(mapping):
                    raise ValueError('malformed or unrequested entity label')
                mapped = {'entities': {mapping[label]: items for label, items in entities.items()}}
                return validate(text, mapped), raw
            except ValueError as exc:
                raise InvalidPrediction(str(exc), raw) from exc
        return predict
    return factory


def main():
    from scripts import extractive_development as e

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frame', choices=tuple(FRAMES), required=True)
    parser.add_argument('--model-dir', type=Path, required=True)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    labels, mapping = schema(args.frame)
    try:
        receipt = e.run('gliner', args.model_dir, args.revision,
                        predictor_factory=predictor_factory(args.frame, e.model_spans))
        receipt['requests'] = len(receipt['cases'])
    except (ValueError, OSError, RuntimeError, ImportError) as exc:
        receipt = {'status':'failed', 'error_type':type(exc).__name__, 'revision':args.revision,
                   'scientific_qualification':False, 'canonical_packs_promoted':0}
    receipt.update({'experiment':'E10-qualifier-framing-development-v1', 'frame':args.frame,
                    'labels':labels, 'canonical_label_mapping':mapping, 'threshold':.5,
                    'overlap_policy':'allow', 'script_sha256_framing':e.file_hash(Path(__file__))})
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf-8')
    if receipt.get('status')=='failed':
        raise SystemExit('framing experiment failed; receipt retained')


if __name__=='__main__':
    main()
