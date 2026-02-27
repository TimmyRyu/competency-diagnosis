"""
Google Sheets 추상화 레이어
동적 테이블(respondents, diagnosis_results, roadmap_items)을 Google Sheets로 관리합니다.

환경변수:
  GOOGLE_CREDENTIALS_JSON : 서비스 계정 JSON 키 파일 전체 내용 (한 줄 문자열)
  SPREADSHEET_ID          : Google Sheets 스프레드시트 ID
"""

import os
import json
import time
import datetime

import gspread
from google.oauth2.service_account import Credentials

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CACHE_TTL = 30        # 동적 데이터 캐시 (30초)
STATIC_CACHE_TTL = 300  # 정적 참조 데이터 캐시 (5분)

_client = None
_spreadsheet = None
_worksheets = {}
_cache = {}         # sheet_name -> (timestamp, [dict, ...])  — 동적 데이터
_static_cache = {}  # sheet_name -> (timestamp, [dict, ...])  — 정적 데이터


# ─── 내부 헬퍼 ────────────────────────────────────────────────────────────────

def _get_client():
    global _client
    if _client is None:
        creds_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
        if not creds_json:
            raise RuntimeError('GOOGLE_CREDENTIALS_JSON 환경변수가 설정되지 않았습니다.')
        creds_info = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
        _client = gspread.authorize(creds)
    return _client


def _get_spreadsheet():
    global _spreadsheet
    if _spreadsheet is None:
        spreadsheet_id = os.environ.get('SPREADSHEET_ID')
        if not spreadsheet_id:
            raise RuntimeError('SPREADSHEET_ID 환경변수가 설정되지 않았습니다.')
        _spreadsheet = _get_client().open_by_key(spreadsheet_id)
    return _spreadsheet


def _get_worksheet(name):
    if name not in _worksheets:
        _worksheets[name] = _get_spreadsheet().worksheet(name)
    return _worksheets[name]


def _invalidate(name):
    _cache.pop(name, None)


def _all_rows_static(sheet_name):
    """정적 참조 데이터를 5분 캐시로 반환 (직접 읽기 전용)."""
    now = time.time()
    if sheet_name in _static_cache:
        ts, data = _static_cache[sheet_name]
        if now - ts < STATIC_CACHE_TTL:
            return data
    ws = _get_worksheet(sheet_name)
    records = ws.get_all_records(numericise_ignore=['all'])
    _static_cache[sheet_name] = (now, records)
    return records


def _all_rows(sheet_name):
    """캐시된 전체 행을 dict 리스트로 반환."""
    now = time.time()
    if sheet_name in _cache:
        ts, data = _cache[sheet_name]
        if now - ts < CACHE_TTL:
            return data
    ws = _get_worksheet(sheet_name)
    records = ws.get_all_records(numericise_ignore=['all'])
    _cache[sheet_name] = (now, records)
    return records


def _next_id(sheet_name):
    rows = _all_rows(sheet_name)
    if not rows:
        return 1
    ids = [int(r['id']) for r in rows if r.get('id')]
    return (max(ids) + 1) if ids else 1


def _delete_rows_for_respondent(sheet_name, respondent_id):
    """지정된 respondent_id의 행을 모두 삭제."""
    ws = _get_worksheet(sheet_name)
    all_values = ws.get_all_values()
    if len(all_values) <= 1:
        return
    header = all_values[0]
    rid_col = header.index('respondent_id')
    # 뒤에서부터 삭제해야 행 번호가 바뀌지 않음
    to_delete = [
        idx + 2   # 1-based sheet row: header=1, data starts at 2
        for idx, row in enumerate(all_values[1:])
        if str(row[rid_col]) == str(respondent_id)
    ]
    for sheet_row in reversed(to_delete):
        ws.delete_rows(sheet_row)
    _invalidate(sheet_name)


# ─── RESPONDENTS ──────────────────────────────────────────────────────────────

