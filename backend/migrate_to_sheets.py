"""
SQLite 정적 데이터를 Google Sheets로 일괄 복사하는 일회성 스크립트.

실행 방법:
    cd backend
    python3 migrate_to_sheets.py

5개 탭을 생성하고 기존 SQLite 데이터를 그대로 옮깁니다.
이미 탭이 존재하면 내용을 덮어씁니다.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

from models import get_db
import sheets


def _ensure_worksheet(spreadsheet, title, headers):
    """탭이 없으면 생성, 있으면 전체 내용을 초기화 후 헤더만 기록."""
    existing = [ws.title for ws in spreadsheet.worksheets()]
    if title in existing:
        ws = spreadsheet.worksheet(title)
        ws.clear()
        print(f"  [{title}] 기존 탭 초기화")
    else:
        ws = spreadsheet.add_worksheet(title=title, rows=500, cols=len(headers))
        print(f"  [{title}] 새 탭 생성")
    ws.append_row(headers, value_input_option='USER_ENTERED')
    return ws


def migrate():
    print("=== SQLite → Google Sheets 마이그레이션 시작 ===\n")
    conn = get_db()
    spreadsheet = sheets._get_spreadsheet()

    # 1. competency_groups
    ws = _ensure_worksheet(spreadsheet, 'competency_groups', ['id', 'name', 'sub_category'])
    rows = conn.execute('SELECT id, name, sub_category FROM competency_groups ORDER BY id').fetchall()
    data = [[r['id'], r['name'], r['sub_category'] or ''] for r in rows]
    if data:
        ws.append_rows(data, value_input_option='USER_ENTERED')
    print(f"  [competency_groups] {len(data)}행 입력 완료")

    # 2. competencies
    ws = _ensure_worksheet(spreadsheet, 'competencies', ['id', 'group_id', 'name', 'description'])
    rows = conn.execute('SELECT id, group_id, name, description FROM competencies ORDER BY id').fetchall()
    data = [[r['id'], r['group_id'], r['name'], r['description'] or ''] for r in rows]
    if data:
        ws.append_rows(data, value_input_option='USER_ENTERED')
    print(f"  [competencies] {len(data)}행 입력 완료")

    # 3. scenarios
    ws = _ensure_worksheet(spreadsheet, 'scenarios', ['id', 'group_id', 'situation'])
    rows = conn.execute('SELECT id, group_id, situation FROM scenarios ORDER BY id').fetchall()
    data = [[r['id'], r['group_id'], r['situation']] for r in rows]
    if data:
        ws.append_rows(data, value_input_option='USER_ENTERED')
    print(f"  [scenarios] {len(data)}행 입력 완료")

    # 4. scenario_competencies
    ws = _ensure_worksheet(spreadsheet, 'scenario_competencies', ['id', 'scenario_id', 'competency_id'])
    rows = conn.execute('SELECT id, scenario_id, competency_id FROM scenario_competencies ORDER BY id').fetchall()
    data = [[r['id'], r['scenario_id'], r['competency_id']] for r in rows]
    if data:
        ws.append_rows(data, value_input_option='USER_ENTERED')
    print(f"  [scenario_competencies] {len(data)}행 입력 완료")

    # 5. courses
    ws = _ensure_worksheet(spreadsheet, 'courses',
                           ['id', 'competency_id', 'name', 'description', 'duration_hours', 'semester'])
    rows = conn.execute(
        'SELECT id, competency_id, name, description, duration_hours, semester FROM courses ORDER BY id'
    ).fetchall()
    data = [[r['id'], r['competency_id'], r['name'], r['description'] or '',
             r['duration_hours'] or 0, r['semester'] or ''] for r in rows]
    if data:
        ws.append_rows(data, value_input_option='USER_ENTERED')
    print(f"  [courses] {len(data)}행 입력 완료")

    conn.close()
    print("\n=== 마이그레이션 완료 ===")
    print("Google Sheets에서 데이터를 확인하고 자유롭게 편집하세요.")
    print("변경 사항은 최대 5분 이내에 서비스에 반영됩니다.")


if __name__ == '__main__':
    migrate()
