"""
Person/contact management routes
Handles CRUD, tags, follow-ups, import/export
"""
from flask import Blueprint, request, jsonify, session, Response

from services.person_service import PersonService
from services.import_export_service import ImportExportService
from middleware.auth_middleware import login_required
from utils.response import APIResponse
from utils.validators import ValidationError
from utils.logger import get_logger

logger = get_logger(__name__)

person_bp = Blueprint('person_routes', __name__, url_prefix='/api/people')

person_service: PersonService = None
import_export_service: ImportExportService = None


def init_person_routes(service: PersonService, ie_service: ImportExportService = None):
    global person_service, import_export_service
    person_service = service
    import_export_service = ie_service


@person_bp.route('', methods=['GET'])
@login_required
def get_people():
    try:
        user_id = session.get('user_id')
        tag = request.args.get('tag')
        if tag:
            people = person_service.get_by_tag(tag, user_id)
        else:
            people = person_service.get_all_people(user_id)
        return jsonify([p.to_dict() for p in people])
    except Exception as e:
        logger.error(f"Error getting people: {e}")
        return APIResponse.server_error()


@person_bp.route('/<person_id>', methods=['GET'])
@login_required
def get_person(person_id):
    try:
        user_id = session.get('user_id')
        person = person_service.get_person_by_id(person_id, user_id)
        if person:
            return jsonify(person.to_dict())
        return APIResponse.not_found('Person not found')
    except Exception as e:
        logger.error(f"Error getting person: {e}")
        return APIResponse.server_error()


@person_bp.route('/search/<query>', methods=['GET'])
@login_required
def search_people(query):
    try:
        user_id = session.get('user_id')
        results = person_service.search_people(query, user_id)
        return jsonify([p.to_dict() for p in results])
    except Exception as e:
        logger.error(f"Error searching people: {e}")
        return APIResponse.server_error()


@person_bp.route('', methods=['POST'])
@login_required
def add_person():
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        person = person_service.create_person(user_id=user_id, **data)
        return APIResponse.created(person.to_dict(), "Person created successfully")
    except ValidationError as e:
        return APIResponse.validation_error(str(e))
    except Exception as e:
        logger.error(f"Error creating person: {e}")
        return APIResponse.server_error()


@person_bp.route('/<person_id>', methods=['PUT'])
@login_required
def update_person(person_id):
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        person = person_service.update_person(person_id, user_id, **data)
        if person:
            return jsonify(person.to_dict())
        return APIResponse.not_found('Person not found')
    except ValidationError as e:
        return APIResponse.validation_error(str(e))
    except Exception as e:
        logger.error(f"Error updating person: {e}")
        return APIResponse.server_error()


@person_bp.route('/<person_id>', methods=['DELETE'])
@login_required
def delete_person(person_id):
    try:
        user_id = session.get('user_id')
        success = person_service.delete_person(person_id, user_id)
        if success:
            return jsonify({'message': 'Person deleted successfully'})
        return APIResponse.not_found('Person not found')
    except Exception as e:
        logger.error(f"Error deleting person: {e}")
        return APIResponse.server_error()


# --- Tags ---

@person_bp.route('/tags', methods=['GET'])
@login_required
def get_all_tags():
    try:
        user_id = session.get('user_id')
        tags = person_service.get_all_tags(user_id)
        return jsonify(tags)
    except Exception as e:
        logger.error(f"Error getting tags: {e}")
        return APIResponse.server_error()


@person_bp.route('/<person_id>/tags', methods=['POST'])
@login_required
def add_tags(person_id):
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        tags = data.get('tags', [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',') if t.strip()]
        person = person_service.add_tags(person_id, user_id, tags)
        if person:
            return jsonify(person.to_dict())
        return APIResponse.not_found('Person not found')
    except Exception as e:
        logger.error(f"Error adding tags: {e}")
        return APIResponse.server_error()


@person_bp.route('/<person_id>/tags/<tag>', methods=['DELETE'])
@login_required
def remove_tag(person_id, tag):
    try:
        user_id = session.get('user_id')
        person = person_service.remove_tag(person_id, user_id, tag)
        if person:
            return jsonify(person.to_dict())
        return APIResponse.not_found('Person not found')
    except Exception as e:
        logger.error(f"Error removing tag: {e}")
        return APIResponse.server_error()


# --- Follow-ups ---

@person_bp.route('/followups', methods=['GET'])
@login_required
def get_due_followups():
    try:
        user_id = session.get('user_id')
        people = person_service.get_due_followups(user_id)
        return jsonify([p.to_dict() for p in people])
    except Exception as e:
        logger.error(f"Error getting follow-ups: {e}")
        return APIResponse.server_error()


@person_bp.route('/<person_id>/followup', methods=['PUT'])
@login_required
def set_follow_up(person_id):
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        person = person_service.set_follow_up(
            person_id, user_id,
            date=data.get('date', ''),
            frequency_days=int(data.get('frequency_days', 0))
        )
        if person:
            return jsonify(person.to_dict())
        return APIResponse.not_found('Person not found')
    except Exception as e:
        logger.error(f"Error setting follow-up: {e}")
        return APIResponse.server_error()


@person_bp.route('/<person_id>/followup/complete', methods=['POST'])
@login_required
def complete_follow_up(person_id):
    try:
        user_id = session.get('user_id')
        person = person_service.complete_follow_up(person_id, user_id)
        if person:
            return jsonify(person.to_dict())
        return APIResponse.not_found('Person not found')
    except Exception as e:
        logger.error(f"Error completing follow-up: {e}")
        return APIResponse.server_error()


# --- Dashboard ---

@person_bp.route('/dashboard/stats', methods=['GET'])
@login_required
def dashboard_stats():
    try:
        user_id = session.get('user_id')
        stats = person_service.get_dashboard_stats(user_id)
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return APIResponse.server_error()


# --- Import/Export ---

@person_bp.route('/import/csv', methods=['POST'])
@login_required
def import_csv():
    try:
        user_id = session.get('user_id')
        if 'file' not in request.files:
            return APIResponse.validation_error('No file provided')
        file = request.files['file']
        if not file.filename.endswith('.csv'):
            return APIResponse.validation_error('File must be CSV format')
        content = file.read().decode('utf-8')
        imported, skipped, errors = import_export_service.import_csv(content, user_id)
        return jsonify({
            'imported': imported,
            'skipped': skipped,
            'errors': errors[:10],
        })
    except Exception as e:
        logger.error(f"Error importing CSV: {e}")
        return APIResponse.server_error()


@person_bp.route('/export/csv', methods=['GET'])
@login_required
def export_csv():
    try:
        user_id = session.get('user_id')
        csv_content = import_export_service.export_csv(user_id)
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=contacts.csv'}
        )
    except Exception as e:
        logger.error(f"Error exporting CSV: {e}")
        return APIResponse.server_error()


@person_bp.route('/export/json', methods=['GET'])
@login_required
def export_json():
    try:
        user_id = session.get('user_id')
        json_content = import_export_service.export_json(user_id)
        return Response(
            json_content,
            mimetype='application/json',
            headers={'Content-Disposition': 'attachment; filename=contacts.json'}
        )
    except Exception as e:
        logger.error(f"Error exporting JSON: {e}")
        return APIResponse.server_error()
