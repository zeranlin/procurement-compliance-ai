#!/usr/bin/env python3
"""Build the new 02 data inventory; keep raw excerpts in a local-only directory."""
import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
BUSINESS = Path('/Users/linzeran/.codex/worktrees/e8b9/procurement-compliance-ai/contracts/task/procurement_document_discriminatory_terms/01_business')
GOVERNANCE = Path('/Users/linzeran/.codex/worktrees/5853/procurement-compliance-ai/docs/governance')
SOURCE_ROOT = Path('/Users/linzeran/code/2026-zn/test_target/深圳10个品目批注文件')
LOCAL = Path('/private/tmp/procurement-discriminatory-terms-02')
DOCS = [
    GOVERNANCE/'采购文件设置差别歧视条款业务需求说明书_V0.3.md',
    GOVERNANCE/'采购文件设置差别歧视条款专项模型审查单元输入规范_V0.2.md',
    BUSINESS/'01_规则范围与来源核验_V0.1.md',
    BUSINESS/'02_六十四点可执行审查规则卡_V0.1.md',
    BUSINESS/'03_专项模型输出规范_V0.1.md',
    BUSINESS/'04_标注与疑难裁决手册_V0.1.md',
    BUSINESS/'05_业务验收案例与覆盖矩阵_V0.1.md',
    BUSINESS/'06_Codex自动复核与移交_V0.1.md',
]
EXPECTED = [
    'e91b2688c829e7898638f1629faa7b0e62d92fa965a1fbfdf061b6862149e223',
    '48430a70f214397c3d4197b612fd49fe5cfe4cf4ec78ab01f1573c5c9cf0dfb1',
    '44b66482baafed50d3910c1776b814c33aa51c9bf23a5610807462b92b3e08c7',
    '43db9af4fd3b8cb7f6f6fe63ce8ff5f4d80fc8f92ef2806d9994751579fdc438',
    '36aa072f742dfcfa28dfa508407679e7609d97b6e39d13bee09a80541af81313',
    '4edb0641e173041862f966c02a255436915dd5c3a8594fb98ea0325b17a2e594',
    '12ae402acdc4db2814569a186eeb40f75bf6d6ae6b60b78a4bc6bc56a9e6e1a7',
    'a46b0c624acdf5d845c94950dcfe77ddb9072d070b76179342d2293d370ea4e5',
]
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')

