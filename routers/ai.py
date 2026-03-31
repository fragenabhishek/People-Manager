"""
AI-powered feature routes.
"""
from fastapi import APIRouter, Depends, Request

from deps import get_current_user
from schemas.note import AskRequest
from utils import response_fastapi as R

router = APIRouter(prefix="/api", tags=["AI"])


def _ai(request: Request):
    return request.app.state.ai_service


def _people(request: Request):
    return request.app.state.person_service


def _notes(request: Request):
    return request.app.state.note_service


@router.post("/people/{person_id}/summary")
def generate_summary(person_id: str, request: Request, user_id: str = Depends(get_current_user)):
    if not _ai(request).is_enabled():
        return R.err("AI feature not configured. Set GEMINI_API_KEY.", 503)
    person = _people(request).get_person_by_id(person_id, user_id)
    if not person:
        return R.not_found("Person not found")
    notes = _notes(request).get_notes_for_person(person_id, user_id) if _notes(request) else []
    result = _ai(request).generate_person_blueprint(person, notes)
    return R.ok(result)


@router.post("/ask")
def central_ask(body: AskRequest, request: Request, user_id: str = Depends(get_current_user)):
    if not _ai(request).is_enabled():
        return R.err("AI feature not configured. Set GEMINI_API_KEY.", 503)
    people = _people(request).get_all_people(user_id)
    if not people:
        return R.validation_error("No people in your contacts yet")
    result = _ai(request).answer_question(body.question, people)
    return R.ok(result)


@router.post("/people/{person_id}/suggest-tags")
def suggest_tags(person_id: str, request: Request, user_id: str = Depends(get_current_user)):
    if not _ai(request).is_enabled():
        return R.err("AI feature not configured. Set GEMINI_API_KEY.", 503)
    person = _people(request).get_person_by_id(person_id, user_id)
    if not person:
        return R.not_found("Person not found")
    tags = _ai(request).suggest_tags(person)
    return R.ok({"tags": tags})
