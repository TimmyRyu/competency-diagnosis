from flask import Blueprint, request, jsonify
from collections import defaultdict
from models import get_db
import sheets

roadmap_bp = Blueprint('roadmap', __name__)

SEMESTER_ORDER = {'상반기': 1, '하반기': 2, '상시': 3}


def _courses_map(conn):
    rows = conn.execute(
        'SELECT id, competency_id, name, description, duration_hours, semester FROM courses'
    ).fetchall()
    return {r['id']: dict(r) for r in rows}


def _competencies_map(conn):
    rows = conn.execute('SELECT id, name FROM competencies').fetchall()
    return {r['id']: dict(r) for r in rows}


@roadmap_bp.route('/courses/<int:respondent_id>', methods=['GET'])
def get_courses(respondent_id):
    diag_rows = sheets.get_diagnosis_rows(respondent_id, active_only=True)
    if not diag_rows:
        return jsonify([])

    priority_map = {}
    for row in diag_rows:
        cid, rank = row['competency_id'], row['priority_rank']
        if rank is not None and (cid not in priority_map or rank < priority_map[cid]):
            priority_map[cid] = rank

    conn = get_db()
    all_courses = _courses_map(conn)
    comp_map = _competencies_map(conn)
    conn.close()

    active_cids = {r['competency_id'] for r in diag_rows}
    grouped = {}
    for cid_key, course in all_courses.items():
        cid = course['competency_id']
        if cid not in active_cids:
            continue
        if cid not in grouped:
            grouped[cid] = {
                'competency_id': cid,
                'competency_name': comp_map.get(cid, {}).get('name', ''),
                'priority_rank': priority_map.get(cid),
                'courses': [],
            }
        grouped[cid]['courses'].append({
            'id': cid_key,
            'name': course['name'],
            'description': course['description'],
            'duration_hours': course['duration_hours'],
            'semester': course['semester'],
        })

    for cid in grouped:
        grouped[cid]['courses'].sort(key=lambda c: SEMESTER_ORDER.get(c['semester'], 99))

    return jsonify(sorted(grouped.values(), key=lambda x: x['priority_rank'] or 999))


@roadmap_bp.route('/roadmap/<int:respondent_id>/generate', methods=['POST'])
def generate_roadmap(respondent_id):
    diag_rows = sheets.get_diagnosis_rows(respondent_id, active_only=True)
    diag_rows = [r for r in diag_rows if r['priority_rank'] is not None]
    if not diag_rows:
        return jsonify({'error': 'No diagnosis results found'}), 404

    comp_priority = {}
    for row in diag_rows:
        cid, rank = row['competency_id'], row['priority_rank']
        if cid not in comp_priority or rank < comp_priority[cid]:
            comp_priority[cid] = rank

    sorted_comps = sorted(comp_priority.items(), key=lambda x: x[1])
    total = len(sorted_comps)
    phase1_cut = max(1, total // 3)
    phase2_cut = max(phase1_cut + 1, 2 * total // 3)

    conn = get_db()
    course_rows = conn.execute('SELECT id, competency_id, semester FROM courses').fetchall()
    conn.close()

    courses_by_comp = defaultdict(list)
    for c in course_rows:
        courses_by_comp[c['competency_id']].append(dict(c))
    for cid in courses_by_comp:
        courses_by_comp[cid].sort(key=lambda c: SEMESTER_ORDER.get(c['semester'], 99))

    sheets.delete_roadmap_by_respondent(respondent_id)

    items, order_index = [], 0
    for i, (comp_id, _) in enumerate(sorted_comps):
        phase = 'Phase 1' if i < phase1_cut else ('Phase 2' if i < phase2_cut else 'Phase 3')
        for course in courses_by_comp.get(comp_id, []):
            items.append({
                'respondent_id': respondent_id,
                'course_id': course['id'],
                'competency_id': comp_id,
                'order_index': order_index,
                'phase': phase,
            })
            order_index += 1

    sheets.insert_roadmap_items(items)
    return jsonify({'message': 'Roadmap generated successfully'}), 201


@roadmap_bp.route('/roadmap/<int:respondent_id>', methods=['GET'])
def get_roadmap(respondent_id):
    roadmap_rows = sheets.get_roadmap_rows(respondent_id)

    course_ids = list({r['course_id'] for r in roadmap_rows})
    comp_ids = list({r['competency_id'] for r in roadmap_rows})

    phases = {'Phase 1': [], 'Phase 2': [], 'Phase 3': []}
    if not roadmap_rows:
        return jsonify(phases)

    conn = get_db()
    course_map = {r['id']: dict(r) for r in conn.execute(
        f"SELECT id, name, description, duration_hours, semester FROM courses "
        f"WHERE id IN ({','.join('?' * len(course_ids))})", course_ids
    ).fetchall()}
    comp_map = {r['id']: dict(r) for r in conn.execute(
        f"SELECT id, name FROM competencies WHERE id IN ({','.join('?' * len(comp_ids))})", comp_ids
    ).fetchall()}
    conn.close()

    for r in roadmap_rows:
        course = course_map.get(r['course_id'], {})
        comp = comp_map.get(r['competency_id'], {})
        item = {
            'id': r['id'],
            'order_index': r['order_index'],
            'phase': r['phase'],
            'competency_id': r['competency_id'],
            'competency_name': comp.get('name', ''),
            'course_id': r['course_id'],
            'course_name': course.get('name', ''),
            'course_description': course.get('description', ''),
            'duration_hours': course.get('duration_hours'),
            'semester': course.get('semester', ''),
        }
        if r['phase'] in phases:
            phases[r['phase']].append(item)

    return jsonify(phases)


@roadmap_bp.route('/roadmap/<int:respondent_id>', methods=['PUT'])
def update_roadmap(respondent_id):
    data = request.get_json()
    items = data.get('items', [])
    if not items:
        return jsonify({'error': 'items are required'}), 400
    sheets.update_roadmap_items(respondent_id, items)
    return jsonify({'message': 'Roadmap updated successfully'})
