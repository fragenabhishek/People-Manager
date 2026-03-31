"""
Tests for SQLAlchemy repository implementations using SQLite in-memory.
Validates that the SQL repos fulfill the same interface contract as JSON repos.
"""
import pytest

from models.database import Base, create_tables, drop_tables, get_session_factory, init_db
from models.note import Note
from models.person import Person
from models.tables import NoteRow, PersonRow, UserRow  # noqa: F401
from models.user import User
from repositories.sql_note_repository import SqlNoteRepository
from repositories.sql_person_repository import SqlPersonRepository
from repositories.sql_user_repository import SqlUserRepository


@pytest.fixture(autouse=True)
def sql_setup():
    """Create fresh in-memory SQLite for each test."""
    init_db("sqlite:///:memory:")
    create_tables()
    yield
    drop_tables()


@pytest.fixture
def sf():
    return get_session_factory()


@pytest.fixture
def user_repo(sf):
    return SqlUserRepository(sf)


@pytest.fixture
def person_repo(sf):
    return SqlPersonRepository(sf)


@pytest.fixture
def note_repo(sf):
    return SqlNoteRepository(sf)


# --- User Repository ---

def test_create_and_find_user(user_repo):
    user = User(username="alice", password_hash="hash123", email="alice@test.com")
    created = user_repo.create(user)
    assert created.id is not None
    assert created.username == "alice"

    found = user_repo.find_by_id(created.id)
    assert found is not None
    assert found.email == "alice@test.com"


def test_find_by_username(user_repo):
    user_repo.create(User(username="bob", password_hash="hash"))
    found = user_repo.find_by_username("bob")
    assert found is not None
    assert found.username == "bob"

    assert user_repo.find_by_username("nobody") is None


def test_update_user(user_repo):
    user = user_repo.create(User(username="carol", password_hash="old_hash"))
    user.password_hash = "new_hash"
    updated = user_repo.update(user.id, user)
    assert updated.password_hash == "new_hash"


def test_delete_user(user_repo):
    user = user_repo.create(User(username="dave", password_hash="hash"))
    assert user_repo.delete(user.id) is True
    assert user_repo.find_by_id(user.id) is None
    assert user_repo.delete("nonexistent") is False


def test_find_all_users(user_repo):
    user_repo.create(User(username="u1", password_hash="h"))
    user_repo.create(User(username="u2", password_hash="h"))
    assert len(user_repo.find_all()) == 2


# --- Person Repository ---

def test_create_and_find_person(user_repo, person_repo):
    user = user_repo.create(User(username="owner", password_hash="h"))
    person = Person(name="John Doe", user_id=user.id, company="Acme", tags=["friend", "work"])
    created = person_repo.create(person)
    assert created.id is not None
    assert created.tags == ["friend", "work"]

    found = person_repo.find_by_id(created.id)
    assert found.name == "John Doe"
    assert found.company == "Acme"


def test_update_person(user_repo, person_repo):
    user = user_repo.create(User(username="owner", password_hash="h"))
    person = person_repo.create(Person(name="Jane", user_id=user.id))
    person.company = "Updated Corp"
    updated = person_repo.update(person.id, person)
    assert updated.company == "Updated Corp"


def test_delete_person(user_repo, person_repo):
    user = user_repo.create(User(username="owner", password_hash="h"))
    person = person_repo.create(Person(name="Del Me", user_id=user.id))
    assert person_repo.delete(person.id) is True
    assert person_repo.find_by_id(person.id) is None


def test_search_by_name(user_repo, person_repo):
    user = user_repo.create(User(username="owner", password_hash="h"))
    person_repo.create(Person(name="Alice Smith", user_id=user.id))
    person_repo.create(Person(name="Bob Jones", user_id=user.id))
    results = person_repo.search_by_name("alice", user.id)
    assert len(results) == 1
    assert results[0].name == "Alice Smith"


