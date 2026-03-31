"""
SQLAlchemy ORM table definitions.
These map directly to database tables. Domain dataclasses remain the
canonical representation used by services; repositories convert between them.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


def _uuid():
    return str(uuid.uuid4())


class UserRow(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    mfa_secret: Mapped[str | None] = mapped_column(String(64), nullable=True)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    people: Mapped[list["PersonRow"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    notes: Mapped[list["NoteRow"]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class PersonRow(Base):
    __tablename__ = "people"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), default="")
    phone: Mapped[str] = mapped_column(String(50), default="")
    company: Mapped[str] = mapped_column(String(255), default="")
    job_title: Mapped[str] = mapped_column(String(255), default="")
    location: Mapped[str] = mapped_column(String(255), default="")
    linkedin_url: Mapped[str] = mapped_column(String(500), default="")
    twitter_handle: Mapped[str] = mapped_column(String(100), default="")
    website: Mapped[str] = mapped_column(String(500), default="")
    details: Mapped[str] = mapped_column(Text, default="")
    how_we_met: Mapped[str] = mapped_column(Text, default="")
    profile_image_url: Mapped[str] = mapped_column(String(500), default="")
    birthday: Mapped[str] = mapped_column(String(20), default="")
    anniversary: Mapped[str] = mapped_column(String(20), default="")
    met_at: Mapped[str] = mapped_column(String(20), default="")
    tags_csv: Mapped[str] = mapped_column(Text, default="")
    next_follow_up: Mapped[str] = mapped_column(String(20), default="")
    follow_up_frequency_days: Mapped[int] = mapped_column(Integer, default=0)
    relationship_score: Mapped[float] = mapped_column(Float, default=0.0)
    relationship_status: Mapped[str] = mapped_column(String(20), default="new")
    last_interaction_at: Mapped[str] = mapped_column(String(30), default="")
    interaction_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[str] = mapped_column(String(30), default=lambda: datetime.now().isoformat())
    updated_at: Mapped[str] = mapped_column(String(30), default=lambda: datetime.now().isoformat())

    owner: Mapped["UserRow"] = relationship(back_populates="people")
    notes: Mapped[list["NoteRow"]] = relationship(back_populates="person", cascade="all, delete-orphan")


class NoteRow(Base):
    __tablename__ = "notes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    person_id: Mapped[str] = mapped_column(String(36), ForeignKey("people.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    note_type: Mapped[str] = mapped_column(String(20), default="general")
    created_at: Mapped[str] = mapped_column(String(30), default=lambda: datetime.now().isoformat())

    person: Mapped["PersonRow"] = relationship(back_populates="notes")
    owner: Mapped["UserRow"] = relationship(back_populates="notes")
