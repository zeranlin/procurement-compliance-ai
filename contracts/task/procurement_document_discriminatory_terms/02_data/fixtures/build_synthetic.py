#!/usr/bin/env python3
"""Create structural acceptance fixtures. These are invented, never real evidence."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REGISTRY = json.loads((HERE.parent/'rule_registry.json').read_text(encoding='utf-8'))

def anchor(text, source, kind='资格条件'):
    return {'project': {'name': '纯合成演示项目', 'object': '演示服务', 'category': '服务',
                        'purchaser_region': '深圳市', 'performance_region': '深圳市'},
            'document': {'type': '演示采购文件', 'published_at': '2026-09-01', 'version': 'SYN-V1', 'effective': True},
            'section': {'heading_path': [kind], 'kind': kind}, 'unit': {'text': text, 'source': source}}

def ev(text, source):
    return {'text': text, 'document_version': 'SYN-V1', 'source': source,
            'source_text': text, 'start': 0, 'end_exclusive': len(text)}

def req(request_id, code, material, element, scope):
    return {'request_id': request_id, 'code': code, 'specific_material': material,
            'blocks_rule_element': element, 'why_needed': '该材料决定当前子点是否满足全部要件',
            'source_scope': scope, 'requested_valid_time': 'SYN-V1'}

def check(status):
    values = ['met', 'met', 'met', 'not_met', 'not_met'] if status == '发现' else (
        ['not_met', 'met', 'met', 'not_met', 'met'] if status == '未发现' else
        ['unknown', 'met', 'unknown', 'unknown', 'unknown'])
    return {key: {'result': value, 'evidence': []} for key, value in zip(
        ['对象', '作用环节', '后果', '限定词或例外', '排除情形'], values)}

def judgment(rule_id, status, case_type, evidence, requests=None, facts=None, reason='按演示原文与补证逐项核对。'):
    form = REGISTRY['forms']['.'.join(rule_id.split('.')[:2])]
    return {'rule_id': rule_id, 'status': status, 'source_stage': form['source_stage'].replace('；', '、').split('、'),
            'actual_stages': ['资格审查' if rule_id == '1.1.1' else '评审、评分'],
            'effective_requirement': True, 'subject': '供应商', 'condition': '见连续原文',
            'timing': '投标前', 'competitive_effect': '见连续原文' if status != '需要补充材料' else 'unknown',
            'evidence': evidence, 'verified_facts': facts or [], 'element_check': check(status),
            'reason': reason, 'requests': requests or [], 'basis_map_status': form['basis_map_status'],
            'basis_text': form['basis_text'], 'case_type': case_type,
            'review_authority': 'CODEX_AI_BUSINESS_SILVER'}

def event(case_id, revision, source_anchor, mode, rule_id, status=None, case_type=None,
          extra_evidence=None, requests=None, search_log=None, resolved=None, scope=False, candidate_rules=None, facts=None):
    own = ev(source_anchor['unit']['text'], source_anchor['unit']['source'])
    extra_evidence = extra_evidence or []
    candidate_rules = candidate_rules if candidate_rules is not None else ([rule_id] if rule_id else [])
    candidates = [{'rule_id': candidate_rule, 'candidate_evidence': own, 'why_candidate': '合成规则线索',
                   'missing_elements': ['评分行'] if requests else []} for candidate_rule in candidate_rules]
    discovery = {'candidate_rule_ids': candidates,
                 'possible_out_of_scope': scope, 'discovery_coverage': 'CURRENT_UNIT_ONLY',
                 'retrieval_requests': requests or []}
    record = {'case_id': case_id, 'data_kind': 'SYNTHETIC', 'source_id': None,
              'model_input': {'task': {'mode': mode, **({'rule_id': rule_id} if mode == 'judge' else {})},
                              'source_anchor': source_anchor, 'evidence': extra_evidence},
              'review_revision': revision, 'discovery': discovery, 'judgments': [],
              'scope_review': None, 'search_log': search_log or [],
              'pass_one': {'status': status, 'basis': 'synthetic fixture; not an independent model run'},
              'pass_two': {'status': status, 'countercheck': 'synthetic fixture; verifies schema and state transitions only'},
              'disagreement': None, 'resolved_request_ids': resolved or []}
    if scope:
        record['scope_review'] = {'source_anchor': source_anchor, 'status': '不在本专项范围',
                                  'rule_id': None, 'case_type': None,
                                  'scope_reason': '合成公告期限，不属于本专项 64 点',
                                  'checked_scope': '当前单元及完整上下文，对照 64 个子点',
                                  'evidence': [own], 'review_authority': 'CODEX_AI_BUSINESS_SILVER'}
    elif mode == 'judge':
        record['judgments'] = [judgment(rule_id, status, case_type, [own] + extra_evidence, requests, facts)]
    return record

def main():
    rows = []
    a = anchor('供应商注册地必须在深圳市，否则资格审查不通过。', '合成资格表第3行')
    rows.append(event('SYN-OBVIOUS-FAIL', 1, a, 'judge', '1.1.1', '发现', '明显违规案例'))
    b = anchor('中标后派驻服务人员到项目现场，不作为投标资格或评分条件。', '合成合同条款第2行', '合同履行')
    rows.append(event('SYN-OBVIOUS-PASS', 1, b, 'judge', '1.1.3', '未发现', '明显合规案例'))
    c = anchor('本地服务能力按附表评分。', '合成商务评分说明')
    request = req('SYN-R1', 'NEED_TABLE_ROW', '附表完整评分行与证明栏', '分支机构性质及得分后果', 'SYN-V1 商务评分附表')
    rows.append(event('SYN-DISCOVER-TWO-CANDIDATES', 1, c, 'discover', None,
                      requests=[request], candidate_rules=['1.1.3', '3.4.3']))
    rows.append(event('SYN-HARD-FAIL', 1, c, 'judge', '1.1.3', '需要补充材料', None, requests=[request]))
    score = ev('投标人在深圳市设立分公司并提交分公司营业执照得3分；未提交不得分。', '合成商务评分附表第4行')
    rows.append(event('SYN-HARD-FAIL', 2, c, 'judge', '1.1.3', '发现', '困难违规案例',
                      extra_evidence=[score], resolved=['SYN-R1']))
    request2 = req('SYN-R2', 'NEED_TABLE_ROW', '本地服务附表', '分支机构性质及竞争作用', 'SYN-V1 附表')
    rows.append(event('SYN-HARD-PASS', 1, c, 'judge', '1.1.3', '需要补充材料', None, requests=[request2]))
    exclusion = ev('中标后可派驻服务人员，所有投标人均不因此加分或失分。', '合成商务评分附表第5行')
    rows.append(event('SYN-HARD-PASS', 2, c, 'judge', '1.1.3', '未发现', '困难合规案例',
                      extra_evidence=[exclusion], resolved=['SYN-R2']))
    d = anchor('投标时须提供生产厂家授权书。', '合成资格表第8行')
    request3 = req('SYN-R3', 'NEED_PROJECT_FACT', '进口货物状态及发布依据', '非进口货物限定词', 'SYN-V1 项目资料')
    rows.append(event('SYN-UNKNOWN', 1, d, 'judge', '7.1.1', '需要补充材料', None, requests=[request3]))
    rows.append(event('SYN-UNKNOWN', 2, d, 'judge', '7.1.1', '需要补充材料', '无法判断案例',
                      requests=[request3], search_log=[{'request_id': 'SYN-R3', 'searched_scope': '合成项目资料目录与发布说明', 'result': '未找到进口状态及依据'}]))
    request4 = req('SYN-R4', 'NEED_PROJECT_FACT', '进口货物状态及发布依据', '非进口货物限定词', 'SYN-V1 项目公告')
    rows.append(event('SYN-IMPORT-EXCEPTION', 1, d, 'judge', '7.1.1', '需要补充材料', None, requests=[request4]))
    import_fact = '该演示项目经批准采购进口货物。'
    rows.append(event('SYN-IMPORT-EXCEPTION', 2, d, 'judge', '7.1.1', '未发现', '困难合规案例',
                      extra_evidence=[ev(import_fact, '合成项目公告第2行')], resolved=['SYN-R4'],
                      facts=[{'fact': import_fact, 'source': '合成项目公告第2行', 'valid_at': '2026-09-01'}]))
    e = anchor('采购公告期限为五日。', '合成公告第1行', '采购公告')
    rows.append(event('SYN-SCOPE', 1, e, 'discover', None, scope=True))
    f = anchor('获取采购文件前须上传营业执照并审核，否则无法下载。', '合成下载公告第2行', '获取文件')
    rows.append(event('SYN-7-4', 1, f, 'judge', '7.4.1', '发现', '明显违规案例'))
    (HERE/'synthetic_review_events.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n' for r in rows), encoding='utf-8')
    print(json.dumps({'synthetic_cases': len({r['case_id'] for r in rows}), 'events': len(rows)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
