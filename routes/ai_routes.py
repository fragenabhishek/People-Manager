"""
AI-powered features routes
Handles person blueprint, Q&A, and tag suggestions
"""
from flask import Blueprint, current_app, request, session

from middleware.auth_middleware import login_required
from utils.response import APIResponse

ai_bp = Blueprint('ai_routes', __name__, url_prefix='/api')


def _ai():
    return current_app.config['ai_service']

def _people():
    return current_app.config['person_service']

def _notes():
    return current_app.config.get('note_service')


@ai_bp.route('/people/<person_id>/summary', methods=['POST'])
@login_required
def generate_summary(person_id):
    if not _ai().is_enabled():
        return APIResponse.error('AI feature not configured. Set GEMINI_API_KEY.', 503)

    person = _people().get_person_by_id(person_id, session['user_id'])
    if not person:
        return APIResponse.not_found('Person not found')

    notes = []
    if _notes():
        notes = _notes().get_notes_for_person(person_id, session['user_id'])
    result = _ai().generate_person_blueprint(person, notes)
    return APIResponse.success(result)


@ai_bp.route('/ask', methods=['POST'])
@login_required
def central_ask():
    if not _ai().is_enabled():
        return APIResponse.error('AI feature not configured. Set GEMINI_API_KEY.', 503)

    data = request.get_json()
    question = data.get('question', '').strip()
    if not question:
        return APIResponse.validation_error('Question is required')

    people = _people().get_all_people(session['user_id'])
    if not people:
        return APIResponse.validation_error('No people in your contacts yet')

    result = _ai().answer_question(question, people)
    return APIResponse.success(result)


@ai_bp.route('/people/<person_id>/suggest-tags', methods=['POST'])
@login_required
def suggest_tags(person_id):
    if not _ai().is_enabled():
        return APIResponse.error('AI feature not configured. Set GEMINI_API_KEY.', 503)

    person = _people().get_person_by_id(person_id, session['user_id'])
    if not person:
        return APIResponse.not_found('Person not found')

    tags = _ai().suggest_tags(person)
    return APIResponse.success({'tags': tags})