def write_jsonl(path, rows):
    path.write_text(''.join(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n' for row in rows), encoding='utf-8')

def binding():
    actual = [sha(path) for path in DOCS]
    if actual != EXPECTED:
        raise SystemExit('Business contract changed; stop and review hashes: ' + json.dumps(actual))
    return [{'name': path.name, 'version': 'V0.3' if i == 0 else 'V0.2' if i == 1 else 'V0.1',
             'sha256': digest, 'source_path': str(path)} for i, (path, digest) in enumerate(zip(DOCS, actual))]

def registry():
    source = DOCS[2].read_text(encoding='utf-8')
    cards = DOCS[3].read_text(encoding='utf-8')
    category_names = {'一': '1', '二': '2', '三': '3', '四': '4', '五': '5', '六': '6', '七': '7'}
    categories = {}
    for number, text in re.findall(r'^\| 第([一二三四五六七])类 \| (.*?) \| \d+ \| \d+ \|', source, re.M):
        categories[category_names[number]] = text
    forms = {}
    rows = re.findall(r'^\| ([1-7]\.\d) \| (.*?) \| (.*?) \| (\d+) \| (.*?) \|$', source, re.M)
    for form_id, text, stage, count, basis in rows:
        forms[form_id] = {'text': text, 'source_stage': stage, 'expected_rule_count': int(count),
                          'basis_group': None if form_id == '7.4' else basis.split('；')[0],
                          'basis_map_status': '待原始附件核实' if form_id == '7.4' else 'V0.3 转写可读、原图待核'}
    basis_groups = {}
    for line in source.splitlines():
        m = re.match(r'^\| ([甲乙丙丁戊己庚辛壬癸子]) \| .*? \| (.*?) \|$', line)
        if m:
            basis_groups[m.group(1)] = m.group(2)
    rules = {}
    for rule_id, name in re.findall(r'^#### ([1-7]\.\d\.\d+) (.+)$', cards, re.M):
        form = '.'.join(rule_id.split('.')[:2])
        rules[rule_id] = {'name': name, 'form_id': form, 'category_id': rule_id.split('.')[0]}
    if len(categories) != 7 or len(forms) != 22 or len(rules) != 64 or any(sum(r['form_id'] == fid for r in rules.values()) != form['expected_rule_count'] for fid, form in forms.items()):
        raise SystemExit(f'Rule count mismatch: categories={len(categories)}, forms={len(forms)}, rules={len(rules)}')
    for fid, form in forms.items():
        form['basis_text'] = None if fid == '7.4' else basis_groups[form['basis_group'].removeprefix('组')]
    return {'version': '02-rule-registry-v0.1', 'source_hashes': [EXPECTED[2], EXPECTED[3]],
            'source_verification': 'V0.3_TRANSCRIPTION_ONLY_ORIGINAL_ATTACHMENT_UNCHECKED',
            'categories': categories, 'forms': forms, 'rules': rules}

def inventory(root):
    files = sorted(path for path in root.rglob('*') if path.is_file() and path.suffix.lower() in {'.doc', '.docx'})
    rows = []
    for path in files:
        relative = path.relative_to(root).as_posix()
        digest = sha(path)
        m = re.search(r'\[([A-Z]{2,6}CG\d{10}-[A-Z])\]', path.name)
        project_code = m.group(1) if m else None
        project_title = re.sub(r'^\[[^]]+\]', '', path.stem)
        family = project_code.rsplit('-', 1)[0] if project_code else 'UNRESOLVED-' + hashlib.sha256(path.stem.encode()).hexdigest()[:16]
        source_id = 'SRC-' + hashlib.sha256((relative + '|' + digest).encode()).hexdigest()[:20]
        rows.append({'source_id': source_id, 'relative_path': relative,
                     'sha256': digest, 'bytes': path.stat().st_size, 'extension': path.suffix.lower(),
                     'source_channel': 'USER_PROVIDED_LOCAL_FOLDER', 'source_url': None,
                     'permission_evidence': None, 'internal_training_permission': 'UNKNOWN',
                     'project_code_from_filename': project_code, 'project_title_from_filename_unverified': project_title,
                     'project_family_key': family, 'category_from_folder': path.parent.name,
                     'category_verification': 'FOLDER_NAME_ONLY', 'region': None,
                     'published_at': None, 'document_version': None, 'effective_version': None,
                     'correction_or_qna_relation': 'UNKNOWN', 'review_state': 'HOLD',
                     'hold_reasons': ['INTERNAL_TRAINING_PERMISSION_UNCONFIRMED', 'EFFECTIVE_VERSION_UNCONFIRMED', 'PUBLICATION_SOURCE_UNVERIFIED']})
    return rows

def document_paragraphs(path):
    with ZipFile(path) as archive:
        root = ET.fromstring(archive.read('word/document.xml'))
    body = root.find(W + 'body')
    out = []
    number = 0
    def walk(node, trail):
        nonlocal number
        for index, child in enumerate(node):
            child_trail = trail + [(child.tag.rsplit('}', 1)[-1], index)]
            if child.tag == W + 'p':
                number += 1
                text = ''.join(t.text or '' for t in child.iter(W + 't')).strip()
                if text:
                    style = child.find(f'{W}pPr/{W}pStyle')
                    out.append({'paragraph_index': number, 'text': text,
                                'xml_path': '/'.join(f'{tag}[{i}]' for tag, i in child_trail),
                                'style': style.get(W + 'val') if style is not None else None})
            else:
                walk(child, child_trail)
    walk(body, [('body', 0)])
    return out

def held_units(root, ledger):
    relative = '物业管理/[SZCG2025000887-A]深圳市南山区人民法院物业管理服务项目.docx'
    entry = next((row for row in ledger if row['relative_path'] == relative), None)
    if not entry:
        return [], [{'source': relative, 'issue': 'EXPECTED_SOURCE_MISSING'}]
    paragraphs = document_paragraphs(root / relative)
    anchors = [
        ('供应商承诺中标后提供本地经营（服务）网点的，得100分。', '评分行', 'SCORING_CONDITION'),
        ('我单位承诺，中标后为本项目提供本地经营（服务）网点', '承诺函', 'POST_AWARD_PROMISE')]
    selected = []
    for needle, kind, role in anchors:
        hits = [row for row in paragraphs if needle in row['text']]
        if len(hits) != 1:
            return [], [{'source': relative, 'issue': 'ANCHOR_NOT_UNIQUE', 'anchor_role': role, 'hit_count': len(hits)}]
        selected.append((hits[0], kind, role))
    units = []
    for row, kind, role in selected:
        # The anchors identify complete, single-requirement paragraphs. Preserve every
        # condition and consequence in the paragraph instead of cutting at a keyword.
        text, start, end = row['text'], 0, len(row['text'])
        unit_id = f"UNIT-{entry['sha256'][:12]}-{row['paragraph_index']}"
        units.append({'unit_id': unit_id, 'project_id': entry['project_code_from_filename'],
                      'source_id': entry['source_id'], 'project_family_key': entry['project_family_key'],
                      'document_version_id': 'sha256:' + entry['sha256'], 'document_effective': None,
                      'section': {'heading_path': [], 'kind': kind, 'heading_verification': 'POSITION_ONLY_NOT_CONFIRMED'},
                      'parent_clause_id': f"CLAUSE-{entry['sha256'][:12]}-{row['paragraph_index']}",
                      'atomization': 'ONE_REQUIREMENT_PER_SELECTED_PARAGRAPH',
                      'requirement_text': text, 'actor': 'unknown', 'timing': '中标后' if '中标后' in text else 'unknown',
                      'region_role': '服务覆盖地' if '本地' in text else 'unknown',
                      'consequence': '得100分' if '得100分' in text else '违约处理' if '违约处理' in text else 'unknown',
                      'competition_stage': '评审、评分' if role == 'SCORING_CONDITION' else '中标后履约',
                      'decisive_context_gap': '完整评分表/证明栏、当前有效版本及来源许可待核',
                      'negation_and_exception_preserved': True,
                      'six_step_trace': {'document_stage': kind, 'clause_effect': 'UNVERIFIED',
                                         'atomic_requirement': 'ONE_REQUIREMENT',
                                         'competition_stage_and_consequence': 'STATED_EFFECT_REQUIRES_CONTEXT',
                                         'rule_elements_and_exceptions': 'NOT_JUDGED',
                                         'continuous_evidence_or_gap': 'EVIDENCE_LOCATED_PERMISSION_AND_VERSION_GAP'},
                      'evidence': [{'source_id': entry['source_id'], 'document_sha256': entry['sha256'],
                                    'part': 'word/document.xml', 'paragraph_index': row['paragraph_index'],
                                    'xml_path': row['xml_path'], 'paragraph_sha256': hashlib.sha256(text.encode()).hexdigest(),
                                    'text': text, 'start': start, 'end_exclusive': end}],
                      'cross_section_role': role, 'linked_unit_ids': [], 'review_state': 'HOLD',
                      'hold_reasons': entry['hold_reasons'], 'label': None, 'split': None})
    for unit in units:
        unit['linked_unit_ids'] = [other['unit_id'] for other in units if other['unit_id'] != unit['unit_id']]
        unit['cross_section_relation'] = 'SCORING_ROW_TO_POST_AWARD_PROMISE'
    return units, []

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source-root', type=Path, default=SOURCE_ROOT)
    p.add_argument('--local-dir', type=Path, default=LOCAL)
    args = p.parse_args()
    args.local_dir.mkdir(parents=True, exist_ok=True)
    bindings = binding()
    rules = registry()
    write_json(HERE/'rule_registry.json', rules)
    sources = inventory(args.source_root)
    write_jsonl(args.local_dir/'source_version_ledger.jsonl', sources)
    units, extraction_issues = held_units(args.source_root, sources)
    write_jsonl(args.local_dir/'real_held_review_units.jsonl', units)
    family_counts = Counter(row['project_family_key'] for row in sources)
    exact = defaultdict(list)
    for row in sources: exact[row['sha256']].append(row['source_id'])
    report = {'generated_at': datetime.now(timezone.utc).isoformat(), 'source_count': len(sources),
              'docx_count': sum(row['extension'] == '.docx' for row in sources),
              'legacy_doc_count': sum(row['extension'] == '.doc' for row in sources),
              'known_project_code_count': sum(row['project_code_from_filename'] is not None for row in sources),
              'source_family_count': len(family_counts), 'multi_file_family_count': sum(count > 1 for count in family_counts.values()),
              'exact_duplicate_groups': [ids for ids in exact.values() if len(ids) > 1],
              'training_permission_confirmed_count': 0, 'effective_version_confirmed_count': 0,
              'real_held_unit_count': len(units), 'real_ai_silver_count': 0, 'train_count': 0, 'dev_count': 0,
              'extraction_issues': extraction_issues, 'cross_split_family_violations': [],
              'near_duplicate_check': 'NOT_APPLICABLE_NO_ELIGIBLE_SPLIT',
              'source_ledger_sha256': sha(args.local_dir/'source_version_ledger.jsonl'),
              'held_units_sha256': sha(args.local_dir/'real_held_review_units.jsonl'),
              'source_ledger_path': str(args.local_dir/'source_version_ledger.jsonl'),
              'held_units_path': str(args.local_dir/'real_held_review_units.jsonl'),
              'raw_documents_copied_to_repository': 0,
              'readiness': 'SOURCE_PERMISSION_AND_VERSION_HOLD'}
    write_json(HERE/'reports/source_quality_report.json', report)
    write_json(HERE/'reports/contract_binding.json', {'bindings': bindings, 'rule_registry_sha256': sha(HERE/'rule_registry.json'),
               'source_status': 'V0.3_TRANSCRIPTION_ONLY_ORIGINAL_ATTACHMENT_UNCHECKED',
               'basis_7_4': None, 'basis_7_4_status': '待原始附件核实',
               '00_interface_reverification': 'BUSINESS_INTERFACE_REWORK_PASS_REPORTED_BY_CONTROL',
               'business_two_pass_history_complete': False, 'legacy_c1_01_labels_adopted': False})
    case_types = ['明显违规案例', '明显合规案例', '困难违规案例', '困难合规案例', '无法判断案例']
    coverage = [{'rule_id': rid, 'form_id': rule['form_id'], 'category_id': rule['category_id'],
                 'real_ai_silver_by_case_type': {name: 0 for name in case_types},
                 'real_held_count': 0, 'gap': 'NO_PERMISSION_AND_EFFECTIVE_VERSION_CONFIRMED'}
                for rid, rule in sorted(rules['rules'].items(), key=lambda x: [int(n) for n in x[0].split('.')])]
    write_json(HERE/'reports/real_coverage_matrix.json', {'scope': 'REAL_ELIGIBLE_ONLY',
               'category_count': 7, 'form_count': len(rules['forms']), 'rule_count': len(coverage),
               'case_type_count': len(case_types), 'total_cells': len(coverage) * len(case_types),
               'covered_cells': 0, 'uncovered_cells': len(coverage) * len(case_types),
               'matrix': coverage, 'synthetic_cases_excluded': True, 'held_units_unlabeled': len(units)})
    write_json(HERE/'reports/split_and_leakage_report.json', {'eligible_real_count': 0, 'train_count': 0, 'dev_count': 0,
               'split_method': 'PROJECT_FAMILY_AND_VERSION_GROUP_WHEN_ELIGIBLE',
               'cross_split_project_family_violations': [], 'cross_split_version_violations': [],
               'cross_split_exact_duplicate_violations': [], 'cross_split_near_duplicate_violations': [],
               'check_status': 'NOT_APPLICABLE_NO_ELIGIBLE_REAL_SAMPLES',
               'held_source_count': len(sources), 'held_unit_count': len(units),
               'blind_gold_accessed': False})
    write_json(HERE/'reports/candidate_manifest.json', {'real_ai_silver_ids': [], 'real_hold_unit_ids': [u['unit_id'] for u in units],
               'synthetic_fixture_path': str(HERE/'fixtures/synthetic_review_events.jsonl'),
               'held_unit_file_path': str(args.local_dir/'real_held_review_units.jsonl'),
               'held_unit_file_sha256': sha(args.local_dir/'real_held_review_units.jsonl'),
               'training_authorized': False, 'benchmark_ready': False, 'gold_eligible': False})
    print(json.dumps({'sources': len(sources), 'held_units': len(units), 'real_ai_silver': 0,
                      'readiness': report['readiness'], 'extraction_issues': extraction_issues}, ensure_ascii=False))

if __name__ == '__main__':
    main()
