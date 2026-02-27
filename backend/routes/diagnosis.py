from flask import Blueprint, request, jsonify
from collections import defaultdict
import sheets

diagnosis_bp = Blueprint('diagnosis', __name__)


def compute_priorities(respondent_id):
    """선택 횟수 × 평균 리커트 점수로 우선순위 산출 후 Sheets에 기록."""
    rows = sheets.get_diagnosis_rows(respondent_id, active_only=True)

    groups = defaultdict(list)
    for row in rows:
        groups[row['competency_id']].append(row['likert_score'])

    scored = []
    for comp_id, scores in groups.items():
        count = len(scores)
        avg = sum(scores) / count
        scored.append((comp_id, count * avg))

    scored.sort(key=lambda x: x[1], reverse=True)
    rank_map = {comp_id: rank for rank, (comp_id, _) in enumerate(scored, 1)}
    sheets.update_priority_ranks(respondent_id, rank_map)
    return rank_map


@diagnosis_bp.route('/diagnosis', methods=['POST'])
def save_diagnosis():
    data = request.get_json()
    respondent_id = data.get('respondent_id')
    results = data.get('results', [])
    if not respondent_id or not results:
        return jsonify({'error': 'respondent_id and results are required'}), 400

    sheets.delete_diagnosis_by_respondent(respondent_id)
    sheets.insert_diagnosis_results(respondent_id, results)
    compute_priorities(respondent_id)
    return jsonify({'message': 'Diagnosis saved successfully'}), 201


@diagnosis_bp.route('/diagnosis/<int:respondent_id>', methods=['GET'])
def get_diagnosis(respondent_id):
    rows = sheets.get_diagnosis_rows(respondent_id, active_only=True)
    if not rows:
        return jsonify([])

    # 역량명/그룹명을 Sheets에서 조회
    comp_map = {c['id']: c for c in sheets.get_competencies()}
    groups_map = {g['id']: g for g in sheets.get_competency_groups()}

    # Python에서 GROUP BY 집계
    grouped = defaultdict(list)
    for row in rows:
        grouped[row['competency_id']].append(row)

    result = []
    for comp_id, comp_rows_list in grouped.items():
        count = len(comp_rows_list)
        avg_likert = sum(r['likert_score'] for r in comp_rows_list) / count
        score = count * avg_likert
        priority_rank = min(
            (r['priority_rank'] for r in comp_rows_list if r['priority_rank'] is not None),
            default=None
        )
        comp_info = comp_map.get(comp_id, {})
        group_info = groups_map.get(comp_info.get('group_id'), {})
        result.append({
            'competency_id': comp_id,
            'competency_name': comp_info.get('name', ''),
            'competency_description': comp_info.get('description', ''),
            'group_name': group_info.get('name', ''),
            'selection_count': count,
            'avg_likert': avg_likert,
            'score': score,
            'priority_rank': priority_rank,
            'is_active': 1,
        })

    result.sort(key=lambda x: (x['priority_rank'] is None, x['priority_rank'] or 0))
    return jsonify(result)


@diagnosis_bp.route('/diagnosis/<int:respondent_id>', methods=['PUT'])
def update_diagnosis(respondent_id):
    data = request.get_json()
    rankings = data.get('rankings', [])
    if not rankings:
        return jsonify({'error': 'rankings are required'}), 400
    sheets.update_diagnosis_rankings(respondent_id, rankings)
    return jsonify({'message': 'Rankings updated successfully'})
