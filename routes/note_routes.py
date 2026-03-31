"""
Note/interaction routes
Handles CRUD operations for notes attached to people
"""
from flask import Blueprint, current_app, request, session

from middleware.auth_middleware import login_required
from utils.response import APIResponse
from utils.validators import ValidationError

note_bp = Blueprint('note_routes', __name__, url_prefix='/api/notes')


def _svc():
    return current_app.config['note_service']


@note_bp.route('/person/<person_id>', methods=['GET'])
@login_required
def get_notes(person_id):
    notes = _svc().get_notes_for_person(person_id, session['user_id'])
    return APIResponse.success([n.to_dict() for n in notes])


@note_bp.route('/person/<person_id>', methods=['POST'])
@login_required
def create_note(person_id):
    data = request.get_json()
    note = _svc().create_note(
        person_id=person_id,
        user_id=session['user_id'],
        content=data.get('content', ''),
        note_type=data.get('note_type', 'general'),
    )
    return APIResponse.created(note.to_dict(), "Note added successfully")


@note_bp.route('/<note_id>', methods=['DELETE'])
@login_required
def delete_note(note_id):
    success = _svc().delete_note(note_id, session['user_id'])
    if not success:
        return APIResponse.not_found('Note not found')
    return APIResponse.success(message='Note deleted')


@note_bp.route('/activity', methods=['GET'])
@login_required
def get_activity():
    limit = request.args.get('limit', 20, type=int)
    activity = _svc().get_recent_activity(session['user_id'], limit)
    return APIResponse.success(activity)
