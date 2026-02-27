from flask import Blueprint, request, jsonify
from models import get_db
import sheets

respondent_bp = Blueprint('respondent', __name__)


@respondent_bp.route('/respondents', methods=['POST'])
def create_respondent():
    data = request.get_json()
    for field in ['name', 'job_type', 'career_stage']:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    new_respondent = sheets.insert_respondent(
        name=data['name'],
        organization=data.get('organization', ''),
        job_type=data['job_type'],
        career_stage=data['career_stage'],
    )
    return jsonify(new_respondent), 201


@respondent_bp.route('/respondents/<int:respondent_id>', methods=['GET'])
def get_respondent(respondent_id):
    respondent = sheets.get_respondent_by_id(respondent_id)
    if not respondent:
        return jsonify({'error': 'Respondent not found'}), 404
    return jsonify(respondent)


@respondent_bp.route('/competencies', methods=['GET'])
def get_competencies():
    job_type = request.args.get('job_type')
    career_stage = request.args.get('career_stage')
    if not job_type or not career_stage:
        return jsonify({'error': 'job_type and career_stage are required'}), 400

    conn = get_db()
    rows = conn.execute('''
        SELECT c.id, c.group_id, c.name, c.description, g.name as group_name, g.sub_category
        FROM competencies c
        JOIN competency_groups g ON c.group_id = g.id
        WHERE g.sub_category IS NULL
           OR (g.name = '리더십' AND g.sub_category = ?)
           OR (g.name = '직무역량' AND g.sub_category = ?)
        ORDER BY g.id, c.id
    ''', (career_stage, job_type)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@respondent_bp.route('/scenarios', methods=['GET'])
def get_scenarios():
    job_type = request.args.get('job_type')
    career_stage = request.args.get('career_stage')
    if not job_type or not career_stage:
        return jsonify({'error': 'job_type and career_stage are required'}), 400

    conn = get_db()
    scenarios = conn.execute('''
        SELECT s.id, s.group_id, s.situation, g.name as group_name, g.sub_category
        FROM scenarios s
        JOIN competency_groups g ON s.group_id = g.id
        WHERE g.sub_category IS NULL
           OR (g.name = '리더십' AND g.sub_category = ?)
           OR (g.name = '직무역량' AND g.sub_category = ?)
        ORDER BY g.id, s.id
    ''', (career_stage, job_type)).fetchall()

    result = []
    for s in scenarios:
        scenario = dict(s)
        comps = conn.execute('''
            SELECT c.id, c.name, c.description
            FROM scenario_competencies sc
            JOIN competencies c ON sc.competency_id = c.id
            WHERE sc.scenario_id = ?
        ''', (s['id'],)).fetchall()
        scenario['competencies'] = [dict(c) for c in comps]
        result.append(scenario)
    conn.close()
    return jsonify(result)
