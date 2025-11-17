"""
AI-powered features routes
Handles person blueprint and Q&A endpoints
"""
from flask import Blueprint, request, jsonify, session

from services.ai_service import AIService
from services.person_service import PersonService
from middleware.auth_middleware import login_required
from utils.response import APIResponse
from utils.logger import get_logger

logger = get_logger(__name__)

# Create blueprint
ai_bp = Blueprint('ai_routes', __name__, url_prefix='/api')

# Services will be injected
ai_service: AIService = None
person_service: PersonService = None


def init_ai_routes(ai_svc: AIService, person_svc: PersonService):
    """Initialize routes with service dependencies"""
    global ai_service, person_service
    ai_service = ai_svc
    person_service = person_svc


@ai_bp.route('/people/<person_id>/summary', methods=['POST'])
@login_required
def generate_summary(person_id):
    """Generate AI-powered person blueprint"""
    try:
        # Check if AI is enabled
        if not ai_service.is_enabled():
            return APIResponse.error(
                'AI feature not configured. Please set GEMINI_API_KEY environment variable.',
                503
            )
        
        # Get person
        user_id = session.get('user_id')
        person = person_service.get_person_by_id(person_id, user_id)
        
        if not person:
            return APIResponse.not_found('Person not found')
        
        # Generate blueprint
        result = ai_service.generate_person_blueprint(person)
        return jsonify(result)
    
    except ValueError as e:
        return APIResponse.validation_error(str(e))
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return APIResponse.server_error(f'Failed to generate summary: {str(e)}')


@ai_bp.route('/ask', methods=['POST'])
@login_required
def central_ask():
    """Central Q&A - Ask questions about any person or across all people"""
    try:
        # Check if AI is enabled
        if not ai_service.is_enabled():
            return APIResponse.error(
                'AI feature not configured. Please set GEMINI_API_KEY environment variable.',
                503
            )
        
        # Get question
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return APIResponse.validation_error('Question is required')
        
        # Get all people for context
        user_id = session.get('user_id')
        people = person_service.get_all_people(user_id)
        
        if not people:
            return APIResponse.validation_error('No people in your contacts yet')
        
        # Answer question
        result = ai_service.answer_question(question, people)
        return jsonify(result)
    
    except ValueError as e:
        return APIResponse.validation_error(str(e))
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        return APIResponse.server_error(f'Failed to answer question: {str(e)}')

