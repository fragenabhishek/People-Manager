"""
Note/interaction routes.
"""
from fastapi import APIRouter, Depends, Request

from deps import get_current_user
from schemas.note import NoteCreate
from utils import response_fastapi as R

router = APIRouter(prefix="/api/notes", tags=["Notes"])


def _svc(request: Request):
    return request.app.state.note_service


@router.get("/person/{person_id}")
def get_notes(person_id: str, request: Request, user_id: str = Depends(get_current_user)):
    notes = _svc(request).get_notes_for_person(person_id, user_id)
    return R.ok([n.to_dict() for n in notes])


@router.post("/person/{person_id}", status_code=201)
def create_note(person_id: str, body: NoteCreate, request: Request, user_id: str = Depends(get_current_user)):
    note = _svc(request).create_note(
        person_id=person_id, user_id=user_id,
        content=body.content, note_type=body.note_type,
    )
    return R.created(note.to_dict(), "Note added successfully")


@router.delete("/{note_id}")
def delete_note(note_id: str, request: Request, user_id: str = Depends(get_current_user)):
    success = _svc(request).delete_note(note_id, user_id)
    if not success:
        return R.not_found("Note not found")
    return R.ok(message="Note deleted")


@router.get("/activity")
def get_activity(request: Request, limit: int = 20, user_id: str = Depends(get_current_user)):
    activity = _svc(request).get_recent_activity(user_id, limit)
    return R.ok(activity)