def insert_respondent(name, organization, job_type, career_stage):
    ws = _get_worksheet('respondents')
    new_id = _next_id('respondents')
    created_at = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    ws.append_row(
        [new_id, name, organization or '', job_type, career_stage, created_at],
        value_input_option='USER_ENTERED'
    )
    _invalidate('respondents')
    return {
        'id': new_id,
        'name': name,
        'organization': organization or '',
        'job_type': job_type,
        'career_stage': career_stage,
        'created_at': created_at,
    }


def get_respondent_by_id(respondent_id):
    for r in _all_rows('respondents'):
        if int(r['id']) == respondent_id:
            return {
                'id': int(r['id']),
                'name': r['name'],
                'organization': r['organization'],
                'job_type': r['job_type'],
                'career_stage': r['career_stage'],
                'created_at': r['created_at'],
            }
    return None


# ─── DIAGNOSIS RESULTS ────────────────────────────────────────────────────────

def delete_diagnosis_by_respondent(respondent_id):
    _delete_rows_for_respondent('diagnosis_results', respondent_id)


def insert_diagnosis_results(respondent_id, results):
    """results: list of {competency_id, scenario_id, likert_score}"""
    ws = _get_worksheet('diagnosis_results')
    next_id = _next_id('diagnosis_results')
    rows = []
    for r in results:
        rows.append([
            next_id, respondent_id,
            r['competency_id'], r['scenario_id'],
            r['likert_score'], '', 1
        ])
        next_id += 1
    if rows:
        ws.append_rows(rows, value_input_option='USER_ENTERED')
    _invalidate('diagnosis_results')


def get_diagnosis_rows(respondent_id, active_only=True):
    result = []
    for r in _all_rows('diagnosis_results'):
        if int(r['respondent_id']) != respondent_id:
            continue
        if active_only and str(r['is_active']) != '1':
            continue
        result.append({
            'id': int(r['id']),
            'respondent_id': int(r['respondent_id']),
            'competency_id': int(r['competency_id']),
            'scenario_id': int(r['scenario_id']),
            'likert_score': int(r['likert_score']),
            'priority_rank': int(r['priority_rank']) if r.get('priority_rank') else None,
            'is_active': int(r['is_active']),
        })
    return result


def update_priority_ranks(respondent_id, rank_map):
    """rank_map: {competency_id: priority_rank}"""
    ws = _get_worksheet('diagnosis_results')
    all_values = ws.get_all_values()
    if len(all_values) <= 1:
        return
    header = all_values[0]
    rid_col = header.index('respondent_id')
    cid_col = header.index('competency_id')
    rank_col = header.index('priority_rank')
    active_col = header.index('is_active')

    cell_updates = []
    for i, row in enumerate(all_values[1:], start=2):
        if str(row[rid_col]) != str(respondent_id):
            continue
        if str(row[active_col]) != '1':
            continue
        comp_id = int(row[cid_col])
        if comp_id in rank_map:
            cell_updates.append(gspread.Cell(i, rank_col + 1, rank_map[comp_id]))
    if cell_updates:
        ws.update_cells(cell_updates)
    _invalidate('diagnosis_results')


def update_diagnosis_rankings(respondent_id, rankings):
    """rankings: list of {competency_id, priority_rank, is_active}"""
    ws = _get_worksheet('diagnosis_results')
    all_values = ws.get_all_values()
    if len(all_values) <= 1:
        return
    header = all_values[0]
    rid_col = header.index('respondent_id')
    cid_col = header.index('competency_id')
    rank_col = header.index('priority_rank')
    active_col = header.index('is_active')

    ranking_map = {int(item['competency_id']): item for item in rankings}
    cell_updates = []
    for i, row in enumerate(all_values[1:], start=2):
        if str(row[rid_col]) != str(respondent_id):
            continue
        comp_id = int(row[cid_col])
        if comp_id in ranking_map:
            item = ranking_map[comp_id]
            cell_updates.append(gspread.Cell(i, rank_col + 1, item['priority_rank']))
            cell_updates.append(gspread.Cell(i, active_col + 1, item.get('is_active', 1)))
    if cell_updates:
        ws.update_cells(cell_updates)
    _invalidate('diagnosis_results')