def test_search_full_text(user_repo, person_repo):
    user = user_repo.create(User(username="owner", password_hash="h"))
    person_repo.create(Person(name="Carol", user_id=user.id, company="TechCorp"))
    person_repo.create(Person(name="Dan", user_id=user.id, company="BizInc"))
    results = person_repo.search("tech", user.id)
    assert len(results) == 1
    assert results[0].name == "Carol"


def test_tags_roundtrip(user_repo, person_repo):
    user = user_repo.create(User(username="owner", password_hash="h"))
    person = person_repo.create(Person(name="Taggy", user_id=user.id, tags=["a", "b", "c"]))
    found = person_repo.find_by_id(person.id)
    assert found.tags == ["a", "b", "c"]

    all_tags = person_repo.get_all_tags(user.id)
    assert all_tags == ["a", "b", "c"]


def test_find_by_tag(user_repo, person_repo):
    user = user_repo.create(User(username="owner", password_hash="h"))
    person_repo.create(Person(name="P1", user_id=user.id, tags=["vip"]))
    person_repo.create(Person(name="P2", user_id=user.id, tags=["regular"]))
    results = person_repo.find_by_tag("vip", user.id)
    assert len(results) == 1


def test_find_due_followups(user_repo, person_repo):
    user = user_repo.create(User(username="owner", password_hash="h"))
    person_repo.create(Person(name="Due", user_id=user.id, next_follow_up="2020-01-01"))
    person_repo.create(Person(name="Future", user_id=user.id, next_follow_up="2099-01-01"))
    person_repo.create(Person(name="None", user_id=user.id))
    results = person_repo.find_due_followups(user.id)
    assert len(results) == 1
    assert results[0].name == "Due"


# --- Note Repository ---

def test_create_and_find_note(user_repo, person_repo, note_repo):
    user = user_repo.create(User(username="owner", password_hash="h"))
    person = person_repo.create(Person(name="Contact", user_id=user.id))
    note = Note(person_id=person.id, user_id=user.id, content="Met at conference")
    created = note_repo.create(note)
    assert created.id is not None

    found = note_repo.find_by_id(created.id)
    assert found.content == "Met at conference"


def test_find_by_person(user_repo, person_repo, note_repo):
    user = user_repo.create(User(username="owner", password_hash="h"))
    p1 = person_repo.create(Person(name="P1", user_id=user.id))
    p2 = person_repo.create(Person(name="P2", user_id=user.id))
    note_repo.create(Note(person_id=p1.id, user_id=user.id, content="Note A"))
    note_repo.create(Note(person_id=p1.id, user_id=user.id, content="Note B"))
    note_repo.create(Note(person_id=p2.id, user_id=user.id, content="Note C"))

    notes = note_repo.find_by_person(p1.id, user.id)
    assert len(notes) == 2


def test_delete_note(user_repo, person_repo, note_repo):
    user = user_repo.create(User(username="owner", password_hash="h"))
    person = person_repo.create(Person(name="P", user_id=user.id))
    note = note_repo.create(Note(person_id=person.id, user_id=user.id, content="X"))
    assert note_repo.delete(note.id) is True
    assert note_repo.find_by_id(note.id) is None


def test_delete_by_person(user_repo, person_repo, note_repo):
    user = user_repo.create(User(username="owner", password_hash="h"))
    person = person_repo.create(Person(name="P", user_id=user.id))
    note_repo.create(Note(person_id=person.id, user_id=user.id, content="A"))
    note_repo.create(Note(person_id=person.id, user_id=user.id, content="B"))
    count = note_repo.delete_by_person(person.id)
    assert count == 2
    assert len(note_repo.find_by_person(person.id, user.id)) == 0


def test_count_by_person(user_repo, person_repo, note_repo):
    user = user_repo.create(User(username="owner", password_hash="h"))
    person = person_repo.create(Person(name="P", user_id=user.id))
    note_repo.create(Note(person_id=person.id, user_id=user.id, content="1"))
    note_repo.create(Note(person_id=person.id, user_id=user.id, content="2"))
    assert note_repo.count_by_person(person.id) == 2
