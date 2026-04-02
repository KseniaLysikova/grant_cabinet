from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User, Competition, UserRole, CompetitionStatus
from app.services.security import hash_password


def seed_data(db: Session) -> None:
    admin = db.scalar(select(User).where(User.email == "admin@example.com"))
    applicant = db.scalar(select(User).where(User.email == "applicant@example.com"))

    if not admin:
        db.add(
            User(
                full_name="Admin User",
                email="admin@example.com",
                password_hash=hash_password("admin123"),
                role=UserRole.admin,
            )
        )

    if not applicant:
        db.add(
            User(
                full_name="Applicant User",
                email="applicant@example.com",
                password_hash=hash_password("applicant123"),
                role=UserRole.applicant,
            )
        )

    competition = db.scalar(select(Competition).where(Competition.title == "Конкурс социальных инициатив 2026"))
    if not competition:
        db.add(
            Competition(
                title="Конкурс социальных инициатив 2026",
                description="Грантовый конкурс для некоммерческих и образовательных проектов.",
                deadline=date.today() + timedelta(days=30),
                status=CompetitionStatus.open,
            )
        )

    db.commit()