# ─── ROADMAP ITEMS ────────────────────────────────────────────────────────────

def delete_roadmap_by_respondent(respondent_id):
    _delete_rows_for_respondent('roadmap_items', respondent_id)


def insert_roadmap_items(items):
    """items: list of {respondent_id, course_id, competency_id, order_index, phase}"""
    ws = _get_worksheet('roadmap_items')
    next_id = _next_id('roadmap_items')
    rows = []
    for item in items:
        rows.append([
            next_id, item['respondent_id'], item['course_id'],
            item['competency_id'], item['order_index'], item['phase']
        ])
        next_id += 1
    if rows:
        ws.append_rows(rows, value_input_option='USER_ENTERED')
    _invalidate('roadmap_items')


def get_roadmap_rows(respondent_id):
    result = []
    for r in _all_rows('roadmap_items'):
        if int(r['respondent_id']) != respondent_id:
            continue
        result.append({
            'id': int(r['id']),
            'respondent_id': int(r['respondent_id']),
            'course_id': int(r['course_id']),
            'competency_id': int(r['competency_id']),
            'order_index': int(r['order_index']),
            'phase': r['phase'],
        })
    result.sort(key=lambda x: (x['phase'], x['order_index']))
    return result


def update_roadmap_items(respondent_id, items):
    """items: list of {id, order_index, phase}"""
    ws = _get_worksheet('roadmap_items')
    all_values = ws.get_all_values()
    if len(all_values) <= 1:
        return
    header = all_values[0]
    id_col = header.index('id')
    rid_col = header.index('respondent_id')
    order_col = header.index('order_index')
    phase_col = header.index('phase')

    item_map = {int(item['id']): item for item in items}
    cell_updates = []
    for i, row in enumerate(all_values[1:], start=2):
        if str(row[rid_col]) != str(respondent_id):
            continue
        row_id = int(row[id_col])
        if row_id in item_map:
            cell_updates.append(gspread.Cell(i, order_col + 1, item_map[row_id]['order_index']))
            cell_updates.append(gspread.Cell(i, phase_col + 1, item_map[row_id]['phase']))
    if cell_updates:
        ws.update_cells(cell_updates)
    _invalidate('roadmap_items')


# ─── 정적 참조 데이터 (Google Sheets에서 읽기 전용, 5분 캐시) ─────────────────

def get_competency_groups():
    """competency_groups 전체 반환. sub_category가 빈 문자열이면 None으로 정규화."""
    result = []
    for r in _all_rows_static('competency_groups'):
        result.append({
            'id': int(r['id']),
            'name': r['name'],
            'sub_category': r['sub_category'] if r.get('sub_category') else None,
        })
    return result


def get_competencies():
    """competencies 전체 반환."""
    return [
        {
            'id': int(r['id']),
            'group_id': int(r['group_id']),
            'name': r['name'],
            'description': r.get('description', ''),
        }
        for r in _all_rows_static('competencies')
    ]


def get_scenarios():
    """scenarios 전체 반환."""
    return [
        {
            'id': int(r['id']),
            'group_id': int(r['group_id']),
            'situation': r['situation'],
        }
        for r in _all_rows_static('scenarios')
    ]


def get_scenario_competencies():
    """scenario_competencies 전체 반환."""
    return [
        {
            'id': int(r['id']),
            'scenario_id': int(r['scenario_id']),
            'competency_id': int(r['competency_id']),
        }
        for r in _all_rows_static('scenario_competencies')
    ]


def get_courses():
    """courses 전체 반환."""
    return [
        {
            'id': int(r['id']),
            'competency_id': int(r['competency_id']),
            'name': r['name'],
            'description': r.get('description', ''),
            'duration_hours': int(r['duration_hours']) if r.get('duration_hours') else 0,
            'semester': r.get('semester', ''),
        }
        for r in _all_rows_static('courses')
    ]
