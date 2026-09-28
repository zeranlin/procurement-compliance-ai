#!/usr/bin/env python3
"""Validate review events, source evidence, authority and revision history."""
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from build_artifacts import SOURCE_ROOT, document_paragraphs

try:
    from jsonschema import Draft202012Validator
except ImportError as exc:
    raise SystemExit('Install jsonschema>=4 to run the machine-readable schema gate') from exc

HERE = Path(__file__).resolve().parent
LOCAL = Path('/private/tmp/procurement-discriminatory-terms-02')
CASE_TYPES = {
    '发现': {'明显违规案例', '困难违规案例'},
    '未发现': {'明显合规案例', '困难合规案例'},
    '需要补充材料': {None, '无法判断案例'},
}

def read_rows(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--events', type=Path, default=HERE/'fixtures/synthetic_review_events.jsonl')
    p.add_argument('--ledger', type=Path, default=LOCAL/'source_version_ledger.jsonl')
    p.add_argument('--held-units', type=Path, default=LOCAL/'real_held_review_units.jsonl')
    p.add_argument('--source-root', type=Path, default=SOURCE_ROOT)
    p.add_argument('--report', type=Path, default=HERE/'reports/validation_report.json')
    args = p.parse_args()
    schema = json.loads((HERE/'review_schema.json').read_text(encoding='utf-8'))
    registry = json.loads((HERE/'rule_registry.json').read_text(encoding='utf-8'))
    binding = json.loads((HERE/'reports/contract_binding.json').read_text(encoding='utf-8'))
    quality = json.loads((HERE/'reports/source_quality_report.json').read_text(encoding='utf-8'))
    candidate_manifest = json.loads((HERE/'reports/candidate_manifest.json').read_text(encoding='utf-8'))
    validator = Draft202012Validator(schema)
    events = read_rows(args.events)
    ledger = read_rows(args.ledger)
    held = read_rows(args.held_units)
    by_source = {row['source_id']: row for row in ledger}
    errors = []
    if len(by_source) != len(ledger):
        errors.append('duplicate_source_id')
    if binding['rule_registry_sha256'] != sha(HERE/'rule_registry.json'):
        errors.append('rule_registry_manifest_hash_mismatch')
    for contract in binding['bindings']:
        source_path = Path(contract['source_path'])
        if not source_path.is_file() or sha(source_path) != contract['sha256']:
            errors.append('business_contract_hash_mismatch:' + contract['name'])
    if quality['source_ledger_sha256'] != sha(args.ledger) or quality['held_units_sha256'] != sha(args.held_units):
        errors.append('local_source_manifest_hash_mismatch')
    if candidate_manifest['held_unit_file_sha256'] != sha(args.held_units):
        errors.append('candidate_manifest_hash_mismatch')
    history = defaultdict(list)
    status_counts = defaultdict(int)
    for index, event in enumerate(events, 1):
        tag = f'event:{index}:{event.get("case_id")}'
        for error in validator.iter_errors(event):
            errors.append(f'{tag}:schema:{error.json_path}:{error.message}')
        if not event.get('case_id') or not isinstance(event.get('review_revision'), int):
            continue
        history[event['case_id']].append(event)
        task = event['model_input']['task']
        anchor = event['model_input']['source_anchor']
        mode = task['mode']
        if mode == 'discover' and 'rule_id' in task:
            errors.append(f'{tag}:discover_has_rule_id')
        if mode == 'judge' and task.get('rule_id') not in registry['rules']:
            errors.append(f'{tag}:invalid_judge_rule_id')
        if anchor['document']['effective'] is not True and mode == 'judge':
            errors.append(f'{tag}:judge_without_effective_version')
        if event['data_kind'] == 'REAL_AI_SILVER':
            source_id = event['source_id']
            source = by_source.get(source_id)
            if not source or source['internal_training_permission'] != 'GRANTED' or source['effective_version'] is not True:
                errors.append(f'{tag}:real_silver_missing_source_permission_or_version')
            one, two = event['pass_one'], event['pass_two']
            required = {'run_id', 'rule_id', 'status', 'evidence_refs', 'reason'}
            if not required.issubset(one) or not required.issubset(two) or one.get('run_id') == two.get('run_id'):
                errors.append(f'{tag}:real_silver_two_independent_passes_missing')
            elif one['rule_id'] != two['rule_id'] or one['status'] != two['status']:
                if not event['disagreement']:
                    errors.append(f'{tag}:two_pass_disagreement_not_recorded')
                if any(j['status'] in {'发现', '未发现'} for j in event['judgments']):
                    errors.append(f'{tag}:disputed_real_silver_forced_to_final_status')
            elif event['judgments'] and event['judgments'][0]['status'] != one['status']:
                errors.append(f'{tag}:final_status_differs_from_two_passes')
        if event['data_kind'] == 'REAL_HOLD' and event['judgments']:
            errors.append(f'{tag}:held_real_must_not_have_judgments')
        for item in event['discovery']['candidate_rule_ids']:
            if item['rule_id'] not in registry['rules']:
                errors.append(f'{tag}:invalid_candidate_rule')
        if event['scope_review'] is not None:
            if mode != 'discover' or event['judgments']:
                errors.append(f'{tag}:scope_review_must_follow_discover_without_judgments')
            if event['discovery']['candidate_rule_ids']:
                errors.append(f'{tag}:scope_review_has_unresolved_candidates')
        if mode == 'judge' and (len(event['judgments']) != 1 or event['scope_review'] is not None):
            errors.append(f'{tag}:judge_must_have_one_judgment_and_no_scope_review')
        evidence_sources = [anchor['unit']['text']] + [e['source_text'] for e in event['model_input']['evidence'] if 'source_text' in e]
        for judgment in event['judgments']:
            status = judgment['status']
            status_counts[status] += 1
            if judgment['rule_id'] != task.get('rule_id'):
                errors.append(f'{tag}:judge_rule_mismatch')
            if judgment['case_type'] not in CASE_TYPES[status]:
                errors.append(f'{tag}:invalid_status_case_type')
            form = registry['forms'][registry['rules'][judgment['rule_id']]['form_id']]
            if judgment['basis_text'] != form['basis_text'] or judgment['basis_map_status'] != form['basis_map_status']:
                errors.append(f'{tag}:basis_mapping_changed')
            if judgment['source_stage'] != form['source_stage'].replace('；', '、').split('、'):
                errors.append(f'{tag}:source_stage_mapping_changed')
            if status == '需要补充材料' and not judgment['requests']:
                errors.append(f'{tag}:missing_specific_request')
            if status in {'发现', '未发现'} and judgment['requests']:
                errors.append(f'{tag}:resolved_judgment_still_requests_material')
            if status == '发现' and any(e['result'] == 'unknown' for e in judgment['element_check'].values()):
                errors.append(f'{tag}:discovery_with_unknown_element')
            if status == '未发现' and not any(e['result'] == 'not_met' for e in judgment['element_check'].values()):
                errors.append(f'{tag}:no_exclusion_element')
            if judgment['case_type'] == '无法判断案例' and not event['search_log']:
                errors.append(f'{tag}:unknown_case_without_completed_search_log')
        for evidence in [*(j for j in event['model_input']['evidence']),
                         *(j['candidate_evidence'] for j in event['discovery']['candidate_rule_ids']),
                         *(j for judgment in event['judgments'] for j in judgment['evidence']),
                         *(event['scope_review']['evidence'] if event['scope_review'] else [])]:
            source_text = evidence.get('source_text')
            if source_text is None:
                source_text = next((s for s in evidence_sources if evidence['text'] in s), None)
            start, end = evidence['start'], evidence['end_exclusive']
            if source_text is None or start >= end or source_text[start:end] != evidence['text']:
                errors.append(f'{tag}:evidence_not_contiguous_or_location_invalid')
            if evidence.get('source_sha256') and hashlib.sha256(source_text.encode()).hexdigest() != evidence['source_sha256']:
                errors.append(f'{tag}:evidence_source_hash_mismatch')
    for case_id, revisions in history.items():
        revisions.sort(key=lambda x: x['review_revision'])
        if [r['review_revision'] for r in revisions] != list(range(1, len(revisions) + 1)):
            errors.append(f'{case_id}:revision_sequence_invalid')
        for previous, current in zip(revisions, revisions[1:]):
            old = previous['model_input']; new = current['model_input']
            if old['task'] != new['task'] or old['source_anchor'] != new['source_anchor']:
                errors.append(f'{case_id}:revision_identity_changed')
            old_ids = {r['request_id'] for j in previous['judgments'] for r in j['requests']}
            if not set(current['resolved_request_ids']).issubset(old_ids):
                errors.append(f'{case_id}:resolved_request_not_in_previous_revision')
            if any(j['case_type'] in {'困难违规案例', '困难合规案例'} for j in current['judgments']) and not new['evidence']:
                errors.append(f'{case_id}:difficult_case_without_added_evidence')
    held_errors = []
    if candidate_manifest['real_hold_unit_ids'] != [row['unit_id'] for row in held]:
        held_errors.append('candidate_manifest_unit_ids_mismatch')
    source_errors = []
    for source in ledger:
        path = args.source_root/source['relative_path']
        if not path.is_file() or sha(path) != source['sha256']:
            source_errors.append(f"{source['source_id']}:source_file_hash_mismatch")
        if (source['internal_training_permission'] != 'GRANTED' or source['effective_version'] is not True) and source['review_state'] != 'HOLD':
            source_errors.append(f"{source['source_id']}:uncleared_source_not_held")
    paragraphs_by_source = {}
    for row in held:
        source = by_source.get(row['source_id'])
        if not source or source['sha256'] != row['document_version_id'].removeprefix('sha256:'):
            held_errors.append(f'{row["unit_id"]}:source_hash_mismatch')
        if row['review_state'] != 'HOLD' or row['label'] is not None or row['split'] is not None:
            held_errors.append(f'{row["unit_id"]}:held_unit_has_label_or_split')
        if source and source['source_id'] not in paragraphs_by_source:
            paragraphs_by_source[source['source_id']] = {
                p['paragraph_index']: p for p in document_paragraphs(args.source_root/source['relative_path'])}
        for e in row['evidence']:
            if e['text'][e['start']:e['end_exclusive']] != row['requirement_text']:
                held_errors.append(f'{row["unit_id"]}:evidence_span_mismatch')
            if hashlib.sha256(e['text'].encode()).hexdigest() != e['paragraph_sha256']:
                held_errors.append(f'{row["unit_id"]}:paragraph_hash_mismatch')
            actual = paragraphs_by_source.get(row['source_id'], {}).get(e['paragraph_index'])
            if not actual or actual['text'] != e['text'] or actual['xml_path'] != e['xml_path']:
                held_errors.append(f'{row["unit_id"]}:original_docx_locator_mismatch')
        if any(link == row['unit_id'] or link not in {u['unit_id'] for u in held} for link in row['linked_unit_ids']):
            held_errors.append(f'{row["unit_id"]}:broken_cross_section_link')
    report = {'status': 'PASS' if not errors and not held_errors and not source_errors else 'FAIL',
              'event_count': len(events), 'synthetic_case_count': len(history),
              'status_counts': dict(status_counts), 'source_count': len(ledger),
              'real_held_units': len(held), 'real_ai_silver_count': sum(e['data_kind'] == 'REAL_AI_SILVER' for e in events),
              'schema_and_event_errors': errors, 'held_unit_errors': held_errors, 'source_errors': source_errors,
              'events_sha256': sha(args.events), 'ledger_sha256': sha(args.ledger), 'held_units_sha256': sha(args.held_units)}
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'events': len(events), 'sources': len(ledger),
                      'held_units': len(held), 'errors': errors[:5] + held_errors[:5] + source_errors[:5]}, ensure_ascii=False))
    raise SystemExit(0 if report['status'] == 'PASS' else 2)

if __name__ == '__main__':
    main()
