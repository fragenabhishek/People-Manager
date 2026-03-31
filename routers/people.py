"""
People/contact CRUD, tags, follow-ups, import/export.
"""
from fastapi import APIRouter, Depends, File, Request, UploadFile
from fastapi.responses import Response

from deps import get_current_user
from schemas.person import FollowUpRequest, PersonCreate, PersonUpdate, TagsRequest
from utils import response_fastapi as R

router = APIRouter(prefix="/api/people", tags=["People"])


def _svc(request: Request):
    return request.app.state.person_service


def _ie(request: Request):
    return request.app.state.import_export_service


# --- CRUD ---

@router.get("")
def get_people(request: Request, tag: str = None, user_id: str = Depends(get_current_user)):
    svc = _svc(request)
    if tag:
        people = svc.get_by_tag(tag, user_id)
    else:
        people = svc.get_all_people(user_id)
    return R.ok([p.to_dict() for p in people])


@router.get("/search/{query}")
def search_people(query: str, request: Request, user_id: str = Depends(get_current_user)):
    results = _svc(request).search_people(query, user_id)
    return R.ok([p.to_dict() for p in results])


@router.get("/tags")
def get_all_tags(request: Request, user_id: str = Depends(get_current_user)):
    return R.ok(_svc(request).get_all_tags(user_id))


@router.get("/followups")
def get_due_followups(request: Request, user_id: str = Depends(get_current_user)):
    people = _svc(request).get_due_followups(user_id)
    return R.ok([p.to_dict() for p in people])


@router.get("/dashboard/stats")
def dashboard_stats(request: Request, user_id: str = Depends(get_current_user)):
    return R.ok(_svc(request).get_dashboard_stats(user_id))


@router.get("/{person_id}")
def get_person(person_id: str, request: Request, user_id: str = Depends(get_current_user)):
    person = _svc(request).get_person_by_id(person_id, user_id)
    if not person:
        return R.not_found("Person not found")
    return R.ok(person.to_dict())


@router.post("", status_code=201)
def add_person(body: PersonCreate, request: Request, user_id: str = Depends(get_current_user)):
    person = _svc(request).create_person(user_id=user_id, **body.model_dump())
    return R.created(person.to_dict(), "Person created successfully")


@router.put("/{person_id}")
def update_person(person_id: str, body: PersonUpdate, request: Request, user_id: str = Depends(get_current_user)):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    person = _svc(request).update_person(person_id, user_id, **data)
    if not person:
        return R.not_found("Person not found")
    return R.ok(person.to_dict())


@router.delete("/{person_id}")
def delete_person(person_id: str, request: Request, user_id: str = Depends(get_current_user)):
    success = _svc(request).delete_person(person_id, user_id)
    if not success:
        return R.not_found("Person not found")
    return R.ok(message="Person deleted successfully")


# --- Tags ---

@router.post("/{person_id}/tags")
def add_tags(person_id: str, body: TagsRequest, request: Request, user_id: str = Depends(get_current_user)):
    tags = body.tags
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    person = _svc(request).add_tags(person_id, user_id, tags)
    if not person:
        return R.not_found("Person not found")
    return R.ok(person.to_dict())


@router.delete("/{person_id}/tags/{tag}")
def remove_tag(person_id: str, tag: str, request: Request, user_id: str = Depends(get_current_user)):
    person = _svc(request).remove_tag(person_id, user_id, tag)
    if not person:
        return R.not_found("Person not found")
    return R.ok(person.to_dict())


# --- Follow-ups ---

@router.put("/{person_id}/followup")
def set_follow_up(person_id: str, body: FollowUpRequest, request: Request, user_id: str = Depends(get_current_user)):
    person = _svc(request).set_follow_up(person_id, user_id, date=body.date or "", frequency_days=body.frequency_days or 0)
    if not person:
        return R.not_found("Person not found")
    return R.ok(person.to_dict())


@router.post("/{person_id}/followup/complete")
def complete_follow_up(person_id: str, request: Request, user_id: str = Depends(get_current_user)):
    person = _svc(request).complete_follow_up(person_id, user_id)
    if not person:
        return R.not_found("Person not found")
    return R.ok(person.to_dict())


# --- Import/Export ---

@router.post("/import/csv")
async def import_csv(request: Request, file: UploadFile = File(...), user_id: str = Depends(get_current_user)):
    if not file.filename or not file.filename.endswith(".csv"):
        return R.validation_error("File must be CSV format")
    content = (await file.read()).decode("utf-8")
    imported, skipped, errors = _ie(request).import_csv(content, user_id)
    return R.ok({"imported": imported, "skipped": skipped, "errors": errors[:10]})


@router.get("/export/csv")
def export_csv(request: Request, user_id: str = Depends(get_current_user)):
    csv_content = _ie(request).export_csv(user_id)
    return Response(csv_content, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=contacts.csv"})


@router.get("/export/json")
def export_json(request: Request, user_id: str = Depends(get_current_user)):
    json_content = _ie(request).export_json(user_id)
    return Response(json_content, media_type="application/json", headers={"Content-Disposition": "attachment; filename=contacts.json"})
