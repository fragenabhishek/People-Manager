"""
Note/interaction routes
Handles CRUD operations for notes attached to people
"""
from flask import Blueprint, request, jsonify, session

from services.note_service import NoteService
from middleware.auth_middleware import login_required
from utils.response import APIResponse
from utils.validators import ValidationError
from utils.logger import get_logger

logger = get_logger(__name__)

note_bp = Blueprint('note_routes', __name__, url_prefix='/api/notes')

note_service: NoteService = None


def init_note_routes(service: NoteService):
    global note_service
    note_service = service


@note_bp.route('/person/<person_id>', methods=['GET'])
@login_required
def get_notes(person_id):
    try:
        user_id = session.get('user_id')
        notes = note_service.get_notes_for_person(person_id, user_id)
        return jsonify([n.to_dict() for n in notes])
    except Exception as e:
        logger.error(f"Error getting notes: {e}")
        return APIResponse.server_error()


@note_bp.route('/person/<person_id>', methods=['POST'])
@login_required
def create_note(person_id):
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        note = note_service.create_note(
            person_id=person_id,
            user_id=user_id,
            content=data.get('content', ''),
            note_type=data.get('note_type', 'general'),
        )
        return APIResponse.created(note.to_dict(), "Note added successfully")
    except ValidationError as e:
        return APIResponse.validation_error(str(e))
    except Exception as e:
        logger.error(f"Error creating note: {e}")
        return APIResponse.server_error()


@note_bp.route('/<note_id>', methods=['DELETE'])
@login_required
def delete_note(note_id):
    try:
        user_id = session.get('user_id')
        success = note_service.delete_note(note_id, user_id)
        if success:
            return jsonify({'message': 'Note deleted'})
        return APIResponse.not_found('Note not found')
    except Exception as e:
        logger.error(f"Error deleting note: {e}")
        return APIResponse.server_error()


@note_bp.route('/activity', methods=['GET'])
@login_required
def get_activity():
    try:
        user_id = session.get('user_id')
        limit = request.args.get('limit', 20, type=int)
        activity = note_service.get_recent_activity(user_id, limit)
        return jsonify(activity)
    except Exception as e:
        logger.error(f"Error getting activity: {e}")
        return APIResponse.server_error()
