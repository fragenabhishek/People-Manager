"""
Person/contact management routes
Handles CRUD operations for people
"""
from flask import Blueprint, request, jsonify, session

from services.person_service import PersonService
from middleware.auth_middleware import login_required
from utils.response import APIResponse
from utils.validators import ValidationError
from utils.logger import get_logger

logger = get_logger(__name__)

# Create blueprint
person_bp = Blueprint('person_routes', __name__, url_prefix='/api/people')

# Service will be injected
person_service: PersonService = None


def init_person_routes(service: PersonService):
    """Initialize routes with service dependency"""
    global person_service
    person_service = service


@person_bp.route('', methods=['GET'])
@login_required
def get_people():
    """Get all people for the logged-in user"""
    try:
        user_id = session.get('user_id')
        people = person_service.get_all_people(user_id)
        return jsonify([p.to_dict() for p in people])
    except Exception as e:
        logger.error(f"Error getting people: {e}")
        return APIResponse.server_error(str(e))


@person_bp.route('/<person_id>', methods=['GET'])
@login_required
def get_person(person_id):
    """Get a specific person by ID"""
    try:
        user_id = session.get('user_id')
        person = person_service.get_person_by_id(person_id, user_id)
        
        if person:
            return jsonify(person.to_dict())
        return APIResponse.not_found('Person not found')
    except Exception as e:
        logger.error(f"Error getting person: {e}")
        return APIResponse.server_error(str(e))


@person_bp.route('/search/<query>', methods=['GET'])
@login_required
def search_people(query):
    """Search people by name"""
    try:
        user_id = session.get('user_id')
        results = person_service.search_people(query, user_id)
        return jsonify([p.to_dict() for p in results])
    except Exception as e:
        logger.error(f"Error searching people: {e}")
        return APIResponse.server_error(str(e))


@person_bp.route('', methods=['POST'])
@login_required
def add_person():
    """Add a new person"""
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        name = data.get('name', '').strip()
        details = data.get('details', '').strip()
        
        person = person_service.create_person(name, details, user_id)
        return APIResponse.created(person.to_dict(), "Person created successfully")
    
    except ValidationError as e:
        return APIResponse.validation_error(str(e))
    except Exception as e:
        logger.error(f"Error creating person: {e}")
        return APIResponse.server_error(str(e))


@person_bp.route('/<person_id>', methods=['PUT'])
@login_required
def update_person(person_id):
    """Update an existing person"""
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        name = data.get('name')
        details = data.get('details')
        
        person = person_service.update_person(person_id, name, details, user_id)
        
        if person:
            return jsonify(person.to_dict())
        return APIResponse.not_found('Person not found')
    
    except ValidationError as e:
        return APIResponse.validation_error(str(e))
    except Exception as e:
        logger.error(f"Error updating person: {e}")
        return APIResponse.server_error(str(e))


@person_bp.route('/<person_id>', methods=['DELETE'])
@login_required
def delete_person(person_id):
    """Delete a person"""
    try:
        user_id = session.get('user_id')
        success = person_service.delete_person(person_id, user_id)
        
        if success:
            return jsonify({'message': 'Person deleted successfully'})
        return APIResponse.not_found('Person not found')
    
    except Exception as e:
        logger.error(f"Error deleting person: {e}")
        return APIResponse.server_error(str(e))

