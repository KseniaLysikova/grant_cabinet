import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Date,
    Enum,
    ForeignKey,
    Float,
    Boolean,
)
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    applicant = "applicant"


class ApplicationStatus(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"
    in_review = "in_review"
    approved = "approved"
    rejected = "rejected"


class CompetitionStatus(str, enum.Enum):
    open = "open"
    closed = "closed"
    archived = "archived"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.applicant)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    applications = relationship("Application", back_populates="owner")


class Competition(Base):
    __tablename__ = "competitions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    deadline = Column(Date, nullable=False)
    status = Column(Enum(CompetitionStatus), nullable=False, default=CompetitionStatus.open)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    applications = relationship("Application", back_populates="competition")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    project_goal = Column(Text, nullable=True)
    requested_amount = Column(Integer, nullable=True)
    status = Column(Enum(ApplicationStatus), nullable=False, default=ApplicationStatus.draft)

    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    competition_id = Column(Integer, ForeignKey("competitions.id", ondelete="RESTRICT"), nullable=False)

    submitted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="applications")
    competition = relationship("Competition", back_populates="applications")
    files = relationship("ApplicationFile", back_populates="application", cascade="all, delete-orphan")
    ai_review = relationship("AIReview", back_populates="application", uselist=False, cascade="all, delete-orphan")


class ApplicationFile(Base):
    __tablename__ = "application_files"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    original_name = Column(String(255), nullable=False)
    stored_name = Column(String(255), nullable=False)
    mime_type = Column(String(255), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    application = relationship("Application", back_populates="files")


class AIReview(Base):
    __tablename__ = "ai_reviews"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), unique=True, nullable=False)
    score = Column(Float, nullable=False, default=0.0)
    summary = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    application = relationship("Application", back_populates="ai_review")