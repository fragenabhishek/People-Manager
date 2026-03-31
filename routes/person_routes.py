"""
Person/contact management routes
Handles CRUD, tags, follow-ups, import/export
"""
from flask import Blueprint, Response, current_app, request, session

from middleware.auth_middleware import login_required
from utils.response import APIResponse
from utils.validators import ValidationError

person_bp = Blueprint('person_routes', __name__, url_prefix='/api/people')


def _svc():
    return current_app.config['person_service']

def _ie_svc():
    return current_app.config['import_export_service']


# --- CRUD ---

@person_bp.route('', methods=['GET'])
@login_required
def get_people():
    user_id = session['user_id']
    tag = request.args.get('tag')
    if tag:
        people = _svc().get_by_tag(tag, user_id)
    else:
        people = _svc().get_all_people(user_id)
    return APIResponse.success([p.to_dict() for p in people])


@person_bp.route('/<person_id>', methods=['GET'])
@login_required
def get_person(person_id):
    person = _svc().get_person_by_id(person_id, session['user_id'])
    if not person:
        return APIResponse.not_found('Person not found')
    return APIResponse.success(person.to_dict())


@person_bp.route('/search/<query>', methods=['GET'])
@login_required
def search_people(query):
    results = _svc().search_people(query, session['user_id'])
    return APIResponse.success([p.to_dict() for p in results])


@person_bp.route('', methods=['POST'])
@login_required
def add_person():
    data = request.get_json()
    person = _svc().create_person(user_id=session['user_id'], **data)
    return APIResponse.created(person.to_dict(), "Person created successfully")


@person_bp.route('/<person_id>', methods=['PUT'])
@login_required
def update_person(person_id):
    data = request.get_json()
    person = _svc().update_person(person_id, session['user_id'], **data)
    if not person:
        return APIResponse.not_found('Person not found')
    return APIResponse.success(person.to_dict())


@person_bp.route('/<person_id>', methods=['DELETE'])
@login_required
def delete_person(person_id):
    success = _svc().delete_person(person_id, session['user_id'])
    if not success:
        return APIResponse.not_found('Person not found')
    return APIResponse.success(message='Person deleted successfully')


# --- Tags ---

@person_bp.route('/tags', methods=['GET'])
@login_required
def get_all_tags():
    tags = _svc().get_all_tags(session['user_id'])
    return APIResponse.success(tags)


@person_bp.route('/<person_id>/tags', methods=['POST'])
@login_required
def add_tags(person_id):
    data = request.get_json()
    tags = data.get('tags', [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(',') if t.strip()]
    person = _svc().add_tags(person_id, session['user_id'], tags)
    if not person:
        return APIResponse.not_found('Person not found')
    return APIResponse.success(person.to_dict())


@person_bp.route('/<person_id>/tags/<tag>', methods=['DELETE'])
@login_required
def remove_tag(person_id, tag):
    person = _svc().remove_tag(person_id, session['user_id'], tag)
    if not person:
        return APIResponse.not_found('Person not found')
    return APIResponse.success(person.to_dict())


# --- Follow-ups ---

@person_bp.route('/followups', methods=['GET'])
@login_required
def get_due_followups():
    people = _svc().get_due_followups(session['user_id'])
    return APIResponse.success([p.to_dict() for p in people])


@person_bp.route('/<person_id>/followup', methods=['PUT'])
@login_required
def set_follow_up(person_id):
    data = request.get_json()
    person = _svc().set_follow_up(
        person_id, session['user_id'],
        date=data.get('date', ''),
        frequency_days=int(data.get('frequency_days', 0))
    )
    if not person:
        return APIResponse.not_found('Person not found')
    return APIResponse.success(person.to_dict())


@person_bp.route('/<person_id>/followup/complete', methods=['POST'])
@login_required
def complete_follow_up(person_id):
    person = _svc().complete_follow_up(person_id, session['user_id'])
    if not person:
        return APIResponse.not_found('Person not found')
    return APIResponse.success(person.to_dict())


# --- Dashboard ---

@person_bp.route('/dashboard/stats', methods=['GET'])
@login_required
def dashboard_stats():
    stats = _svc().get_dashboard_stats(session['user_id'])
    return APIResponse.success(stats)


# --- Import/Export ---

@person_bp.route('/import/csv', methods=['POST'])
@login_required
def import_csv():
    if 'file' not in request.files:
        return APIResponse.validation_error('No file provided')
    file = request.files['file']
    if not file.filename.endswith('.csv'):
        return APIResponse.validation_error('File must be CSV format')
    content = file.read().decode('utf-8')
    imported, skipped, errors = _ie_svc().import_csv(content, session['user_id'])
    return APIResponse.success({
        'imported': imported,
        'skipped': skipped,
        'errors': errors[:10],
    })


@person_bp.route('/export/csv', methods=['GET'])
@login_required
def export_csv():
    csv_content = _ie_svc().export_csv(session['user_id'])
    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=contacts.csv'}
    )


@person_bp.route('/export/json', methods=['GET'])
@login_required
def export_json():
    json_content = _ie_svc().export_json(session['user_id'])
    return Response(
        json_content,
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment; filename=contacts.json'}
    )
