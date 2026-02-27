from flask import Blueprint, request, jsonify
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

    groups = {g['id']: g for g in sheets.get_competency_groups()}
    comps = sheets.get_competencies()

    result = []
    for c in comps:
        g = groups.get(c['group_id'], {})
        sub = g.get('sub_category')
        gname = g.get('name', '')
        if (sub is None
                or (gname == '리더십' and sub == career_stage)
                or (gname == '직무역량' and sub == job_type)):
            result.append({
                'id': c['id'],
                'group_id': c['group_id'],
                'name': c['name'],
                'description': c['description'],
                'group_name': gname,
                'sub_category': sub,
            })

    result.sort(key=lambda x: (x['group_id'], x['id']))
    return jsonify(result)


@respondent_bp.route('/scenarios', methods=['GET'])
def get_scenarios():
    job_type = request.args.get('job_type')
    career_stage = request.args.get('career_stage')
    if not job_type or not career_stage:
        return jsonify({'error': 'job_type and career_stage are required'}), 400

    groups = {g['id']: g for g in sheets.get_competency_groups()}
    all_scenarios = sheets.get_scenarios()
    all_comps = {c['id']: c for c in sheets.get_competencies()}
    sc_links = sheets.get_scenario_competencies()

    # 시나리오별 역량 목록 사전 구성
    sc_comp_map = {}
    for link in sc_links:
        sid = link['scenario_id']
        sc_comp_map.setdefault(sid, []).append(link['competency_id'])

    result = []
    for s in all_scenarios:
        g = groups.get(s['group_id'], {})
        sub = g.get('sub_category')
        gname = g.get('name', '')
        if not (sub is None
                or (gname == '리더십' and sub == career_stage)
                or (gname == '직무역량' and sub == job_type)):
            continue

        comps = []
        for cid in sc_comp_map.get(s['id'], []):
            comp = all_comps.get(cid)
            if comp:
                comps.append({'id': comp['id'], 'name': comp['name'], 'description': comp['description']})

        result.append({
            'id': s['id'],
            'group_id': s['group_id'],
            'situation': s['situation'],
            'group_name': gname,
            'sub_category': sub,
            'competencies': comps,
        })

    result.sort(key=lambda x: (x['group_id'], x['id']))
    return jsonify(result)
