"""
AI-powered features routes
Handles person blueprint, Q&A, and tag suggestions
"""
from flask import Blueprint, request, jsonify, session

from services.ai_service import AIService
from services.person_service import PersonService
from services.note_service import NoteService
from middleware.auth_middleware import login_required
from utils.response import APIResponse
from utils.logger import get_logger

logger = get_logger(__name__)

ai_bp = Blueprint('ai_routes', __name__, url_prefix='/api')

ai_service: AIService = None
person_service: PersonService = None
note_service: NoteService = None


def init_ai_routes(ai_svc: AIService, person_svc: PersonService, note_svc: NoteService = None):
    global ai_service, person_service, note_service
    ai_service = ai_svc
    person_service = person_svc
    note_service = note_svc


@ai_bp.route('/people/<person_id>/summary', methods=['POST'])
@login_required
def generate_summary(person_id):
    try:
        if not ai_service.is_enabled():
            return APIResponse.error('AI feature not configured. Set GEMINI_API_KEY.', 503)
        user_id = session.get('user_id')
        person = person_service.get_person_by_id(person_id, user_id)
        if not person:
            return APIResponse.not_found('Person not found')

        notes = []
        if note_service:
            notes = note_service.get_notes_for_person(person_id, user_id)
        result = ai_service.generate_person_blueprint(person, notes)
        return jsonify(result)
    except ValueError as e:
        return APIResponse.validation_error(str(e))
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return APIResponse.server_error()


@ai_bp.route('/ask', methods=['POST'])
@login_required
def central_ask():
    try:
        if not ai_service.is_enabled():
            return APIResponse.error('AI feature not configured. Set GEMINI_API_KEY.', 503)
        data = request.get_json()
        question = data.get('question', '').strip()
        if not question:
            return APIResponse.validation_error('Question is required')
        user_id = session.get('user_id')
        people = person_service.get_all_people(user_id)
        if not people:
            return APIResponse.validation_error('No people in your contacts yet')
        result = ai_service.answer_question(question, people)
        return jsonify(result)
    except ValueError as e:
        return APIResponse.validation_error(str(e))
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        return APIResponse.server_error()


@ai_bp.route('/people/<person_id>/suggest-tags', methods=['POST'])
@login_required
def suggest_tags(person_id):
    try:
        if not ai_service.is_enabled():
            return APIResponse.error('AI feature not configured. Set GEMINI_API_KEY.', 503)
        user_id = session.get('user_id')
        person = person_service.get_person_by_id(person_id, user_id)
        if not person:
            return APIResponse.not_found('Person not found')
        tags = ai_service.suggest_tags(person)
        return jsonify({'tags': tags})
    except Exception as e:
        logger.error(f"Error suggesting tags: {e}")
        return APIResponse.server_error()
